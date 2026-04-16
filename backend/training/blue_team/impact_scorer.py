from training.red_team.virtual_snapshot import VirtualSnapshot

def score_impact(
    before: VirtualSnapshot,
    after: VirtualSnapshot,
    resource_type: str     # "cpu" | "memory" | "disk" | "network" | "multi"
) -> float:
    # Measure improvement (higher is better)
    cpu_imp = max(0.0, before.cpu_percent - after.cpu_percent)
    mem_imp = max(0.0, before.memory_percent - after.memory_percent)
    disk_imp = max(0.0, before.disk_percent - after.disk_percent)
    net_imp = max(0.0, getattr(before, "network_percent", 0.0) - getattr(after, "network_percent", 0.0))

    if resource_type == "cpu":
        return cpu_imp / 100.0  # Normalized roughly to 0-1
    elif resource_type == "memory":
        # Memory leaks are scored higher on memory improvement
        return mem_imp / 100.0
    elif resource_type == "disk":
        return disk_imp / 100.0
    elif resource_type == "network":
        return net_imp / 100.0
    else:
        # "multi" or unknown, use weighted combo
        return (cpu_imp * 0.4 + mem_imp * 0.4 + disk_imp * 0.1 + net_imp * 0.1) / 100.0
