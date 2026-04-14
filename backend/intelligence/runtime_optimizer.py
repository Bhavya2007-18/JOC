from typing import Any

from training.taxonomy import ScenarioTraits


class RuntimeOptimizer:
    def __init__(self, memory_store: Any):
        self.memory = memory_store

    def _get_avg_impact(self, scenario: str, action_type: str):
        scenario_index = getattr(self.memory, "scenario_index", {})
        if not isinstance(scenario_index, dict):
            return None

        scenario_actions = scenario_index.get(scenario, {})
        if not isinstance(scenario_actions, dict):
            return None

        action_stats = scenario_actions.get(action_type, {})
        if not isinstance(action_stats, dict):
            return None

        avg_impact = action_stats.get("avg_impact")
        if isinstance(avg_impact, (int, float)):
            return float(avg_impact)
        return None

    def get_boosted_action(
        self,
        scenario: str,
        traits: ScenarioTraits,
        fallback_action: dict,
    ):
        learned = self.memory.get_best_action(scenario, traits)

        # Case 1: no learned action.
        if not learned:
            return fallback_action

        learned_action = dict(learned) if isinstance(learned, dict) else {}
        learned_type = learned_action.get("action_type")

        # Case 2: no fallback action.
        if not fallback_action:
            learned_action.setdefault("source", "memory")
            return learned_action

        fallback_type = fallback_action.get("action_type")

        # Keep existing behavior for same action types.
        if fallback_type == learned_type:
            merged = dict(fallback_action)
            base_conf = merged.get("confidence", 0.5)
            if not isinstance(base_conf, (int, float)):
                base_conf = 0.5
            merged["confidence"] = min(
                1.0,
                float(base_conf) + 0.2,
            )
            merged["source"] = "engine+memory"
            return merged

        learned_avg_impact = self._get_avg_impact(scenario, str(learned_type or ""))
        fallback_avg_impact = fallback_action.get("avg_impact")
        if not isinstance(fallback_avg_impact, (int, float)):
            if isinstance(learned_avg_impact, (int, float)):
                fallback_avg_impact = learned_avg_impact - 0.01
            else:
                fallback_avg_impact = None

        fallback_confidence = fallback_action.get("confidence", 1.0)
        if not isinstance(fallback_confidence, (int, float)):
            fallback_confidence = 1.0

        # Case 3: both exist and actions differ.
        should_override = learned_type != fallback_type

        # Force override when engine confidence is low.
        if float(fallback_confidence) < 0.7:
            should_override = True

        if should_override:
            override = dict(learned_action)
            override["source"] = "memory_override"
            override["reason"] = "memory_outperformed_engine"
            if isinstance(learned_avg_impact, (int, float)):
                override["avg_impact"] = float(learned_avg_impact)
            if isinstance(fallback_avg_impact, (int, float)):
                override["fallback_estimated_impact"] = float(fallback_avg_impact)
            return override

        return fallback_action