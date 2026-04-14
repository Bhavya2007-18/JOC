from typing import Any

from training.taxonomy import ScenarioTraits


class RuntimeOptimizer:
    def __init__(self, memory_store: Any):
        self.memory = memory_store

    def get_boosted_action(
        self,
        scenario: str,
        traits: ScenarioTraits,
        fallback_action: dict,
    ):
        learned = self.memory.get_best_action(scenario, traits)

        # Case 1: no learned action, keep engine fallback.
        if not learned:
            return fallback_action

        learned_action = dict(learned) if isinstance(learned, dict) else {}

        # Case 2: no fallback action, use memory action directly.
        if not fallback_action:
            learned_action.setdefault("source", "memory")
            return learned_action

        # Case 3: both exist.
        if fallback_action.get("action_type") == learned_action.get("action_type"):
            base_conf = fallback_action.get("confidence", 0.5)
            if not isinstance(base_conf, (int, float)):
                base_conf = 0.5
            fallback_action["confidence"] = min(1.0, float(base_conf) + 0.2)
            fallback_action["source"] = "engine+memory"
            return fallback_action

        learned_action["source"] = "memory_override"
        return learned_action