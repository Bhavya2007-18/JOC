import random
from typing import Tuple, List

from training.red_team.virtual_snapshot import VirtualSnapshot
from training.red_team.scenario_vault import list_scenarios, get_scenario
from training.red_team.variation_engine import generate_variations

class RedAgent:
    def __init__(self, strategy="random"):
        self.strategy = strategy   # "random" | "adversarial" | "sweep"
        self._failure_log: dict[str, int] = {}  # scenario -> fail count
        self._sweep_index = 0

    def pick_episode(self) -> Tuple[str, List[VirtualSnapshot]]:
        all_scenarios = list_scenarios()
        
        if not all_scenarios:
            raise ValueError("No scenarios available in vault")

        if self.strategy == "sweep":
            chosen_name = all_scenarios[self._sweep_index % len(all_scenarios)]
            self._sweep_index += 1
        elif self.strategy == "adversarial" and self._failure_log:
            # Pick the scenario that blue failed at most
            chosen_name = max(self._failure_log, key=self._failure_log.get)
        else:
            chosen_name = random.choice(all_scenarios)
            
        # For base scenarios, sometimes get a variation instead of the default
        if chosen_name in list_scenarios() and not chosen_name.startswith("compound_"):
            # 50% chance to use variation if single
            if random.random() < 0.5:
                variations = generate_variations(chosen_name, n=1)
                if variations:
                    return chosen_name, variations[0]

        # Use default if no variation chosen or it's a compound scenario
        return chosen_name, get_scenario(chosen_name)

    def record_failure(self, scenario_name: str):
        self._failure_log[scenario_name] = self._failure_log.get(scenario_name, 0) + 1
