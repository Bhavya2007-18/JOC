import time
from intelligence.learning.pattern_memory import PatternMemory

class CrossScenarioEngine:
    OUTCOME_WAIT_TICKS = 1   # wait 1 tick (~15s) after tweak before measuring outcome

    def __init__(self):
        self.memory = PatternMemory()
        self._pending_outcome: dict | None = None
        self._ticks_since_tweak: int = 0
        self._current_pattern_id: str | None = None

    def update(self, pattern: dict, current_threat_score: float) -> dict:
        """
        Called every tick. Two jobs:
        1. Check if a pending outcome is ready to record
        2. Return a recommendation for the active pattern
        """
        # Job 1: Check pending outcome
        if self._pending_outcome:
            self._ticks_since_tweak += 1
            if self._ticks_since_tweak >= self.OUTCOME_WAIT_TICKS:
                self._resolve_outcome(current_threat_score)

        # Job 2: Upsert current pattern + get recommendation
        if pattern["pattern_type"] != "stable" and pattern["confidence"] > 0.3:
            best_response = self.memory.get_best_response(pattern)
            pattern_id    = self.memory.upsert(pattern, response=best_response or "no_action")
            self._current_pattern_id = pattern_id
            return {
                "recommended_response": best_response,
                "pattern_id":           pattern_id,
                "confidence":           pattern["confidence"]
            }

        self._current_pattern_id = None
        return {}

    def record_tweak_executed(self, tweak_name: str, pattern_id: str, pre_threat: float) -> None:
        """Called by api/tweak.py immediately after a tweak runs."""
        self._pending_outcome = {
            "tweak_name":   tweak_name,
            "pattern_id":   pattern_id,
            "pre_threat":   pre_threat,
            "timestamp":    time.time()
        }
        self._ticks_since_tweak = 0

    def _resolve_outcome(self, post_threat: float) -> None:
        """Computes improvement, updates pattern memory, clears pending state."""
        if not self._pending_outcome: return

        pre = self._pending_outcome["pre_threat"]
        pid = self._pending_outcome["pattern_id"]

        if pre > 0:
            improvement = (pre - post_threat) / pre   # 0.0–1.0
            success     = improvement > 0.15           # 15% reduction = success
            impact      = improvement * 100
        else:
            success, impact = False, 0.0

        self.memory.update_score(pid, success=success, impact=impact)
        self._pending_outcome    = None
        self._ticks_since_tweak  = 0

    def get_learning_summary(self) -> dict:
        all_patterns = self.memory.get_all(limit=50)
        return {
            "total_patterns":    len(all_patterns),
            "top_patterns":      all_patterns[:10],
            "pending_outcome":   bool(self._pending_outcome),
            "current_pattern_id": self._current_pattern_id
        }
