"""Risk scoring stage for detected threats."""

from backend.security.sec_models import RiskLevel, ThreatItem, ThreatSeverity


def calculate_risk(threats: list[ThreatItem]) -> tuple[int, RiskLevel]:
    """Calculate risk score (0-100) and mapped risk level from threat severities."""
    severity_points = {
        ThreatSeverity.HIGH: 25,
        ThreatSeverity.MEDIUM: 15,
        ThreatSeverity.LOW: 5,
    }

    score = sum(severity_points.get(threat.severity, 0) for threat in threats)
    score = max(0, min(100, int(score)))

    if score <= 25:
        level = RiskLevel.LOW
    elif score <= 60:
        level = RiskLevel.MODERATE
    else:
        level = RiskLevel.HIGH

    return score, level


def evaluate_risk(threats: list[ThreatItem]) -> dict:
    """Compatibility wrapper for existing orchestrator output shape."""
    score, level = calculate_risk(threats)
    return {
        "security_score": score,
        "risk_level": level.value,
    }
