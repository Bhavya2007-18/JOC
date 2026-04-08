from typing import Any, Dict, List, Optional

from utils.logger import get_logger

from .anomaly_detector import detect_anomalies
from .pattern_analyzer import compute_patterns


logger = get_logger("intelligence.decision_engine")


def _confidence_from_delta(delta: float) -> str:
    if delta >= 40.0:
        return "high"
    if delta >= 20.0:
        return "medium"
    return "low"


def generate_decisions(window_seconds: Optional[int] = None) -> List[Dict[str, Any]]:
    anomalies = detect_anomalies(window_seconds=window_seconds)
    patterns = compute_patterns(window_seconds=window_seconds)
    decisions: List[Dict[str, Any]] = []

    for anomaly in anomalies:
        anomaly_type = anomaly.get("type")
        anomaly_id = anomaly.get("id")
        data = anomaly.get("data", {})

        if anomaly_type == "cpu_spike":
            cpu = float(data.get("cpu_percent", 0.0))
            avg_cpu = float(data.get("average_cpu_percent", 0.0))
            delta = max(0.0, cpu - avg_cpu)
            confidence = _confidence_from_delta(delta)

            decision_text = "Reduce priority of high-CPU processes"
            reason = f"CPU usage exceeded normal by {delta:.1f}%"
            decisions.append(
                {
                    "decision": decision_text,
                    "reason": reason,
                    "confidence": confidence,
                    "data_used": {
                        "cpu_percent": cpu,
                        "average_cpu_percent": avg_cpu,
                    },
                    "related_anomalies": [anomaly_id],
                    "suggested_actions": [
                        {
                            "action_type": "lower_priority",
                            "target": "top_cpu_processes",
                            "parameters": {
                                "cpu_threshold": cpu,
                            },
                        }
                    ],
                }
            )

        elif anomaly_type == "unknown_high_cpu_process":
            name = str(data.get("process_name", "unknown"))
            cpu = float(data.get("cpu_percent", 0.0))
            confidence = _confidence_from_delta(cpu - 30.0)
            decision_text = f"Review or limit process {name}"
            reason = f"Unknown process {name} is using {cpu:.1f}% CPU"

            decisions.append(
                {
                    "decision": decision_text,
                    "reason": reason,
                    "confidence": confidence,
                    "data_used": {
                        "process_name": name,
                        "cpu_percent": cpu,
                    },
                    "related_anomalies": [anomaly_id],
                    "suggested_actions": [
                        {
                            "action_type": "inspect_process",
                            "target": name,
                            "parameters": {},
                        }
                    ],
                }
            )

        elif anomaly_type == "idle_period_activity":
            cpu = float(data.get("cpu_percent", 0.0))
            hour = int(data.get("hour_of_day", 0))
            confidence = _confidence_from_delta(cpu - 30.0)

            decisions.append(
                {
                    "decision": "Investigate activity during idle hours",
                    "reason": f"CPU usage {cpu:.1f}% detected during typical idle hour {hour}",
                    "confidence": confidence,
                    "data_used": {
                        "cpu_percent": cpu,
                        "hour_of_day": hour,
                    },
                    "related_anomalies": [anomaly_id],
                    "suggested_actions": [
                        {
                            "action_type": "review_scheduled_tasks",
                            "target": "system",
                            "parameters": {},
                        }
                    ],
                }
            )

    avg_mem = float(patterns.get("average_memory_percent", 0.0))
    if avg_mem > 80.0:
        delta = avg_mem - 80.0
        confidence = _confidence_from_delta(delta)
        decisions.append(
            {
                "decision": "Suggest cleanup to free memory",
                "reason": f"Average memory usage is {avg_mem:.1f}%, above the safe threshold",
                "confidence": confidence,
                "data_used": {
                    "average_memory_percent": avg_mem,
                },
                "related_anomalies": [],
                "suggested_actions": [
                    {
                        "action_type": "run_cleanup",
                        "target": "system",
                        "parameters": {
                            "endpoint": "/optimize/cleanup",
                            "dry_run": True,
                        },
                    }
                ],
            }
        )

    logger.info("Generated decisions count=%s", len(decisions))
    return decisions
