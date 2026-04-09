"""Risk scoring stage."""

from .sec_config import BASE_SECURITY_SCORE, SCORING_WEIGHTS


def calculate_security_score(threats: list[dict]) -> int:
    """Calculate a placeholder security score in the range 0-100."""
    score = float(BASE_SECURITY_SCORE)

    for threat in threats:
        if threat.get("type") == "high_resource_usage":
            score -= SCORING_WEIGHTS["high_resource_usage"] * 20
        elif threat.get("type") == "unknown_network_activity":
            score -= SCORING_WEIGHTS["unknown_network_activity"] * 30
        else:
            score -= 5

    return max(0, min(100, int(round(score))))


def assign_risk_level(security_score: int) -> str:
    """Convert a numeric score into a risk level label."""
    if security_score >= 80:
        return "low"
    if security_score >= 50:
        return "medium"
    return "high"


def evaluate_risk(threats: list[dict]) -> dict:
    """Return risk scoring output for the final payload."""
    score = calculate_security_score(threats)
    return {
        "security_score": score,
        "risk_level": assign_risk_level(score),
    }
