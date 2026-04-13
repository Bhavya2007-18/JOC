import time
from typing import Dict, Any, Optional, List

class MemoryEngine:
    def __init__(self):
        """
        Stores historical patterns to accelerate DecisionEngine via direct recall 
        of successful actions under similar conditions.
        """
        self.memory_bank: List[Dict[str, Any]] = []
        self.max_memory = 1000

    def update_memory(self, feedback: Dict[str, Any]) -> None:
        """Stores the result of an action into memory if it was successful."""
        # Only memorize successful outcomes for active reinforcement
        if feedback.get("result") != "success":
             return 

        entry = {
            "action": feedback.get("action"),
            "target": feedback.get("target"),
            "threat_before": feedback.get("threat_before", 0),
            "threat_after": feedback.get("threat_after", 0),
            "impact": feedback.get("impact_reduction", 0),
            "timestamp": time.time()
        }
        
        self.memory_bank.append(entry)
        
        if len(self.memory_bank) > self.max_memory:
            self.memory_bank.pop(0)

    def lookup(
        self, 
        threat_data: Dict[str, Any], 
        causal_data: Dict[str, Any], 
        pred_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Finds a matched pattern for the current state.
        Returns a dict with 'recommended_action' if a strong match is found.
        """
        current_threat = threat_data.get("threat_score", 0)
        root_cause = causal_data.get("root_cause")
        
        if not root_cause:
            return None # Without a known root cause, memory matching is too broad
            
        best_match = None
        highest_impact = 0.0
        
        # Search backwards (most recent first)
        for mem in reversed(self.memory_bank):
            # Same target and similar threat tier (+/- 15 points)
            if abs(mem.get("threat_before", 0) - current_threat) <= 15:
                 if mem.get("target") == root_cause and mem.get("impact", 0) > highest_impact:
                     best_match = mem
                     highest_impact = mem.get("impact", 0)
                     
        if best_match:
            return {
                "matched_pattern": f"threat_tier_{int(current_threat // 10)}_{root_cause}",
                "recommended_action": best_match["action"],
                "confidence": min(0.5, best_match["impact"] / 100.0) # Extracted impact as a boost factor
            }
            
        return None
