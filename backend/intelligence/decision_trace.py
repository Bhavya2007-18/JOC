from dataclasses import dataclass, asdict
from typing import List, Dict

@dataclass
class DecisionTrace:
    timestamp: float
    pattern_state: str              # "cpu_spike/single/critical"
    engine_recommendation: str      # What static engine decided
    memory_recommendation: str      # What cognitive memory decided
    final_decision: str             # The winner
    override_reason: str            # "confidence > 0.6" | "no_memory_match" | "static_only"
    confidence: float
    action_type: str
    
    def to_dict(self):
        return asdict(self)

class DecisionTraceLog:
    _instance = None
    
    def __init__(self):
        self._traces: List[DecisionTrace] = []
        self.MAX = 200

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def record(self, trace: DecisionTrace):
        self._traces.append(trace)
        if len(self._traces) > self.MAX:
            self._traces.pop(0)

    def get_recent(self, n: int = 50) -> List[Dict]:
        return [t.to_dict() for t in self._traces[-n:]]
        
    def clear(self):
        self._traces = []
