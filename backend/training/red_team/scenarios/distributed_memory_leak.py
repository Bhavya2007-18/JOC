import math
import random
from typing import List

from training.red_team.virtual_snapshot import VirtualProcessInfo, VirtualSnapshot
from training.red_team.scenario_params import ScenarioParams


def generate_distributed_memory_leak_scenario(params: ScenarioParams = None) -> List[VirtualSnapshot]:
    if params is None:
        params = ScenarioParams(intensity=0.95, duration_steps=10, concentration="distributed", ramp_style="gradual")
        
    random.seed(params.seed)
    n_steps = params.duration_steps
    peak_memory = params.intensity * 100.0
    
    scenario: List[VirtualSnapshot] = []

    for idx in range(n_steps):
        if params.ramp_style == "sudden":
            current_memory = 50.0 if idx < n_steps // 2 else peak_memory
        elif params.ramp_style == "oscillating":
            progress = idx / max(1, n_steps - 1)
            base_mem = 50.0 + (peak_memory - 50.0) * progress
            current_memory = base_mem + 3.0 * math.sin(idx * 2)
        else: # gradual
            progress = idx / max(1, n_steps - 1)
            current_memory = 50.0 + (peak_memory - 50.0) * progress
            
        current_memory = min(100.0, max(0.0, current_memory))

        current_cpu = 22.0 + (idx * 0.5)
        current_disk = 30.0 + (idx * 0.3)
        
        # Distributed memory leak = many processes growing slowly
        if params.concentration == "distributed":
            chrome_mem = current_memory * 0.20
            code_mem = current_memory * 0.18
            helper_mem = current_memory * 0.16
            service_mem = current_memory * 0.15
            bg_mem = current_memory * 0.12
        else:
            # Fallback if concentration is single incorrectly passed here
            chrome_mem = current_memory * 0.50
            code_mem = current_memory * 0.10
            helper_mem = current_memory * 0.10
            service_mem = current_memory * 0.10
            bg_mem = current_memory * 0.05

        processes = [
            VirtualProcessInfo(
                name="chrome.exe",
                pid=1234,
                cpu_percent=5.0 + (idx * 0.2),
                memory_percent=chrome_mem,
            ),
            VirtualProcessInfo(
                name="code.exe",
                pid=2345,
                cpu_percent=4.5 + (idx * 0.1),
                memory_percent=code_mem,
            ),
            VirtualProcessInfo(
                name="helper.exe",
                pid=3456,
                cpu_percent=4.0 + (idx * 0.1),
                memory_percent=helper_mem,
            ),
            VirtualProcessInfo(
                name="service.exe",
                pid=4567,
                cpu_percent=3.5 + (idx * 0.1),
                memory_percent=service_mem,
            ),
            VirtualProcessInfo(
                name="background.exe",
                pid=5678,
                cpu_percent=3.0,
                memory_percent=bg_mem,
            ),
        ]

        scenario.append(
            VirtualSnapshot(
                cpu_percent=current_cpu,
                memory_percent=current_memory,
                disk_percent=current_disk,
                process_count=112 + idx * 3,
                top_processes=processes,
            )
        )

    return scenario
