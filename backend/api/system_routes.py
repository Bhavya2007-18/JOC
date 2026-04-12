from typing import List, Literal

from fastapi import APIRouter
from pydantic import BaseModel

from models.system_models import (
    CpuStats,
    DiskStats,
    MemoryStats,
    NetworkStats,
    ProcessesResponse,
    ProcessInfoModel,
    SystemStatsResponse,
    LoadAverage,
)
from services.system_monitor import (
    get_cpu_stats,
    get_disk_stats,
    get_memory_stats,
    get_network_stats,
    get_top_processes,
)
from services.optimizer.power_mode import apply_system_mode, get_current_mode
from storage.db import get_timeline_events


router = APIRouter(prefix="/system", tags=["system"])


class SetModeRequest(BaseModel):
    mode: Literal["chill", "smart", "beast"]


@router.get("/stats", response_model=SystemStatsResponse)
def get_system_stats() -> SystemStatsResponse:
    """Return current CPU, memory, disk, and network statistics."""
    cpu_data = get_cpu_stats()
    memory_data = get_memory_stats()
    disk_data = get_disk_stats()
    network_data = get_network_stats()

    load_average_data = cpu_data.get("load_average")
    load_average_model = None
    if isinstance(load_average_data, dict):
        load_average_model = LoadAverage(**load_average_data)

    cpu_model = CpuStats(
        usage_percent=cpu_data["usage_percent"],
        per_core_usage=cpu_data["per_core_usage"],
        load_average=load_average_model,
    )
    memory_model = MemoryStats(**memory_data)
    disk_model = DiskStats(**disk_data)
    network_model = NetworkStats(**network_data)

    return SystemStatsResponse(
        cpu=cpu_model,
        memory=memory_model,
        disk=disk_model,
        network=network_model,
    )


@router.get("/processes", response_model=ProcessesResponse)
def get_top_processes_route(limit: int = 10) -> ProcessesResponse:
    """Return the top processes sorted by CPU usage."""
    raw_processes = get_top_processes(limit=limit)
    processes: List[ProcessInfoModel] = [ProcessInfoModel(**process) for process in raw_processes]
    return ProcessesResponse(top_processes=processes)

@router.get("/timeline")
def get_timeline(limit: int = 50):
    """Return historical system timeline events."""
    events = get_timeline_events(limit=limit)
    return {"events": events}


@router.post("/mode")
def set_system_mode(payload: SetModeRequest):
    """Switch the system operating mode (chill / smart / beast)."""
    result = apply_system_mode(payload.mode)
    return result


@router.get("/mode")
def get_system_mode():
    """Return the current system operating mode."""
    return {"mode": get_current_mode()}
