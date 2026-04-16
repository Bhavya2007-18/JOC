from collections import deque
from typing import Dict, Any, Optional

class AbstractionEngine:
    # Thresholds (all tunable without changing logic)
    Z_SPIKE_THRESHOLD    = 2.0   # z-score at which we call something abnormal
    Z_LEAK_THRESHOLD     = 1.5   # lower bar for slow leaks
    OSCILLATION_FLIPS    = 3     # how many sign changes = oscillation
    BURST_DECAY_TICKS    = 2     # how quickly a burst must resolve

    def __init__(self):
        # Oscillation detection: rolling z-score sign history
        self._cpu_z_history: deque = deque(maxlen=6)  # last 6 ticks = 90 seconds
        self._ram_z_history: deque = deque(maxlen=6)

        # Burst detection: remember z-score from previous tick
        self._prev_cpu_z: Optional[float] = None
        self._prev_ram_z: Optional[float] = None

    def _is_spike(self, cpu_z, ram_z, cpu_trend, ram_trend) -> tuple[bool, str]:
        """Returns (is_spike, dominant_resource)"""
        cpu_spike = cpu_z is not None and abs(cpu_z) >= self.Z_SPIKE_THRESHOLD and cpu_trend in ("rising_fast",)
        ram_spike = ram_z is not None and abs(ram_z) >= self.Z_SPIKE_THRESHOLD and ram_trend in ("rising_fast",)
        if cpu_spike and ram_spike: return True, "combined"
        if cpu_spike: return True, "cpu"
        if ram_spike: return True, "memory"
        return False, "none"

    def _is_leak(self, cpu_z, ram_z, cpu_trend, ram_trend) -> tuple[bool, str]:
        """Gradual rise below spike threshold"""
        cpu_leak = cpu_z is not None and self.Z_LEAK_THRESHOLD <= abs(cpu_z) < self.Z_SPIKE_THRESHOLD and cpu_trend == "rising"
        ram_leak = ram_z is not None and self.Z_LEAK_THRESHOLD <= abs(ram_z) < self.Z_SPIKE_THRESHOLD and ram_trend == "rising"
        if cpu_leak and ram_leak: return True, "combined"
        if cpu_leak: return True, "cpu"
        if ram_leak: return True, "memory"
        return False, "none"

    def _is_oscillation(self) -> bool:
        """Counts sign changes in recent z-score history"""
        def sign_changes(history):
            signs = [1 if z > 0 else -1 for z in history if z is not None]
            return sum(1 for i in range(1, len(signs)) if signs[i] != signs[i-1])
        return sign_changes(self._cpu_z_history) >= self.OSCILLATION_FLIPS \
            or sign_changes(self._ram_z_history) >= self.OSCILLATION_FLIPS

    def _is_burst(self, cpu_z, ram_z) -> bool:
        """High z-score this tick, low z-score last tick (sudden spike that appeared fast)"""
        if self._prev_cpu_z is None: return False
        cpu_burst = abs(cpu_z or 0) >= self.Z_SPIKE_THRESHOLD and abs(self._prev_cpu_z or 0) < 1.0
        ram_burst = abs(ram_z or 0) >= self.Z_SPIKE_THRESHOLD and abs(self._prev_ram_z or 0) < 1.0
        return cpu_burst or ram_burst

    def classify(self, cpu: float, ram: float, baseline_data: dict, pred_data: dict) -> dict:
        # 1. Extract inputs
        cpu_z     = baseline_data.get("cpu_z_score")
        ram_z     = baseline_data.get("ram_z_score")
        win_fill  = baseline_data.get("window_fill", 0.0)
        cpu_trend = pred_data.get("predicted_cpu", {}).get("trend", "stable")
        ram_trend = pred_data.get("predicted_ram", {}).get("trend", "stable")

        # 2. Guard: not enough data yet
        if win_fill < 0.15 or (cpu_z is None and ram_z is None):
            return self._stable_result(cpu_z, ram_z)

        # 3. Update history buffers for oscillation/burst detection
        self._cpu_z_history.append(cpu_z)
        self._ram_z_history.append(ram_z)

        # 4. Classify (priority order matters: spike > burst > oscillation > leak > stable)
        is_spike, spike_res = self._is_spike(cpu_z, ram_z, cpu_trend, ram_trend)
        is_burst            = self._is_burst(cpu_z, ram_z)
        is_osc              = self._is_oscillation()
        is_leak, leak_res   = self._is_leak(cpu_z, ram_z, cpu_trend, ram_trend)

        # 5. Store prev tick values
        self._prev_cpu_z = cpu_z
        self._prev_ram_z = ram_z

        # 6. Pick winner
        max_z = max((abs(cpu_z or 0), abs(ram_z or 0)))
        derivative = ((cpu_z or 0) + (ram_z or 0)) / 2

        if is_spike:
            ptype, resource = "spike", spike_res
        elif is_burst:
            ptype, resource = "burst", "cpu" if abs(cpu_z or 0) > abs(ram_z or 0) else "memory"
        elif is_osc:
            ptype, resource = "oscillation", "combined"
        elif is_leak:
            ptype, resource = "leak", leak_res
        else:
            ptype, resource = "stable", "none"

        # 7. Compute scoring
        intensity  = min(max_z / 3.0, 1.0)
        confidence = win_fill * min(max_z, 3.0) / 3.0

        return {
            "pattern_type":  ptype,
            "resource":      resource,
            "intensity":     round(intensity, 3),
            "duration":      round(win_fill * 90, 1),   # proxy: window_fill × max_window_seconds
            "derivative":    round(derivative, 3),
            "confidence":    round(confidence, 3),
            "raw_z_scores":  {"cpu": round(cpu_z or 0, 3), "ram": round(ram_z or 0, 3)}
        }

    def _stable_result(self, cpu_z, ram_z):
        return {
            "pattern_type": "stable", "resource": "none",
            "intensity": 0.0, "duration": 0.0, "derivative": 0.0, "confidence": 0.0,
            "raw_z_scores": {"cpu": round(cpu_z or 0, 3), "ram": round(ram_z or 0, 3)}
        }
