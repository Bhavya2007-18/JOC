import logging
import threading
import time

from backend.security.alert_engine import check_for_alert, save_alert
from backend.security.security_engine import analyze_security

running = False
interval = 10
monitor_thread = None
monitor_lock = threading.Lock()
logger = logging.getLogger(__name__)

def _monitor_loop():
    while True:
        with monitor_lock:
            if not running:
                break
            current_interval = interval

        try:
            result = analyze_security()
            alert = check_for_alert(result)
            if alert:
                save_alert(alert)
        except Exception:
            logger.exception("Security monitor iteration failed")

        time.sleep(current_interval)


def start_security_monitor():
    global running, monitor_thread

    with monitor_lock:
        if running:
            return
        running = True
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
