import math
import random
from typing import List

from training.red_team.virtual_snapshot import VirtualProcessInfo, VirtualSnapshot
from training.red_team.scenario_params import ScenarioParams


def generate_disk_pressure_scenario(params: ScenarioParams = None) -> List[VirtualSnapshot]:
    if params is None:
        params = ScenarioParams(intensity=0.9, duration_steps=10, concentration="single", ramp_style="gradual")
        
    random.seed(params.seed)
    n_steps = params.duration_steps
    peak_disk = params.intensity * 100.0
    
    scenario: List[VirtualSnapshot] = []

    for idx in range(n_steps):
        if params.ramp_style == "sudden":
            current_disk = 30.0 if idx < n_steps // 3 else peak_disk
        elif params.ramp_style == "oscillating":
            progress = idx / max(1, n_steps - 1)
            current_disk = 30.0 + (peak_disk - 30.0) * abs(math.sin(idx * math.pi / (n_steps / 2)))
        else: # gradual
            progress = idx / max(1, n_steps - 1)
            current_disk = 30.0 + (peak_disk - 30.0) * progress
            
        current_disk = min(100.0, max(0.0, current_disk))

        current_cpu = 30.0 + (idx * 0.5)
        current_memory = 45.0 + (idx * 0.5)
        
        if params.concentration == "distributed":
            indexer_cpu = current_cpu * 0.3
            backup_cpu = current_cpu * 0.3
            system_cpu = current_cpu * 0.2
        else:
            indexer_cpu = current_cpu * 0.7
            backup_cpu = current_cpu * 0.1
            system_cpu = current_cpu * 0.1

        processes = [
            VirtualProcessInfo(
                name="indexer.exe" if params.concentration == "single" else "db_writer_1.exe",
                pid=9001,
                cpu_percent=indexer_cpu,
                memory_percent=15.0,
            ),
            VirtualProcessInfo(
                name="backup.exe" if params.concentration == "single" else "db_writer_2.exe",
                pid=9002,
                cpu_percent=backup_cpu,
                memory_percent=12.0,
            ),
            VirtualProcessInfo(
                name="system.exe",
                pid=1,
                cpu_percent=system_cpu,
                memory_percent=5.0,
            ),
        ]

        scenario.append(
            VirtualSnapshot(
                cpu_percent=current_cpu,
                memory_percent=current_memory,
                disk_percent=current_disk,
                process_count=100 + idx,
                top_processes=processes,
            )
        )

    return scenario
