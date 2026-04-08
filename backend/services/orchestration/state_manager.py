from __future__ import annotations

import threading
import time
from typing import Any, Dict, List

import psutil

from core.config import ValidationConfig
from models.simulation_models import SimulationState


class RuntimeStateManager:
    def __init__(self) -> None:
        self._state = SimulationState.idle
        self._lock = threading.Lock()
        self._transitions: List[Dict[str, Any]] = []

    def transition(self, new_state: SimulationState, correlation_id: str, note: str = "") -> None:
        with self._lock:
            self._state = new_state
            self._transitions.append(
                {
                    "timestamp": time.time(),
                    "state": new_state.value,
                    "correlation_id": correlation_id,
                    "note": note,
                }
            )

    def get_state(self) -> SimulationState:
        with self._lock:
            return self._state

    def get_transitions(self) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._transitions)


class RuntimeControl:
    def __init__(self) -> None:
        self._kill_switch = threading.Event()

    def trigger_kill_switch(self) -> None:
        self._kill_switch.set()

    def clear_kill_switch(self) -> None:
        self._kill_switch.clear()

    def is_stop_requested(self) -> bool:
        return self._kill_switch.is_set()


class SafetyGuard:
    def __init__(self, config: ValidationConfig, runtime_control: RuntimeControl) -> None:
        self.config = config
        self.runtime_control = runtime_control

    def raise_if_abort_requested(self) -> None:
        if self.runtime_control.is_stop_requested():
            raise RuntimeError("Simulation aborted by kill switch")

    def ensure_within_limits(self) -> None:
        cpu_percent = psutil.cpu_percent(interval=0.05)
        mem_percent = psutil.virtual_memory().percent
        if cpu_percent >= self.config.cpu_ceiling_percent:
            raise RuntimeError(
                f"CPU safety ceiling exceeded: {cpu_percent:.1f}% >= {self.config.cpu_ceiling_percent:.1f}%"
            )
        if mem_percent >= self.config.memory_ceiling_percent:
            raise RuntimeError(
                f"Memory safety ceiling exceeded: {mem_percent:.1f}% >= {self.config.memory_ceiling_percent:.1f}%"
            )

