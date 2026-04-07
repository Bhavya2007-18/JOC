import time
import threading

from intelligence.snapshot_provider import collect_snapshot
from intelligence.engine import IntelligenceEngine
from storage.db import save_snapshot
from utils.logger import get_logger

logger = get_logger("monitor")

class MonitorLoop:
    def __init__(self, interval: int = 5):
        self.interval = interval
        self.engine = IntelligenceEngine()
        self.running = False

    def start(self):
        if self.running:
            return

        self.running = True
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()

    def stop(self):
        self.running = False

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