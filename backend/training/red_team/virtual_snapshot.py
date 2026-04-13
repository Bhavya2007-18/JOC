from dataclasses import dataclass
from typing import List
import time


@dataclass
class VirtualProcessInfo:
    name: str
    pid: int
    cpu_percent: float
    memory_percent: float

    @property
    def memory_mb(self) -> float:
        # IntelligenceEngine expects memory_mb for memory-heavy process ranking.
        return float(self.memory_percent) * 100.0

    @property
    def create_time(self) -> float:
        # Keep startup heuristics stable for virtual snapshots.
        return time.time() - 600.0

    @property
    def io_read_bytes(self) -> int:
        return 0

    @property
    def io_write_bytes(self) -> int:
        return 0


@dataclass
class VirtualSnapshot:
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    process_count: int
    top_processes: List[VirtualProcessInfo]

    @property
    def disk_heavy_processes(self) -> List[VirtualProcessInfo]:
        # Reuse top_processes for compatibility with disk-related engine branches.
        return list(self.top_processes)

    @property
    def boot_time(self) -> float:
        return time.time() - 3600.0

    @property
    def services(self) -> List[dict]:
        return []

    @property
    def timestamp(self) -> float:
        return time.time()


def create_mock_snapshot() -> VirtualSnapshot:
    processes = [
        VirtualProcessInfo("chrome.exe", 1234, 65.0, 25.0),
        VirtualProcessInfo("code.exe", 2345, 10.0, 10.0),
        VirtualProcessInfo("system.exe", 1, 5.0, 5.0),
    ]

    return VirtualSnapshot(
        cpu_percent=85.0,
        memory_percent=70.0,
        disk_percent=40.0,
        process_count=120,
        top_processes=processes,
    )
