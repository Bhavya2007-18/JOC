"""Adaptive threshold engine using Exponential Moving Average (EMA)."""
from __future__ import annotations

import math
from typing import Tuple

from utils.logger import get_logger

from .defense_memory import DefenseMemory

logger = get_logger("blue_team.adaptive_thresholds")


class AdaptiveThresholds:
    """Learns what is 'normal' for this specific machine and detects deviations.

    Uses Exponential Moving Average (EMA) for both the baseline and standard deviation.
    An anomaly is detected when the current value exceeds baseline + k * std_dev.

    The system gets smarter over time as it sees more samples and tightens its baselines.
    """

    def __init__(self, memory: DefenseMemory, alpha: float = 0.1, k: float = 2.0) -> None:
        self.memory = memory
        self.alpha = alpha  # EMA smoothing factor (lower = slower adaptation)
        self.k = k          # Number of std_devs for anomaly threshold

    def update(self, cpu: float, memory_pct: float) -> None:
        """Feed a new observation to update the adaptive baselines."""
        n = self.memory.samples_seen

        if n == 0:
            # First observation — initialize baselines
            self.memory.baseline_cpu = cpu
            self.memory.baseline_memory = memory_pct
            self.memory.baseline_std_cpu = 10.0
            self.memory.baseline_std_memory = 10.0
        else:
            # EMA update for baseline: baseline = α * current + (1-α) * baseline
            self.memory.baseline_cpu = (
                self.alpha * cpu + (1 - self.alpha) * self.memory.baseline_cpu
            )
            self.memory.baseline_memory = (
                self.alpha * memory_pct + (1 - self.alpha) * self.memory.baseline_memory
            )

            # EMA update for standard deviation
            cpu_dev = abs(cpu - self.memory.baseline_cpu)
            mem_dev = abs(memory_pct - self.memory.baseline_memory)
            self.memory.baseline_std_cpu = (
                self.alpha * cpu_dev + (1 - self.alpha) * self.memory.baseline_std_cpu
            )
            self.memory.baseline_std_memory = (
                self.alpha * mem_dev + (1 - self.alpha) * self.memory.baseline_std_memory
            )

        self.memory.samples_seen = n + 1
        self.memory.save()

    def is_anomalous(self, cpu: float, memory_pct: float) -> Tuple[bool, float]:
        """Check if current values are anomalous and return confidence.

        Returns:
            (is_anomaly, confidence) where confidence is 0.0 to 1.0
        """
        if self.memory.samples_seen < 5:
            # Not enough data to make a judgement
            return False, 0.0

        # Calculate z-scores relative to learned baselines
        cpu_std = max(self.memory.baseline_std_cpu, 1.0)
        mem_std = max(self.memory.baseline_std_memory, 1.0)

        cpu_z = (cpu - self.memory.baseline_cpu) / cpu_std
        mem_z = (memory_pct - self.memory.baseline_memory) / mem_std

        # Anomaly if either exceeds k standard deviations
        cpu_anomaly = cpu_z > self.k
        mem_anomaly = mem_z > self.k

        is_anomaly = cpu_anomaly or mem_anomaly

        # Confidence based on how far beyond the threshold we are
        max_z = max(cpu_z, mem_z)
        if max_z <= 0:
            confidence = 0.0
        elif max_z <= self.k:
            confidence = max_z / self.k * 0.5  # Below threshold = low confidence
        else:
            # Beyond threshold: confidence scales from 0.5 to 1.0
            overshoot = (max_z - self.k) / self.k
            confidence = min(1.0, 0.5 + overshoot * 0.5)

        return is_anomaly, round(confidence, 3)

    def get_thresholds(self) -> dict:
        """Return current computed thresholds for transparency."""
        cpu_std = max(self.memory.baseline_std_cpu, 1.0)
        mem_std = max(self.memory.baseline_std_memory, 1.0)
        return {
            "cpu_baseline": round(self.memory.baseline_cpu, 1),
            "memory_baseline": round(self.memory.baseline_memory, 1),
            "cpu_threshold": round(self.memory.baseline_cpu + self.k * cpu_std, 1),
            "memory_threshold": round(self.memory.baseline_memory + self.k * mem_std, 1),
            "cpu_std": round(cpu_std, 2),
            "memory_std": round(mem_std, 2),
            "samples_seen": self.memory.samples_seen,
        }
