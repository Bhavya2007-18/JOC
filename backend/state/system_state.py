import asyncio
from datetime import datetime, timezone
from typing import Optional


class SystemState:
    def __init__(self):
        self.mode: str = "SMART"  # CHILL | SMART | BEAST
        self.cpu_usage: float = 0.0
        self.ram_usage: float = 0.0
        self.threat_level: int = 0
        self.simulation_status: str = "stopped"  # running | paused | stopped
        self.timestamp: str = datetime.now(timezone.utc).isoformat()
        self._lock = asyncio.Lock()

    async def update(self, partial_data: dict):
        async with self._lock:
            for key, value in partial_data.items():
                if hasattr(self, key) and key != "_lock":
                    setattr(self, key, value)
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self):
        # We don't acquire lock here to allow fast non-blocking reads.
        # This is generally safe for atomic python fields
        return {
            "mode": self.mode,
            "cpu_usage": self.cpu_usage,
            "ram_usage": self.ram_usage,
            "threat_level": self.threat_level,
            "simulation_status": self.simulation_status,
            "timestamp": self.timestamp
        }


# Singleton instance
_state_instance = SystemState()


def get_state() -> SystemState:
    """Get the global state singleton instance."""
    return _state_instance
