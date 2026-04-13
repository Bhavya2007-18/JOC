from pathlib import Path
import sys

# Ensure backend root is importable when running this file directly.
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from intelligence.engine import IntelligenceEngine
from training.red_team.scenarios.cpu_spike import generate_cpu_spike_scenario


def test() -> None:
    engine = IntelligenceEngine()
    scenario = generate_cpu_spike_scenario()

    for idx, snapshot in enumerate(scenario):
        result = engine.analyze(snapshot)

        best_action = {}
        if result.issues:
            first_issue = result.issues[0]
            best_action = first_issue.best_action or {}

        print(
            f"step={idx} cpu={snapshot.cpu_percent:.1f}% "
            f"issues={len(result.issues)} best_action={best_action}"
        )


if __name__ == "__main__":
    test()
