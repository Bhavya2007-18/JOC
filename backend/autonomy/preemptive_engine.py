from typing import Dict, Any, Optional

class PreemptiveEngine:
    def __init__(self):
        """
        Analyzes statistical predictive trajectories to inject early interventions
        before threat limits are intrinsically breached.
        """
        self.cpu_threshold = 90.0
        self.ram_threshold = 90.0

    def check(self, pred_data: Dict[str, Any], threat_data: Dict[str, Any], system_mode: str = "smart") -> Optional[Dict[str, Any]]:
        """
        Calculates preemptive triggers based on upcoming timeline signals.
        Returns mapped urgency payloads for the DecisionEngine.
        """
        if not pred_data or "trajectory" not in pred_data:
            return None
            
        trajectory = pred_data.get("trajectory", [])
        if not trajectory:
            return None
        
        # Adjust thresholds based on system mode
        # CHILL: Very aggressive saving
        # SMART: Balance
        # BEAST: Performance prioritized, let it run hot
        mode_thresholds = {
            "chill": (70.0, 70.0),
            "smart": (90.0, 90.0),
            "beast": (98.0, 98.0)
        }
        cpu_limit, ram_limit = mode_thresholds.get(system_mode.lower(), (90.0, 90.0))

        # Examine worst-case scenario dynamically
        max_pred_cpu = max([point.get("cpu", 0) for point in trajectory] + [0])
        max_pred_ram = max([point.get("ram", 0) for point in trajectory] + [0])
        
        if max_pred_cpu > cpu_limit:
            return {
                "recommended_action": "preemptive_throttle",
                "urgency": 0.90,
                "reason": f"[{system_mode.upper()}] Predicted CPU spike to {max_pred_cpu:.1f}% (Limit: {cpu_limit}%)"
            }
            
        if max_pred_ram > ram_limit:
            return {
                "recommended_action": "clear_cache",
                "urgency": 0.85,
                "reason": f"[{system_mode.upper()}] Predicted RAM exhaustion to {max_pred_ram:.1f}% (Limit: {ram_limit}%)"
            }
            
        return None
