"""Threat detection stage that combines analysis signals."""

from .sec_utils import current_timestamp


def detect_threats(process_analysis: dict, network_analysis: dict) -> list[dict]:
    """Merge process and network findings into threat records."""
    threats: list[dict] = []

    for process in process_analysis.get("high_usage", []):
        threats.append(
            {
                "type": "high_resource_usage",
                "severity": "medium",
                "details": {
                    "pid": process.get("pid"),
                    "name": process.get("name"),
                    "cpu_percent": process.get("cpu_percent"),
                    "ram_percent": process.get("ram_percent"),
                },
                "detected_at": current_timestamp(),
            }
        )

    for connection in network_analysis.get("unknown_network_apps", []):
        threats.append(
            {
                "type": "unknown_network_activity",
                "severity": "high",
                "details": {
                    "pid": connection.get("pid"),
                    "status": connection.get("status"),
                },
                "detected_at": current_timestamp(),
            }
        )

    return threats
