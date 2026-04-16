import sys
import os
import time
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from intelligence.monitor_loop import MonitorLoop
from training.red_team.scenario_vault import get_scenario
from training.red_team.scenario_params import ScenarioParams

def test_e2e():
    print("=== Testing End-to-End Autonomous Intelligence ===")
    
    # 1. Initialize System
    monitor = MonitorLoop()
    monitor.autonomy_orchestrator.enabled = True
    
    # 2. Grab a scenario
    params = ScenarioParams(intensity=0.9, duration_steps=6, concentration="single", ramp_style="sudden")
    snapshots = get_scenario("cpu_spike", params)
    
    # 3. Mock the collect_snapshot globally so feedback engine reads correctly
    import intelligence.snapshot_provider as sp
    
    for idx, snap in enumerate(snapshots):
        print(f"\n[Step {idx+1}/{len(snapshots)}] Simulating Snapshot (CPU: {snap.cpu_percent:.1f}%)")
        
        # Intercept globals
        def mock_collect():
            return snap
        sp.collect_snapshot = mock_collect
        
        monitor.latest_snapshot = snap
        
        # Force baseline window to pretend full
        intelligence = {
            "baseline": {"window_fill": 60}, 
            "threat": {
                "threat_score": snap.cpu_percent,
                "raw_inputs": {"cpu": snap.cpu_percent, "ram": snap.memory_percent}
            },
            "causal_graph": {"root_cause": snap.top_processes[0].name if snap.top_processes else "unknown"},
            "prediction": {},
            "learning": {},
            "thermal": {}
        }
        
        report = monitor.engine.analyze(snap)
        intelligence["issues"] = report.issues
        
        # Tick the orchestrator directly
        out = monitor.autonomy_orchestrator.tick(intelligence)
        
        decision = out.get("decision")
        if decision:
            print(f"   -> Engine Decided: {decision.get('action')} on {decision.get('target')} (confidence: {decision.get('confidence'):.2f})")
        else:
            print("   -> No decision taken.")
            
        action = out.get("action")
        if action:
            print(f"   -> Action Status: {action.get('status')}")
            
        feedback = out.get("feedback")
        if feedback:
             print(f"   -> Memory Recorded Feedback: {feedback.get('result')} | Impact: {feedback.get('impact_reduction')}%")

if __name__ == "__main__":
    test_e2e()
