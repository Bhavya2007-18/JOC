# Global configuration for JOC

# 🔥 System thresholds
CPU_THRESHOLD = 80
MEMORY_THRESHOLD = 80
PROCESS_COUNT_THRESHOLD = 300

# 🔥 Snapshot settings
SNAPSHOT_INTERVAL_SECONDS = 5
MAX_HISTORY_LENGTH = 100

# 🔥 Safety flags
DRY_RUN = False  # Phase 2 will use this heavily

# 🔥 Scoring weights (future use)
CPU_WEIGHT = 0.4
MEMORY_WEIGHT = 0.4
PROCESS_WEIGHT = 0.2