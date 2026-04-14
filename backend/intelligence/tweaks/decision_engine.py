from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

import psutil


@dataclass
class DecisionThresholds:
    combat_cpu_high: float = 80.0
    stealth_battery_low: float = 25.0
    neural_cpu_pressure: float = 70.0
    memory_flush_pressure: float = 85.0


class TweakDecisionEngine:
    def __init__(self, thresholds: Optional[DecisionThresholds] = None) -> None:
        self.thresholds = thresholds or DecisionThresholds()

    def _collect_metrics(self) -> Dict[str, object]:
        cpu = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory().percent
        battery = psutil.sensors_battery()
        battery_percent = battery.percent if battery else None
        power_plugged = bool(battery.power_plugged) if battery else None
        return {
            "cpu": cpu,
            "memory": memory,
            "battery": battery_percent,
            "power_plugged": power_plugged,
        }

    def suggest(self) -> Dict[str, object]:
        metrics = self._collect_metrics()
        cpu = float(metrics["cpu"])
        memory = float(metrics["memory"])
        battery = metrics["battery"]
        power_plugged = metrics["power_plugged"]

        recommended = None
        reason = "System appears balanced. No urgent protocol shift required."
        confidence = 0.65

        # Priority order intentionally prefers power safety when unplugged.
        if (
            battery is not None
            and power_plugged is False
            and float(battery) <= self.thresholds.stealth_battery_low
        ):
            recommended = "battery_saver"
            reason = f"Battery is low ({battery}%) while unplugged. Stealth Mode is recommended."
            confidence = 0.96
        elif memory >= self.thresholds.memory_flush_pressure:
            recommended = "clean_ram"
            reason = f"Memory pressure is high ({memory:.1f}%). Memory Flush is recommended."
            confidence = 0.91
        elif cpu >= self.thresholds.combat_cpu_high:
            recommended = "gaming_boost"
            reason = f"CPU pressure is very high ({cpu:.1f}%). Combat Mode is recommended."
            confidence = 0.88
        elif cpu >= self.thresholds.neural_cpu_pressure:
            recommended = "performance_boost"
            reason = f"CPU load is elevated ({cpu:.1f}%). Neural Sync can rebalance workloads."
            confidence = 0.82

        return {
            "recommended": recommended,
            "reason": reason,
            "confidence": confidence,
            "metrics": metrics,
            "decision": {
                "engine": "rule_based_v1",
                "auto_trigger_candidate": recommended is not None,
                "thresholds": {
                    "combat_cpu_high": self.thresholds.combat_cpu_high,
                    "stealth_battery_low": self.thresholds.stealth_battery_low,
                    "neural_cpu_pressure": self.thresholds.neural_cpu_pressure,
                    "memory_flush_pressure": self.thresholds.memory_flush_pressure,
                },
            },
        }

