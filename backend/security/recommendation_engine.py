"""Recommendation generation stage."""


def _recommendation_for(threat: dict) -> str:
    threat_type = threat.get("type", "unknown")

    if threat_type == "high_resource_usage":
        name = threat.get("details", {}).get("name", "unknown process")
        return f"Review {name} for unusual CPU or RAM behavior and verify it is trusted."

    if threat_type == "unknown_network_activity":
        pid = threat.get("details", {}).get("pid", "unknown")
        return f"Inspect network activity for PID {pid} and confirm application legitimacy."

    return "Investigate detected behavior and confirm whether it is expected."


def generate_recommendations(threats: list[dict]) -> list[str]:
    """Return minimal human-readable recommendations."""
    if not threats:
        return ["No immediate threats detected. Continue routine monitoring."]
    return [_recommendation_for(threat) for threat in threats]
