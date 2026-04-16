from fastapi import APIRouter
from intelligence.decision_trace import DecisionTraceLog

router = APIRouter(prefix="/trace", tags=["trace"])

@router.get("/")
def get_traces(limit: int = 50):
    return DecisionTraceLog.get_instance().get_recent(limit)

@router.delete("/")
def clear_traces():
    DecisionTraceLog.get_instance().clear()
    return {"status": "cleared"}
