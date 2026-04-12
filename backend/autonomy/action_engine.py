import time
from typing import Dict, Any, List

from intelligence.config import DRY_RUN

PROTECTED_PROCESSES = {
    "system", "svchost.exe", "lsass.exe", "csrss.exe", 
    "wininit.exe", "explorer.exe"
}

class ActionEngine:
    def __init__(self):
        self._handlers = {
            "throttle_process":       self._throttle,
            "kill_process":           self._kill,
            "clear_cache":            self._clear_cache,
            "rate_limit":             self._rate_limit,
            "preemptive_throttle":    self._throttle,
            "no_action":              self._noop,
        }
        
        self._rollback_stack: List[Dict[str, Any]] = []
        self._last_action_time: float = 0.0
        self._cooldown_seconds: float = 30.0

    def execute(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Executes a decision with pre-flight checks and rollback tracking."""
        action_name = decision.get("action")
        target = decision.get("target")
        confidence = decision.get("confidence", 0.0)

        # 1. Unknown action
        if action_name not in self._handlers:
            return self._build_result("failed", action_name, target, reason="unknown_action")

        # 2. No action
        if action_name == "no_action":
            return self._build_result("skipped", action_name, target, reason="no_action")

        # 3. Confidence Check
        if confidence < 0.60:
            return self._build_result("skipped", action_name, target, reason="low_confidence")

        # 4. Protected Process Check
        if target and target.lower() in PROTECTED_PROCESSES:
            return self._build_result("skipped", action_name, target, reason="protected_process")

        # 5. Cooldown Check
        now = time.time()
        if now - self._last_action_time < self._cooldown_seconds:
            return self._build_result("skipped", action_name, target, reason="cooldown_active")

        # Ready to execute
        self._last_action_time = now
        handler = self._handlers[action_name]
        
        try:
            result = handler(target)
            return self._build_result(result["status"], action_name, target, params=result.get("params"))
        except Exception as e:
            return self._build_result("failed", action_name, target, reason=str(e))

    def rollback_last(self) -> bool:
        if not self._rollback_stack:
            return False
            
        token = self._rollback_stack.pop()
        # In a real system, you would reverse the action defined by the token here
        print(f"Rolling back action: {token['action']} on {token.get('target')}")
        return True

    def _build_result(
        self, 
        status: str, 
        action: str, 
        target: str = None, 
        reason: str = None, 
        params: dict = None
    ) -> Dict[str, Any]:
        res = {
            "status": status,
            "action": action,
            "target": target,
            "timestamp": time.time(),
            "rollback_available": status in ["executed", "simulated"]
        }
        if reason:
            res["reason"] = reason
        if params:
            res["params"] = params
            
        if status in ["executed", "simulated"]:
            self._rollback_stack.append(res)
            
        return res

    # --- Handlers ---
    
    def _throttle(self, target: str) -> Dict[str, Any]:
        if DRY_RUN:
            return {"status": "simulated", "params": {"cpu_limit": 20}}
        return {"status": "executed", "params": {"cpu_limit": 20}}

    def _kill(self, target: str) -> Dict[str, Any]:
        if DRY_RUN:
            return {"status": "simulated"}
        return {"status": "executed"}

    def _clear_cache(self, target: str) -> Dict[str, Any]:
        if DRY_RUN:
            return {"status": "simulated", "params": {"strategy": "aggressive"}}
        return {"status": "executed", "params": {"strategy": "aggressive"}}

    def _rate_limit(self, target: str) -> Dict[str, Any]:
        if DRY_RUN:
            return {"status": "simulated", "params": {"requests_per_sec": 100}}
        return {"status": "executed", "params": {"requests_per_sec": 100}}

    def _noop(self, target: str) -> Dict[str, Any]:
        return {"status": "skipped"}
