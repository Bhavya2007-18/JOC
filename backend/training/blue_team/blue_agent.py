from training.red_team.virtual_snapshot import VirtualSnapshot
from intelligence.engine import IntelligenceEngine
from training.learning.global_memory import memory
from training.taxonomy import ScenarioTraits

class BlueAgent:
    def __init__(self):
        self.engine = IntelligenceEngine()

    def observe(self, snapshot: VirtualSnapshot) -> dict: # returns analysis result
        return self.engine.analyze(snapshot)

    def decide(self, analysis) -> dict: # analysis is IntelligenceResult
        best_action = None
        if analysis.issues:
            best_action = analysis.issues[0].best_action
        return best_action or {}

    def act(self, snapshot: VirtualSnapshot, action: dict) -> VirtualSnapshot:
        # Import apply_action from training_loop.py or implement it here
        from training.blue_team.training_loop import apply_action
        return apply_action(snapshot, action)

    def learn(self, scenario_name: str, traits: ScenarioTraits, action_type: str, impact_score: float):
        memory.update(scenario_name, traits, action_type, impact_score)
