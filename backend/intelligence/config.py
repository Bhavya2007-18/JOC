import os

# Global configuration for JOC

# 🔥 System thresholds
CPU_THRESHOLD = 80
MEMORY_THRESHOLD = 80
PROCESS_COUNT_THRESHOLD = 300

# 🔥 Snapshot settings
SNAPSHOT_INTERVAL_SECONDS = 15
MAX_HISTORY_LENGTH = 100

# 🔥 Safety flags
DRY_RUN = os.getenv("JOC_DRY_RUN", "true").lower() == "true"
AUTOPILOT_MODE = "passive"  # passive | assist | aggressive
# 🔥 Scoring weights 
CPU_WEIGHT = 0.4
MEMORY_WEIGHT = 0.4
PROCESS_WEIGHT = 0.2