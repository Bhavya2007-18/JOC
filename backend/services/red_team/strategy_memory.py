"""Persistent storage for Red Team ε-greedy Q-table and attack history."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from utils.logger import get_logger

logger = get_logger("red_team.strategy_memory")

_STORAGE_PATH = Path(__file__).resolve().parents[2] / "storage" / "red_team_memory.json"
_MAX_HISTORY = 200


def _default_state() -> Dict[str, Any]:
    return {
        "q_table": {},
        "episode_count": 0,
        "epsilon": 0.5,
        "history": [],
    }


class StrategyMemory:
    """Manages the Red Team's learned attack strategy data."""

    def __init__(self, path: Optional[Path] = None) -> None:
        self._path = path or _STORAGE_PATH
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._state = self._load()

    # ── public API ────────────────────────────────────────────

    @property
    def q_table(self) -> Dict[str, float]:
        return self._state["q_table"]

    @property
    def epsilon(self) -> float:
        return float(self._state.get("epsilon", 0.5))

    @epsilon.setter
    def epsilon(self, value: float) -> None:
        self._state["epsilon"] = max(0.05, min(1.0, value))
        self._save()

    @property
    def episode_count(self) -> int:
        return int(self._state.get("episode_count", 0))

    @property
    def history(self) -> List[Dict[str, Any]]:
        return self._state.get("history", [])

    def get_q_value(self, key: str) -> float:
        """Get Q-value for an (attack|intensity) key. Default 0.5 (neutral)."""
        return float(self.q_table.get(key, 0.5))

    def update_q_value(self, key: str, reward: float, alpha: float = 0.2) -> None:
        """Update Q-value using exponential moving average: Q = Q + α(reward - Q)."""
        old = self.get_q_value(key)
        new_q = old + alpha * (reward - old)
        self._state["q_table"][key] = round(new_q, 4)
        self._save()

    def record_episode(self, episode: Dict[str, Any]) -> None:
        """Record a completed attack episode and increment counter."""
        episode["timestamp"] = time.time()
        self._state["history"].append(episode)
        if len(self._state["history"]) > _MAX_HISTORY:
            self._state["history"] = self._state["history"][-_MAX_HISTORY:]
        self._state["episode_count"] = self.episode_count + 1
        self._save()

    def decay_epsilon(self, decay_rate: float = 0.98, floor: float = 0.1) -> None:
        """Decay exploration rate after each episode."""
        self.epsilon = max(floor, self.epsilon * decay_rate)

    def get_top_strategies(self, n: int = 5) -> List[Dict[str, Any]]:
        """Return the top N strategies by Q-value."""
        sorted_q = sorted(self.q_table.items(), key=lambda x: x[1], reverse=True)
        return [{"key": k, "q_value": v} for k, v in sorted_q[:n]]

    def get_recent_win_rates(self, window: int = 10) -> List[float]:
        """Return win rates (undetected %) in sliding windows."""
        hist = self.history
        if not hist:
            return []
        rates = []
        for i in range(0, len(hist), window):
            batch = hist[i : i + window]
            if not batch:
                break
            undetected = sum(1 for ep in batch if not ep.get("detected", True))
            rates.append(round(undetected / len(batch), 2))
        return rates

    def reset(self) -> None:
        """Wipe all learned data and start fresh."""
        self._state = _default_state()
        self._save()
        logger.info("Strategy memory reset")

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
            logger.warning("Corrupted strategy memory, starting fresh")
            return _default_state()

    def _save(self) -> None:
        try:
            with self._path.open("w", encoding="utf-8") as f:
                json.dump(self._state, f, indent=2)
        except OSError:
            logger.error("Failed to save strategy memory")
