import time
from typing import Dict, List, Optional

class AuditLogger:
    """
    Audit Logger for the Sentinel Engine.
    Provides a queryable, deterministic record of autonomous decisions and outcomes
    for replay and debugging purposes.
    """
    _instance = None
    
    def __init__(self):
        self.logs = []
        
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = AuditLogger()
        return cls._instance
        
    def record_tick(self, state: Dict, decision: Optional[Dict], feedback: Optional[Dict]):
        """Records a single tick in the autonomy loop."""
        log_entry = {
            "timestamp": time.time(),
            "state_snapshot": {
                "cpu": state.get("cpu_usage", 0),
                "ram": state.get("ram_usage", 0),
                "threat": state.get("threat_level", 0)
            },
            "decision": decision, 
            "feedback": feedback
        }
        self.logs.append(log_entry)
        
        # Prevent memory leak over long sim sessions
        if len(self.logs) > 1000:
            self.logs.pop(0)
            
    def get_history(self, limit: int = 100) -> List[Dict]:
        """Fetch the most recent logs."""
        return self.logs[-limit:]
        
    def clear(self):
        """Purge the audit log."""
        self.logs = []
