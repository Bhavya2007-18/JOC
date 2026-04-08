from __future__ import annotations

import time
from typing import Any, Dict, List

from services.intelligence import detect_anomalies, generate_decisions


class IntelligenceBridge:
    """Read-only bridge that consumes Phase 3 outputs without duplicating logic."""

    def fetch_intelligence_outputs(self, window_seconds: int) -> Dict[str, Any]:
        anomalies = detect_anomalies(window_seconds=window_seconds)
        anomaly_time = time.time() if anomalies else None

        decisions = generate_decisions(window_seconds=window_seconds)
        decision_time = time.time() if decisions else None

        return {
            "anomalies": anomalies,
            "decisions": decisions,
            "anomaly_detected_at": anomaly_time,
            "decision_made_at": decision_time,
        }

