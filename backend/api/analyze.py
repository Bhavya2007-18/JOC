import dataclasses
from enum import Enum

from fastapi import APIRouter
from intelligence.engine import IntelligenceEngine
from intelligence.snapshot_provider import collect_snapshot
from storage.db import save_snapshot
from utils.system import is_admin

router = APIRouter()

intelligence_engine = IntelligenceEngine()


def _serialize(obj):
    if isinstance(obj, Enum):
        return obj.value
    if dataclasses.is_dataclass(obj):
        return {k: _serialize(v) for k, v in dataclasses.asdict(obj).items()}
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_serialize(v) for v in obj]
    return obj

@router.get("/analyze")
def analyze_system():
    snapshot = collect_snapshot()
    save_snapshot(snapshot)
    report = intelligence_engine.analyze(snapshot)

    return {
        "summary": report.snapshot_summary,
        "issues": [_serialize(issue) for issue in report.issues],
        "changes": _serialize(report.changes_detected),
        "system_health_score": report.system_health_score,
        "is_admin": is_admin()
    }