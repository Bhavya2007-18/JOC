"""Persistent storage for Blue Team adaptive learning data."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from utils.logger import get_logger

logger = get_logger("blue_team.defense_memory")

from utils.paths import get_persistent_path
_STORAGE_PATH = get_persistent_path("blue_team_memory.json", "storage")


def _default_state() -> Dict[str, Any]:
    return {
        "baseline_cpu": 0.0,
        "baseline_memory": 0.0,
        "baseline_std_cpu": 10.0,
        "baseline_std_memory": 10.0,
        "samples_seen": 0,
        "known_patterns": {},
        "action_success_rates": {},
        "action_attempts": {},
        "total_detections": 0,
        "total_misses": 0,
        "detection_latencies": [],
        "avg_detection_latency": 0.0,
        "history": [],
    }


class DefenseMemory:
    """Manages Blue Team's learned defense data."""

    def __init__(self, path: Optional[Path] = None) -> None:
        self._path = path or _STORAGE_PATH
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._state = self._load()

    # ── baselines ─────────────────────────────────────────────

    @property
    def baseline_cpu(self) -> float:
        return float(self._state.get("baseline_cpu", 0.0))

    @baseline_cpu.setter
    def baseline_cpu(self, value: float) -> None:
        self._state["baseline_cpu"] = value

    @property
    def baseline_memory(self) -> float:
        return float(self._state.get("baseline_memory", 0.0))

    @baseline_memory.setter
    def baseline_memory(self, value: float) -> None:
        self._state["baseline_memory"] = value

    @property
    def baseline_std_cpu(self) -> float:
        return float(self._state.get("baseline_std_cpu", 10.0))

    @baseline_std_cpu.setter
    def baseline_std_cpu(self, value: float) -> None:
        self._state["baseline_std_cpu"] = value

    @property
    def baseline_std_memory(self) -> float:
        return float(self._state.get("baseline_std_memory", 10.0))

    @baseline_std_memory.setter
    def baseline_std_memory(self, value: float) -> None:
        self._state["baseline_std_memory"] = value

    @property
    def samples_seen(self) -> int:
        return int(self._state.get("samples_seen", 0))

    @samples_seen.setter
    def samples_seen(self, value: int) -> None:
        self._state["samples_seen"] = value

    # ── patterns ──────────────────────────────────────────────

    @property
    def known_patterns(self) -> Dict[str, Dict[str, Any]]:
        return self._state.get("known_patterns", {})

    def register_pattern(self, fingerprint: str, data: Dict[str, Any]) -> None:
        self._state.setdefault("known_patterns", {})[fingerprint] = data
        self._save()

    def get_pattern(self, fingerprint: str) -> Optional[Dict[str, Any]]:
        return self._state.get("known_patterns", {}).get(fingerprint)

    # ── action tracking ───────────────────────────────────────

    def record_action_outcome(self, action: str, effective: bool) -> None:
        rates = self._state.setdefault("action_success_rates", {})
        attempts = self._state.setdefault("action_attempts", {})

        old_rate = float(rates.get(action, 0.5))
        old_attempts = int(attempts.get(action, 0))
        new_attempts = old_attempts + 1

        # Incremental mean update
        new_rate = old_rate + (1.0 if effective else 0.0 - old_rate) / new_attempts
        rates[action] = round(new_rate, 4)
        attempts[action] = new_attempts
        self._save()

    def get_action_success_rate(self, action: str) -> float:
        return float(self._state.get("action_success_rates", {}).get(action, 0.5))

    def get_best_action(self) -> Optional[str]:
        rates = self._state.get("action_success_rates", {})
        if not rates:
            return None
        return max(rates, key=rates.get)

    # ── detection tracking ────────────────────────────────────

    def record_detection(self, detected: bool, latency: float) -> None:
        if detected:
            self._state["total_detections"] = self._state.get("total_detections", 0) + 1
            latencies = self._state.setdefault("detection_latencies", [])
            latencies.append(round(latency, 3))
            if len(latencies) > 100:
                self._state["detection_latencies"] = latencies[-100:]
            self._state["avg_detection_latency"] = round(
                sum(self._state["detection_latencies"]) / len(self._state["detection_latencies"]), 3
            )
        else:
            self._state["total_misses"] = self._state.get("total_misses", 0) + 1
        self._save()

    def record_episode(self, episode: Dict[str, Any]) -> None:
        episode["timestamp"] = time.time()
        self._state.setdefault("history", []).append(episode)
        if len(self._state["history"]) > 200:
            self._state["history"] = self._state["history"][-200:]
        self._save()

    # ── stats ─────────────────────────────────────────────────

    def get_stats(self) -> Dict[str, Any]:
        total_d = self._state.get("total_detections", 0)
        total_m = self._state.get("total_misses", 0)
        total = total_d + total_m

        latencies = self._state.get("detection_latencies", [])
        recent_latencies = latencies[-10:] if latencies else []

        return {
            "baseline_cpu": round(self.baseline_cpu, 1),
            "baseline_memory": round(self.baseline_memory, 1),
            "baseline_std_cpu": round(self.baseline_std_cpu, 2),
            "baseline_std_memory": round(self.baseline_std_memory, 2),
            "samples_seen": self.samples_seen,
            "total_detections": total_d,
            "total_misses": total_m,
            "detection_rate": round(total_d / total * 100, 1) if total > 0 else 0.0,
            "avg_detection_latency": self._state.get("avg_detection_latency", 0.0),
            "recent_latencies": recent_latencies,
            "patterns_known": len(self.known_patterns),
            "action_success_rates": self._state.get("action_success_rates", {}),
            "best_action": self.get_best_action(),
        }

    def save(self) -> None:
        self._save()

    def reset(self) -> None:
        self._state = _default_state()
        self._save()
        logger.info("Defense memory reset")

    # ── persistence ───────────────────────────────────────────

    def _load(self) -> Dict[str, Any]:
        if not self._path.exists():
            return _default_state()
        try:
            with self._path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                return _default_state()
            return data
        except (json.JSONDecodeError, OSError):
            logger.warning("Corrupted defense memory, starting fresh")
            return _default_state()

    def _save(self) -> None:
        try:
            with self._path.open("w", encoding="utf-8") as f:
                json.dump(self._state, f, indent=2)
        except OSError:
            logger.error("Failed to save defense memory")
