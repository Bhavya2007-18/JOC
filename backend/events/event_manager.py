import asyncio
import uuid
from datetime import datetime, timezone
from typing import List, Callable, Dict, Any, Awaitable
from collections import deque
from pydantic import BaseModel, Field

class Event(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    type: str  # red_action | blue_action | system
    action: str
    source: str
    impact: Dict[str, float] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class EventManager:
    def __init__(self):
        # Newest events always appended to the left for easy retrieval
        self._queue = deque(maxlen=500)
        self._subscribers: List[Callable[[Event], Awaitable[None]]] = []

    async def log_event(self, event: Event) -> None:
        self._queue.appendleft(event)
        
        # Notify subscribers concurrently
        if getattr(self, "_subscribers", []):
            tasks = [sub(event) for sub in self._subscribers]
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

    def get_events(self, limit: int = 100) -> List[Event]:
        # Return newest events up to `limit`
        q_list = list(self._queue)
        return q_list[:limit]

    def subscribe(self, callback: Callable[[Event], Awaitable[None]]) -> None:
        if hasattr(self, "_subscribers") and callback not in self._subscribers:
            self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[Event], Awaitable[None]]) -> None:
        if hasattr(self, "_subscribers") and callback in self._subscribers:
            self._subscribers.remove(callback)

# Singleton
_event_manager_instance = EventManager()

def get_event_manager() -> EventManager:
    return _event_manager_instance
