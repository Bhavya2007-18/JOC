"""Alert generation and persistence for security monitoring."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone


def check_for_alert(result: dict) -> dict | None:
    """Build an alert payload from a security result when thresholds are met."""
    risk_score = int(result.get("risk_score", 0) or 0)

    if risk_score >= 70:
        return {
            "type": "HIGH_RISK",
            "message": "High risk detected on system",
            "risk_score": risk_score,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    if risk_score >= 40:
        return {
            "type": "MEDIUM_RISK",
            "message": "Moderate risk detected on system",
            "risk_score": risk_score,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    return None


def save_alert(alert: dict) -> None:
    """Append an alert to the JSON alert log, retaining only the last 50 entries."""
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    alerts_file = os.path.join(logs_dir, "security_alerts.json")

    os.makedirs(logs_dir, exist_ok=True)

    if os.path.exists(alerts_file):
        try:
            with open(alerts_file, "r", encoding="utf-8") as file:
                existing = json.load(file)
            alerts = existing if isinstance(existing, list) else []
        except (json.JSONDecodeError, OSError):
            alerts = []
    else:
        alerts = []

    alerts.append(alert)
    alerts = alerts[-50:]

    try:
        with open(alerts_file, "w", encoding="utf-8") as file:
            json.dump(alerts, file, indent=2)
    except OSError:
        return
