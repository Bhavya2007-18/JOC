from fastapi import APIRouter
from pydantic import BaseModel
from intelligence.fixer import FixEngine
from intelligence.tweaks.decision_engine import TweakDecisionEngine
from intelligence.monitor_loop import MonitorLoop
from utils.execution_context import ExecutionContext

router = APIRouter()
engine = FixEngine()
decision_engine = TweakDecisionEngine()

class TweakExecuteRequest(BaseModel):
    tweak_name: str
    dry_run: bool = False
    confirm_high_risk: bool = False

@router.post("/tweak/execute")
def execute_tweak(request: TweakExecuteRequest):
    context = ExecutionContext.from_request(dry_run=request.dry_run, confirmed_high_risk=request.confirm_high_risk)
    monitor = MonitorLoop.get_instance()
    pre_threat = 0.0
    pattern_id = None
    if monitor:
        latest = monitor.latest_intelligence
        pre_threat = latest.get("threat", {}).get("threat_score", 0.0)
        pattern_id = latest.get("learning", {}).get("pattern_id")

    res = engine.execute_tweak(
        request.tweak_name,
        context=context,
        confirm_high_risk=request.confirm_high_risk,
    )
    
    if monitor and pattern_id and not request.dry_run:
        monitor.cross_scenario_engine.record_tweak_executed(
            request.tweak_name, pattern_id, pre_threat
        )

    return res

@router.get("/tweak/suggest")
def suggest_tweak():
    """
    Analyzes system telemetry to suggest the most appropriate optimization protocol.
    """
    try:
        return decision_engine.suggest()
    except Exception as e:
        return {"error": str(e), "recommended": None, "reason": "Failed to analyze telemetry."}
