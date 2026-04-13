"""Unit tests for process collection engine."""

from types import SimpleNamespace
import unittest
from unittest.mock import patch

import psutil

from security.process_engine import MAX_PROCESSES, classify_process, get_processes
from security.sec_models import ProcessInfo


class _FakeProcess:
    def __init__(self, pid: int, name: str, exe: str, cpu: float, rss: int):
        self.info = {"pid": pid, "name": name, "exe": exe}
        self._cpu = cpu
        self._rss = rss

    def cpu_percent(self, interval: float = 0.1) -> float:
        return self._cpu

    def memory_info(self):
        return SimpleNamespace(rss=self._rss)


class _DeniedProcess(_FakeProcess):
    def memory_info(self):
        raise psutil.AccessDenied(pid=self.info.get("pid"), name=self.info.get("name"))


class TestProcessEngine(unittest.TestCase):
    def test_returns_process_info_objects(self) -> None:
        fake_items = [
            _FakeProcess(10, "alpha.exe", "C:/alpha.exe", 30.0, 300 * 1024 * 1024),
            _FakeProcess(11, "beta.exe", "C:/beta.exe", 20.0, 200 * 1024 * 1024),
            _FakeProcess(12, "gamma.exe", "C:/gamma.exe", 10.0, 100 * 1024 * 1024),
        ]

        with patch("security.process_engine.psutil.process_iter", return_value=fake_items):
            results = get_processes()

        self.assertEqual(len(results), 3)
        self.assertTrue(all(isinstance(item, ProcessInfo) for item in results))

    def test_skips_permission_denied_processes(self) -> None:
        fake_items = [
            _DeniedProcess(20, "locked.exe", "", 40.0, 100 * 1024 * 1024),
            _FakeProcess(21, "ok.exe", "C:/ok.exe", 5.0, 50 * 1024 * 1024),
        ]

        with patch("security.process_engine.psutil.process_iter", return_value=fake_items):
            results = get_processes()

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].pid, 21)

    def test_limit_and_sorting(self) -> None:
        fake_items = [
            _FakeProcess(i, f"proc{i}.exe", f"C:/proc{i}.exe", float(i), i * 1024 * 1024)
            for i in range(1, 80)
        ]

        with patch("security.process_engine.psutil.process_iter", return_value=fake_items):
            results = get_processes()

        self.assertEqual(len(results), MAX_PROCESSES)
        self.assertGreaterEqual(results[0].cpu_percent, results[-1].cpu_percent)
        self.assertEqual(results[0].pid, 79)

    def test_classify_known_safe(self) -> None:
        proc = ProcessInfo(
            pid=101,
            name="python.exe",
            cpu_percent=2.0,
            ram_mb=150.0,
            exe_path="C:/Python/python.exe",
        )

        classified = classify_process(proc)
        self.assertEqual(classified.classification, "known_safe")
        self.assertTrue(classified.is_background)
        self.assertFalse(classified.is_idle)

    def test_classify_suspicious_and_idle(self) -> None:
        proc = ProcessInfo(
            pid=202,
            name="random_tool.exe",
            cpu_percent=0.2,
            ram_mb=1500.0,
            exe_path="C:/Temp/random_tool.exe",
        )

        classified = classify_process(proc)
        self.assertEqual(classified.classification, "suspicious")
        self.assertTrue(classified.is_background)
        self.assertTrue(classified.is_idle)


if __name__ == "__main__":
    unittest.main()