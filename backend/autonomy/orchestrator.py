import time
from typing import Dict, Any, Optional

from .decision_engine import DecisionEngine
from .action_engine import ActionEngine
from .feedback_engine import FeedbackEngine
from .learning_engine import LearningEngine
from .memory_engine import MemoryEngine
from .preemptive_engine import PreemptiveEngine
from .audit_log import AuditLogger
from services.optimizer.power_mode import get_current_mode

class AutonomyOrchestrator:
    def __init__(self):
        self.enabled = False
        self.decision_engine = DecisionEngine()
        self.action_engine = ActionEngine()
        self.feedback_engine = FeedbackEngine()
        self.learning_engine = LearningEngine()
        self.memory_engine = MemoryEngine()
        # Phase 3: Persistent Learning
        self.learning_engine.load()
        self.memory_engine.load()
        
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
        
        # STEP 1: Memory Lookup (Static Rule-Based)
        static_pattern = self.memory_engine.lookup(threat_data, causal_data, pred_data)
        
        # New: Cognitive Pattern (Phase 7/8 Learning Engine)
        cognitive_data = intelligence.get("learning", {})
        
        # Bridge: Use cognitive data as primary matched_pattern if confidence is high
        if cognitive_data.get("confidence", 0) > 0.6:
            matched_pattern = {
                "recommended_action": cognitive_data.get("recommended_response"),
                "confidence": cognitive_data.get("confidence", 0.5),
                "pattern_id": cognitive_data.get("pattern_id")
            }
        else:
            matched_pattern = static_pattern
        
        # STEP 2: Preemptive Check
        current_mode = get_current_mode()
        preemptive_signal = self.preemptive_engine.check(pred_data, threat_data, system_mode=current_mode)
        
        # Pull latest weights from LearningEngine
        context = intelligence.get("threat", {}).get("raw_inputs", {})
        current_weights = self.learning_engine.get_weights(context=context)
        self.decision_engine.update_weights(current_weights)

        # STEP 3: Decision
        # Pass all detected issues to the decision engine for prioritization
        issues = intelligence.get("issues", [])
        
        # Phase 4: Inject synthetic thermal issues when state is HOT/CRITICAL
        thermal = intelligence.get("thermal", {})
        if thermal.get("state") in ["HOT", "CRITICAL"]:
            thermal_issue = {
                "id": f"THERMAL_{thermal['state']}",
                "category": "thermal",
                "severity": "critical" if thermal["state"] == "CRITICAL" else "high",
                "title": f"System thermal state: {thermal['state']}",
                "evidence": {"temperature": thermal.get("temperature"), "score": thermal.get("score")},
            }
            issues.insert(0, thermal_issue)
            intelligence["issues"] = issues
            
        decision = self.decision_engine.decide(intelligence, matched_pattern, preemptive_signal)

        # STEP 4: Feedback (on prior action, using current state)
        feedback = self.feedback_engine.measure(
            current_threat=threat_data.get("threat_score", 0),
            current_cpu=threat_data.get("raw_inputs", {}).get("cpu", 0.0),
            current_ram=threat_data.get("raw_inputs", {}).get("ram", 0.0)
        )

        if feedback:
            # STEP 5: Learning
            self.learning_engine.record_outcome(feedback["action"], feedback, context=context)
            self.learning_engine.save()
            
            # STEP 6: Memory Update
            self.memory_engine.update_memory(feedback)
            self.memory_engine.save()

        # STEP 7: Action Execution (if enabled)
        action_result = None
        if self.enabled and decision and decision.get("action") and decision.get("action") != "no_action":
            from utils.execution_context import ExecutionContext
            
            # Create a dedicated context for this autonomous action
            context = ExecutionContext.from_request(
                dry_run=False, # Autonomy usually runs LIVE if enabled
                mode="autonomy"
            )
            
            action_result = self.action_engine.execute(decision, context=context)
            
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
        
        # Phase 6A: Decision Trace
        from intelligence.decision_trace import DecisionTrace, DecisionTraceLog
        override_reason = "static_only"
        
        static_pattern_safe = static_pattern or {}
        matched_pattern_safe = matched_pattern or {}
        
        if cognitive_data.get("confidence", 0) > 0.6:
            override_reason = "confidence > 0.6"
        elif matched_pattern_safe.get("pattern_id"):
            override_reason = "memory_match"
            
        trace = DecisionTrace(
            timestamp=time.time(),
            pattern_state=static_pattern_safe.get("pattern_id", "unknown"),
            engine_recommendation=static_pattern_safe.get("recommended_action", "none"),
            memory_recommendation=cognitive_data.get("recommended_response", "none"),
            final_decision=decision.get("action", "none") if decision else "none",
            override_reason=override_reason,
            confidence=matched_pattern_safe.get("confidence", 0.0),
            action_type=decision.get("action", "none") if decision else "none"
        )
        DecisionTraceLog.get_instance().record(trace)
        
        return self.latest_output

    def set_enabled(self, enabled: bool):
        self.enabled = enabled

    def get_health(self) -> Dict[str, Any]:
        """Returns the self-monitoring health state of the autonomy pipeline."""
        return {
            "uptime_status": "operational" if self.enabled else "offline",
            "engines": {
                "decision": {
                    "active": bool(self.decision_engine),
                    "oscillation_window_size": len(getattr(self.decision_engine, "_oscillation_window", []))
                },
                "learning": {
                    "active": bool(self.learning_engine),
                    "tracked_actions": len(self.learning_engine.get_performance_summary()),
                },
                "memory": {
                    "active": bool(self.memory_engine),
                    "pattern_count": len(getattr(self.memory_engine, "memory_bank", []))
                },
                "feedback": {
                    "active": bool(self.feedback_engine)
                }
            },
            "metrics": {
                "total_autonomous_decisions": sum(
                    stat.get("total_executions", 0) 
                    for stat in self.learning_engine.get_performance_summary().values()
                )
            }
        }
