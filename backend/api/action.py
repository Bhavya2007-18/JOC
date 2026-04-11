from fastapi import APIRouter
from pydantic import BaseModel
from intelligence.fixer import FixEngine
from services.rollback import rollback_manager

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

class RollbackExecRequest(BaseModel):
    rollback_id: str

@router.post("/action/rollback_intercept")
def rollback_intercept(request: RollbackExecRequest):
    """Executes a rollback payload previously saved by RollbackManager"""
    success = rollback_manager.execute_rollback(request.rollback_id)
    if success:
        return {"status": "success", "message": f"Successfully reversed action {request.rollback_id}"}
    return {"status": "error", "message": "Failed to reverse action or invalid ID"}