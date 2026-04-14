"""Unit tests for the security pipeline orchestrator."""

import unittest
from unittest.mock import patch

from security.sec_models import (
    ProcessInfo,
    Recommendation,
    RiskLevel,
    ThreatItem,
    ThreatSeverity,
)
from security.security_engine import analyze_security


class TestSecurityEngine(unittest.TestCase):
    @patch("security.security_engine.generate_recommendations")
    @patch("security.security_engine.calculate_risk")
    @patch("security.security_engine.detect_threats")
    @patch("security.security_engine.get_processes")
    def test_analyze_security_pipeline_and_output(
        self,
        mock_get_processes,
        mock_detect_threats,
        mock_calculate_risk,
        mock_generate_recommendations,
    ) -> None:
        processes = [
            ProcessInfo(
                pid=123,
                name="bad.exe",
                cpu_percent=85.0,
                ram_mb=900.0,
                exe_path="C:/bad.exe",
                classification="suspicious",
                is_background=True,
                is_idle=False,
            )
        ]
        threats = [
            ThreatItem(
                id="123_suspicious_process",
                category="suspicious_process",
                severity=ThreatSeverity.HIGH,
                title="Suspicious Process Detected",
                description="Process bad.exe flagged as suspicious.",
                pid=123,
                process_name="bad.exe",
            )
        ]
        recommendations = [
            Recommendation(
                category="suspicious_process",
                action="Terminate process",
                explanation="Process shows abnormal CPU/RAM usage",
                urgency=ThreatSeverity.HIGH,
                process_name="bad.exe",
                pid=123,
            )
        ]

        mock_get_processes.return_value = processes
        mock_detect_threats.return_value = threats
        mock_calculate_risk.return_value = (25, RiskLevel.LOW)
        mock_generate_recommendations.return_value = recommendations

        result = analyze_security()

        mock_get_processes.assert_called_once_with()
        mock_detect_threats.assert_called_once_with(processes)
        mock_calculate_risk.assert_called_once_with(threats)
        mock_generate_recommendations.assert_called_once_with(threats)

        self.assertEqual(result["risk_score"], 25)
        self.assertEqual(result["risk_level"], "low")
        self.assertEqual(
            result["threats"],
            [
                {
                    "id": "123_suspicious_process",
                    "category": "suspicious_process",
                    "severity": "high",
                    "title": "Suspicious Process Detected",
                    "description": "Process bad.exe flagged as suspicious.",
                    "pid": 123,
                    "process_name": "bad.exe",
                }
            ],
        )
        self.assertEqual(
            result["recommendations"],
            [
                {
                    "category": "suspicious_process",
                    "action": "Terminate process",
                    "explanation": "Process shows abnormal CPU/RAM usage",
                    "urgency": "high",
                    "pid": 123,
                    "process_name": "bad.exe",
                }
            ],
        )

    @patch("security.security_engine.generate_recommendations")
    @patch("security.security_engine.calculate_risk")
    @patch("security.security_engine.detect_threats")
    @patch("security.security_engine.get_processes")
    def test_analyze_security_empty_results(
        self,
        mock_get_processes,
        mock_detect_threats,
        mock_calculate_risk,
        mock_generate_recommendations,
    ) -> None:
        mock_get_processes.return_value = []
        mock_detect_threats.return_value = []
        mock_calculate_risk.return_value = (0, RiskLevel.LOW)
        mock_generate_recommendations.return_value = []

        result = analyze_security()

        self.assertEqual(
            result,
            {
                "risk_score": 0,
                "risk_level": "low",
                "threats": [],
                "recommendations": [],
            },
        )

    @patch("security.security_engine.generate_recommendations")
    @patch("security.security_engine.calculate_risk")
    @patch("security.security_engine.detect_threats")
    @patch("security.security_engine.get_processes")
    def test_analyze_security_serializes_moderate_level_and_medium_urgency(
        self,
        mock_get_processes,
        mock_detect_threats,
        mock_calculate_risk,
        mock_generate_recommendations,
    ) -> None:
        processes = [
            ProcessInfo(
                pid=88,
                name="mystery.exe",
                cpu_percent=4.0,
                ram_mb=128.0,
                exe_path="C:/mystery.exe",
                classification="unknown",
                is_background=False,
                is_idle=False,
            )
        ]
        threats = [
            ThreatItem(
                id="88_unknown_process",
                category="unknown_process",
                severity=ThreatSeverity.MEDIUM,
                title="Unknown Process",
                description="Process is not recognized.",
                pid=88,
                process_name="mystery.exe",
            )
        ]
        recommendations = [
            Recommendation(
                category="unknown_process",
                action="Review process manually",
                explanation="Process is not recognized",
                urgency=ThreatSeverity.MEDIUM,
                process_name="mystery.exe",
                pid=88,
            )
        ]

        mock_get_processes.return_value = processes
        mock_detect_threats.return_value = threats
        mock_calculate_risk.return_value = (40, RiskLevel.MODERATE)
        mock_generate_recommendations.return_value = recommendations

        result = analyze_security()

        self.assertEqual(result["risk_score"], 40)
        self.assertEqual(result["risk_level"], "moderate")
        self.assertEqual(result["threats"][0]["severity"], "medium")
        self.assertEqual(result["recommendations"][0]["urgency"], "medium")


if __name__ == "__main__":
    unittest.main()
