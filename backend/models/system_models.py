from typing import List, Optional

from pydantic import BaseModel


class LoadAverage(BaseModel):
    """Represents system load average over common time windows."""

    one_min: Optional[float]
    five_min: Optional[float]
    fifteen_min: Optional[float]


class CpuStats(BaseModel):
    """CPU usage statistics."""

    usage_percent: float
    per_core_usage: List[float]
    load_average: Optional[LoadAverage]


class MemoryStats(BaseModel):
    """Memory usage statistics."""

    total: int
    used: int
    available: int
    percent: float


class DiskStats(BaseModel):
    """Aggregated disk usage statistics."""

    total: int
    used: int
    free: int
    percent: float


class NetworkStats(BaseModel):
    """Network I/O statistics."""

    bytes_sent: int
    bytes_received: int


class ProcessInfoModel(BaseModel):
    """Basic information about a running process."""

    pid: int
    name: str
    cpu_percent: float
    memory_percent: float


class SystemStatsResponse(BaseModel):
    """Combined system statistics for dashboard consumption."""

    cpu: CpuStats
    memory: MemoryStats
    disk: DiskStats
    network: NetworkStats


class ProcessesResponse(BaseModel):
    """Response model for top processes endpoint."""

    top_processes: List[ProcessInfoModel]

