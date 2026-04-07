from collections import deque
from typing import List

from intelligence.models import SystemSnapshot


class StateManager:
    def __init__(self, max_history: int = 50):
        self.history = deque(maxlen=max_history)

    def add_snapshot(self, snapshot: SystemSnapshot):
        self.history.append(snapshot)

    def get_recent(self, n: int = 5) -> List[SystemSnapshot]:
        return list(self.history)[-n:]

    def get_all(self) -> List[SystemSnapshot]:
        return list(self.history)

    def has_enough_data(self, n: int = 3) -> bool:
        return len(self.history) >= n