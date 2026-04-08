from typing import Any, Dict, List, Optional
import time

import psutil


_CACHE_TTL_SECONDS = 1.0
_last_disk_stats: Optional[Dict[str, Any]] = None
_last_disk_timestamp: float = 0.0


def _get_mountpoints() -> List[str]:
    """Return a list of relevant disk mountpoints for aggregation."""
    mountpoints: List[str] = []
    for partition in psutil.disk_partitions(all=False):
        if not partition.fstype:
            continue
        if "cdrom" in (partition.opts or "").lower():
            continue
        mountpoints.append(partition.mountpoint)
    unique_mounts: List[str] = []
    for mount in mountpoints:
        if mount not in unique_mounts:
            unique_mounts.append(mount)
    return unique_mounts


def get_disk_stats() -> Dict[str, Any]:
    """Collect aggregated disk usage statistics with light caching."""
    global _last_disk_stats, _last_disk_timestamp

    now = time.time()
    if _last_disk_stats is not None and now - _last_disk_timestamp <= _CACHE_TTL_SECONDS:
        return _last_disk_stats

    total = 0
    used = 0
    free = 0

    for mountpoint in _get_mountpoints():
        try:
            usage = psutil.disk_usage(mountpoint)
        except PermissionError:
            continue
        total += int(usage.total)
        used += int(usage.used)
        free += int(usage.free)

    percent = float((used / total) * 100.0) if total > 0 else 0.0

    stats: Dict[str, Any] = {
        "total": total,
        "used": used,
        "free": free,
        "percent": percent,
    }

    _last_disk_stats = stats
    _last_disk_timestamp = now
    return stats

