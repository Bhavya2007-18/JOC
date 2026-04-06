from fastapi import APIRouter
from pydantic import BaseModel
from intelligence.fixer import FixEngine

router = APIRouter()
engine = FixEngine()

class ActionRevertRequest(BaseModel):
    action_id: str

@router.post("/action/revert")
def revert_action(request: ActionRevertRequest):
    return engine.revert_action(request.action_id)