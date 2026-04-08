from fastapi import APIRouter, HTTPException

from models.simulation_models import (
    SimulationHistoryResponse,
    SimulationReport,
    SimulationRunRequest,
    SimulationRunResponse,
    SimulationStopRequest,
)
from services.orchestration import IntegrityEngine


router = APIRouter(tags=["simulation"])
engine = IntegrityEngine()


@router.post("/simulate/run", response_model=SimulationRunResponse)
def run_simulation(payload: SimulationRunRequest) -> SimulationRunResponse:
    return engine.run(payload)


@router.get("/simulation/{simulation_id}", response_model=SimulationReport)
def get_simulation_report(simulation_id: str) -> SimulationReport:
    report = engine.get_report(simulation_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Simulation report not found")
    return report


@router.get("/simulation/history", response_model=SimulationHistoryResponse)
def get_simulation_history() -> SimulationHistoryResponse:
    return SimulationHistoryResponse(reports=engine.get_history())


@router.post("/simulate/stop")
def stop_simulation(payload: SimulationStopRequest):
    return engine.stop(payload.reason)

