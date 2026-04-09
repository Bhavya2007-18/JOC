from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SimulationType(str, Enum):
    cpu_spike = "cpu_spike"
    memory_stress = "memory_stress"
    process_simulator = "process_simulator"
    network_burst = "network_burst"
    auto = "auto"  # ML-chosen by AttackStrategist


class SimulationState(str, Enum):
    idle = "IDLE"
    initializing = "INITIALIZING"
    running = "RUNNING_SIMULATION"
    observing = "OBSERVING"
    analyzing = "ANALYZING"
    completed = "COMPLETED"
    failed = "FAILED"


class Verdict(str, Enum):
    effective = "effective"
    partial = "partial"
    failed = "failed"


class SimulationRunRequest(BaseModel):
    simulation_type: SimulationType
    parameters: Dict[str, Any] = Field(default_factory=dict)
    dry_run: bool = False
    observation_window_seconds: int = Field(default=10, ge=1, le=300)
    chain: List[SimulationType] = Field(default_factory=list)
    queue_if_busy: bool = True
    replay_simulation_id: Optional[str] = None
    difficulty: str = Field(default="auto", description="easy/medium/hard/auto")


class SimulationStopRequest(BaseModel):
    reason: str = "manual_stop"


class TimelineData(BaseModel):
    start: Optional[float] = None
    anomaly_detected_at: Optional[float] = None
    decision_made_at: Optional[float] = None
    completed_at: Optional[float] = None
    transitions: List[Dict[str, Any]] = Field(default_factory=list)


class MetricsData(BaseModel):
    response_time: float = 0.0
    detection_delay: float = 0.0


class EvaluationData(BaseModel):
    detection_score: int
    decision_score: int
    time_score: int
    total_score: int
    false_negatives: int
    false_positives: int
    verdict: Verdict


class SimulationReport(BaseModel):
    simulation_id: str
    simulation_type: str
    parameters: Dict[str, Any]
    timeline: TimelineData
    metrics: MetricsData
    evaluation: EvaluationData
    observations: List[Dict[str, Any]]
    logs_ref: str
    state: SimulationState
    correlation_id: str
    feedback: Optional[Dict[str, Any]] = None  # ML feedback from feedback loop
    attack_plan: Optional[Dict[str, Any]] = None  # Red Team attack plan used


class SimulationHistoryResponse(BaseModel):
    reports: List[SimulationReport]


class SimulationQueueItem(BaseModel):
    simulation_id: str
    simulation_type: SimulationType
    parameters: Dict[str, Any]
    dry_run: bool
    observation_window_seconds: int
    correlation_id: str


class SimulationRunResponse(BaseModel):
    queued: bool
    report: Optional[SimulationReport] = None
    simulation_id: str
    message: str
