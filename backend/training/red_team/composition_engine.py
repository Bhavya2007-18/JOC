from typing import List, Tuple

from training.red_team.virtual_snapshot import VirtualSnapshot, VirtualProcessInfo
from training.red_team.scenario_params import ScenarioParams
from training.red_team.scenario_vault import get_scenario

def compose(
    name_a: str, params_a: ScenarioParams,
    name_b: str, params_b: ScenarioParams,
    label: str = None
) -> Tuple[str, List[VirtualSnapshot]]:
    """
    Combines two scenarios into a single sequence of compound snapshots.
    """
    seq_a = get_scenario(name_a, params_a)
    seq_b = get_scenario(name_b, params_b)
    
    # Pad the shorter one by repeating the last frame
    max_len = max(len(seq_a), len(seq_b))
    
    while len(seq_a) < max_len:
        seq_a.append(seq_a[-1])
        
    while len(seq_b) < max_len:
        seq_b.append(seq_b[-1])
        
    merged = []
    
    for a, b in zip(seq_a, seq_b):
        # Merge basic metrics
        cpu = min(100.0, a.cpu_percent + b.cpu_percent)
        mem = min(100.0, a.memory_percent + b.memory_percent)
        disk = min(100.0, a.disk_percent + b.disk_percent)
        net = min(100.0, a.network_percent + b.network_percent)
        therm = max(a.thermal_percent, b.thermal_percent)
        count = max(a.process_count, b.process_count)
        
        # Merge processes
        proc_dict = {}
        # Keep process with highest CPU
        for p in a.top_processes + b.top_processes:
            if p.pid not in proc_dict:
                proc_dict[p.pid] = p
            else:
                existing = proc_dict[p.pid]
                if p.cpu_percent > existing.cpu_percent:
                    proc_dict[p.pid] = p
                    
        merged_procs = list(proc_dict.values())
        
        merged.append(
            VirtualSnapshot(
                cpu_percent=cpu,
                memory_percent=mem,
                disk_percent=disk,
                process_count=count,
                top_processes=merged_procs,
                network_percent=net,
                thermal_percent=therm
            )
        )
        
    final_label = label or f"compound_{name_a}_{name_b}"
    return final_label, merged
