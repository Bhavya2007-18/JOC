from fastapi import APIRouter
from pydantic import BaseModel
from intelligence.fixer import FixEngine

router = APIRouter()
engine = FixEngine()

class RevertRequest(BaseModel):
    action_id: str


@router.post("/action/revert")
def revert_action(request: RevertRequest):
    return engine.revert_action(request.action_id)


@router.get("/action/history")
def get_action_history():
    actions = engine.store.get_all_actions()
    result = []
    for action in actions:
        result.append({
            "id": action.action_id,
            "action": action.action_type.value,
            "target": action.target,
            "timestamp": action.timestamp,
            "status": action.status,
            "reversible": action.reversible,
            "result": action.result,
            "parameters": action.parameters,
        })
    # Return newest first
    result.reverse()
    return {"actions": result}