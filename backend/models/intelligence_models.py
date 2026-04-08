from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, confloat


class ConfidenceLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class BehaviorProcessSnapshot(BaseModel):
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float


class BehaviorLogEntry(BaseModel):
    timestamp: float
    hour_of_day: int = Field(..., ge=0, le=23)
    cpu_percent: float
    memory_percent: float
    top_processes: List[BehaviorProcessSnapshot]


class LogResponse(BaseModel):
    success: bool
    entry: BehaviorLogEntry


class FrequentAppInfo(BaseModel):
    name: str
    count: int
    average_cpu_percent: float


class HourlyUsageInfo(BaseModel):
    hour: int = Field(..., ge=0, le=23)
    average_cpu_percent: float
    average_memory_percent: float


class TimeSeriesPoint(BaseModel):
    timestamp: float
    cpu_percent: float
    memory_percent: float


class PatternsResponse(BaseModel):
    average_cpu_percent: float
    average_memory_percent: float
    peak_hours: List[HourlyUsageInfo]
    idle_hours: List[int]
    frequent_apps: List[FrequentAppInfo]
    cpu_memory_timeseries: List[TimeSeriesPoint]


class AnomalySeverity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Anomaly(BaseModel):
    id: str
    type: str
    timestamp: float
    description: str
    severity: AnomalySeverity
    data: Dict[str, Any]


class AnomaliesResponse(BaseModel):
    anomalies: List[Anomaly]


class DecisionSuggestedAction(BaseModel):
    action_type: str
    target: str
    parameters: Dict[str, Any]


class Decision(BaseModel):
    decision: str
    reason: str
    confidence: ConfidenceLevel
    data_used: Dict[str, Any]
    related_anomalies: List[str]
    suggested_actions: List[DecisionSuggestedAction]


class DecisionsResponse(BaseModel):
    decisions: List[Decision]

