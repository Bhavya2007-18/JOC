import random
from typing import List

from training.red_team.virtual_snapshot import VirtualSnapshot
from training.red_team.scenario_params import ScenarioParams
from training.red_team.scenario_vault import get_scenario

INTENSITY_BANDS = [0.5, 0.7, 0.85, 1.0]           # moderate -> critical
DURATION_STEPS = [5, 10, 20]                      # short, medium, long
CONCENTRATIONS = ["single", "distributed"]
RAMP_STYLES = ["sudden", "gradual", "oscillating"]

def generate_variations(scenario_name: str, n: int = 50) -> List[List[VirtualSnapshot]]:
    variations = []
    
    # Generate random combinations up to n
    for i in range(n):
        intensity = random.choice(INTENSITY_BANDS)
        duration = random.choice(DURATION_STEPS)
        concentration = random.choice(CONCENTRATIONS)
        ramp = random.choice(RAMP_STYLES)
        
        # Add slight jitter to intensity
        jittered_intensity = max(0.1, min(1.0, intensity + random.uniform(-0.05, 0.05)))
        
        params = ScenarioParams(
            intensity=jittered_intensity,
            duration_steps=duration,
            concentration=concentration,
            ramp_style=ramp,
            seed=i  # Deterministic seed for this variation
        )
        
        snapshotSequence = get_scenario(scenario_name, params)
        variations.append(snapshotSequence)
        
    return variations
