import time
from typing import Dict, Any, Optional

from .decision_engine import DecisionEngine
from .action_engine import ActionEngine
from .feedback_engine import FeedbackEngine
from .learning_engine import LearningEngine
from .memory_engine import MemoryEngine
from .preemptive_engine import PreemptiveEngine
from .audit_log import AuditLogger

class AutonomyOrchestrator:
    def __init__(self):
        self.enabled = False
        self.decision_engine = DecisionEngine()
        self.action_engine = ActionEngine()
        self.feedback_engine = FeedbackEngine()
        self.learning_engine = LearningEngine()
        self.memory_engine = MemoryEngine()
        self.preemptive_engine = PreemptiveEngine()
        
        self.latest_output: Dict[str, Any] = {}
        self.pending_action: Optional[Dict[str, Any]] = None

    def tick(self, intelligence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes one cycle of the autonomy loop.
        Called by the MonitorLoop after Stage 5 (XAI).
        """
        if not intelligence.get("baseline", {}).get("window_fill", 0):
            # Check for warming up state
            pass # Keep going if not provided

        # If we have no baseline stats, we're still warming up
        if not intelligence.get("baseline", {}):
            return {"enabled": self.enabled, "reason": "warming_up"}

        threat_data = intelligence.get("threat", {})
        causal_data = intelligence.get("causal_graph", {})
        pred_data = intelligence.get("prediction", {})
        
        # STEP 1: Memory Lookup
        matched_pattern = self.memory_engine.lookup(threat_data, causal_data, pred_data)
        
        # STEP 2: Preemptive Check
        preemptive_signal = self.preemptive_engine.check(pred_data, threat_data)
        
        # Pull latest weights from LearningEngine
        current_weights = self.learning_engine.get_weights()
        self.decision_engine.update_weights(current_weights)

        # STEP 3: Decision
        decision = self.decision_engine.decide(intelligence, matched_pattern, preemptive_signal)

        # STEP 4: Feedback (on prior action, using current state)
        feedback = self.feedback_engine.measure(
            current_threat=threat_data.get("threat_score", 0),
            current_cpu=threat_data.get("raw_inputs", {}).get("cpu", 0.0),
            current_ram=threat_data.get("raw_inputs", {}).get("ram", 0.0)
        )

        if feedback:
            # STEP 5: Learning
            self.learning_engine.record_outcome(feedback["action"], feedback)
            
            # STEP 6: Memory Update
            self.memory_engine.update_memory(feedback)

        # STEP 7: Action Execution (if enabled)
        action_result = None
        if self.enabled and decision and decision.get("action") and decision.get("action") != "no_action":
            action_result = self.action_engine.execute(decision)
            
            # Register action with feedback engine
            if action_result and action_result.get("status") in ["executed", "simulated"]:
                self.feedback_engine.register_action(
                    action_result,
                    pre_threat_score=threat_data.get("threat_score", 0),
                    pre_cpu=threat_data.get("raw_inputs", {}).get("cpu", 0.0),
                    pre_ram=threat_data.get("raw_inputs", {}).get("ram", 0.0)
                )

        # Compile Output
        self.latest_output = {
            "enabled": self.enabled,
            "decision": decision,
            "action": action_result,
            "feedback": feedback,
            "memory_match": matched_pattern,
            "timestamp": time.time()
        }
        
        # Phase 4: Deterministic Audit Logging
        AuditLogger.get_instance().record_tick(
            state=threat_data.get("raw_inputs", {}),
            decision=decision,
            feedback=feedback
        )
        
        return self.latest_output

    def set_enabled(self, enabled: bool):
        self.enabled = enabled
