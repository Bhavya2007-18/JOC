from fastapi import APIRouter
from intelligence.engine import IntelligenceEngine
from intelligence.snapshot_provider import collect_snapshot

router = APIRouter()

intelligence_engine = IntelligenceEngine()

@router.get("/analyze")
def analyze_system():
    snapshot = collect_snapshot()
    report = intelligence_engine.analyze(snapshot)

    return {
        "summary": report.snapshot_summary,
        "issues": [issue.__dict__ for issue in report.issues],
        "changes": report.changes_detected,
    }