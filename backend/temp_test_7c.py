from intelligence.patterns.abstraction_engine import AbstractionEngine
from intelligence.learning.cross_scenario_engine import CrossScenarioEngine

eng  = AbstractionEngine()
cse  = CrossScenarioEngine()

baseline = {'cpu_z_score': 3.1, 'ram_z_score': 0.2, 'window_fill': 0.9, 'cpu_baseline': 40, 'ram_baseline': 60, 'cpu_std': 5, 'ram_std': 4}
pred     = {'predicted_cpu': {'trend': 'rising_fast'}, 'predicted_ram': {'trend': 'stable'}}

for i in range(6):
    pattern = eng.classify(cpu=90, ram=55, baseline_data=baseline, pred_data=pred)
    result  = cse.update(pattern, current_threat_score=80)
    print(f'Tick {i}: pattern={pattern["pattern_type"]}, rec={result}')

cse.record_tweak_executed('neural_sync', result.get('pattern_id', 'x'), pre_threat=80)

for i in range(2):
    result = cse.update(pattern, current_threat_score=55)
    print(f'Post-tweak tick {i}: {cse.get_learning_summary()}')
