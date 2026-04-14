from pathlib import Path
import sys

# Ensure backend root is importable when running this file directly.
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from intelligence.engine import IntelligenceEngine
from training.red_team.virtual_snapshot import create_mock_snapshot


def test() -> None:
    engine = IntelligenceEngine()
    snapshot = create_mock_snapshot()

    result = engine.analyze(snapshot)

    print("CPU:", snapshot.cpu_percent)
    print("Memory:", snapshot.memory_percent)
    print("Issues:", result.issues)

    if not result.issues:
        raise AssertionError("Expected at least one issue to be detected")


if __name__ == "__main__":
    test()
