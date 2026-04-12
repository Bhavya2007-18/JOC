from fastapi import APIRouter
from pydantic import BaseModel
from intelligence.config import DRY_RUN
from intelligence.fixer import FixEngine
from services.optimizer.process_manager import kill_process_safe

router = APIRouter()
engine = FixEngine()

class FixRequest(BaseModel):
    action: str
    target: str | None = None
    pid: int | None = None

@router.post("/fix")
def apply_fix(request: FixRequest):
    if request.action == "kill_process":
        if DRY_RUN:
            return {
                "success": True,
                "message": "Simulated action (DRY RUN)",
                "dry_run": True,
            }
        if request.pid:
            return kill_process_safe(request.pid, dry_run=DRY_RUN)
        return {
            "error": "PID required for safe process termination"
        }
    elif request.action == "system_tweak":
        if DRY_RUN:
            return {
                "success": True,
                "message": "Simulated action (DRY RUN)",
                "dry_run": True,
            }
        return engine.execute_tweak(request.target)

    return {"error": "Unsupported action"}