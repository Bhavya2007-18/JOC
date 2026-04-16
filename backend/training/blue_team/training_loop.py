from training.red_team.virtual_snapshot import VirtualSnapshot, VirtualProcessInfo
from training.red_team.red_agent import RedAgent
from training.blue_team.blue_agent import BlueAgent
from training.blue_team.impact_scorer import score_impact
from training.training_report import TrainingReport
from training.taxonomy import ScenarioTraits
from training.learning.global_memory import memory

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
            network_percent=getattr(snapshot, "network_percent", 0.0),
            thermal_percent=getattr(snapshot, "thermal_percent", 50.0)
        )
        
    elif action_type == "clear_cache":
        new_memory = max(0.0, snapshot.memory_percent - 10.0)
        return VirtualSnapshot(
            cpu_percent=snapshot.cpu_percent,
            memory_percent=new_memory,
            disk_percent=snapshot.disk_percent,
            process_count=snapshot.process_count,
            top_processes=list(snapshot.top_processes),
            network_percent=getattr(snapshot, "network_percent", 0.0),
            thermal_percent=getattr(snapshot, "thermal_percent", 50.0)
        )

    return snapshot


def extract_traits(snapshot: VirtualSnapshot, scenario_name: str, action: dict) -> ScenarioTraits:
    concentration = "distributed"
    if snapshot.top_processes:
        if "distributed" in scenario_name:
            concentration = "distributed"
        else:
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
        
    res_type = "cpu"
    if "memory" in scenario_name:
        res_type = "memory"
    elif "disk" in scenario_name:
        res_type = "disk"
    elif "network" in scenario_name:
        res_type = "network"
    elif "thermal" in scenario_name:
        res_type = "thermal"

    pattern = "spike"
    if "leak" in scenario_name:
        pattern = "leak"
    if "burst" in scenario_name:
        pattern = "burst"

    has_root = bool(action and (action.get("pid") or action.get("parameters", {}).get("pid")))
    
    return ScenarioTraits(
        resource_type=res_type,
        pattern=pattern,
        process_concentration=concentration,
        severity_band=severity_band,
        has_root_cause_process=has_root
    )

def run_training_battle(n_episodes: int = 100, strategy: str = "random") -> TrainingReport:
    red = RedAgent(strategy=strategy)
    blue = BlueAgent()
    
    all_results = []
    
    memory_before = memory.size()
    
    for ep in range(n_episodes):
        try:
            scenario_name, steps = red.pick_episode()
        except ValueError:
            break
            
        ep_results = []
        
        current_snapshot = steps[0]
        
        for step_idx, _ in enumerate(steps):
            analysis = blue.observe(current_snapshot)
            action = blue.decide(analysis)
            new_snapshot = blue.act(current_snapshot, action)
            
            traits = extract_traits(current_snapshot, scenario_name, action)
            impact = score_impact(current_snapshot, new_snapshot, traits.resource_type)
            
            if impact > 0.1:
                ac_type = action.get("action_type")
                if ac_type:
                    blue.learn(scenario_name, traits, ac_type, impact)
            else:
                red.record_failure(scenario_name)
            
            ep_results.append({"step": step_idx, "impact": impact, "action": action})
            current_snapshot = new_snapshot
        
        all_results.append({"episode": ep, "scenario": scenario_name, "steps": ep_results})
    
    memory_after = memory.size()
    return TrainingReport.from_results(all_results, memory_before, memory_after)

