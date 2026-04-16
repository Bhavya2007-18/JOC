from typing import Callable, Dict, List

from training.red_team.virtual_snapshot import VirtualSnapshot
from training.red_team.scenario_params import ScenarioParams
from training.red_team.scenarios.cpu_spike import generate_cpu_spike_scenario
from training.red_team.scenarios.memory_leak import generate_memory_leak_scenario
from training.red_team.scenarios.distributed_memory_leak import generate_distributed_memory_leak_scenario
from training.red_team.scenarios.disk_pressure import generate_disk_pressure_scenario
from training.red_team.scenarios.network_burst import generate_network_burst_scenario
from training.red_team.scenarios.thermal_spike import generate_thermal_spike_scenario
from training.red_team.scenarios.stealth_spike import generate_stealth_spike_scenario

VAULT: dict[str, callable] = {
    "cpu_spike": generate_cpu_spike_scenario,
    "memory_leak": generate_memory_leak_scenario,
    "distributed_memory_leak": generate_distributed_memory_leak_scenario,
    "disk_pressure": generate_disk_pressure_scenario,
    "network_burst": generate_network_burst_scenario,
    "thermal_spike": generate_thermal_spike_scenario,
    "stealth_spike": generate_stealth_spike_scenario,
}

COMPOUND_VAULT = [
    "compound_memleak_cpuspike",
    "compound_disk_cpuspike",
    "compound_thermal_cpuspike"
]

def get_scenario(name: str, params: ScenarioParams = None) -> List[VirtualSnapshot]:
    if name in VAULT:
        return VAULT[name](params)
        
    if name in COMPOUND_VAULT:
        from training.red_team.composition_engine import compose
        
        # Need base params to compose
        base_params = params or ScenarioParams(intensity=0.8, duration_steps=10, concentration="single", ramp_style="gradual")
        
        if name == "compound_memleak_cpuspike":
            _, snapshots = compose("memory_leak", base_params, "cpu_spike", base_params, name)
            return snapshots
        elif name == "compound_disk_cpuspike":
            _, snapshots = compose("disk_pressure", base_params, "cpu_spike", base_params, name)
            return snapshots
        elif name == "compound_thermal_cpuspike":
            _, snapshots = compose("thermal_spike", base_params, "cpu_spike", base_params, name)
            return snapshots
            
    raise ValueError(f"Unknown scenario: {name}")

def list_scenarios() -> List[str]:
    return list(VAULT.keys()) + COMPOUND_VAULT


