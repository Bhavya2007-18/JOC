from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, Optional
from autonomy.orchestrator import AutonomyOrchestrator
from intelligence.monitor_loop import MonitorLoop
from utils.logger import get_logger

logger = get_logger("api.autonomy")
router = APIRouter(prefix="/autonomy", tags=["autonomy"])

@router.post("/toggle")
def toggle_autonomy(enabled: bool = Body(..., embed=True)):
    orchestrator = AutonomyOrchestrator() # In reality, we want the global instance
    # MonitorLoop has the orchestrator instance
    monitor = MonitorLoop.get_instance()
    if not monitor:
        raise HTTPException(status_code=500, detail="MonitorLoop not initialized")
    
    monitor.autonomy_orchestrator.set_enabled(enabled)
    return {"success": True, "enabled": enabled}

@router.post("/force_action")
def force_action(action_data: Dict[str, Any]):
    """
    Force a specific action to be executed by the autonomy engine immediately.
    Example: {"action": "kill_process", "target": "notepad.exe", "pid": 1234}
    """
    monitor = MonitorLoop.get_instance()
    if not monitor:
        raise HTTPException(status_code=500, detail="MonitorLoop not initialized")
        
    result = monitor.autonomy_orchestrator.action_engine.execute(action_data)
    return {"success": True, "result": result}

@router.post("/inject_intelligence")
def inject_intelligence(payload: Dict[str, Any]):
    """
    Inject fake intelligence into the monitor loop for the next tick.
    Useful for triggering specific autonomy behaviors in demos.
    """
    monitor = MonitorLoop.get_instance()
    if not monitor:
        raise HTTPException(status_code=500, detail="MonitorLoop not initialized")
        
    # We override the latest_intelligence which will be picked up by the next autonomy tick
    # if it's currently sleeping.
    monitor.latest_intelligence.update(payload)
    return {"success": True, "message": "Intelligence injected for next tick"}

@router.post("/reset_learning")
def reset_learning():
    """
    Resets the learning engine's weights and outcomes.
    """
    monitor = MonitorLoop.get_instance()
    if not monitor:
        raise HTTPException(status_code=500, detail="MonitorLoop not initialized")
        
    monitor.autonomy_orchestrator.learning_engine.outcomes = {}
    monitor.autonomy_orchestrator.learning_engine.weights = {
        action: 1.0 for action in monitor.autonomy_orchestrator.decision_engine.ACTION_CATALOG
    }
    return {"success": True, "message": "Learning weights reset"}
