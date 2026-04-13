"""Unit tests for rule-based threat detection."""

import unittest

from backend.security.sec_models import ProcessInfo, ThreatSeverity
from backend.security.threat_engine import detect_threats


class TestThreatEngine(unittest.TestCase):
    def test_suspicious_process_and_background_activity(self) -> None:
        proc = ProcessInfo(
            pid=101,
            name="bad.exe",
            cpu_percent=90.0,
            ram_mb=1000.0,
            exe_path="C:/bad.exe",
            classification="suspicious",
            is_background=True,
            is_idle=False,
        )

        threats = detect_threats([proc])
        categories = {threat.category for threat in threats}

        self.assertEqual(len(threats), 2)
        self.assertIn("suspicious_process", categories)
        self.assertIn("background_suspicious", categories)
        self.assertIn("101_suspicious_process", {t.id for t in threats})
        self.assertIn("101_background_suspicious", {t.id for t in threats})

    def test_unknown_process(self) -> None:
        proc = ProcessInfo(
            pid=102,
            name="mystery.exe",
            cpu_percent=4.0,
            ram_mb=120.0,
            exe_path="C:/mystery.exe",
            classification="unknown",
            is_background=False,
            is_idle=False,
        )

        threats = detect_threats([proc])

        self.assertEqual(len(threats), 1)
        self.assertEqual(threats[0].category, "unknown_process")
        self.assertEqual(threats[0].id, "102_unknown_process")
        self.assertEqual(threats[0].severity, ThreatSeverity.MEDIUM)
        self.assertIn("not recognized", threats[0].description)

    def test_idle_resource_hog(self) -> None:
        proc = ProcessInfo(
            pid=103,
            name="memoryhog.exe",
            cpu_percent=0.2,
            ram_mb=2048.0,
            exe_path="C:/memoryhog.exe",
            classification="known_safe",
            is_background=True,
            is_idle=True,
        )

        threats = detect_threats([proc])

        self.assertEqual(len(threats), 1)
        self.assertEqual(threats[0].category, "idle_resource_hog")
        self.assertEqual(threats[0].id, "103_idle_resource_hog")
        self.assertEqual(threats[0].severity, ThreatSeverity.MEDIUM)

    def test_avoids_duplicate_same_pid_and_category(self) -> None:
        proc_a = ProcessInfo(
            pid=200,
            name="dup.exe",
            cpu_percent=60.0,
            ram_mb=900.0,
            exe_path="C:/dup.exe",
            classification="suspicious",
            is_background=False,
            is_idle=False,
        )
        proc_b = ProcessInfo(
            pid=200,
            name="dup.exe",
            cpu_percent=70.0,
            ram_mb=1100.0,
            exe_path="C:/dup.exe",
            classification="suspicious",
            is_background=False,
            is_idle=False,
        )

        threats = detect_threats([proc_a, proc_b])

        self.assertEqual(len(threats), 1)
        self.assertEqual(threats[0].id, "200_suspicious_process")


if __name__ == "__main__":
    unittest.main()