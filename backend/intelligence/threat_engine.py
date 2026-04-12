"""
Multi-Factor Threat Scoring Engine — Phase 2, JOC Sentinel
-----------------------------------------------------------
Replaces the primitive `(cpu * 0.6 + ram * 0.4)` formula with a nuanced,
multi-dimensional threat model that accounts for four independent factors:

  1. Z-Score Factor     — how many standard deviations above baseline?
  2. Rate-of-Change     — how fast are metrics moving right now?
  3. Duration Factor    — how long has the anomaly persisted?
  4. Correlation Factor — are CPU *and* RAM both spiking together?

Final score is normalised to [0, 100] with exponential smoothing applied
across cycles to prevent score flickering on transient spikes.

Threat Levels:
    0 – 24  → SAFE
   25 – 49  → SUSPICIOUS
   50 – 74  → THREAT
   75 – 100 → CRITICAL
"""

import time
from typing import Dict, Optional


# ────────────────────────────────────────────────────── #
#  Threat Level Thresholds                               #
# ────────────────────────────────────────────────────── #

_THREAT_BANDS = [
    (0,   25,  "SAFE"),
    (25,  50,  "SUSPICIOUS"),
    (50,  75,  "THREAT"),
    (75,  101, "CRITICAL"),
]


def _score_to_level(score: int) -> str:
    """Map a 0–100 integer score to its categorical threat label."""
    for lo, hi, label in _THREAT_BANDS:
        if lo <= score < hi:
            return label
    return "CRITICAL"


# ────────────────────────────────────────────────────── #
#  Engine                                                #
# ────────────────────────────────────────────────────── #

class ThreatEngine:
    """
    Produces a composite 0–100 threat score each cycle.

    Each cycle the engine computes four normalised factors (each in [0, 1])
    then combines them via fixed weights:

        raw = w_z * f_z  +  w_roc * f_roc  +  w_dur * f_dur  +  w_corr * f_corr
        score = int(raw * 100)                   # scale to 0–100
        smoothed = 0.3 * score + 0.7 * prev     # EMA smoothing across cycles

    The EMA smoothing prevents alarm fatigue from one-cycle spikes.
    """

    # Factor weights — must sum to 1.0
    _W_Z_SCORE     = 0.35   # Statistical surprise (strongest signal)
    _W_ROC         = 0.25   # Speed of change
    _W_DURATION    = 0.20   # Persistence
    _W_CORRELATION = 0.20   # Multi-metric coupling

    # Tuning constants
    _Z_ANOMALY_THRESHOLD  = 2.0    # z-score that counts as "anomalous"
    _Z_SATURATION         = 4.0    # z-score where f_z reaches 1.0
    _ROC_SATURATION       = 20.0   # %-pt/cycle where f_roc reaches 1.0
    _DURATION_SATURATION  = 120.0  # seconds of sustained anomaly → f_dur = 1.0
    _EMA_ALPHA            = 0.30   # smoothing: 0=very slow, 1=instant

    def __init__(self) -> None:
        # Previous cycle values for rate-of-change computation
        self._prev_cpu: Optional[float] = None
        self._prev_ram: Optional[float] = None

        # Timestamps when each metric first crossed the anomaly threshold
        self._anomaly_onset: Dict[str, Optional[float]] = {
            "cpu": None,
            "ram": None,
        }

        # Score history for EMA smoothing
        self._smoothed_score: float = 0.0
        self._last_level: str = "SAFE"

    # ------------------------------------------------------------------ #
    #  Private Factor Computations                                         #
    # ------------------------------------------------------------------ #

    def _f_z_score(
        self,
        cpu_z: Optional[float],
        ram_z: Optional[float],
    ) -> float:
        """
        Factor from z-score magnitude (worst of CPU / RAM).

        Linearly maps from [0, Z_SATURATION] → [0.0, 1.0].
        """
        cpu_mag = abs(cpu_z) if cpu_z is not None else 0.0
        ram_mag = abs(ram_z) if ram_z is not None else 0.0
        worst = max(cpu_mag, ram_mag)
        return min(worst / self._Z_SATURATION, 1.0)

    def _f_roc(self, cpu: float, ram: float) -> float:
        """
        Rate-of-change factor — captures sudden jumps in either metric.

        Uses the absolute single-step delta against a saturation cap.
        """
        cpu_roc = abs(cpu - self._prev_cpu) if self._prev_cpu is not None else 0.0
        ram_roc = abs(ram - self._prev_ram) if self._prev_ram is not None else 0.0
        worst_roc = max(cpu_roc, ram_roc)
        return min(worst_roc / self._ROC_SATURATION, 1.0)

    def _f_duration(
        self,
        cpu_z: Optional[float],
        ram_z: Optional[float],
    ) -> float:
        """
        Duration factor — how long has ANY metric been anomalous?

        Onset is marked when |z| > Z_ANOMALY_THRESHOLD; cleared when
        the metric returns to normal. The longest running anomaly drives
        the factor value.
        """
        now = time.monotonic()

        # Update onset timestamps
        for metric, z in (("cpu", cpu_z), ("ram", ram_z)):
            is_anomalous = z is not None and abs(z) > self._Z_ANOMALY_THRESHOLD
            if is_anomalous and self._anomaly_onset[metric] is None:
                self._anomaly_onset[metric] = now
            elif not is_anomalous:
                self._anomaly_onset[metric] = None

        # Factor driven by the longest current anomaly streak
        max_duration = max(
            (now - onset) if onset is not None else 0.0
            for onset in self._anomaly_onset.values()
        )
        return min(max_duration / self._DURATION_SATURATION, 1.0)

    def _f_correlation(
        self,
        cpu: float,
        ram: float,
        cpu_z: Optional[float],
        ram_z: Optional[float],
    ) -> float:
        """
        Cross-metric correlation factor.

        The idea: a CPU spike alone may be a normal workload burst.
        CPU *and* RAM spiking together is a stronger signal of a genuine
        threat (e.g. a runaway process leaking memory while burning cycles).

        The factor uses the product of normalised values, which is high
        only when BOTH dimensions are simultaneously elevated.
        """
        cpu_z_mag = abs(cpu_z) if cpu_z is not None else 0.0
        ram_z_mag = abs(ram_z) if ram_z is not None else 0.0

        cpu_elevated = cpu > 60.0 and cpu_z_mag > 1.5
        ram_elevated = ram > 60.0 and ram_z_mag > 1.5

        if cpu_elevated and ram_elevated:
            # Both elevated: joint product scaled to [0, 1]
            joint = (cpu / 100.0) * (ram / 100.0)
            return min(joint * 4.0, 1.0)   # 50% × 50% → 1.0 at joint=0.25+
        elif cpu_elevated or ram_elevated:
            return 0.4   # Partial elevation
        return 0.0

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def compute(
        self,
        cpu: float,
        ram: float,
        cpu_z: Optional[float] = None,
        ram_z: Optional[float] = None,
    ) -> Dict:
        """
        Compute the composite threat score for one monitor cycle.

        Must be called every cycle (in order) so rate-of-change and
        duration tracking remain accurate.

        Args:
            cpu:   Current CPU usage percentage (0–100).
            ram:   Current RAM usage percentage (0–100).
            cpu_z: Z-score from BaselineEngine (None while warming up).
            ram_z: Z-score from BaselineEngine (None while warming up).

        Returns:
            {
                "threat_score": int,          # 0–100
                "level":        str,          # SAFE|SUSPICIOUS|THREAT|CRITICAL
                "factors": {
                    "z_score_factor":     float,
                    "roc_factor":         float,
                    "duration_factor":    float,
                    "correlation_factor": float,
                },
                "raw_inputs": { cpu, ram, cpu_z_score, ram_z_score }
            }
        """
        # Compute normalised factors — each in [0, 1]
        f_z    = self._f_z_score(cpu_z, ram_z)
        f_roc  = self._f_roc(cpu, ram)
        f_dur  = self._f_duration(cpu_z, ram_z)
        f_corr = self._f_correlation(cpu, ram, cpu_z, ram_z)

        # Weighted combination → raw score in [0, 1]
        raw = (
            self._W_Z_SCORE     * f_z    +
            self._W_ROC         * f_roc  +
            self._W_DURATION    * f_dur  +
            self._W_CORRELATION * f_corr
        )

        # Scale to 0–100, then apply EMA to smooth cross-cycle fluctuations
        instant = min(max(raw * 100, 0.0), 100.0)
        self._smoothed_score = (
            self._EMA_ALPHA * instant +
            (1.0 - self._EMA_ALPHA) * self._smoothed_score
        )
        score = int(self._smoothed_score)
        self._last_level = _score_to_level(score)

        # Persist values for next-cycle delta computation
        self._prev_cpu = cpu
        self._prev_ram = ram

        return {
            "threat_score": score,
            "level": self._last_level,
            "factors": {
                "z_score_factor":     round(f_z,    4),
                "roc_factor":         round(f_roc,  4),
                "duration_factor":    round(f_dur,  4),
                "correlation_factor": round(f_corr, 4),
            },
            "raw_inputs": {
                "cpu":          round(cpu, 2),
                "ram":          round(ram, 2),
                "cpu_z_score":  round(cpu_z, 4) if cpu_z is not None else None,
                "ram_z_score":  round(ram_z, 4) if ram_z is not None else None,
            },
        }

    # ------------------------------------------------------------------ #
    #  Properties                                                          #
    # ------------------------------------------------------------------ #

    @property
    def last_score(self) -> int:
        """Most recent smoothed threat score (0–100)."""
        return int(self._smoothed_score)

    @property
    def last_level(self) -> str:
        """Most recent threat level label."""
        return self._last_level
