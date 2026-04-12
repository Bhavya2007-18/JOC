from __future__ import annotations

from typing import Any, Dict, List


class ResponseAnalyzer:
    """Analyzes if intelligence outputs match expected simulation behavior."""

    # Corrected mapping: each simulation type maps to the anomaly it SHOULD trigger
    _EXPECTED_ANOMALY_BY_SIM = {
        "cpu_spike": "cpu_spike",
        "memory_stress": "cpu_spike",  # memory stress raises CPU via allocation loops
        "process_simulator": "unknown_high_cpu_process",
        "network_burst": "idle_period_activity",
    }

    # Broader keyword matching for decision relevance
    _DECISION_KEYWORDS_BY_SIM = {
        "cpu_spike": ["priority", "reduce", "cpu", "lower"],
        "memory_stress": ["cleanup", "clean", "memory", "free", "ram"],
        "process_simulator": ["review", "inspect", "limit", "process", "unknown"],
        "network_burst": ["idle", "investigate", "scheduled", "activity"],
    }

    def analyze(
        self,
        simulation_type: str,
        anomalies: List[Dict[str, Any]],
        decisions: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        expected_type = self._EXPECTED_ANOMALY_BY_SIM.get(simulation_type)
        detected_types = [str(item.get("type", "")) for item in anomalies]

        detection_presence = len(anomalies) > 0
        detection_correctness = expected_type in detected_types if expected_type else detection_presence

        # Improved decision relevance scoring with broader keyword matching
        decision_relevance = 0
        keywords = self._DECISION_KEYWORDS_BY_SIM.get(simulation_type, [])
        if decisions:
            for decision in decisions:
                text = str(decision.get("decision", "")).lower()
                reason = str(decision.get("reason", "")).lower()
                combined = text + " " + reason
                for keyword in keywords:
                    if keyword in combined:
                        decision_relevance += 1
                        break  # one match per decision is enough

        false_negatives = 0 if detection_presence else 1
        false_positives = 0
        if detection_presence and expected_type and expected_type not in detected_types:
            false_positives = len(anomalies)

        return {
            "detection_presence": detection_presence,
            "detection_correctness": detection_correctness,
            "decision_relevance": decision_relevance,
            "false_negatives": false_negatives,
            "false_positives": false_positives,
        }
