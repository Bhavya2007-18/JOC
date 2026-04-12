import hashlib
import logging
import threading
import time
import json
from datetime import datetime, timezone

from backend.security.alert_engine import check_for_alert, save_alert
from backend.security.security_engine import analyze_security

running = False
interval = 10
last_hash = None
monitor_thread = None
monitor_lock = threading.Lock()
logger = logging.getLogger(__name__)
start_time = None
scan_count = 0
skipped_scans = 0
alerts_triggered = 0
last_scan_time = None
last_risk_score = None


def _hash_result(result: dict) -> str:
    try:
        return hashlib.md5(
            json.dumps(result, sort_keys=True).encode()
        ).hexdigest()
    except Exception:
        return ""

def _monitor_loop():
    global alerts_triggered, last_hash, last_risk_score, last_scan_time, scan_count, skipped_scans

    while True:
        with monitor_lock:
            if not running:
                break
            current_interval = interval

        try:
            result = analyze_security()
            now = datetime.now(timezone.utc)
            current_hash = _hash_result(result)
            risk_score = int(result.get("risk_score", 0) or 0)

            with monitor_lock:
                last_scan_time = now
                last_risk_score = risk_score
                scan_count += 1
                result_changed = current_hash != last_hash

            if result_changed:
                with monitor_lock:
                    last_hash = current_hash

                alert = check_for_alert(result)
                if alert:
                    with monitor_lock:
                        alerts_triggered += 1
                    save_alert(alert)
            else:
                with monitor_lock:
                    skipped_scans += 1

            if risk_score >= 70:
                sleep_time = max(2, current_interval // 2)
            else:
                sleep_time = current_interval
        except Exception:
            logger.exception("Security monitor iteration failed")
            sleep_time = current_interval

        time.sleep(sleep_time)


def start_security_monitor():
    global alerts_triggered, last_hash, last_risk_score, last_scan_time, monitor_thread
    global running, scan_count, skipped_scans, start_time

    with monitor_lock:
        if running:
            return
        running = True
        start_time = datetime.now(timezone.utc)
        scan_count = 0
        skipped_scans = 0
        alerts_triggered = 0
        last_scan_time = None
        last_risk_score = None
        last_hash = None
        monitor_thread = threading.Thread(target=_monitor_loop, daemon=True)
        monitor_thread.start()

def stop_monitor():
    global running, monitor_thread

    thread_to_join = None
    with monitor_lock:
        running = False
        thread_to_join = monitor_thread

    if (
        thread_to_join
        and thread_to_join.is_alive()
        and thread_to_join is not threading.current_thread()
    ):
        thread_to_join.join(timeout=1)

    with monitor_lock:
        monitor_thread = None


def set_interval(new_interval: int):
    global interval
    with monitor_lock:
        interval = max(1, int(new_interval))


def get_status():
    with monitor_lock:
        thread_alive = monitor_thread.is_alive() if monitor_thread else False
        return {
            "running": running,
            "interval": interval,
            "thread_alive": thread_alive,
        }


def get_health():
    with monitor_lock:
        now = datetime.now(timezone.utc)

        uptime = 0
        if start_time:
            uptime = int((now - start_time).total_seconds())

        return {
            "status": "healthy" if running else "stopped",
            "running": running,
            "thread_alive": monitor_thread.is_alive() if monitor_thread else False,
            "interval": interval,
            "uptime_seconds": uptime,
            "scan_count": scan_count,
            "skipped_scans": skipped_scans,
            "alerts_triggered": alerts_triggered,
            "last_scan_time": last_scan_time.isoformat() if last_scan_time else None,
            "last_risk_score": last_risk_score,
        }
