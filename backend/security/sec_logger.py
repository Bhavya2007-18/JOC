"""Lightweight file-based logging for security analysis results."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone


def save_security_log(result: dict) -> None:
    """Persist a security analysis result as a timestamped JSON log entry."""
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    log_file = os.path.join(logs_dir, "security_logs.json")

    os.makedirs(logs_dir, exist_ok=True)

    if os.path.exists(log_file):
        try:
            with open(log_file, "r", encoding="utf-8") as file:
                existing = json.load(file)
            logs = existing if isinstance(existing, list) else []
        except (json.JSONDecodeError, OSError):
            logs = []
    else:
        logs = []

    logs.append(
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": result,
        }
    )

    logs = logs[-50:]

    try:
        with open(log_file, "w", encoding="utf-8") as file:
            json.dump(logs, file, indent=2)
    except OSError:
        return
