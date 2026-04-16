import time
from typing import Dict, Any

from intelligence.decision_trace import DecisionTraceLog
from intelligence.monitor_loop import MonitorLoop

class ReportEngine:
    def __init__(self, monitor: MonitorLoop):
        self.monitor = monitor
        
    def generate_session_report(self) -> Dict[str, Any]:
        """
        Creates a comprehensive JSON summary of the current session's intelligence context.
        """
        latest_intel = self.monitor.get_latest_intelligence()
        
        # Pull XAI Narrative
        xai_data = latest_intel.get("xai", {})
        
        # Pull Decision Traces
        decision_traces = DecisionTraceLog.get_instance().get_recent(n=10)
        
        # Pull Memory Stats (Training)
        from training.learning.global_memory import memory
        memory_stats = {
            "total_patterns_learned": memory.size(),
            "recent_lessons": [
                {
                    "scenario": e.scenario_type,
                    "action": e.action,
                    "impact_score": e.score
                }
                for e in memory.get_all()[-5:]
            ]
        }
        
        # Pull Autonomy Status
        autonomy_enabled = False
        from main import monitor as app_monitor
        if hasattr(app_monitor, 'orchestrator'):
            autonomy_enabled = app_monitor.orchestrator.enabled
            
        return {
            "timestamp": time.time(),
            "timestamp_iso": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            "threat_state": latest_intel.get("threat", {}).get("level", "SAFE"),
            "autonomy_mode": "ACTIVE" if autonomy_enabled else "PASSIVE",
            "narrative": {
                "summary": xai_data.get("summary", "No data"),
                "cause": xai_data.get("cause", "No data"),
                "impact": xai_data.get("impact", "No data"),
                "prediction": xai_data.get("prediction", "No data"),
                "recommended_action": xai_data.get("recommended_action", "No data"),
                "autonomy_context": xai_data.get("autonomy_context", "No data")
            },
            "recent_decisions": decision_traces,
            "intelligence_memory": memory_stats,
            "system_metrics_snapshot": latest_intel.get("threat", {}).get("raw_inputs", {})
        }
