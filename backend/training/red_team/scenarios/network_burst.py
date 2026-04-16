import math
import random
from typing import List

from training.red_team.virtual_snapshot import VirtualProcessInfo, VirtualSnapshot
from training.red_team.scenario_params import ScenarioParams


def generate_network_burst_scenario(params: ScenarioParams = None) -> List[VirtualSnapshot]:
    if params is None:
        params = ScenarioParams(intensity=0.9, duration_steps=10, concentration="distributed", ramp_style="sudden")
        
    random.seed(params.seed)
    n_steps = params.duration_steps
    peak_network = params.intensity * 100.0
    
    scenario: List[VirtualSnapshot] = []

    for idx in range(n_steps):
        if params.ramp_style == "sudden":
            current_network = 10.0 if idx < n_steps // 3 else peak_network
        elif params.ramp_style == "oscillating":
            current_network = 10.0 + (peak_network - 10.0) * abs(math.sin(idx * math.pi / (n_steps / 2)))
        else: # gradual
            progress = idx / max(1, n_steps - 1)
            current_network = 10.0 + (peak_network - 10.0) * progress
            
        current_network = min(100.0, max(0.0, current_network))

        current_cpu = 15.0 + (current_network * 0.2) # Network implies some CPU usage
        current_memory = 40.0 + (idx * 0.2)
        
        if params.concentration == "distributed":
            chrome_cpu = current_cpu * 0.4
            torrent_cpu = current_cpu * 0.4
            system_cpu = current_cpu * 0.1
        else:
            chrome_cpu = current_cpu * 0.1
            torrent_cpu = current_cpu * 0.8
            system_cpu = current_cpu * 0.05

        processes = [
            VirtualProcessInfo(
                name="chrome.exe" if params.concentration == "single" else "downloader_1.exe",
                pid=1234,
                cpu_percent=chrome_cpu,
                memory_percent=25.0,
            ),
            VirtualProcessInfo(
                name="qbittorrent.exe" if params.concentration == "single" else "downloader_2.exe",
                pid=2345,
                cpu_percent=torrent_cpu,
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
                disk_percent=30.0 + (current_network * 0.1), # High net might mean disk writes
                process_count=110 + idx,
                top_processes=processes,
                network_percent=current_network
            )
        )

    return scenario
