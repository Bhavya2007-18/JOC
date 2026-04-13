"""Recommendation generation stage from detected threats."""

from security.sec_models import Recommendation, ThreatItem, ThreatSeverity


def generate_recommendations(threats: list[ThreatItem]) -> list[Recommendation]:
    """Convert threat items into actionable recommendation objects."""
    recommendations: list[Recommendation] = []
    seen: set[tuple[str, int | None]] = set()

    for threat in threats:
        key = (threat.category, threat.pid)
        if key in seen:
            continue

        if threat.category == "suspicious_process":
            recommendations.append(
                Recommendation(
                    category=threat.category,
                    action="Terminate process",
                    explanation="Process shows abnormal CPU/RAM usage",
                    urgency=ThreatSeverity.HIGH,
                    process_name=threat.process_name,
                    pid=threat.pid,
                )
            )
            seen.add(key)
            continue

        if threat.category == "background_suspicious":
            recommendations.append(
                Recommendation(
                    category=threat.category,
                    action="Investigate background process",
                    explanation="Suspicious activity running in background",
                    urgency=ThreatSeverity.HIGH,
                    process_name=threat.process_name,
                    pid=threat.pid,
                )
            )
            seen.add(key)
            continue

        if threat.category == "unknown_process":
            recommendations.append(
                Recommendation(
                    category=threat.category,
                    action="Review process manually",
                    explanation="Process is not recognized",
                    urgency=ThreatSeverity.MEDIUM,
                    process_name=threat.process_name,
                    pid=threat.pid,
                )
            )
            seen.add(key)
            continue

        if threat.category == "idle_resource_hog":
            recommendations.append(
                Recommendation(
                    category=threat.category,
                    action="Close unused application",
                    explanation="Process consuming memory while idle",
                    urgency=ThreatSeverity.MEDIUM,
                    process_name=threat.process_name,
                    pid=threat.pid,
                )
            )
            seen.add(key)

    return recommendations
