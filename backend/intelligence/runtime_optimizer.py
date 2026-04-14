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

        # Case 3: both exist — merge but prioritize memory identity.
        if fallback_action.get("action_type") == learned_action.get("action_type"):
            merged = dict(fallback_action)
            merged["confidence"] = min(
                1.0,
                float(fallback_action.get("confidence", 0.5)) + 0.2,
            )
            merged["source"] = "memory_confirmed"
            merged["learned_action"] = learned_action.get("action_type")
            return merged

        learned_action["source"] = "memory_override"
        return learned_action