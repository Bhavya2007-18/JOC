from pathlib import Path
import sys

# Ensure backend root is importable when running this file directly.
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from training.blue_team.training_loop import run_training_episode
from training.learning.global_memory import memory


def test() -> None:
    for i in range(5):
        print(f"\nEpisode {i + 1}")
        results = run_training_episode()

        for r in results:
            action_type = r["action"]["action_type"] if r["action"] else None

            print(
                f"step={r['step']} "
                f"before={r['cpu_before']:.1f} "
                f"after={r['cpu_after']:.1f} "
                f"improvement={r['improvement']:.1f} "
                f"impact={r['impact_score']:.1f} "
                f"action={action_type}"
            )

    memory.save()

    print("\nLearned memory across all episodes")
    memory.print_memory()


if __name__ == "__main__":
    test()
