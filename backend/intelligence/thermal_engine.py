"""
Thermal Intelligence Engine — Phase 1, JOC Sentinel
---------------------------------------------------
Acts as a governor, not just a sensor:
- Estimates temperature from live CPU usage (synthetic fallback model)
- Classifies thermal state with hysteresis
- Tracks thermal velocity (stable/rising/spiking)
- Computes normalized thermal risk score (0-100)
- Maintains bounded history for trend analytics
"""

from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass
from threading import Lock
from typing import Deque, Dict, List, Optional


@dataclass(frozen=True)
class ThermalReading:
    timestamp: float
    cpu_usage: float
    temperature: float
    smoothed_temperature: float
    state: str
    velocity: str
    score: float
    is_critical: bool
    delta_temp: float


class ThermalEngine:
    # Synthetic fallback model constraints
    _MIN_TEMP = 40.0
    _MAX_TEMP = 95.0

    # Thermal bands (base thresholds)
    _COOL_MAX = 65.0
    _WARM_MAX = 80.0
    _HOT_MAX = 90.0

    # Hysteresis exits (anti-oscillation)
    _CRITICAL_ENTER = 90.0
    _CRITICAL_EXIT = 75.0
    _HOT_ENTER = 80.0
    _HOT_EXIT = 72.0
    _WARM_ENTER = 65.0
    _WARM_EXIT = 60.0

    # Velocity thresholds per update tick
    _RISING_DELTA = 1.0
    _SPIKE_DELTA = 5.0

    # EMA smoothing for thermal signal stability
    _EMA_ALPHA = 0.35

    def __init__(self) -> None:
        self._lock = Lock()
        self._previous_temp: Optional[float] = None
        self._smoothed_temp: Optional[float] = None
        self._state: str = "COOL"
        self._history: Deque[ThermalReading] = deque(maxlen=10)

    @staticmethod
    def _clamp(value: float, lo: float, hi: float) -> float:
        return max(lo, min(hi, value))

    def _estimate_temperature(self, cpu_usage: float) -> float:
        estimated = 40.0 + (cpu_usage * 0.5)
        return round(self._clamp(estimated, self._MIN_TEMP, self._MAX_TEMP), 2)

    def _apply_ema(self, current_temp: float) -> float:
        if self._smoothed_temp is None:
            self._smoothed_temp = current_temp
        else:
            self._smoothed_temp = (
                (self._EMA_ALPHA * current_temp)
                + ((1.0 - self._EMA_ALPHA) * self._smoothed_temp)
            )
        return round(self._smoothed_temp, 2)

    def _classify_velocity(self, delta_temp: float) -> str:
        if delta_temp > self._SPIKE_DELTA:
            return "spiking"
        if delta_temp > self._RISING_DELTA:
            return "rising"
        return "stable"

    def _classify_state_with_hysteresis(self, temp: float) -> str:
        """
        Two-threshold state machine.
        Enter thresholds are higher than exit thresholds to prevent mode flapping.
        """
        prev = self._state

        if prev == "CRITICAL":
            if temp <= self._CRITICAL_EXIT:
                # Exit critical to hottest non-critical band.
                self._state = "HOT" if temp >= self._HOT_ENTER else "WARM"
            return self._state

        if prev == "HOT":
            if temp >= self._CRITICAL_ENTER:
                self._state = "CRITICAL"
            elif temp <= self._HOT_EXIT:
                self._state = "WARM" if temp >= self._WARM_ENTER else "COOL"
            return self._state

        if prev == "WARM":
            if temp >= self._CRITICAL_ENTER:
                self._state = "CRITICAL"
            elif temp >= self._HOT_ENTER:
                self._state = "HOT"
            elif temp <= self._WARM_EXIT:
                self._state = "COOL"
            return self._state

        # COOL
        if temp >= self._CRITICAL_ENTER:
            self._state = "CRITICAL"
        elif temp >= self._HOT_ENTER:
            self._state = "HOT"
        elif temp >= self._WARM_ENTER:
            self._state = "WARM"
        else:
            self._state = "COOL"
        return self._state

    def _compute_score(self, temp: float, cpu_usage: float, delta_temp: float) -> float:
        """
        Weighted thermal score in [0, 100].
        - Temperature dominates
        - CPU usage contributes sustained load context
        - Positive thermal acceleration penalizes fast rise
        """
        temp_norm = self._clamp((temp - self._MIN_TEMP) / (self._MAX_TEMP - self._MIN_TEMP), 0.0, 1.0)
        cpu_norm = self._clamp(cpu_usage / 100.0, 0.0, 1.0)
        velocity_norm = self._clamp(max(delta_temp, 0.0) / 10.0, 0.0, 1.0)

        score = (0.6 * temp_norm) + (0.25 * cpu_norm) + (0.15 * velocity_norm)
        return round(self._clamp(score * 100.0, 0.0, 100.0), 2)

    def update(self, cpu_usage: float, timestamp: float) -> Dict[str, object]:
        """
        Main entry point.
        Returns structured thermal state for control decisions.
        """
        with self._lock:
            cpu = self._clamp(float(cpu_usage), 0.0, 100.0)
            temperature = self._estimate_temperature(cpu)
            smoothed = self._apply_ema(temperature)

            if self._previous_temp is None:
                delta_temp = 0.0
            else:
                delta_temp = round(smoothed - self._previous_temp, 2)
            self._previous_temp = smoothed

            velocity = self._classify_velocity(delta_temp)
            state = self._classify_state_with_hysteresis(smoothed)
            score = self._compute_score(smoothed, cpu, delta_temp)
            is_critical = state == "CRITICAL"

            reading = ThermalReading(
                timestamp=float(timestamp),
                cpu_usage=round(cpu, 2),
                temperature=temperature,
                smoothed_temperature=smoothed,
                state=state,
                velocity=velocity,
                score=score,
                is_critical=is_critical,
                delta_temp=delta_temp,
            )
            self._history.append(reading)

            return {
                "temperature": reading.smoothed_temperature,
                "raw_temperature": reading.temperature,
                "state": reading.state,
                "velocity": reading.velocity,
                "score": reading.score,
                "is_critical": reading.is_critical,
                "delta_temp": reading.delta_temp,
                "history_size": len(self._history),
                "history": [asdict(item) for item in self._history],
            }

    def latest(self) -> Optional[Dict[str, object]]:
        with self._lock:
            if not self._history:
                return None
            return asdict(self._history[-1])

    def history(self) -> List[Dict[str, object]]:
        with self._lock:
            return [asdict(item) for item in self._history]

