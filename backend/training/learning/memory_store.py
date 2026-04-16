import json
import os

from training.taxonomy import ScenarioTraits

BASE_DIR = os.path.dirname(__file__)
MEMORY_PATH = os.path.join(BASE_DIR, "memory.json")


class UnifiedMemoryStore:
    def __init__(self) -> None:
        self.scenario_index = {}
        self.trait_index = {}

    def _traits_key(self, traits: ScenarioTraits) -> tuple:
        return (
            traits.resource_type,
            traits.pattern,
            traits.process_concentration,
            traits.severity_band,
            traits.has_root_cause_process,
        )

    def _update_action_stats(self, action_map: dict, action: str, impact: float) -> None:
        if action not in action_map:
            action_map[action] = {
                "total_runs": 0,
                "total_impact": 0.0,
                "avg_impact": 0.0,
            }

        action_stats = action_map[action]
        action_stats["total_runs"] += 1
        action_stats["total_impact"] += impact
        action_stats["avg_impact"] = (
            action_stats["total_impact"] / action_stats["total_runs"]
        )

    def _best_action_from_map(self, action_map: dict):
        if not action_map:
            return None

        return max(
            action_map,
            key=lambda action_name: action_map[action_name]["avg_impact"],
        )

    def update(self, scenario: str, traits: ScenarioTraits, action: str, impact: float) -> None:
        if scenario not in self.scenario_index:
            self.scenario_index[scenario] = {}
        self._update_action_stats(self.scenario_index[scenario], action, impact)

        key = self._traits_key(traits)
        if key not in self.trait_index:
            self.trait_index[key] = {}
        self._update_action_stats(self.trait_index[key], action, impact)

    def get_best_action(self, scenario: str, traits: ScenarioTraits):
        scenario_actions = self.scenario_index.get(scenario)
        best_action = self._best_action_from_map(scenario_actions)
        if best_action:
            return {
                "action_type": best_action,
                "source": "memory",
            }

        if not self.trait_index:
            return None

        best_key = None
        best_similarity = -1.0

        for key in self.trait_index:
            indexed_traits = ScenarioTraits(
                resource_type=key[0],
                pattern=key[1],
                process_concentration=key[2],
                severity_band=key[3],
                has_root_cause_process=key[4],
            )
            similarity = traits.similarity(indexed_traits)
            if similarity < 0.4:
                continue
            if similarity > best_similarity:
                best_similarity = similarity
                best_key = key

        if best_key is None:
            return None

        best_action = self._best_action_from_map(self.trait_index.get(best_key, {}))
        if not best_action:
            return None

        return {
            "action_type": best_action,
            "source": "memory",
        }

    def print_memory(self) -> None:
        if not self.scenario_index and not self.trait_index:
            print("Memory is empty")
            return

        if self.scenario_index:
            print("scenario_index:")
            for scenario, actions in self.scenario_index.items():
                print(f"  {scenario}:")
                for action_name, stats in actions.items():
                    print(
                        f"    {action_name} -> "
                        f"runs={stats['total_runs']} "
                        f"total_impact={stats['total_impact']:.2f} "
                        f"avg_impact={stats['avg_impact']:.2f}"
                    )

    def save(self, filepath=MEMORY_PATH):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(
                {
                    "scenario_index": self.scenario_index,
                    "trait_index": {str(k): v for k, v in self.trait_index.items()},
                },
                f,
            )

    def load(self, filepath=MEMORY_PATH):
        if not os.path.exists(filepath):
            return

        with open(filepath, "r") as f:
            data = json.load(f)

        self.scenario_index = data.get("scenario_index", {})

        import ast
        self.trait_index = {}
        for k, v in data.get("trait_index", {}).items():
            key = ast.literal_eval(k)
            self.trait_index[key] = v

        if self.trait_index:
            print("trait_index:")
            for key, actions in self.trait_index.items():
                print(f"  {key}:")
                for action_name, stats in actions.items():
                    print(
                        f"    {action_name} -> "
                        f"runs={stats['total_runs']} "
                        f"total_impact={stats['total_impact']:.2f} "
                        f"avg_impact={stats['avg_impact']:.2f}"
                    )
