from fastapi import APIRouter
from pydantic import BaseModel
from intelligence.monitor_loop import MonitorLoop
from autonomy.audit_log import AuditLogger

router = APIRouter(prefix="/api/autonomy", tags=["autonomy"])

@router.get("/decision")
def get_decision():
    monitor = MonitorLoop.get_instance()
    if monitor and hasattr(monitor, 'latest_autonomy_state'):
        state = monitor.latest_autonomy_state
        return {
            "enabled": state.get("enabled", False),
            "decision": state.get("decision", {}),
            "timestamp": state.get("timestamp")
        }
    return {"status": "unavailable"}

@router.get("/history")
def get_history():
    monitor = MonitorLoop.get_instance()
    if monitor and hasattr(monitor, 'autonomy_orchestrator'):
        # Fetch directly from the memory bank as proxy history
        history = monitor.autonomy_orchestrator.memory_engine.memory_bank
        return {"history": history}
    return {"history": []}

@router.get("/audit/history")
def get_audit_history():
    """Phase 4: Deterministic Audit Query for Replay"""
    logger = AuditLogger.get_instance()
    return {"audit": logger.get_history(limit=500)}

@router.post("/enable")
def enable_autonomy():
    monitor = MonitorLoop.get_instance()
    if monitor and hasattr(monitor, 'autonomy_orchestrator'):
        monitor.autonomy_orchestrator.set_enabled(True)
        return {"status": "success", "enabled": True}
    return {"status": "error", "message": "Autonomy orchestrator not found"}

@router.post("/disable")
def disable_autonomy():
    monitor = MonitorLoop.get_instance()
    if monitor and hasattr(monitor, 'autonomy_orchestrator'):
        monitor.autonomy_orchestrator.set_enabled(False)
        return {"status": "success", "enabled": False}
    return {"status": "error", "message": "Autonomy orchestrator not found"}
