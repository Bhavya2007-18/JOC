from typing import List

from fastapi import APIRouter

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


router = APIRouter(prefix="/system", tags=["system"])


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

