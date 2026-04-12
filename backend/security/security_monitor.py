import time

from backend.security.alert_engine import check_for_alert, save_alert
from backend.security.security_engine import analyze_security


def start_security_monitor(interval: int = 10):
    while True:
        try:
            result = analyze_security()
            alert = check_for_alert(result)
            if alert:
                save_alert(alert)
        except Exception:
            pass
        time.sleep(interval)
