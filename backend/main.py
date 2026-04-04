from fastapi import FastAPI

from intelligence.engine import IntelligenceEngine
from intelligence.snapshot_provider import collect_snapshot

app = FastAPI()

engine = IntelligenceEngine()


@app.get("/analyze")
def analyze_system():
	snapshot = collect_snapshot()
	report = engine.analyze(snapshot)

	return {
		"summary": report.snapshot_summary,
		"issues": [issue.__dict__ for issue in report.issues],
		"changes": report.changes_detected,
	}
from pydantic import BaseModel
from backend.intelligence.fixer import FixEngine

fix_engine = FixEngine()


class FixRequest(BaseModel):
    action: str
    target: str


@app.post("/fix")
def apply_fix(request: FixRequest):
    if request.action == "kill_process":
        return fix_engine.kill_process_by_name(request.target)

    return {"error": "Unsupported action"}