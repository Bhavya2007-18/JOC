from __future__ import annotations

import time
from typing import Any, Dict, List

from utils.logger import get_logger

from .base_simulation import BaseSimulation


logger = get_logger("validation.red.memory_stress")


class MemoryStressSimulation(BaseSimulation):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._buffers: List[bytearray] = []

    def setup(self) -> None:
        self.safety_guard.ensure_within_limits()

    def execute(self) -> Dict[str, Any]:
        chunk_mb = max(1, int(self.parameters.get("chunk_mb", 16)))
        steps = max(1, int(self.parameters.get("steps", 5)))
        pause_seconds = float(self.parameters.get("pause_seconds", 0.4))

        if self.dry_run:
            return {
                "simulation": "memory_stress",
                "dry_run": True,
                "chunk_mb": chunk_mb,
                "steps": steps,
                "pause_seconds": pause_seconds,
            }

        for _ in range(steps):
            self.safety_guard.raise_if_abort_requested()
            self.safety_guard.ensure_within_limits()
            self._buffers.append(bytearray(chunk_mb * 1024 * 1024))
            time.sleep(pause_seconds)

        hold_seconds = float(self.parameters.get("hold_seconds", 2))
        start_hold = time.time()
        while time.time() - start_hold < hold_seconds:
            self.safety_guard.raise_if_abort_requested()
            self.safety_guard.ensure_within_limits()
            time.sleep(0.1)

        return {
            "simulation": "memory_stress",
            "dry_run": False,
            "chunk_mb": chunk_mb,
            "steps": steps,
            "allocated_mb": chunk_mb * steps,
        }

    def cleanup(self) -> None:
        self._buffers.clear()
        logger.info("Memory stress cleanup completed id=%s", self.simulation_id)

    def metadata(self) -> Dict[str, Any]:
        return {
            "type": "memory_stress",
            "simulation_id": self.simulation_id,
            "correlation_id": self.correlation_id,
            "parameters": self.parameters,
        }

