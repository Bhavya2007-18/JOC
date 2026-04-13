"""Unit tests for recommendation generation engine."""

import unittest

from backend.security.recommendation_engine import generate_recommendations
from backend.security.sec_models import Recommendation, ThreatItem, ThreatSeverity


class TestRecommendationEngine(unittest.TestCase):
    def test_maps_all_supported_categories(self) -> None:
        threats = [
            ThreatItem("1_suspicious_process", "suspicious_process", ThreatSeverity.HIGH, "", "", pid=1, process_name="bad.exe"),
            ThreatItem("2_background_suspicious", "background_suspicious", ThreatSeverity.HIGH, "", "", pid=2, process_name="bg_bad.exe"),
            ThreatItem("3_unknown_process", "unknown_process", ThreatSeverity.MEDIUM, "", "", pid=3, process_name="mystery.exe"),
            ThreatItem("4_idle_resource_hog", "idle_resource_hog", ThreatSeverity.MEDIUM, "", "", pid=4, process_name="memhog.exe"),
        ]

        recs = generate_recommendations(threats)

        self.assertEqual(len(recs), 4)
        self.assertTrue(all(isinstance(item, Recommendation) for item in recs))

        by_category = {rec.category: rec for rec in recs}
        self.assertEqual(by_category["suspicious_process"].action, "Terminate process")
        self.assertEqual(by_category["suspicious_process"].urgency, ThreatSeverity.HIGH)
        self.assertEqual(
            by_category["suspicious_process"].explanation,
            "Process shows abnormal CPU/RAM usage",
        )
        self.assertEqual(by_category["suspicious_process"].process_name, "bad.exe")
        self.assertEqual(by_category["suspicious_process"].pid, 1)

        self.assertEqual(
            by_category["background_suspicious"].action,
            "Investigate background process",
        )
        self.assertEqual(by_category["background_suspicious"].urgency, ThreatSeverity.HIGH)

        self.assertEqual(by_category["unknown_process"].action, "Review process manually")
        self.assertEqual(by_category["unknown_process"].urgency, ThreatSeverity.MEDIUM)
        self.assertEqual(
            by_category["unknown_process"].explanation,
            "Process is not recognized",
        )
        self.assertEqual(by_category["unknown_process"].process_name, "mystery.exe")
        self.assertEqual(by_category["unknown_process"].pid, 3)

        self.assertEqual(by_category["idle_resource_hog"].action, "Close unused application")
        self.assertEqual(by_category["idle_resource_hog"].urgency, ThreatSeverity.MEDIUM)

    def test_avoids_duplicates_for_same_category_and_process(self) -> None:
        threats = [
            ThreatItem("10_unknown_process", "unknown_process", ThreatSeverity.MEDIUM, "", "", pid=10, process_name="dup.exe"),
            ThreatItem("10_unknown_process_dup", "unknown_process", ThreatSeverity.MEDIUM, "", "", pid=10, process_name="dup.exe"),
        ]

        recs = generate_recommendations(threats)

        self.assertEqual(len(recs), 1)
        self.assertEqual(recs[0].category, "unknown_process")
        self.assertEqual(recs[0].pid, 10)
        self.assertEqual(recs[0].process_name, "dup.exe")

    def test_keeps_distinct_processes_same_category(self) -> None:
        threats = [
            ThreatItem(
                "20_unknown_process",
                "unknown_process",
                ThreatSeverity.MEDIUM,
                "",
                "",
                pid=20,
                process_name="a.exe",
            ),
            ThreatItem(
                "21_unknown_process",
                "unknown_process",
                ThreatSeverity.MEDIUM,
                "",
                "",
                pid=21,
                process_name="b.exe",
            ),
        ]

        recs = generate_recommendations(threats)

        self.assertEqual(len(recs), 2)
        self.assertEqual({rec.pid for rec in recs}, {20, 21})

    def test_ignores_unmapped_categories(self) -> None:
        threats = [
            ThreatItem("99_other", "other", ThreatSeverity.LOW, "", "", pid=99, process_name="other.exe"),
        ]

        recs = generate_recommendations(threats)

        self.assertEqual(recs, [])


if __name__ == "__main__":
    unittest.main()
