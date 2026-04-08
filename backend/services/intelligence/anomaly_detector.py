from typing import Any, Dict, List, Optional

from utils.logger import get_logger

from .behavior_tracker import load_logs
from .pattern_analyzer import compute_patterns


logger = get_logger("intelligence.anomaly_detector")


def detect_anomalies(window_seconds: Optional[int] = None) -> List[Dict[str, Any]]:
    entries = load_logs(window_seconds=window_seconds)
    if not entries:
        return []

    patterns = compute_patterns(window_seconds=window_seconds)
    avg_cpu = float(patterns.get("average_cpu_percent", 0.0))

    frequent_apps = {item["name"] for item in patterns.get("frequent_apps", [])}
    idle_hours = set(patterns.get("idle_hours", []))

    anomalies: List[Dict[str, Any]] = []

    for entry in entries:
        timestamp = float(entry.get("timestamp", 0.0))
        hour = int(entry.get("hour_of_day", 0))
        cpu = float(entry.get("cpu_percent", 0.0))
        mem = float(entry.get("memory_percent", 0.0))
        processes = entry.get("top_processes", [])

        cpu_spike_threshold = avg_cpu + 25.0
        if cpu > max(cpu_spike_threshold, 70.0):
            severity = "high" if cpu > max(cpu_spike_threshold + 20.0, 90.0) else "medium"
            anomalies.append(
                {
                    "id": f"CPU_SPIKE_{int(timestamp)}",
                    "type": "cpu_spike",
                    "timestamp": timestamp,
                    "description": f"CPU usage {cpu:.1f}% exceeds normal average {avg_cpu:.1f}%",
                    "severity": severity,
                    "data": {
                        "cpu_percent": cpu,
                        "average_cpu_percent": avg_cpu,
                        "memory_percent": mem,
                        "hour_of_day": hour,
                    },
                }
            )

        for process in processes:
            name = str(process.get("name", "unknown"))
            proc_cpu = float(process.get("cpu_percent", 0.0))

            if proc_cpu < 40.0:
                continue

            if name not in frequent_apps:
                anomalies.append(
                    {
                        "id": f"UNKNOWN_HIGH_CPU_{name}_{int(timestamp)}",
                        "type": "unknown_high_cpu_process",
                        "timestamp": timestamp,
                        "description": f"Process {name} uses {proc_cpu:.1f}% CPU and is not a frequent app",
                        "severity": "medium",
                        "data": {
                            "process_name": name,
                            "cpu_percent": proc_cpu,
                            "hour_of_day": hour,
                        },
                    }
                )

        if hour in idle_hours and cpu > 40.0:
            anomalies.append(
                {
                    "id": f"IDLE_PERIOD_ACTIVITY_{int(timestamp)}",
                    "type": "idle_period_activity",
                    "timestamp": timestamp,
                    "description": f"CPU usage {cpu:.1f}% during typically idle hour {hour}",
                    "severity": "medium",
                    "data": {
                        "cpu_percent": cpu,
                        "memory_percent": mem,
                        "hour_of_day": hour,
                    },
                }
            )

    logger.info("Detected anomalies count=%s", len(anomalies))
    return anomalies
