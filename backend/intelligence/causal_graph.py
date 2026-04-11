from typing import List, Dict, Any
from .models import SystemSnapshot

class CausalGraphEngine:
    """
    Generates a directed graph of system influences using correlation
    and domain-knowledge structural priors.
    """
    def __init__(self):
        self.history = []

    def observe(self, snapshot: SystemSnapshot):
        self.history.append(snapshot)
        if len(self.history) > 60:
            self.history.pop(0)

    def generate_graph(self) -> Dict[str, Any]:
        if len(self.history) < 5:
            return {"nodes": [], "edges": [], "root_cause_node": None}

        nodes = []
        edges = []
        latest = self.history[-1]
        
        nodes.extend([
            {"id": "CPU", "type": "resource"},
            {"id": "Memory", "type": "resource"},
            {"id": "Network", "type": "resource"}
        ])

        candidates = latest.top_processes[:5]
        for p in candidates:
            nodes.append({"id": p.name, "type": "process", "pid": p.pid})
            
            if p.cpu_percent > 15:
                edges.append({
                    "from": p.name, "to": "CPU", 
                    "weight": p.cpu_percent / 100.0, 
                    "confidence": 0.85
                })
            if p.memory_percent > 15:
                edges.append({
                    "from": p.name, "to": "Memory", 
                    "weight": p.memory_percent / 100.0,
                    "confidence": 0.90
                })
            if getattr(p, "net_connections", 0) > 50:
                edges.append({
                    "from": p.name, "to": "Network",
                    "weight": min(1.0, getattr(p, "net_connections", 0) / 200.0),
                    "confidence": 0.8
                })

        root_cause = None
        max_influence = 0
        for p in candidates:
            influence = sum(e["weight"] for e in edges if e["from"] == p.name)
            if influence > max_influence:
                max_influence = influence
                root_cause = p.name

        return {
            "nodes": nodes,
            "edges": edges,
            "root_cause_node": root_cause
        }
