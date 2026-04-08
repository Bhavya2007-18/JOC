from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Tuple

from utils.logger import get_logger

from .behavior_tracker import load_logs


logger = get_logger("intelligence.pattern_analyzer")


def _calculate_hourly_stats(entries: List[Dict[str, Any]]) -> Dict[int, Tuple[float, float]]:
    totals: Dict[int, Tuple[float, float, int]] = {}
    for entry in entries:
        hour = int(entry.get("hour_of_day", 0))
        cpu = float(entry.get("cpu_percent", 0.0))
        mem = float(entry.get("memory_percent", 0.0))
        total_cpu, total_mem, count = totals.get(hour, (0.0, 0.0, 0))
        totals[hour] = (total_cpu + cpu, total_mem + mem, count + 1)

    averaged: Dict[int, Tuple[float, float]] = {}
    for hour, (total_cpu, total_mem, count) in totals.items():
        if count <= 0:
            continue
        averaged[hour] = (total_cpu / count, total_mem / count)
    return averaged


def _extract_frequent_apps(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    counts: Counter[str] = Counter()
    cpu_totals: defaultdict[str, float] = defaultdict(float)

    for entry in entries:
        for process in entry.get("top_processes", []):
            name = str(process.get("name", "unknown"))
            cpu = float(process.get("cpu_percent", 0.0))
            counts[name] += 1
            cpu_totals[name] += cpu

    frequent: List[Dict[str, Any]] = []
    for name, count in counts.items():
        avg_cpu = cpu_totals[name] / max(count, 1)
        frequent.append(
            {
                "name": name,
                "count": int(count),
                "average_cpu_percent": float(avg_cpu),
            }
        )

    frequent.sort(key=lambda item: (item["count"], item["average_cpu_percent"]), reverse=True)
    return frequent[:10]


def compute_patterns(window_seconds: Optional[int] = None) -> Dict[str, Any]:
    entries = load_logs(window_seconds=window_seconds)
    if not entries:
        return {
            "average_cpu_percent": 0.0,
            "average_memory_percent": 0.0,
            "peak_hours": [],
            "idle_hours": [],
            "frequent_apps": [],
            "cpu_memory_timeseries": [],
        }

    cpu_values = [float(entry.get("cpu_percent", 0.0)) for entry in entries]
    mem_values = [float(entry.get("memory_percent", 0.0)) for entry in entries]

    average_cpu = sum(cpu_values) / len(cpu_values)
    average_mem = sum(mem_values) / len(mem_values)

    hourly_stats = _calculate_hourly_stats(entries)

    peak_hours: List[Dict[str, Any]] = []
    for hour, (avg_cpu, avg_mem) in hourly_stats.items():
        peak_hours.append(
            {
                "hour": int(hour),
                "average_cpu_percent": float(avg_cpu),
                "average_memory_percent": float(avg_mem),
            }
        )
    peak_hours.sort(key=lambda item: item["average_cpu_percent"], reverse=True)

    idle_hours = [
        hour
        for hour, (avg_cpu, _) in hourly_stats.items()
        if avg_cpu < max(10.0, average_cpu * 0.5)
    ]
    idle_hours.sort()

    frequent_apps = _extract_frequent_apps(entries)

    timeseries: List[Dict[str, Any]] = []
    for entry in entries:
        timeseries.append(
            {
                "timestamp": float(entry.get("timestamp", 0.0)),
                "cpu_percent": float(entry.get("cpu_percent", 0.0)),
                "memory_percent": float(entry.get("memory_percent", 0.0)),
            }
        )

    logger.info(
        "Computed patterns entries=%s avg_cpu=%.2f avg_mem=%.2f",
        len(entries),
        average_cpu,
        average_mem,
    )

    return {
        "average_cpu_percent": float(average_cpu),
        "average_memory_percent": float(average_mem),
        "peak_hours": peak_hours[:6],
        "idle_hours": idle_hours,
        "frequent_apps": frequent_apps,
        "cpu_memory_timeseries": timeseries,
    }
