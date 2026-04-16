import time
import json
import os
import datetime
from typing import Dict, Any, Optional, List

class MemoryEngine:
    def __init__(self):
        """
        Stores historical patterns to accelerate DecisionEngine via direct recall 
        of successful actions under similar conditions.
        """
        self.memory_bank: List[Dict[str, Any]] = []
        self.max_memory = 1000

    def _time_bucket(self) -> str:
        """Classify current hour into usage context."""
        hour = datetime.datetime.now().hour
        if 6 <= hour < 12: return "morning"
        if 12 <= hour < 18: return "afternoon"
        if 18 <= hour < 23: return "evening"
        return "night"

    def update_memory(self, feedback: Dict[str, Any]) -> None:
        """Stores the result of an action into memory."""
        result = feedback.get("result", "failure")

        entry = {
            "action": feedback.get("action"),
            "target": feedback.get("target"),
            "threat_before": feedback.get("threat_before", 0),
            "threat_after": feedback.get("threat_after", 0),
            "impact": feedback.get("impact_reduction", 0),
            "result": result,
            "time_bucket": self._time_bucket(),
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
        current_time_bucket = self._time_bucket()
        for mem in reversed(self.memory_bank):
            # Same target and similar threat tier (+/- 15 points)
            if abs(mem.get("threat_before", 0) - current_threat) <= 15:
                 if mem.get("target") == root_cause:
                     # Check for negative reinforcement
                     if mem.get("result") in ["failure", "over-correction"]:
                         # We tried this recently on this target and it failed, avoid returning it as a match
                         # (Ideally we'd track a "do not do" list, but for now we just skip the action match)
                         continue
                     
                     if mem.get("impact", 0) > highest_impact:
                         # Context bonus
                         bonus = 10 if mem.get("time_bucket") == current_time_bucket else 0
                         best_match = mem
                         highest_impact = mem.get("impact", 0) + bonus
                     
        if best_match:
            return {
                "matched_pattern": f"threat_tier_{int(current_threat // 10)}_{root_cause}",
                "recommended_action": best_match["action"],
                "confidence": min(0.5, best_match["impact"] / 100.0) # Extracted impact as a boost factor
            }
            
        return None

    def save(self, path: str = None) -> None:
        if path is None:
            path = os.path.join(os.path.dirname(__file__), "memory_bank.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.memory_bank, f, indent=2)

    def load(self, path: str = None) -> None:
        if path is None:
            path = os.path.join(os.path.dirname(__file__), "memory_bank.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                self.memory_bank = json.load(f)
