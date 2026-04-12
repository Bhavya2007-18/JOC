"""Main entry point and orchestrator for security analysis."""

from .process_engine import get_processes
from .recommendation_engine import generate_recommendations
from .risk_engine import calculate_risk
from .sec_logger import save_security_log
from .threat_engine import detect_threats


def analyze_security() -> dict:
    """Run the full security pipeline and return serialized output."""
    processes = get_processes()
    threats = detect_threats(processes)
    score, level = calculate_risk(threats)
    recommendations = generate_recommendations(threats)

    result = {
        "risk_score": score,
        "risk_level": level.name.lower(),
        "threats": [
            {
                "id": threat.id,
                "category": threat.category,
                "severity": threat.severity.name.lower(),
                "title": threat.title,
                "description": threat.description,
                "pid": threat.pid,
                "process_name": threat.process_name,
            }
            for threat in threats
        ],
        "recommendations": [
            {
                "category": recommendation.category,
                "action": recommendation.action,
                "explanation": recommendation.explanation,
                "urgency": recommendation.urgency.name.lower(),
                "pid": recommendation.pid,
                "process_name": recommendation.process_name,
            }
            for recommendation in recommendations
        ],
    }

    save_security_log(result)
    return result
