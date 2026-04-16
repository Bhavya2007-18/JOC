import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from intelligence.action_engine import ActionEngine
from intelligence.config import AUTOPILOT_MODE

engine = ActionEngine()

def run_test(name, decision):
    print(f"\n===== TEST: {name} =====")
    result = engine.execute(decision)
    print(result)


# ------------------------
# TEST CASES
# ------------------------

# 1. PASSIVE MODE TEST
run_test(
    "PASSIVE MODE",
    {
        "action": "kill_process",
        "target": "notepad.exe",  # change if not present
        "confidence": 0.9,
        "autopilot_mode": "passive",
    }
)

# 2. LOW CONFIDENCE TEST
run_test(
    "LOW CONFIDENCE",
    {
        "action": "kill_process",
        "target": "notepad.exe",
        "confidence": 0.3,
        "autopilot_mode": "aggressive",
    }
)

# 3. NO ACTION TEST
run_test(
    "NO ACTION",
    {
        "action": "no_action",
        "target": None,
        "confidence": 1.0,
        "autopilot_mode": "aggressive",
    }
)

# 4. INVALID ACTION TEST
run_test(
    "INVALID ACTION",
    {
        "action": "random_action",
        "target": "notepad.exe",
        "confidence": 1.0,
        "autopilot_mode": "aggressive",
    }
)

# 5. SAFE EXECUTION TEST (change to real running process)
run_test(
    "SAFE PROCESS",
    {
        "action": "kill_process",
        "target": "python.exe",
        "pid": os.getpid(),
        "confidence": 0.9,
        "autopilot_mode": "aggressive",
    }
)

# 6. CRITICAL PROCESS TEST
run_test(
    "CRITICAL PROCESS",
    {
        "action": "kill_process",
        "target": "explorer.exe",
        "confidence": 0.9,
        "autopilot_mode": "aggressive",
    }
)