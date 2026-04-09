import threading
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from models.simulation_models import (
    SimulationHistoryResponse,
    SimulationReport,
    SimulationRunRequest,
    SimulationRunResponse,
    SimulationStopRequest,
    SimulationType,
)
from services.orchestration import IntegrityEngine


router = APIRouter(tags=["simulation"])
engine = IntegrityEngine()


@router.post("/simulate/run", response_model=SimulationRunResponse)
def run_simulation(payload: SimulationRunRequest) -> SimulationRunResponse:
    return engine.run(payload)


@router.get("/simulation/history", response_model=SimulationHistoryResponse)
def get_simulation_history() -> SimulationHistoryResponse:
    return SimulationHistoryResponse(reports=engine.get_history())


@router.get("/simulation/evolution")
def get_evolution_stats():
    """Return Red/Blue Team learning progression and evolution metrics."""
    return engine.feedback_loop.get_evolution_stats()


@router.get("/simulation/strategies")
def get_strategies():
    """Return current Red Team attack strategy state."""
    return engine.strategist.get_evolution_stats()


@router.get("/simulation/{simulation_id}", response_model=SimulationReport)
def get_simulation_report(simulation_id: str) -> SimulationReport:
    report = engine.get_report(simulation_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Simulation report not found")
    return report


@router.post("/simulate/stop")
def stop_simulation(payload: SimulationStopRequest):
    return engine.stop(payload.reason)


class AutoTrainRequest(BaseModel):
    episodes: int = Field(default=5, ge=1, le=50, description="Number of training episodes")
    difficulty: str = Field(default="auto", description="easy/medium/hard/auto")
    observation_window_seconds: int = Field(default=10, ge=1, le=60)


@router.post("/simulate/auto-train")
def auto_train(payload: AutoTrainRequest):
    """Run N simulations in background using ML-driven auto mode.

    This trains both Red and Blue teams simultaneously.
    """
    def _run_training():
        for i in range(payload.episodes):
            try:
                request = SimulationRunRequest(
                    simulation_type=SimulationType.auto,
                    difficulty=payload.difficulty,
                    observation_window_seconds=payload.observation_window_seconds,
                    queue_if_busy=True,
                )
                engine.run(request)
            except Exception as e:
                print(f"Auto-train episode {i+1} failed: {e}")

    thread = threading.Thread(target=_run_training, daemon=True)
    thread.start()

    return {
        "status": "started",
        "episodes": payload.episodes,
        "difficulty": payload.difficulty,
        "message": f"Auto-training started: {payload.episodes} episodes in background",
    }


@router.post("/simulate/reset-learning")
def reset_learning():
    """Wipe all Red/Blue Team learned data and start fresh."""
    engine.feedback_loop.reset_all()
    return {
        "status": "success",
        "message": "All learning data reset. Red and Blue teams will start fresh.",
    }
