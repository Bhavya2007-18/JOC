"""Dataclass models for the security analysis pipeline."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ThreatSeverity(str, Enum):
    """Threat severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RiskLevel(str, Enum):
    """Overall report risk levels."""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


@dataclass
class ProcessInfo:
    """Normalized process details used in security analysis."""

    pid: int
    name: str
    cpu_percent: float
    ram_mb: float
    exe_path: str
    classification: str = "unknown"
    is_background: bool = False
    is_idle: bool = False


@dataclass
class ThreatItem:
    """A detected threat record."""

    id: str
    category: str
    severity: ThreatSeverity
    title: str
    description: str
    pid: Optional[int] = None
    process_name: Optional[str] = None


@dataclass
class Recommendation:
    """Actionable recommendation for a detected threat."""

    category: str
    action: str
    explanation: str
    urgency: ThreatSeverity
    process_name: Optional[str] = None
    pid: Optional[int] = None


@dataclass
class SecurityReport:
    """Final structured output for the security pipeline."""

    risk_score: int
    risk_level: RiskLevel
    threats: list[ThreatItem] = field(default_factory=list)
    recommendations: list[Recommendation] = field(default_factory=list)
