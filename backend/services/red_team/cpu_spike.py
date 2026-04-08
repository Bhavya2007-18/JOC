from __future__ import annotations

import threading
import time
from typing import Any, Dict, List

from utils.logger import get_logger

from .base_simulation import BaseSimulation


logger = get_logger("validation.red.cpu_spike")


class CpuSpikeSimulation(BaseSimulation):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._stop_event = threading.Event()
        self._threads: List[threading.Thread] = []

    def setup(self) -> None:
        self.safety_guard.ensure_within_limits()

    def _worker(self, throttling: float) -> None:
        while not self._stop_event.is_set():
            _ = sum(i * i for i in range(10000))
            if throttling > 0:
                time.sleep(throttling)
            self.safety_guard.raise_if_abort_requested()
            self.safety_guard.ensure_within_limits()

    def execute(self) -> Dict[str, Any]:
        duration = float(self.parameters.get("duration", 5))
        intensity = max(1, int(self.parameters.get("intensity", 2)))
        throttling = float(self.parameters.get("throttle_seconds", 0.001))

        if self.dry_run:
            return {
                "simulation": "cpu_spike",
                "dry_run": True,
                "threads": intensity,
                "duration": duration,
                "throttle_seconds": throttling,
            }

        start = time.time()
        for _ in range(intensity):
            thread = threading.Thread(target=self._worker, args=(throttling,), daemon=True)
            self._threads.append(thread)
            thread.start()

        while time.time() - start < duration:
            self.safety_guard.raise_if_abort_requested()
            self.safety_guard.ensure_within_limits()
            time.sleep(0.1)

        return {
            "simulation": "cpu_spike",
            "dry_run": False,
            "threads": intensity,
            "duration": duration,
            "throttle_seconds": throttling,
        }

    def cleanup(self) -> None:
        self._stop_event.set()
        for thread in self._threads:
            thread.join(timeout=1.0)
        logger.info("CPU spike simulation cleaned up id=%s", self.simulation_id)

    def metadata(self) -> Dict[str, Any]:
        return {
            "type": "cpu_spike",
            "simulation_id": self.simulation_id,
            "correlation_id": self.correlation_id,
            "parameters": self.parameters,
        }

