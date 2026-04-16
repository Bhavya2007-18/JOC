from dataclasses import dataclass

@dataclass
class ScenarioParams:
    intensity: float       # 0.0–1.0 -> maps to peak CPU/RAM/Disk %
    duration_steps: int    # 5=short, 15=medium, 30=long
    concentration: str     # "single" | "distributed"
    ramp_style: str        # "sudden" | "gradual" | "oscillating"
    seed: int = 0
