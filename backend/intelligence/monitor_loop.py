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
        self._thread = None
        self._running = False
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self.latest_snapshot = None
        self.latest_analysis = None
        MonitorLoop._instance = self

    @classmethod
    def get_instance(cls):
        return cls._instance

    def start(self):
        with self._lock:
            if self._running:
                return

            self._running = True
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()

    def stop(self):
        with self._lock:
            self._running = False
            self._stop_event.set()

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=self.interval + 1)
        self._thread = None

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
        self._run_loop()

    def _run_loop(self):
        while not self._stop_event.is_set():
            try:
                logger.info("Loop running")

                snapshot = collect_snapshot()
                self.latest_snapshot = snapshot

                analysis = self.engine.analyze(snapshot)
                self.latest_analysis = analysis

                save_snapshot(snapshot)
            except Exception as e:
                logger.error(f"[MonitorLoop Error] {e}")

            self._stop_event.wait(self.interval)