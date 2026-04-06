from fastapi import APIRouter
from pydantic import BaseModel
from intelligence.fixer import FixEngine

router = APIRouter()
engine = FixEngine()

class FixRequest(BaseModel):
    action: str
    target: str

@router.post("/fix")
def apply_fix(request: FixRequest):
    if request.action == "kill_process":
        return engine.kill_process_by_name(request.target)

    return {"error": "Unsupported action"}