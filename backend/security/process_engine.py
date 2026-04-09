"""Process collection engine for Phase 3."""

from __future__ import annotations

import psutil

from .sec_models import ProcessInfo
from .sec_utils import safe_proc_attr

MAX_PROCESSES = 40


def _rss_to_mb(rss_bytes: int) -> float:
    """Convert RSS bytes to MB."""
    return float(max(rss_bytes, 0)) / (1024 * 1024)


def get_processes() -> list[ProcessInfo]:
    """Collect running processes and return top entries by CPU or memory."""
    processes: list[ProcessInfo] = []

    for proc in psutil.process_iter(attrs=["pid", "name", "exe"]):
        try:
            pid = int(safe_proc_attr(proc, "pid", 0) or 0)
            if pid <= 0:
                continue

            name = str(safe_proc_attr(proc, "name", "unknown") or "unknown")
            exe_path = str(safe_proc_attr(proc, "exe", "") or "")
            cpu_percent = float(proc.cpu_percent(interval=0.1) or 0.0)

            mem_info = proc.memory_info()
            rss_bytes = int(getattr(mem_info, "rss", 0) or 0)
            ram_mb = _rss_to_mb(rss_bytes)

            processes.append(
                ProcessInfo(
                    pid=pid,
                    name=name,
                    cpu_percent=cpu_percent,
                    ram_mb=ram_mb,
                    exe_path=exe_path,
                )
            )
        except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
            continue

    processes.sort(key=lambda p: (p.cpu_percent, p.ram_mb), reverse=True)
    return processes[:MAX_PROCESSES]


def analyze_processes() -> dict:
    """Compatibility wrapper for older pipeline calls."""
    items = get_processes()
    return {
        "processes": [
            {
                "pid": p.pid,
                "name": p.name,
                "cpu_percent": p.cpu_percent,
                "ram_mb": p.ram_mb,
                "exe_path": p.exe_path,
                "classification": p.classification,
                "is_background": p.is_background,
                "is_idle": p.is_idle,
            }
            for p in items
        ]
    }
