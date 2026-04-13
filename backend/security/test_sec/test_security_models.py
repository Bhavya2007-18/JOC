"""Unit tests for security dataclass models."""

import unittest

from security.sec_models import (
    ProcessInfo,
    Recommendation,
    RiskLevel,
    SecurityReport,
    ThreatItem,
    ThreatSeverity,
)


class TestSecurityModels(unittest.TestCase):
    def test_enum_values(self) -> None:
        self.assertEqual(ThreatSeverity.LOW.value, "low")
        self.assertEqual(ThreatSeverity.MEDIUM.value, "medium")
        self.assertEqual(ThreatSeverity.HIGH.value, "high")
        self.assertEqual(RiskLevel.LOW.value, "low")
        self.assertEqual(RiskLevel.MODERATE.value, "moderate")
        self.assertEqual(RiskLevel.HIGH.value, "high")

    def test_process_info_defaults(self) -> None:
        proc = ProcessInfo(
            pid=123,
            name="test.exe",
            cpu_percent=45.5,
            ram_mb=200.0,
            exe_path="C:/test.exe",
        )
        self.assertEqual(proc.classification, "unknown")
        self.assertFalse(proc.is_background)
        self.assertFalse(proc.is_idle)

    def test_report_holds_full_output(self) -> None:
        threat = ThreatItem(
            id="T1",
            category="high_cpu",
            severity=ThreatSeverity.HIGH,
            title="High CPU Usage",
            description="Process consuming excessive CPU",
            pid=123,
            process_name="test.exe",
        )
        recommendation = Recommendation(
            category="process",
            action="Terminate process",
            explanation="This process is using too much CPU",
            urgency=ThreatSeverity.HIGH,
            process_name="test.exe",
            pid=123,
        )
        report = SecurityReport(
            risk_score=60,
            risk_level=RiskLevel.MODERATE,
            threats=[threat],
            recommendations=[recommendation],
        )
        self.assertEqual(report.risk_score, 60)
        self.assertEqual(report.risk_level, RiskLevel.MODERATE)
        self.assertEqual(len(report.threats), 1)
        self.assertEqual(len(report.recommendations), 1)


if __name__ == "__main__":
    unittest.main()