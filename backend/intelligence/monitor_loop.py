import time
import threading

from intelligence.snapshot_provider import collect_snapshot
from intelligence.engine import IntelligenceEngine
from storage.db import save_snapshot
from utils.logger import get_logger

logger = get_logger("monitor")

class MonitorLoop:
    _instance = None

    def __init__(self, interval: int = 5):
        self.interval = interval
        self.engine = IntelligenceEngine()
        self.running = False
        MonitorLoop._instance = self

    @classmethod
    def get_instance(cls):
        return cls._instance

    def start(self):
        if self.running:
            return

        self.running = True
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()

    def stop(self):
        self.running = False

    def nudge(self):
        """Force an immediate snapshot + analysis cycle (called by simulation engine)."""
        try:
            logger.info("Nudge: forced immediate snapshot")
            snapshot = collect_snapshot()
            save_snapshot(snapshot)
            self.engine.analyze(snapshot)
        except Exception as e:
            logger.error(f"[MonitorLoop Nudge Error] {e}")

    def run(self):
        while self.running:
            try:
                logger.info("Loop running")

                snapshot = collect_snapshot()
                save_snapshot(snapshot)
                threading.Thread(
                    target=self.engine.analyze,
                    args=(snapshot,),
                    daemon=True
                ).start()
            except Exception as e:
                print(f"[MonitorLoop Error] {e}")

            time.sleep(self.interval)