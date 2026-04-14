"""
Phase 3: Predictive Thermal Intelligence

Lightweight slope-based forecasting for near-future thermal risk.
No external ML dependencies; designed for real-time loop usage.
"""

from __future__ import annotations

from collections import deque
from typing import Deque, Dict, Optional


class ThermalPredictor:
    def __init__(
        self,
        history_size: int = 20,
        prediction_window_seconds: float = 5.0,
        critical_temp: float = 90.0,
    ) -> None:
        self.history: Deque[Dict[str, float]] = deque(maxlen=history_size)
        self.prediction_window_seconds = max(1.0, float(prediction_window_seconds))
        self.critical_temp = float(critical_temp)
        self._ema_temp: Optional[float] = None
        self._ema_alpha: float = 0.35

    def update(self, temp: float, timestamp: float) -> None:
        value = float(temp)
        if self._ema_temp is None:
            self._ema_temp = value
        else:
            self._ema_temp = (
                (self._ema_alpha * value)
                + ((1.0 - self._ema_alpha) * self._ema_temp)
            )
        self.history.append(
            {
                "temp": round(self._ema_temp, 2),
                "timestamp": float(timestamp),
            }
        )

    @staticmethod
    def _classify_risk(predicted_temp: float) -> str:
        if predicted_temp > 90.0:
            return "CRITICAL"
        if predicted_temp >= 85.0:
            return "HIGH"
        if predicted_temp >= 75.0:
            return "WARNING"
        return "SAFE"

    def predict(self) -> Dict[str, object]:
        if not self.history:
            return {
                "predicted_temp": 0.0,
                "risk": "SAFE",
                "time_to_critical": None,
                "confidence": "low",
            }

        latest = self.history[-1]
        current_temp = float(latest["temp"])
        current_ts = float(latest["timestamp"])

        if len(self.history) < 2:
            return {
                "predicted_temp": round(current_temp, 2),
                "risk": self._classify_risk(current_temp),
                "time_to_critical": None,
                "confidence": "low",
            }

        # O(1) trend estimate using oldest+latest points in bounded history.
        oldest = self.history[0]
        oldest_temp = float(oldest["temp"])
        oldest_ts = float(oldest["timestamp"])
        delta_t = max(current_ts - oldest_ts, 1e-6)
        rate = (current_temp - oldest_temp) / delta_t

        predicted_temp = current_temp + (rate * self.prediction_window_seconds)
        predicted_temp = round(predicted_temp, 2)
        risk = self._classify_risk(predicted_temp)

        time_to_critical = None
        if rate > 0.0 and current_temp < self.critical_temp:
            seconds = (self.critical_temp - current_temp) / rate
            if seconds >= 0:
                time_to_critical = round(seconds, 2)

        confidence = "medium" if len(self.history) >= 5 else "low"
        return {
            "predicted_temp": predicted_temp,
            "risk": risk,
            "time_to_critical": time_to_critical,
            "confidence": confidence,
        }

