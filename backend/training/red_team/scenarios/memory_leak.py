import math
import random
from typing import List

from training.red_team.virtual_snapshot import VirtualProcessInfo, VirtualSnapshot
from training.red_team.scenario_params import ScenarioParams


def generate_memory_leak_scenario(params: ScenarioParams = None) -> List[VirtualSnapshot]:
    if params is None:
        params = ScenarioParams(intensity=0.95, duration_steps=10, concentration="single", ramp_style="gradual")
        
    random.seed(params.seed)
    n_steps = params.duration_steps
    peak_memory = params.intensity * 100.0
    
    scenario: List[VirtualSnapshot] = []

    for idx in range(n_steps):
        # Memory leak typically grows over time
        if params.ramp_style == "sudden":
            current_memory = 40.0 if idx < n_steps // 2 else peak_memory
        elif params.ramp_style == "oscillating":
            # Leaks don't usually oscillate, but they could step up
            progress = idx / max(1, n_steps - 1)
            base_mem = 40.0 + (peak_memory - 40.0) * progress
            current_memory = base_mem + 5.0 * math.sin(idx)
        else: # gradual
            # Leaks often accelerate
            progress = idx / max(1, n_steps - 1)
            current_memory = 40.0 + (peak_memory - 40.0) * (progress ** 1.5)
            
        current_memory = min(100.0, max(0.0, current_memory))

        current_cpu = 24.0 + (idx * 0.5)
        current_disk = 31.0 + (idx * 0.2)
        
        if params.concentration == "distributed":
            leaky_app_mem = current_memory * 0.4
            code_mem = current_memory * 0.3
            system_mem = current_memory * 0.1
            helper_mem = current_memory * 0.1
        else:
            leaky_app_mem = current_memory * 0.7
            code_mem = current_memory * 0.1
            system_mem = current_memory * 0.05
            helper_mem = current_memory * 0.05

        processes = [
            VirtualProcessInfo(
                name="leaky_app.exe" if params.concentration == "single" else "worker_node_1.exe",
                pid=4321,
                cpu_percent=10.0 + (idx * 0.5),
                memory_percent=leaky_app_mem,
            ),
            VirtualProcessInfo(
                name="code.exe" if params.concentration == "single" else "worker_node_2.exe",
                pid=2345,
                cpu_percent=9.0,
                memory_percent=code_mem,
            ),
            VirtualProcessInfo(
                name="system.exe",
                pid=1,
                cpu_percent=5.0,
                memory_percent=system_mem,
            ),
            VirtualProcessInfo(
                name="helper_service.exe",
                pid=7890,
                cpu_percent=3.0,
                memory_percent=helper_mem,
            ),
        ]

        scenario.append(
            VirtualSnapshot(
                cpu_percent=current_cpu,
                memory_percent=current_memory,
                disk_percent=current_disk,
                process_count=104 + idx * 2,
                top_processes=processes,
            )
        )

    return scenario
