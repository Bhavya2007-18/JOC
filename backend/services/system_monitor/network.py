from typing import Any, Dict, Optional
import time

import psutil


_CACHE_TTL_SECONDS = 1.0
_last_network_stats: Optional[Dict[str, Any]] = None
_last_network_timestamp: float = 0.0


def get_network_stats() -> Dict[str, Any]:
    """Collect basic network I/O statistics with light caching."""
    global _last_network_stats, _last_network_timestamp

    now = time.time()
    if _last_network_stats is not None and now - _last_network_timestamp <= _CACHE_TTL_SECONDS:
        return _last_network_stats

    counters = psutil.net_io_counters()

    if counters is None:
        stats: Dict[str, Any] = {"bytes_sent": 0, "bytes_received": 0}
    else:
        stats = {
            "bytes_sent": int(counters.bytes_sent),
            "bytes_received": int(counters.bytes_recv),
        }

    _last_network_stats = stats
    _last_network_timestamp = now
    return stats

