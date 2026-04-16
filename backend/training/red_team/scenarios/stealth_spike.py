import math
import random
from typing import List

from training.red_team.virtual_snapshot import VirtualProcessInfo, VirtualSnapshot
from training.red_team.scenario_params import ScenarioParams


def generate_stealth_spike_scenario(params: ScenarioParams = None) -> List[VirtualSnapshot]:
    if params is None:
        params = ScenarioParams(intensity=0.7, duration_steps=12, concentration="distributed", ramp_style="sudden")
        
    random.seed(params.seed)
    n_steps = params.duration_steps
    
    scenario: List[VirtualSnapshot] = []

    for idx in range(n_steps):
        # Stealth spike logic: Many small spikes in randomly named background processes
        is_spiking = idx % 2 == 1  # Pulse every other step
        base_cpu = 25.0
        
        current_cpu = base_cpu
        if is_spiking:
            current_cpu += params.intensity * 40.0
            
        current_memory = 40.0 + (idx * 0.2)
        current_disk = 15.0

        processes = []
        process_count = 150 + idx
        
        if is_spiking:
            # Spread the cpu load across 5 "stealth" instances
            spread_cpu = (current_cpu - base_cpu) / 5.0
            for i in range(5):
                processes.append(
                    VirtualProcessInfo(
                        name=f"svchost_{i}.exe", # Camouflaged name
                        pid=3000 + i,
                        cpu_percent=spread_cpu + random.uniform(0.1, 1.0),
                        memory_percent=1.0,
                    )
                )

        processes.extend([
            VirtualProcessInfo(
                name="explorer.exe",
                pid=999,
                cpu_percent=5.0,
                memory_percent=10.0,
            ),
            VirtualProcessInfo(
                name="dwm.exe",
                pid=1000,
                cpu_percent=3.0,
                memory_percent=5.0,
            )
        ])

        scenario.append(
            VirtualSnapshot(
                cpu_percent=current_cpu,
                memory_percent=current_memory,
                disk_percent=current_disk,
                process_count=process_count,
                top_processes=processes,
            )
        )

    return scenario
