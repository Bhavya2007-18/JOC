from typing import Dict, Any, Optional

class FeedbackEngine:
    def __init__(self):
        self._action_context: Optional[Dict[str, Any]] = None
        self._baseline_snapshot: Optional[Dict[str, Any]] = None
        self._measurement_delay: int = 3
        self._cycles_since_action: int = 0
        self._monitor_interval_sec: float = 5.0

    def register_action(
        self, 
        action_result: Dict[str, Any], 
        pre_threat_score: int, 
        pre_cpu: float, 
        pre_ram: float
    ) -> None:
        """Called immediately after ActionEngine executes."""
        self._action_context = action_result
        self._baseline_snapshot = {
            "threat_score": pre_threat_score,
            "cpu": pre_cpu,
            "ram": pre_ram
        }
        self._cycles_since_action = 0

    def measure(self, current_threat: int, current_cpu: float, current_ram: float) -> Optional[Dict[str, Any]]:
        """
        Called every monitor loop tick. Retuns measurement once delay is saturated.
        """
        if not self._action_context or not self._baseline_snapshot:
            return None

        self._cycles_since_action += 1

        if self._cycles_since_action < self._measurement_delay:
            return None

        # Delay reached, calculate feedback
        pre_threat = self._baseline_snapshot["threat_score"]
        threat_delta = pre_threat - current_threat
        
        # Guard divide by zero
        if pre_threat == 0:
            pre_threat = 1

        impact_reduction = min(100.0, max(-100.0, (threat_delta / pre_threat) * 100.0))
        recovery_time = self._cycles_since_action * self._monitor_interval_sec

        result_label = "failure"
        if impact_reduction > 20:
            result_label = "success"
        elif impact_reduction > 0:
            result_label = "partial"
            
        # Over-correction detection
        if current_threat < 10 and pre_threat < 40 and impact_reduction <= 0:
            result_label = "over-correction"

        feedback = {
            "result": result_label,
            "impact_reduction": round(impact_reduction, 2),
            "recovery_time": recovery_time,
            "threat_before": self._baseline_snapshot["threat_score"],
            "threat_after": current_threat,
            "action": self._action_context.get("action"),
            "target": self._action_context.get("target")
        }

        # Reset state after measurement
        self._action_context = None
        self._baseline_snapshot = None
        self._cycles_since_action = 0

        return feedback
