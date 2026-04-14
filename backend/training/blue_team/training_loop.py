from training.red_team.scenarios.cpu_spike import generate_cpu_spike_scenario
from training.red_team.scenarios.memory_leak import generate_memory_leak_scenario
from intelligence.engine import IntelligenceEngine
from training.red_team.virtual_snapshot import VirtualSnapshot, VirtualProcessInfo
from training.learning.global_memory import memory
from training.taxonomy import ScenarioTraits


def apply_action(snapshot: VirtualSnapshot, action: dict) -> VirtualSnapshot:
    """
    Simulate effect of action on snapshot.
    """
    if not action:
        return snapshot

    action_type = action.get("action_type")

    if action_type == "kill_process":
        target_pid = action.get("parameters", {}).get("pid")

        new_processes = []
        cpu_reduction = 0.0
        memory_reduction = 0.0

        for p in snapshot.top_processes:
            if p.pid == target_pid:
                reduced_cpu = p.cpu_percent * 0.5
                memory_reduction = p.memory_percent * 0.5
                cpu_reduction += p.cpu_percent - reduced_cpu

                new_processes.append(
                    VirtualProcessInfo(
                        name=p.name,
                        pid=p.pid,
                        cpu_percent=reduced_cpu,
                        memory_percent=p.memory_percent,
                    )
                )
            else:
                new_processes.append(p)

        new_cpu = max(0.0, snapshot.cpu_percent - cpu_reduction)
        new_memory = max(0.0, snapshot.memory_percent - memory_reduction)

        return VirtualSnapshot(
            cpu_percent=new_cpu,
            memory_percent=new_memory,
            disk_percent=snapshot.disk_percent,
            process_count=snapshot.process_count,
            top_processes=new_processes,
        )

    return snapshot


def run_training_episode() -> list[dict]:
    scenarios = [
        ("cpu_spike", generate_cpu_spike_scenario()),
        ("memory_leak", generate_memory_leak_scenario()),
    ]
    engine = IntelligenceEngine()

    results = []

    for scenario_name, scenario in scenarios:
        for idx, snapshot in enumerate(scenario):
            result = engine.analyze(snapshot)

            best_action = None
            if result.issues:
                best_action = result.issues[0].best_action

            cpu_before = snapshot.cpu_percent

            new_snapshot = apply_action(snapshot, best_action or {})

            cpu_after = new_snapshot.cpu_percent

            improvement = cpu_before - cpu_after

            impact_score = improvement * 0.7

            if best_action:
                action_type = best_action.get("action_type")
                if action_type:
                    concentration = "distributed"
                    if snapshot.top_processes:
                        top_cpu = max(float(p.cpu_percent or 0.0) for p in snapshot.top_processes)
                        total_cpu = max(float(snapshot.cpu_percent or 0.0), 1.0)
                        if (top_cpu / total_cpu) >= 0.6:
                            concentration = "single"

                    if snapshot.cpu_percent >= 90:
                        severity_band = "critical"
                    elif snapshot.cpu_percent >= 75:
                        severity_band = "high"
                    else:
                        severity_band = "moderate"

                    traits = ScenarioTraits(
                        resource_type=(
                            "memory"
                            if float(snapshot.memory_percent or 0.0) > float(snapshot.cpu_percent or 0.0)
                            else "cpu"
                        ),
                        pattern="leak" if scenario_name == "memory_leak" else "spike",
                        process_concentration=concentration,
                        severity_band=severity_band,
                        has_root_cause_process=bool(
                            best_action.get("pid")
                            or best_action.get("parameters", {}).get("pid")
                        ),
                    )
                    memory.update(scenario_name, traits, action_type, impact_score)

            results.append(
                {
                    "step": idx,
                    "cpu_before": cpu_before,
                    "cpu_after": cpu_after,
                    "improvement": improvement,
                    "impact_score": impact_score,
                    "action": best_action,
                }
            )

    return results
