from __future__ import annotations

from typing import Any, Dict

from core.config import ValidationConfig


class ScoringEngine:
    def __init__(self, config: ValidationConfig) -> None:
        self.config = config

    def score(
        self,
        analysis: Dict[str, Any],
        response_time: float,
        detection_delay: float,
    ) -> Dict[str, Any]:
        detection_score = 0
        if analysis.get("detection_presence"):
            detection_score += self.config.scoring_detection_weight // 2
        if analysis.get("detection_correctness"):
            detection_score += self.config.scoring_detection_weight // 2

        decision_relevance = int(analysis.get("decision_relevance", 0))
        decision_score = min(self.config.scoring_decision_weight, decision_relevance * 10)

        time_score = 0
        target = max(0.1, self.config.response_time_target_seconds)
        if response_time <= target:
            time_score = self.config.scoring_time_weight
        elif response_time <= target * 1.5:
            time_score = int(self.config.scoring_time_weight * 0.6)
        elif detection_delay <= target * 2:
            time_score = int(self.config.scoring_time_weight * 0.4)

        total = detection_score + decision_score + time_score
        if total >= 75:
            verdict = "effective"
        elif total >= 45:
            verdict = "partial"
        else:
            verdict = "failed"

        return {
            "detection_score": int(detection_score),
            "decision_score": int(decision_score),
            "time_score": int(time_score),
            "total_score": int(total),
            "false_negatives": int(analysis.get("false_negatives", 0)),
            "false_positives": int(analysis.get("false_positives", 0)),
            "verdict": verdict,
        }

