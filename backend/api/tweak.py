from fastapi import APIRouter
from pydantic import BaseModel
from intelligence.fixer import FixEngine
from intelligence.tweaks.decision_engine import TweakDecisionEngine

router = APIRouter()
engine = FixEngine()
decision_engine = TweakDecisionEngine()

class TweakExecuteRequest(BaseModel):
    tweak_name: str
    dry_run: bool = False
    confirm_high_risk: bool = False

@router.post("/tweak/execute")
def execute_tweak(request: TweakExecuteRequest):
    return engine.execute_tweak(
        request.tweak_name,
        dry_run=request.dry_run,
        confirm_high_risk=request.confirm_high_risk,
    )

@router.get("/tweak/suggest")
def suggest_tweak():
    """
    Analyzes system telemetry to suggest the most appropriate optimization protocol.
    """
    try:
        return decision_engine.suggest()
    except Exception as e:
        return {"error": str(e), "recommended": None, "reason": "Failed to analyze telemetry."}
