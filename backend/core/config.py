import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass
class ValidationConfig:
    cpu_ceiling_percent: float = 90.0
    memory_ceiling_percent: float = 90.0
    simulation_timeout_seconds: int = 60
    observation_window_seconds: int = 10
    max_concurrent_simulations: int = 1
    scoring_detection_weight: int = 40
    scoring_decision_weight: int = 40
    scoring_time_weight: int = 20
    response_time_target_seconds: float = 8.0
    log_file_path: str = "logs/simulation_logs.json"


def _load_json_config_file() -> Dict[str, Any]:
    config_path = os.getenv("JOC_VALIDATION_CONFIG_PATH", "")
    if not config_path:
        return {}

    path = Path(config_path)
    if not path.exists():
        return {}

    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
            return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def get_validation_config() -> ValidationConfig:
    file_data = _load_json_config_file()

    return ValidationConfig(
        cpu_ceiling_percent=float(
            os.getenv("JOC_CPU_CEILING", file_data.get("cpu_ceiling_percent", 90.0))
        ),
        memory_ceiling_percent=float(
            os.getenv("JOC_MEMORY_CEILING", file_data.get("memory_ceiling_percent", 90.0))
        ),
        simulation_timeout_seconds=int(
            os.getenv("JOC_SIM_TIMEOUT", file_data.get("simulation_timeout_seconds", 60))
        ),
        observation_window_seconds=int(
            os.getenv("JOC_OBSERVATION_WINDOW", file_data.get("observation_window_seconds", 10))
        ),
        max_concurrent_simulations=int(
            os.getenv("JOC_MAX_CONCURRENT_SIMS", file_data.get("max_concurrent_simulations", 1))
        ),
        scoring_detection_weight=int(
            os.getenv("JOC_SCORE_WEIGHT_DETECTION", file_data.get("scoring_detection_weight", 40))
        ),
        scoring_decision_weight=int(
            os.getenv("JOC_SCORE_WEIGHT_DECISION", file_data.get("scoring_decision_weight", 40))
        ),
        scoring_time_weight=int(
            os.getenv("JOC_SCORE_WEIGHT_TIME", file_data.get("scoring_time_weight", 20))
        ),
        response_time_target_seconds=float(
            os.getenv("JOC_RESPONSE_TARGET", file_data.get("response_time_target_seconds", 8.0))
        ),
        log_file_path=str(
            os.getenv("JOC_SIM_LOG_PATH", file_data.get("log_file_path", "logs/simulation_logs.json"))
        ),
    )

