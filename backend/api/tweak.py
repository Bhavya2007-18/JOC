from fastapi import APIRouter
from pydantic import BaseModel
from intelligence.fixer import FixEngine

router = APIRouter()
engine = FixEngine()

class TweakExecuteRequest(BaseModel):
    tweak_name: str
    dry_run: bool = False

@router.post("/tweak/execute")
def execute_tweak(request: TweakExecuteRequest):
    return engine.execute_tweak(request.tweak_name, dry_run=request.dry_run)