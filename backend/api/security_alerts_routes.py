import json
from pathlib import Path

from fastapi import APIRouter

router = APIRouter()

from utils.paths import get_persistent_path
_ALERTS_FILE = get_persistent_path("security_alerts.json", "logs")


@router.get("/security/alerts")
def get_security_alerts(limit: int = 20):
    if not _ALERTS_FILE.exists():
        return []

    try:
        with _ALERTS_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, OSError):
        return []

    if not isinstance(data, list):
        return []

    if limit <= 0:
        return []

    return data[-limit:]
