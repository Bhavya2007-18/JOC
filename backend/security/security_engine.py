"""Main entry point and orchestrator for security analysis."""

from .network_engine import analyze_network
from .process_engine import analyze_processes
from .recommendation_engine import generate_recommendations
from .risk_engine import evaluate_risk
from .threat_engine import detect_threats


def analyze_security() -> dict:
    """Run security pipeline and return structured placeholder output."""
    process_analysis = analyze_processes()
    network_analysis = analyze_network(process_analysis)
    threats = detect_threats(process_analysis, network_analysis)
    risk = evaluate_risk(threats)
    recommendations = generate_recommendations(threats)

    return {
        "security_score": risk["security_score"],
        "risk_level": risk["risk_level"],
        "threats": threats,
        "recommendations": recommendations,
    }
