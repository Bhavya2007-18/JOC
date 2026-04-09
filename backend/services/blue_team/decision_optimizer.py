"""Decision optimization for Blue Team — tracks which actions work best."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from utils.logger import get_logger

from .defense_memory import DefenseMemory

logger = get_logger("blue_team.decision_optimizer")


class DecisionOptimizer:
    """Learns which defensive actions are most effective over time.

    Tracks the success rate of each action type and uses historical data
    to recommend the best response for each anomaly type.
    """

    def __init__(self, memory: DefenseMemory) -> None:
        self.memory = memory

    def record_outcome(self, action: str, effective: bool) -> None:
        """Record whether a defensive action was effective."""
        self.memory.record_action_outcome(action, effective)
        logger.info("Action outcome: %s effective=%s", action, effective)

    def suggest_optimal_action(self, anomaly_type: str) -> Dict[str, Any]:
        """Suggest the best action for a given anomaly type based on history.

        Returns a recommendation with confidence based on sample size.
        """
        # Default action mappings (fallback when no history exists)
        default_actions = {
            "cpu_spike": "lower_priority",
            "unknown_high_cpu_process": "inspect_process",
            "idle_period_activity": "review_scheduled_tasks",
            "memory_leak": "suggest_cleanup",
        }

        default = default_actions.get(anomaly_type, "investigate")
        best = self.memory.get_best_action()

        if best:
            success_rate = self.memory.get_action_success_rate(best)
            attempts = self.memory._state.get("action_attempts", {}).get(best, 0)
            confidence = min(1.0, attempts / 20)  # Confidence grows with sample size
            return {
                "recommended_action": best,
                "success_rate": round(success_rate * 100, 1),
                "confidence": round(confidence, 2),
                "sample_size": attempts,
                "source": "learned",
            }
        else:
            return {
                "recommended_action": default,
                "success_rate": 50.0,
                "confidence": 0.3,
                "sample_size": 0,
                "source": "default",
            }

    def get_all_action_stats(self) -> List[Dict[str, Any]]:
        """Return stats for all tracked actions."""
        rates = self.memory._state.get("action_success_rates", {})
        attempts = self.memory._state.get("action_attempts", {})

        stats = []
        for action in rates:
            stats.append({
                "action": action,
                "success_rate": round(rates[action] * 100, 1),
                "attempts": attempts.get(action, 0),
            })

        stats.sort(key=lambda x: x["success_rate"], reverse=True)
        return stats
