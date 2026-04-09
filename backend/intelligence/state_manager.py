from collections import deque
import threading
from typing import List

from intelligence.models import SystemSnapshot


class StateManager:
    def __init__(self, max_history: int = 50):
        self.history = deque(maxlen=max_history)
        self._lock = threading.RLock()

    def add_snapshot(self, snapshot: SystemSnapshot):
        with self._lock:
            self.history.append(snapshot)

    def get_recent(self, n: int = 5) -> List[SystemSnapshot]:
        with self._lock:
            return list(self.history)[-n:]

    def get_all(self) -> List[SystemSnapshot]:
        with self._lock:
            return list(self.history)

    def has_enough_data(self, n: int = 3) -> bool:
        with self._lock:
            return len(self.history) >= n