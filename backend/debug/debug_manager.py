import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Deque
from collections import deque
from pydantic import BaseModel, Field

class DebugEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    component: str  # "red_agent" | "blue_agent" | "engine" | "system"
    severity: str = "info"  # "info" | "warning" | "critical"
    message: str
    data: Dict[str, Any] = Field(default_factory=dict)

class DebugManager:
    def __init__(self):
        self._enabled: bool = True
        self._queue: Deque[DebugEntry] = deque(maxlen=500)
        self._subscribers = []

    async def log(self, component: str, message: str, data: dict = None, severity: str = "info") -> None:
        if not self._enabled:
            return

        entry = DebugEntry(
            component=component,
            message=message,
            severity=severity,
            data=data or {}
        )
        self._queue.appendleft(entry)
        
        # Notify subscribers
        for sub in getattr(self, "_subscribers", []):
            try:
                await sub(entry)
            except Exception as e:
                print(f"Debug subscriber error: {e}")

    def get_logs(self, limit: int = 100, component: str = None) -> List[DebugEntry]:
        logs = list(self._queue)
        if component and component != "all":
            logs = [log for log in logs if log.component == component]
        return logs[:limit]

    def enable(self) -> None:
        self._enabled = True

    def disable(self) -> None:
        self._enabled = False

    def is_enabled(self) -> bool:
        return self._enabled

    def clear(self) -> None:
        self._queue.clear()

    def subscribe(self, callback) -> None:
        if callback not in self._subscribers:
            self._subscribers.append(callback)

    def unsubscribe(self, callback) -> None:
        if callback in self._subscribers:
            self._subscribers.remove(callback)

# Singleton
_debug_manager_instance = DebugManager()

def get_debug_manager() -> DebugManager:
    return _debug_manager_instance
