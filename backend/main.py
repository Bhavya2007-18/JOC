from fastapi import FastAPI
from pydantic import BaseModel

from intelligence.engine import IntelligenceEngine
from intelligence.fixer import FixEngine
from intelligence.snapshot_provider import collect_snapshot

app = FastAPI()

intelligence_engine = IntelligenceEngine()
engine = FixEngine()


@app.get("/analyze")
def analyze_system():
	snapshot = collect_snapshot()
	report = intelligence_engine.analyze(snapshot)

	return {
		"summary": report.snapshot_summary,
		"issues": [issue.__dict__ for issue in report.issues],
		"changes": report.changes_detected,
	}


class FixRequest(BaseModel):
	action: str
	target: str


class TweakExecuteRequest(BaseModel):
	tweak_name: str


class ActionRevertRequest(BaseModel):
	action_id: str


@app.post("/fix")
def apply_fix(request: FixRequest):
    if request.action == "kill_process":
        return engine.kill_process_by_name(request.target)

    return {"error": "Unsupported action"}


@app.post("/tweak/execute")
def execute_tweak(request: TweakExecuteRequest):
    return engine.execute_tweak(request.tweak_name)


@app.post("/action/revert")
def revert_action(request: ActionRevertRequest):
    return engine.revert_action(request.action_id)