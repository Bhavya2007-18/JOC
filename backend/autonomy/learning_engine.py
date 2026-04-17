import time
import json
import os
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
            "rate_limit", "reduce_io", "suspend_process", 
            "no_action", "preemptive_throttle"
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
                "last_updated": 0.0,
                "experiences": []
            }

    def record_outcome(self, action: str, feedback: Dict[str, Any], context: Dict[str, float] = None) -> None:
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
                "last_updated": 0.0,
                "experiences": []
            }

        stats = self._performance[action]
        stats["total_executions"] += 1
        
        result_type = feedback.get("result", "failure")
        impact = feedback.get("impact_reduction", 0.0)

        # Record Q-learning context experience
        if context:
            stats["experiences"].append({
                "context": context,
                "impact": impact,
                "timestamp": time.time()
            })
            # keep history bounded
            if len(stats["experiences"]) > 100:
                stats["experiences"].pop(0)

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

    def get_weights(self, context: Dict[str, float] = None) -> Dict[str, float]:
        """Returns the current learned multiplier for each action, with Q-learning interpolation."""
        weights = {}
        for action, stats in self._performance.items():
            base_w = stats.get("current_weight", self.BASE_WEIGHT)
            
            if not context or not stats.get("experiences"):
                weights[action] = base_w
                continue
                
            # Q-learning interpolation (KNN weighting)
            # Find close experiences in state space
            total_influence = 0.0
            weighted_impact_sum = 0.0
            
            # Simple euclidean distance over CPU and RAM
            req_cpu = context.get("cpu_percent", 0.0)
            req_ram = context.get("memory_percent", 0.0)
            
            for exp in stats["experiences"][-20:]:  # Look at recent 20 context matches
                exp_ctx = exp["context"]
                e_cpu = exp_ctx.get("cpu_percent", req_cpu)
                e_ram = exp_ctx.get("memory_percent", req_ram)
                
                dist_sq = (req_cpu - e_cpu)**2 + (req_ram - e_ram)**2
                # Convert distance to influence (closer = higher influence)
                influence = 1.0 / (1.0 + (dist_sq / 100.0))  
                
                weighted_impact_sum += exp["impact"] * influence
                total_influence += influence
                
            if total_influence > 0:
                expected_impact = weighted_impact_sum / total_influence
                # Modulate the base weight by contextual expectations
                context_modulator = 1.0 + (expected_impact / 200.0) # slightly boost or penalize
                context_weight = base_w * context_modulator
                weights[action] = max(self.MIN_WEIGHT, min(self.MAX_WEIGHT, context_weight))
            else:
                weights[action] = base_w
                
        return weights
    def get_performance_summary(self) -> Dict[str, Any]:
        """Returns full internal state for API reporting."""
        return self._performance

    def save(self, path: str = None) -> None:
        if path is None:
            path = os.path.join(os.path.dirname(__file__), "learning_state.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(self._performance, f, indent=2)

    def load(self, path: str = None) -> None:
        if path is None:
            path = os.path.join(os.path.dirname(__file__), "learning_state.json")
        if not os.path.exists(path):
            return
        with open(path, "r") as f:
            data = json.load(f)
        for action, stats in data.items():
            if action in self._performance:
                self._performance[action].update(stats)
            else:
                self._performance[action] = stats
