from typing import Any, Dict, Optional
import time

import psutil


_CACHE_TTL_SECONDS = 1.0
_last_memory_stats: Optional[Dict[str, Any]] = None
_last_memory_timestamp: float = 0.0


def get_memory_stats() -> Dict[str, Any]:
    """Collect current memory usage statistics with light caching."""
    global _last_memory_stats, _last_memory_timestamp

    now = time.time()
    if _last_memory_stats is not None and now - _last_memory_timestamp <= _CACHE_TTL_SECONDS:
        return _last_memory_stats

    virtual_memory = psutil.virtual_memory()

    stats: Dict[str, Any] = {
        "total": int(virtual_memory.total),
        "used": int(virtual_memory.used),
        "available": int(virtual_memory.available),
        "percent": float(virtual_memory.percent),
    }

    _last_memory_stats = stats
    _last_memory_timestamp = now
    return stats

