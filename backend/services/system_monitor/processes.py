from typing import Any, Dict, List, Optional
import time

import psutil


_CACHE_TTL_SECONDS = 1.0
_last_process_list: Optional[List[Dict[str, Any]]] = None
_last_process_timestamp: float = 0.0


def get_top_processes(limit: int = 10) -> List[Dict[str, Any]]:
    """Return the top N processes sorted by CPU usage."""
    global _last_process_list, _last_process_timestamp

    now = time.time()
    if _last_process_list is not None and now - _last_process_timestamp <= _CACHE_TTL_SECONDS:
        return _last_process_list[:limit]

    processes: List[Dict[str, Any]] = []

    for proc in psutil.process_iter(attrs=["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            info = proc.info
            cpu_percent = info.get("cpu_percent")
            if cpu_percent is None:
                cpu_percent = proc.cpu_percent(interval=None)

            memory_percent = info.get("memory_percent") or 0.0

            processes.append(
                {
                    "pid": int(info["pid"]),
                    "name": info.get("name") or "unknown",
                    "cpu_percent": float(cpu_percent),
                    "memory_percent": float(memory_percent),
                }
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    processes.sort(key=lambda process: (process["cpu_percent"], process["memory_percent"]), reverse=True)
    top_processes = processes[:limit]

    _last_process_list = top_processes
    _last_process_timestamp = now
    return top_processes

