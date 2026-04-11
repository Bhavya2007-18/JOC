from typing import Dict, Any, List
from .models import SystemSnapshot

class PolicyEngine:
    """
    Translates user goals (Beast, Chill, Smart) into constraints and decisions.
    Acts as a lightweight RL rule-engine.
    """
    def __init__(self):
        self.current_goal = "smart"
        # thresholds: [cpu_soft, cpu_hard, mem_soft, mem_hard]
        self.policies = {
            "chill": {"cpu": [30, 50], "mem": [50, 70], "aggressiveness": 0.8},
            "smart": {"cpu": [60, 85], "mem": [75, 90], "aggressiveness": 0.5},
            "beast": {"cpu": [85, 98], "mem": [85, 95], "aggressiveness": 0.2}
        }

    def set_goal(self, goal: str):
        if goal in self.policies:
            self.current_goal = goal

    def evaluate(self, snapshot: SystemSnapshot, forecast: Dict[str, dict], causal_graph: Dict[str, Any]) -> List[Dict[str, Any]]:
        policy = self.policies[self.current_goal]
        actions = []

        # Example: check forecast against hard limits
        if forecast.get("cpu") and forecast["cpu"].get("5m", 0) > policy["cpu"][1]:
            # Imminent hard breach, check causal root
            root = causal_graph.get("root_cause_node")
            if root:
                actions.append({
                    "action_type": "suspend" if self.current_goal == "chill" else "priority_down",
                    "target": root,
                    "reason": f"Predicted to breach CPU hard limit ({policy['cpu'][1]}%) under '{self.current_goal}' policy.",
                    "urgency": "high"
                })

        return actions
