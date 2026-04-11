from typing import Dict, Any

class TrustEngine:
    """
    Explainable AI (XAI) layer filtering programmatic reasoning into natural language narratives.
    """
    
    @staticmethod
    def generate_explanation(causal_root: str, predicted_breach: str, policy: str) -> str:
        """
        Creates a natural language explanation of system state.
        """
        if not causal_root:
            return f"System is operating normally under the '{policy}' policy. No critical vectors detected."
            
        return (f"Based on causal analysis, '{causal_root}' has been identified as the root stressor. "
                f"Forecasting predicts a {predicted_breach} breach under the current '{policy}' constraints. "
                "Intervention is recommended to stabilize the engine.")

    @staticmethod
    def explain_action(action: Dict[str, Any]) -> str:
        reason = action.get("reason", "Unknown telemetry.")
        target = action.get("target", "Target")
        atype = action.get("action_type", "modification")
        
        return f"Executing {atype} protocol on '{target}'. Justification: {reason}"
