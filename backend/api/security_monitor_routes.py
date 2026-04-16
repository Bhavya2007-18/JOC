import json
import threading
from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel

from security.security_monitor import (
    get_health,
    get_status,
    set_interval,
    start_security_monitor,
    stop_monitor,
)

router = APIRouter()


class IntervalPayload(BaseModel):
    interval: int


@router.post("/security/monitor/start")
def start_security_monitor_route():
    status = get_status()
    if not status["running"]:
        thread = threading.Thread(target=start_security_monitor, daemon=True)
        thread.start()
    return get_status()


@router.post("/security/monitor/stop")
def stop_security_monitor_route():
    stop_monitor()
    return get_status()


@router.post("/security/monitor/set-interval")
def set_security_monitor_interval(payload: IntervalPayload):
    set_interval(payload.interval)
    return get_status()


@router.get("/security/monitor/status")
def get_security_monitor_status():
    return get_status()


@router.get("/security/monitor/health")
def monitor_health():
    return get_health()


@router.get("/security/logs")
def get_security_logs(limit: int = 20):
    log_file = Path(__file__).resolve().parent.parent / "logs" / "security_logs.json"
    if not log_file.exists():
        return []

    try:
        with log_file.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, OSError):
        return []

    if not isinstance(data, list):
        return []

    return data[-limit:]
