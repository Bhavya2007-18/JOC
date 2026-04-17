from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from intelligence.fixer import FixEngine
from intelligence.action_store import ActionStore
from services.rollback import rollback_manager

router = APIRouter()
fix_engine = FixEngine()
action_store = ActionStore()

@router.get("/action/recent")
def get_recent_actions(limit: int = 10):
    """
    Returns the most recent optimization actions and their revert status.
    """
    actions = action_store.get_all_actions()
    # Sort by timestamp desc
    sorted_actions = sorted(actions, key=lambda x: x.timestamp, reverse=True)
    
    return [
        {
            "action_id": a.action_id,
            "type": a.action_type.value,
            "target": a.target,
            "timestamp": a.timestamp,
            "status": a.status,
            "reversible": a.reversible or (a.parameters.get("checkpoint_id") is not None),
            "checkpoint_id": a.parameters.get("checkpoint_id"),
        }
        for a in sorted_actions[:limit]
    ]

@router.post("/action/revert/{action_id}")
def revert_action(action_id: str):
    """
    Attempts to revert a specific action using its associated checkpoint.
    """
    action = action_store.get_action_by_id(action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")

    # Try standard tweak revert first
    if action.reversible:
        res = fix_engine.revert_action(action_id)
        if "error" not in res:
            return res

    # Otherwise try checkpoint-based rollback
    checkpoint_id = action.parameters.get("checkpoint_id")
    if checkpoint_id:
        success = rollback_manager.execute_rollback(checkpoint_id)
        if success:
            return {"status": "success", "message": f"Successfully reverted to checkpoint {checkpoint_id}"}
        else:
             raise HTTPException(status_code=500, detail="Failed to restore system state from checkpoint.")

    raise HTTPException(status_code=400, detail="This action is not reversible.")
