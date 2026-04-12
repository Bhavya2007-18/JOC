"""
Predictive Engine — Phase 2, JOC Sentinel
-----------------------------------------
Forecasts CPU and RAM usage 1 minute and 5 minutes into the future
using Holt's Double Exponential Smoothing. Pure Python implementation
without heavy ML/numpy dependencies.

Identifies usage trends and estimates time-to-critical thresholds.

Usage (one call per monitor cycle):
    pred = PredictiveEngine()
    pred.observe(cpu=65.0, ram=45.0, timestamp=time.time())
    report = pred.forecast()
    # → {"predicted_cpu": {"1m": 68.2, "5m": 75.1, "trend": "rising_fast"}, ...}
"""

from typing import Dict, Any, List, Tuple
from collections import deque

class PredictiveEngine:
    """
    Implements Holt's Double Exponential Smoothing to generate
    short-to-medium term forecasts of system metrics.
    """
    
    # Smoothing Factors
    # Alpha (Level): High alpha gives more weight to recent observations
    _ALPHA = 0.3
    # Beta (Trend): Lower beta makes the trend less reactive to sudden, brief spikes
    _BETA = 0.1
    
    # Assumed sampling rate internally for predictions (1 sample per 5 seconds)
    _ASSUMED_SAMPLE_RATE_SEC = 5.0

    def __init__(self) -> None:
        # Holt state tracking
        self.state: Dict[str, Dict[str, float]] = {
            "cpu": {"level": 0.0, "trend": 0.0, "last_val": None},
            "ram": {"level": 0.0, "trend": 0.0, "last_val": None}
        }
        
        # Keep a small history to compute pure linear slope for verification / fallback
        self.history: Dict[str, deque] = {
            "cpu": deque(maxlen=24),  # rolling 2 minutes at 5s interval
            "ram": deque(maxlen=24)
        }
        
    # ------------------------------------------------------------------ #
    #  Core Observation Update                                             #
    # ------------------------------------------------------------------ #

    def observe(self, cpu: float, ram: float, timestamp: float) -> None:
        """
        Updates the internal Holt smoothing models with the new observation.
        Call this exactly once per monitoring cycle.
        """
        self._update_holt("cpu", cpu)
        self._update_holt("ram", ram)
        
        self.history["cpu"].append(cpu)
        self.history["ram"].append(ram)
        
    def _update_holt(self, metric: str, value: float) -> None:
        s = self.state[metric]
        
        # Initialization
        if s["last_val"] is None:
            s["level"] = value
            s["trend"] = 0.0
            s["last_val"] = value
            return
            
        # Bootstrap trend on second observation if it's 0
        if s["trend"] == 0.0 and len(self.history[metric]) == 1:
            s["trend"] = value - s["last_val"]
            
        # Holt's Double Exponential Smoothing Update
        prev_level = s["level"]
        prev_trend = s["trend"]
        
        # Equation 1: Update Level    L(t) = α * y(t) + (1 - α) * (L(t-1) + T(t-1))
        new_level = (self._ALPHA * value) + ((1.0 - self._ALPHA) * (prev_level + prev_trend))
        
        # Equation 2: Update Trend    T(t) = β * (L(t) - L(t-1)) + (1 - β) * T(t-1)
        new_trend = (self._BETA * (new_level - prev_level)) + ((1.0 - self._BETA) * prev_trend)
        
        s["level"] = new_level
        s["trend"] = new_trend
        s["last_val"] = value

    # ------------------------------------------------------------------ #
    #  Trend Analysis Helper                                               #
    # ------------------------------------------------------------------ #

    def _determine_trend_label(self, metric: str) -> str:
        """
        Calculates a simple descriptive label for the current trajectory.
        Uses both the Holt trend state and a pure linear slope over recent history.
        """
        history = list(self.history[metric])
        if len(history) < 5:
            return "stable"
            
        # Pure python least-squares linear regression slope
        n = len(history)
        sum_x = sum(range(n))
        sum_y = sum(history)
        sum_xy = sum(x * y for x, y in enumerate(history))
        sum_xx = sum(x * x for x in range(n))
        
        # Prevent ZeroDivisionError (though shouldn't happen with range(n))
        denominator = (n * sum_xx) - (sum_x * sum_x)
        if denominator == 0:
            linear_slope = 0.0
        else:
            linear_slope = ((n * sum_xy) - (sum_x * sum_y)) / denominator
            
        # Combine Holt trend and Linear slope for stability
        holt_trend = self.state[metric]["trend"]
        combined_slope = (0.7 * holt_trend) + (0.3 * linear_slope)
        
        if combined_slope > 1.5:
            return "rising_fast"
        elif combined_slope > 0.3:
            return "rising"
        elif combined_slope < -1.5:
            return "falling_fast"
        elif combined_slope < -0.3:
            return "falling"
        else:
            return "stable"

    # ------------------------------------------------------------------ #
    #  Forecast Generation                                                 #
    # ------------------------------------------------------------------ #

    def forecast(self, threshold: float = 90.0) -> Dict[str, Any]:
        """
        Generates 1m and 5m forecasts for CPU and RAM, computes expected
        time-to-critical, and assigns an overall risk level.
        
        Args:
            threshold: The value considered "critical" (default 90%).
            
        Returns:
            Dict containing predictions, trends, and risk assessment.
        """
        # If we haven't warmed up at all, return empty predictions
        if self.state["cpu"]["last_val"] is None:
            return {
                "predicted_cpu": {"1m": 0.0, "5m": 0.0, "trend": "stable", "time_to_critical_s": -1},
                "predicted_ram": {"1m": 0.0, "5m": 0.0, "trend": "stable", "time_to_critical_s": -1},
                "risk": "LOW"
            }
            
        # Steps ahead calculation (assuming 1 step = 5 seconds)
        steps_1m = 60.0 / self._ASSUMED_SAMPLE_RATE_SEC
        steps_5m = 300.0 / self._ASSUMED_SAMPLE_RATE_SEC
        
        result = {}
        min_eta = -1.0
        
        for metric in ["cpu", "ram"]:
            s = self.state[metric]
            current_level = s["level"]
            current_trend = s["trend"]
            
            # Forecast Equation:  F(t+h) = L(t) + h * T(t)
            pred_1m = min(100.0, max(0.0, current_level + (steps_1m * current_trend)))
            pred_5m = min(100.0, max(0.0, current_level + (steps_5m * current_trend)))
            
            trend_label = self._determine_trend_label(metric)
            
            # Estimated Time to threshold breach (seconds)
            eta_seconds = -1.0
            if current_trend > 0.1 and current_level < threshold:
                steps_to_breach = (threshold - current_level) / current_trend
                eta_seconds = steps_to_breach * self._ASSUMED_SAMPLE_RATE_SEC
                
                if min_eta == -1.0 or eta_seconds < min_eta:
                    min_eta = eta_seconds
                    
            elif current_level >= threshold:
                 # Already breaching
                 eta_seconds = 0.0
                 min_eta = 0.0
                
            result[f"predicted_{metric}"] = {
                "1m": round(pred_1m, 1),
                "5m": round(pred_5m, 1),
                "trend": trend_label,
                "time_to_critical_s": round(eta_seconds, 1) if eta_seconds >= 0 else -1
            }

        # Determine aggregate predictive risk
        risk = "LOW"
        c_trend = result["predicted_cpu"]["trend"]
        r_trend = result["predicted_ram"]["trend"]
        
        # High Risk: Already breaching or breaching in < 60s
        if min_eta >= 0 and min_eta < 60:
            risk = "CRITICAL"
        # Medium Risk: Breaching in < 5m OR rising fast
        elif (min_eta >= 0 and min_eta < 300) or c_trend == "rising_fast" or r_trend == "rising_fast":
            risk = "HIGH"
        # Low Risk: Just rising steadily
        elif c_trend == "rising" or r_trend == "rising":
            risk = "MEDIUM"
            
        result["risk"] = risk
        
        return result
