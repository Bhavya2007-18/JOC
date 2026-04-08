from __future__ import annotations

import threading
from collections import deque
from typing import Deque, List, Optional

from models.simulation_models import SimulationQueueItem


class SimulationScheduler:
    """Single-run scheduler with queue support for future scaling."""

    def __init__(self) -> None:
        self._queue: Deque[SimulationQueueItem] = deque()
        self._lock = threading.Lock()

    def enqueue(self, item: SimulationQueueItem) -> None:
        with self._lock:
            self._queue.append(item)

    def dequeue(self) -> Optional[SimulationQueueItem]:
        with self._lock:
            if not self._queue:
                return None
            return self._queue.popleft()

    def snapshot(self) -> List[SimulationQueueItem]:
        with self._lock:
            return list(self._queue)
