from typing import Dict, Any, Optional

class PreemptiveEngine:
    def __init__(self):
        """
        Analyzes statistical predictive trajectories to inject early interventions
        before threat limits are intrinsically breached.
        """
        self.cpu_threshold = 90.0
        self.ram_threshold = 90.0

    def check(self, pred_data: Dict[str, Any], threat_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Calculates preemptive triggers based on upcoming timeline signals.
        Returns mapped urgency payloads for the DecisionEngine.
        """
        if not pred_data or "trajectory" not in pred_data:
            return None
            
        trajectory = pred_data.get("trajectory", [])
        if not trajectory:
            return None
        
        # Examine worst-case scenario dynamically
        max_pred_cpu = max([point.get("cpu", 0) for point in trajectory] + [0])
        max_pred_ram = max([point.get("ram", 0) for point in trajectory] + [0])
        
        if max_pred_cpu > self.cpu_threshold:
            return {
                "recommended_action": "preemptive_throttle",
                "urgency": 0.90,
                "reason": f"Predicted CPU spike to {max_pred_cpu:.1f}%"
            }
            
        if max_pred_ram > self.ram_threshold:
            return {
                "recommended_action": "clear_cache",
                "urgency": 0.85,
                "reason": f"Predicted RAM exhaustion to {max_pred_ram:.1f}%"
            }
            
        return None
