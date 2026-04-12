import time
from typing import Dict, Any

class LearningEngine:
    # Hyperparameters
    LEARNING_RATE = 0.15
    IMPACT_WEIGHT_FACTOR = 0.10
    MIN_WEIGHT = 0.3
    MAX_WEIGHT = 2.5
    BASE_WEIGHT = 1.0
    EMA_ALPHA = 0.3

    def __init__(self):
        # We track performance of default actions, assuming catalog from DecisionEngine
        # action_name -> performance_stats
        self._performance: Dict[str, Dict[str, Any]] = {}
        
        _initial_actions = [
            "throttle_process", "kill_process", "clear_cache", 
            "rate_limit", "no_action", "preemptive_throttle"
        ]
        
        for act in _initial_actions:
            self._performance[act] = {
                "total_executions": 0,
                "successes": 0,
                "partial": 0,
                "failures": 0,
                "over_corrections": 0,
                "avg_impact_reduction": 0.0,
                "current_weight": self.BASE_WEIGHT,
                "last_updated": 0.0
            }

    def record_outcome(self, action: str, feedback: Dict[str, Any]) -> None:
        """Updates performance stats and adjusts action weights based on feedback."""
        if action not in self._performance:
            self._performance[action] = {
                "total_executions": 0,
                "successes": 0,
                "partial": 0,
                "failures": 0,
                "over_corrections": 0,
                "avg_impact_reduction": 0.0,
                "current_weight": self.BASE_WEIGHT,
                "last_updated": 0.0
            }

        stats = self._performance[action]
        stats["total_executions"] += 1
        
        result_type = feedback.get("result", "failure")
        impact = feedback.get("impact_reduction", 0.0)

        # Update tallies
        if result_type == "success":
            stats["successes"] += 1
        elif result_type == "partial":
            stats["partial"] += 1
        elif result_type == "failure":
            stats["failures"] += 1
        elif result_type == "over-correction":
            stats["over_corrections"] += 1

        # EMA of impact reduction
        if stats["total_executions"] == 1:
            stats["avg_impact_reduction"] = impact
        else:
            stats["avg_impact_reduction"] = (self.EMA_ALPHA * impact) + ((1 - self.EMA_ALPHA) * stats["avg_impact_reduction"])

        # Calculate new weight
        success_rate = stats["successes"] / stats["total_executions"]
        weight_adjust = 0.0
        
        if result_type == "success":
            weight_adjust = self.LEARNING_RATE * (impact / 100.0)
        elif result_type == "failure":
            weight_adjust = -self.LEARNING_RATE * 0.5
        elif result_type == "over-correction":
            weight_adjust = -self.LEARNING_RATE * 0.8
        
        new_weight = self.BASE_WEIGHT + (success_rate - 0.5) * self.LEARNING_RATE + (stats["avg_impact_reduction"] / 100.0) * self.IMPACT_WEIGHT_FACTOR
        new_weight += weight_adjust
        
        # Clamp weight
        stats["current_weight"] = max(self.MIN_WEIGHT, min(self.MAX_WEIGHT, new_weight))
        stats["last_updated"] = time.time()

    def get_weights(self) -> Dict[str, float]:
        """Returns the current learned multiplier for each action."""
        return {action: stats["current_weight"] for action, stats in self._performance.items()}
        
    def get_performance_summary(self) -> Dict[str, Any]:
        """Returns full internal state for API reporting."""
        return self._performance
