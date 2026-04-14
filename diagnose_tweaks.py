import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from intelligence.tweaks.executor import execute_tweak
from intelligence.tweaks.registry import get_all_tweaks

print("Starting tweak diagnostic...")

for tweak in get_all_tweaks():
    print(f"Testing tweak: {tweak.name} (Dry Run)")
    try:
        # Pass dry_run=True explicitly
        result = execute_tweak(tweak.name, dry_run=True)
        if "error" in result:
            print(f"  [ERROR] {result['error']}")
        else:
            print(f"  [SUCCESS] {result['summary']}")
    except Exception as e:
        import traceback
        print(f"  [CRASH] {str(e)}")
        traceback.print_exc()

print("Diagnostic complete.")
