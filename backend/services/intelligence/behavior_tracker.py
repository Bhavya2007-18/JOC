import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from utils.logger import get_logger


logger = get_logger("intelligence.behavior_tracker")


def _get_storage_path() -> Path:
    base_dir = Path(__file__).resolve().parents[2]
    storage_dir = base_dir / "storage"
    storage_dir.mkdir(parents=True, exist_ok=True)
    return storage_dir / "behavior_logs.json"


def _load_raw_logs() -> List[Dict[str, Any]]:
    path = _get_storage_path()
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (json.JSONDecodeError, OSError):
        logger.warning("Failed to load behavior logs, starting fresh")
        return []
    if not isinstance(data, list):
        return []
    return [entry for entry in data if isinstance(entry, dict)]


def _save_raw_logs(entries: List[Dict[str, Any]]) -> None:
    path = _get_storage_path()
    try:
        with path.open("w", encoding="utf-8") as handle:
            json.dump(entries, handle, indent=2)
    except OSError:
        logger.error("Failed to persist behavior logs")


def append_log_entry(
    cpu_percent: float,
    memory_percent: float,
    top_processes: List[Dict[str, Any]],
    timestamp: Optional[float] = None,
    max_entries: int = 1000,
) -> Dict[str, Any]:
    if timestamp is None:
        timestamp = time.time()
    hour_of_day = time.localtime(timestamp).tm_hour

    sanitized_processes: List[Dict[str, Any]] = []
    for process in top_processes:
        try:
            sanitized_processes.append(
                {
                    "pid": int(process.get("pid", 0)),
                    "name": str(process.get("name", "unknown")),
                    "cpu_percent": float(process.get("cpu_percent", 0.0)),
                    "memory_percent": float(process.get("memory_percent", 0.0)),
                }
            )
        except (TypeError, ValueError):
            continue

    entry: Dict[str, Any] = {
        "timestamp": float(timestamp),
        "hour_of_day": int(hour_of_day),
        "cpu_percent": float(cpu_percent),
        "memory_percent": float(memory_percent),
        "top_processes": sanitized_processes,
    }

    entries = _load_raw_logs()
    entries.append(entry)
    if len(entries) > max_entries:
        entries = entries[-max_entries:]
    _save_raw_logs(entries)

    logger.info(
        "Appended behavior log cpu=%s memory=%s processes=%s",
        cpu_percent,
        memory_percent,
        len(sanitized_processes),
    )

    return entry


def load_logs(window_seconds: Optional[int] = None) -> List[Dict[str, Any]]:
    entries = _load_raw_logs()
    if window_seconds is None:
        return entries

    now = time.time()
    cutoff = now - float(window_seconds)
    filtered = [entry for entry in entries if float(entry.get("timestamp", 0.0)) >= cutoff]
    return filtered

