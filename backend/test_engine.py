from intelligence.snapshot_provider import collect_snapshot
from intelligence.engine import IntelligenceEngine
import time
import json

engine = IntelligenceEngine()

while True:
    snapshot = collect_snapshot()
    report = engine.analyze(snapshot)

    print("\n" + "="*50)
    print("SYSTEM REPORT")
    print("="*50)
    print(json.dumps({
        "summary": report.snapshot_summary,
        "issues": [issue.__dict__ for issue in report.issues],
        "changes": report.changes_detected
    }, indent=2))

    time.sleep(2)