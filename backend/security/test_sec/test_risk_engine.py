"""Unit tests for risk scoring engine."""

import unittest

from backend.security.risk_engine import calculate_risk
from backend.security.sec_models import RiskLevel, ThreatItem, ThreatSeverity


class TestRiskEngine(unittest.TestCase):
    def test_empty_threats_is_low(self) -> None:
        score, level = calculate_risk([])

        self.assertEqual(score, 0)
        self.assertEqual(level, RiskLevel.LOW)

    def test_low_boundary_at_25(self) -> None:
        threats = [
            ThreatItem("1", "t1", ThreatSeverity.HIGH, "", ""),
        ]

        score, level = calculate_risk(threats)

        self.assertEqual(score, 25)
        self.assertEqual(level, RiskLevel.LOW)

    def test_moderate_range(self) -> None:
        threats = [
            ThreatItem("1", "t1", ThreatSeverity.HIGH, "", ""),
            ThreatItem("2", "t2", ThreatSeverity.MEDIUM, "", ""),
        ]

        score, level = calculate_risk(threats)

        self.assertEqual(score, 40)
        self.assertEqual(level, RiskLevel.MODERATE)

    def test_moderate_lower_boundary_at_26(self) -> None:
        threats = [
            ThreatItem("1", "t1", ThreatSeverity.HIGH, "", ""),
            ThreatItem("2", "t2", ThreatSeverity.LOW, "", ""),
        ]

        score, level = calculate_risk(threats)

        self.assertEqual(score, 30)
        self.assertEqual(level, RiskLevel.MODERATE)

    def test_moderate_upper_boundary_at_60(self) -> None:
        threats = [
            ThreatItem("1", "t1", ThreatSeverity.MEDIUM, "", ""),
            ThreatItem("2", "t2", ThreatSeverity.MEDIUM, "", ""),
            ThreatItem("3", "t3", ThreatSeverity.MEDIUM, "", ""),
            ThreatItem("4", "t4", ThreatSeverity.MEDIUM, "", ""),
        ]

        score, level = calculate_risk(threats)

        self.assertEqual(score, 60)
        self.assertEqual(level, RiskLevel.MODERATE)

    def test_high_lower_boundary_at_61_or_more(self) -> None:
        threats = [
            ThreatItem("1", "t1", ThreatSeverity.HIGH, "", ""),
            ThreatItem("2", "t2", ThreatSeverity.HIGH, "", ""),
            ThreatItem("3", "t3", ThreatSeverity.MEDIUM, "", ""),
        ]

        score, level = calculate_risk(threats)

        self.assertEqual(score, 65)
        self.assertEqual(level, RiskLevel.HIGH)

    def test_high_range_above_60(self) -> None:
        threats = [
            ThreatItem("1", "t1", ThreatSeverity.HIGH, "", ""),
            ThreatItem("2", "t2", ThreatSeverity.HIGH, "", ""),
            ThreatItem("3", "t3", ThreatSeverity.HIGH, "", ""),
        ]

        score, level = calculate_risk(threats)

        self.assertEqual(score, 75)
        self.assertEqual(level, RiskLevel.HIGH)

    def test_score_clamped_to_100(self) -> None:
        threats = [
            ThreatItem(str(i), f"t{i}", ThreatSeverity.HIGH, "", "")
            for i in range(1, 10)
        ]

        score, level = calculate_risk(threats)

        self.assertEqual(score, 100)
        self.assertEqual(level, RiskLevel.HIGH)


if __name__ == "__main__":
    unittest.main()
    