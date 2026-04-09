"""Process collection and behavior analysis stage."""

import importlib

from .sec_config import KNOWN_SAFE_PROCESSES, THRESHOLDS
from .sec_utils import current_timestamp, safe_process_attr


def collect_processes() -> list[dict]:
    """Collect running process snapshots from psutil."""
    try:
        psutil = importlib.import_module("psutil")
    except Exception:
        return []

    items: list[dict] = []
    for proc in psutil.process_iter(attrs=["pid", "name", "cpu_percent", "memory_percent"]):
        name = (safe_process_attr(proc, "name", "unknown") or "unknown").lower()
        items.append(
            {
                "pid": safe_process_attr(proc, "pid"),
                "name": name,
                "cpu_percent": float(safe_process_attr(proc, "cpu_percent", 0.0) or 0.0),
                "ram_percent": float(safe_process_attr(proc, "memory_percent", 0.0) or 0.0),
                "is_known": name in KNOWN_SAFE_PROCESSES,
            }
        )
    return items


def analyze_processes() -> dict:
    """Build basic behavior signals from process data."""
    processes = collect_processes()
    high_usage = [
        process
        for process in processes
        if process["cpu_percent"] >= THRESHOLDS["cpu_percent"]
        or process["ram_percent"] >= THRESHOLDS["ram_percent"]
    ]
    unknown_processes = [process for process in processes if not process["is_known"]]

    return {
        "timestamp": current_timestamp(),
        "processes": processes,
        "high_usage": high_usage,
        "unknown_processes": unknown_processes,
    }
