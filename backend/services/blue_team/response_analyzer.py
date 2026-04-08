from __future__ import annotations

from typing import Any, Dict, List


class ResponseAnalyzer:
    """Analyzes if intelligence outputs match expected simulation behavior."""

    _EXPECTED_ANOMALY_BY_SIM = {
        "cpu_spike": "cpu_spike",
        "memory_stress": "cpu_spike",
        "process_simulator": "unknown_high_cpu_process",
        "network_burst": "idle_period_activity",
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

        decision_relevance = 0
        if decisions:
            for decision in decisions:
                text = str(decision.get("decision", "")).lower()
                if simulation_type == "cpu_spike" and "priority" in text:
                    decision_relevance += 1
                elif simulation_type == "memory_stress" and "cleanup" in text:
                    decision_relevance += 1
                elif simulation_type == "process_simulator" and ("review" in text or "inspect" in text):
                    decision_relevance += 1
                elif simulation_type == "network_burst" and "idle" in text:
                    decision_relevance += 1

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

