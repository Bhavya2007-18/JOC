from dataclasses import dataclass, asdict
import datetime

@dataclass
class TrainingReport:
    episodes_run: int
    total_steps: int
    avg_impact_score: float
    best_scenario: str        # highest avg impact
    worst_scenario: str       # lowest avg impact / most failures
    memory_size_before: int
    memory_size_after: int
    patterns_added: int
    timestamp: str
    
    @classmethod
    def from_results(cls, results: list[dict], memory_before: int, memory_after: int) -> "TrainingReport":
        total_steps = 0
        total_impact = 0.0
        scenario_impacts = {}
        
        for ep in results:
            scenario = ep.get("scenario", "unknown")
            if scenario not in scenario_impacts:
                scenario_impacts[scenario] = {"total": 0.0, "count": 0}
                
            for step in ep.get("steps", []):
                total_steps += 1
                impact = step.get("impact", 0.0)
                total_impact += impact
                scenario_impacts[scenario]["total"] += impact
                scenario_impacts[scenario]["count"] += 1
                
        avg_impact = total_impact / total_steps if total_steps > 0 else 0.0
        
        best_scenario = "none"
        worst_scenario = "none"
        
        if scenario_impacts:
            averages = {k: v["total"]/v["count"] if v["count"] > 0 else 0.0 for k,v in scenario_impacts.items()}
            best_scenario = max(averages, key=averages.get)
            worst_scenario = min(averages, key=averages.get)

        return cls(
            episodes_run=len(results),
            total_steps=total_steps,
            avg_impact_score=avg_impact,
            best_scenario=best_scenario,
            worst_scenario=worst_scenario,
            memory_size_before=memory_before,
            memory_size_after=memory_after,
            patterns_added=memory_after - memory_before,
            timestamp=datetime.datetime.now().isoformat()
        )
    
    def to_dict(self) -> dict:
        return asdict(self)
