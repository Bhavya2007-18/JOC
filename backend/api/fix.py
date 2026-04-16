from fastapi import APIRouter
from pydantic import BaseModel
from intelligence.fixer import FixEngine
from services.optimizer.process_manager import kill_process_safe
from utils.execution_context import ExecutionContext

router = APIRouter()
engine = FixEngine()

class FixRequest(BaseModel):
    action: str
    target: str | None = None
    pid: int | None = None
    dry_run: bool = False

@router.post("/fix")
def apply_fix(request: FixRequest):
    context = ExecutionContext.from_request(dry_run=request.dry_run)
    
    if request.action == "kill_process":
        if request.pid:
            return kill_process_safe(request.pid, context=context)
        return {
            "error": "PID required for safe process termination"
        }
    elif request.action == "system_tweak":
        return engine.execute_tweak(request.target, context=context)

    return {"error": "Unsupported action"}