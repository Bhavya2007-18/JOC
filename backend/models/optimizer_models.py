from typing import List, Optional

from pydantic import BaseModel, Field, conint, confloat


class ProcessKillRequest(BaseModel):
    pid: int = Field(..., gt=0)
    dry_run: bool = False


class ProcessPriorityRequest(BaseModel):
    pid: int = Field(..., gt=0)
    priority: conint(ge=-20, le=19)
    dry_run: bool = False


class ProcessSuspendRequest(BaseModel):
    pid: int = Field(..., gt=0)
    dry_run: bool = False


class ProcessResumeRequest(BaseModel):
    pid: int = Field(..., gt=0)
    dry_run: bool = False


class BoostRequest(BaseModel):
    cpu_threshold: confloat(ge=0.0, le=100.0) = 50.0
    max_processes: conint(ge=1, le=50) = 5
    dry_run: bool = False


class CleanupRequest(BaseModel):
    dry_run: bool = False


class OptimizationScore(BaseModel):
    value: float = Field(..., ge=0.0, le=100.0)


class ProcessActionResult(BaseModel):
    pid: int
    name: str
    action: str
    success: bool
    message: str
    dry_run: bool
    protected: bool
    action_id: Optional[str] = None
    risk: str = "medium"
    confidence: float = 0.75


class BoostedProcessInfo(BaseModel):
    pid: int
    name: str
    cpu_percent: float
    old_priority: Optional[int]
    new_priority: Optional[int]
    changed: bool
    protected: bool
    dry_run: bool
    action_id: Optional[str] = None


class BoostResponse(BaseModel):
    success: bool
    message: str
    dry_run: bool
    optimization_score_before: Optional[OptimizationScore]
    optimization_score_after: Optional[OptimizationScore]
    processes: List[BoostedProcessInfo]
    risk: str = "medium"
    confidence: float = 0.75


class CleanupItemResult(BaseModel):
    path: str
    bytes_freed: int
    simulated: bool


class CleanupResponse(BaseModel):
    success: bool
    message: str
    dry_run: bool
    total_bytes_freed: int
    items: List[CleanupItemResult]
    risk: str = "medium"
    confidence: float = 0.75


class HighCpuProcessSuggestion(BaseModel):
    pid: int
    name: str
    cpu_percent: float
    current_priority: Optional[int]
    suggested_priority: Optional[int]
    reason: str
    protected: bool


class SuggestedAction(BaseModel):
    action_type: str
    target: str
    reason: str
    dry_run_only: bool = True


class SuggestionsResponse(BaseModel):
    optimization_score: Optional[OptimizationScore]
    high_cpu_processes: List[HighCpuProcessSuggestion]
    recommended_actions: List[SuggestedAction]
