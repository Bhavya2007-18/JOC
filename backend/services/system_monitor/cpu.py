from typing import Any, Dict, List, Optional
import time

import psutil


_CACHE_TTL_SECONDS = 1.0
_last_cpu_stats: Optional[Dict[str, Any]] = None
_last_cpu_timestamp: float = 0.0


def _get_load_average() -> Optional[Dict[str, float]]:
    """Return system load average where supported."""
    try:
        one, five, fifteen = psutil.getloadavg()
        return {"one_min": float(one), "five_min": float(five), "fifteen_min": float(fifteen)}
    except (AttributeError, OSError):
        return None


def get_cpu_stats() -> Dict[str, Any]:
    """Collect current CPU usage statistics with light caching."""
    global _last_cpu_stats, _last_cpu_timestamp

    now = time.time()
    if _last_cpu_stats is not None and now - _last_cpu_timestamp <= _CACHE_TTL_SECONDS:
        return _last_cpu_stats

    overall_usage = float(psutil.cpu_percent(interval=0.2))
    per_core_usage: List[float] = [float(value) for value in psutil.cpu_percent(interval=None, percpu=True)]
    load_average = _get_load_average()

    stats: Dict[str, Any] = {
        "usage_percent": overall_usage,
        "per_core_usage": per_core_usage,
        "load_average": load_average,
    }

    _last_cpu_stats = stats
    _last_cpu_timestamp = now
    return stats

