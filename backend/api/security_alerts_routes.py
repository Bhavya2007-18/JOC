import json
from pathlib import Path

from fastapi import APIRouter

router = APIRouter()

_ALERTS_FILE = Path(__file__).resolve().parent.parent / "logs" / "security_alerts.json"


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
