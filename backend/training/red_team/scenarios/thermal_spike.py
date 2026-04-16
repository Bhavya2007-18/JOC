import math
import random
from typing import List

from training.red_team.virtual_snapshot import VirtualProcessInfo, VirtualSnapshot
from training.red_team.scenario_params import ScenarioParams


def generate_thermal_spike_scenario(params: ScenarioParams = None) -> List[VirtualSnapshot]:
    if params is None:
        params = ScenarioParams(intensity=0.9, duration_steps=10, concentration="single", ramp_style="gradual")
        
    random.seed(params.seed)
    n_steps = params.duration_steps
    # Thermal maps 0.0-1.0 to 50C - 105C
    peak_thermal = 50.0 + (55.0 * params.intensity)
    
    scenario: List[VirtualSnapshot] = []

    for idx in range(n_steps):
        if params.ramp_style == "sudden":
            current_thermal = 50.0 if idx < n_steps // 2 else peak_thermal
        elif params.ramp_style == "oscillating":
            progress = idx / max(1, n_steps - 1)
            current_thermal = 50.0 + (peak_thermal - 50.0) * progress
            current_thermal += 10.0 * math.sin(idx) # fluctuate
        else: # gradual
            progress = idx / max(1, n_steps - 1)
            current_thermal = 50.0 + (peak_thermal - 50.0) * progress
            
        current_thermal = min(110.0, max(30.0, current_thermal))

        # High thermal is usually driven by high CPU/GPU
        current_cpu = 40.0 + ((current_thermal - 50.0) / 55.0) * 60.0
        current_memory = 55.0

        if params.concentration == "distributed":
            chrome_cpu = current_cpu * 0.3
            game_cpu = current_cpu * 0.3
            video_cpu = current_cpu * 0.3
        else:
            chrome_cpu = current_cpu * 0.1
            game_cpu = current_cpu * 0.8
            video_cpu = current_cpu * 0.05

        processes = [
            VirtualProcessInfo(
                name="chrome.exe",
                pid=1234,
                cpu_percent=chrome_cpu,
                memory_percent=15.0,
            ),
            VirtualProcessInfo(
                name="cyberpunk2077.exe" if params.concentration == "single" else "rendering_node.exe",
                pid=9999,
                cpu_percent=game_cpu,
                memory_percent=40.0,
            ),
            VirtualProcessInfo(
                name="ffmpeg.exe",
                pid=5555,
                cpu_percent=video_cpu,
                memory_percent=10.0,
            ),
        ]

        scenario.append(
            VirtualSnapshot(
                cpu_percent=current_cpu,
                memory_percent=current_memory,
                disk_percent=20.0,
                process_count=120,
                top_processes=processes,
                thermal_percent=current_thermal
            )
        )

    return scenario
