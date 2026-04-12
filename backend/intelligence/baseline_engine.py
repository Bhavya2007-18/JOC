"""
Adaptive Baseline Engine — Phase 2, JOC Sentinel
-------------------------------------------------
Continuously tracks rolling statistics (mean, std-dev, z-score) for CPU
and RAM metrics to establish what "normal" system behaviour looks like.

No external ML libraries — pure Python math via the standard library.

Usage (one call per monitor cycle):
    baseline = BaselineEngine(window_size=60)
    report   = baseline.analyze(cpu=45.2, ram=62.8)
    # → {"cpu_baseline": 42.1, "cpu_z_score": 0.74, ...}
"""

import math
from collections import deque
from typing import Dict, Optional


class BaselineEngine:
    """
    Sliding-window adaptive baseline engine.

    Maintains separate deques for CPU and RAM readings and exposes
    per-metric baseline (mean), standard deviation, and z-score.

    Window size defaults to 60 samples — at a 5-second poll interval
    that represents the last 5 minutes of history.
    """

    def __init__(self, window_size: int = 60) -> None:
        self.window_size: int = window_size

        # Auto-evict oldest sample when full — O(1) append/pop
        self.metrics_history: Dict[str, deque] = {
            "cpu": deque(maxlen=window_size),
            "ram": deque(maxlen=window_size),
        }

    # ------------------------------------------------------------------ #
    #  Core Update                                                         #
    # ------------------------------------------------------------------ #

    def update_metrics(self, cpu: float, ram: float) -> None:
        """Push one observation into each rolling window."""
        self.metrics_history["cpu"].append(float(cpu))
        self.metrics_history["ram"].append(float(ram))

    # ------------------------------------------------------------------ #
    #  Statistical Primitives                                              #
    # ------------------------------------------------------------------ #

    def get_baseline(self, metric: str) -> Optional[float]:
        """
        Arithmetic mean over the rolling window.
        Returns None when fewer than 2 samples are present.
        """
        history = list(self.metrics_history.get(metric, []))
        if len(history) < 2:
            return None
        return sum(history) / len(history)

    def get_std(self, metric: str) -> Optional[float]:
        """
        Population standard deviation over the rolling window.

        Returns None when fewer than 2 samples are present.
        A floor of 0.5 is applied to prevent division-by-zero in z-score
        computation when the signal is perfectly flat (e.g. idle system).
        """
        history = list(self.metrics_history.get(metric, []))
        if len(history) < 2:
            return None
        mean = sum(history) / len(history)
        variance = sum((x - mean) ** 2 for x in history) / len(history)
        return max(math.sqrt(variance), 0.5)  # floor prevents unstable z-scores

    def get_z_score(self, current: float, metric: str) -> Optional[float]:
        """
        Standardise `current` relative to the rolling baseline.

            z = (current - μ) / σ

        A |z| > 2.0 is generally considered a statistically unusual value.
        Returns None while the engine is warming up (< 2 samples).
        """
        baseline = self.get_baseline(metric)
        std = self.get_std(metric)
        if baseline is None or std is None:
            return None
        return (current - baseline) / std

    # ------------------------------------------------------------------ #
    #  Full Snapshot Output                                                #
    # ------------------------------------------------------------------ #

    def analyze(self, cpu: float, ram: float) -> Dict[str, Optional[float]]:
        """
        Update rolling windows and return a complete baseline report.

        Called once per monitor/simulation cycle — must be fast.

        Returns:
            {
                "cpu_baseline": float | None,
                "cpu_std":      float | None,
                "cpu_z_score":  float | None,
                "ram_baseline": float | None,
                "ram_std":      float | None,
                "ram_z_score":  float | None,
                "window_fill":  float   # 0.0–1.0 fraction of window used
            }
        """
        self.update_metrics(cpu, ram)

        return {
            "cpu_baseline": self.get_baseline("cpu"),
            "cpu_std":      self.get_std("cpu"),
            "cpu_z_score":  self.get_z_score(cpu, "cpu"),
            "ram_baseline": self.get_baseline("ram"),
            "ram_std":      self.get_std("ram"),
            "ram_z_score":  self.get_z_score(ram, "ram"),
            "window_fill":  len(self.metrics_history["cpu"]) / self.window_size,
        }

    # ------------------------------------------------------------------ #
    #  Readiness Guard                                                     #
    # ------------------------------------------------------------------ #

    def is_warmed_up(self) -> bool:
        """
        True once the window holds ≥ 10 samples.
        Below this count, statistical estimates are unreliable.
        """
        return len(self.metrics_history["cpu"]) >= 10

    @property
    def sample_count(self) -> int:
        """Current number of samples in the CPU window."""
        return len(self.metrics_history["cpu"])
