from fastapi import APIRouter
from pydantic import BaseModel
from intelligence.fixer import FixEngine

router = APIRouter()
engine = FixEngine()

class FixRequest(BaseModel):
    action: str
    target: str | None = None
    pid: int | None = None

@router.post("/fix")
def apply_fix(request: FixRequest):
    if request.action == "kill_process":
        if request.pid:
            return engine.kill_process_by_pid(request.pid)
        elif request.target:
            return engine.kill_process_by_name(request.target)
        else:
            return {"error": "No target or pid provided"}

    return {"error": "Unsupported action"}