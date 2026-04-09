from fastapi import APIRouter
from intelligence.config import DRY_RUN

from models.optimizer_models import (
    BoostRequest,
    BoostResponse,
    CleanupRequest,
    CleanupResponse,
    ProcessKillRequest,
    ProcessPriorityRequest,
    ProcessSuspendRequest,
    ProcessResumeRequest,
    ProcessActionResult,
    SuggestionsResponse,
)
from services.optimizer import (
    boost_system_performance,
    change_process_priority_safe,
    kill_process_safe,
    resume_process_safe,
    run_cleanup,
    suspend_process_safe,
    get_optimization_suggestions,
)


router = APIRouter()


@router.post("/optimize/boost", response_model=BoostResponse)
def optimize_boost(payload: BoostRequest) -> BoostResponse:
    result = boost_system_performance(
        cpu_threshold=float(payload.cpu_threshold),
        max_processes=int(payload.max_processes),
        dry_run=DRY_RUN,
    )
    return BoostResponse(
        success=bool(result["success"]),
        message=str(result["message"]),
        dry_run=bool(result["dry_run"]),
        optimization_score_before=None
        if result.get("optimization_score_before") is None
        else {"value": float(result["optimization_score_before"])},
        optimization_score_after=None
        if result.get("optimization_score_after") is None
        else {"value": float(result["optimization_score_after"])},
        processes=[
            {
                "pid": int(p["pid"]),
                "name": str(p["name"]),
                "cpu_percent": float(p["cpu_percent"]),
                "old_priority": p.get("old_priority"),
                "new_priority": p.get("new_priority"),
                "changed": bool(p.get("changed", False)),
                "protected": bool(p.get("protected", False)),
                "dry_run": bool(p.get("dry_run", False)),
                "action_id": p.get("action_id"),
            }
            for p in result.get("processes", [])
        ],
    )


@router.post("/optimize/cleanup", response_model=CleanupResponse)
def optimize_cleanup(payload: CleanupRequest) -> CleanupResponse:
    result = run_cleanup(dry_run=DRY_RUN)
    return CleanupResponse(
        success=bool(result["success"]),
        message=str(result["message"]),
        dry_run=bool(result["dry_run"]),
        total_bytes_freed=int(result["total_bytes_freed"]),
        items=[
            {
                "path": str(item["path"]),
                "bytes_freed": int(item["bytes_freed"]),
                "simulated": bool(item["simulated"]),
            }
            for item in result.get("items", [])
        ],
    )


@router.post("/process/kill", response_model=ProcessActionResult)
def process_kill(payload: ProcessKillRequest) -> ProcessActionResult:
    result = kill_process_safe(pid=payload.pid, dry_run=DRY_RUN)
    return ProcessActionResult(**result)


@router.post("/process/priority", response_model=ProcessActionResult)
def process_priority(payload: ProcessPriorityRequest) -> ProcessActionResult:
    result = change_process_priority_safe(pid=payload.pid, priority=payload.priority, dry_run=DRY_RUN)
    return ProcessActionResult(**result)


@router.post("/process/suspend", response_model=ProcessActionResult)
def process_suspend(payload: ProcessSuspendRequest) -> ProcessActionResult:
    result = suspend_process_safe(pid=payload.pid, dry_run=DRY_RUN)
    return ProcessActionResult(**result)


@router.post("/process/resume", response_model=ProcessActionResult)
def process_resume(payload: ProcessResumeRequest) -> ProcessActionResult:
    result = resume_process_safe(pid=payload.pid, dry_run=DRY_RUN)
    return ProcessActionResult(**result)


@router.get("/optimize/suggestions", response_model=SuggestionsResponse)
def optimize_suggestions(cpu_threshold: float = 30.0, max_processes: int = 10) -> SuggestionsResponse:
    result = get_optimization_suggestions(cpu_threshold=cpu_threshold, max_processes=max_processes)
    return SuggestionsResponse(
        optimization_score=None
        if result.get("optimization_score") is None
        else {"value": float(result["optimization_score"])},
        high_cpu_processes=result.get("high_cpu_processes", []),
        recommended_actions=result.get("recommended_actions", []),
    )

