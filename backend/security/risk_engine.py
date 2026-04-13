"""Risk scoring stage for detected threats."""

from backend.security.sec_models import RiskLevel, ThreatItem


def calculate_risk(threats: list[ThreatItem]) -> tuple[int, RiskLevel]:
    """Calculate score from unique affected processes and map to a risk level."""
    unique_processes = {threat.process_name for threat in threats if threat.process_name}
    score = min(100, len(unique_processes) * 10)

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
