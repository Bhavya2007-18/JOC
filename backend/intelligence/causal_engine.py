"""
Causal Graph Engine — Phase 2, JOC Sentinel
-------------------------------------------
Identifies root cause chains rather than just reporting symptoms.
Tracks temporal relationships between high-resource processes and 
system-wide CPU/RAM spikes to build a directed influence graph.

Usage (one call per monitor cycle):
    causal = CausalEngine()
    causal.ingest_snapshot(cpu=85.0, ram=60.0, processes=[...], cpu_z=2.5, ram_z=0.8)
    # → graph gets updated
    
    report = causal.get_root_cause()
    # → {"root_cause": "chrome.exe", "chain": ["chrome.exe", "CPU_SPIKE"], ...}
"""

import time
from collections import deque
from typing import Dict, List, Optional, Any


class CausalEngine:
    """
    Constructs a temporal causal graph by linking recent process observations
    to subsequent system resource spikes.
    """

    # Time window (in seconds) to look backward for causes when a spike occurs
    _TEMPORAL_WINDOW = 15.0
    
    # The absolute z-score threshold required to register a system-wide "spike" event
    _Z_SPIKE_THRESHOLD = 2.0
    
    def __init__(self) -> None:
        # Event log: ordered sequence of events for temporal linking
        self.event_log: deque = deque(maxlen=500)
        
        # Directed graph: edge_weights["source_node"]["target_node"] = score
        self.edge_weights: Dict[str, Dict[str, float]] = {}

    # ------------------------------------------------------------------ #
    #  Core Update Workflow                                                #
    # ------------------------------------------------------------------ #

    def ingest_snapshot(
        self, 
        cpu: float, 
        ram: float, 
        processes: List[Dict[str, Any]], 
        cpu_z: Optional[float], 
        ram_z: Optional[float]
    ) -> None:
        """
        Processes a single monitoring cycle snapshot.
        1. Emits events for top processes.
        2. Emits events for system spikes (if z-scores are high).
        3. Attempts to build causal links if a spike was precisely detected.
        """
        now = time.monotonic()
        
        # 1. Log process load events (top consumers)
        for p in processes:
            name = p.get("name", "unknown")
            p_cpu = p.get("cpu_percent", 0.0)
            p_ram = p.get("memory_percent", 0.0)
            
            if p_cpu > 5.0 or p_ram > 5.0:
                self._record_event(now, "PROCESS", name, {"cpu": p_cpu, "ram": p_ram})

        # 2. Detect & link CPU spike
        if cpu_z is not None and abs(cpu_z) > self._Z_SPIKE_THRESHOLD:
            self._record_event(now, "RESOURCE_SPIKE", "CPU_SPIKE", {"magnitude": cpu, "z_score": cpu_z})
            self._link_causes(now, "CPU_SPIKE")

        # 3. Detect & link RAM spike
        if ram_z is not None and abs(ram_z) > self._Z_SPIKE_THRESHOLD:
            self._record_event(now, "RESOURCE_SPIKE", "RAM_SPIKE", {"magnitude": ram, "z_score": ram_z})
            self._link_causes(now, "RAM_SPIKE")
            
        # Optional: Prune old edges to allow graph to decay dynamically over long runtimes
        self._decay_graph()

    def emit_event(
        self,
        event_type: str,
        node_id: str,
        data: Optional[Dict[str, Any]] = None,
        link_to: Optional[List[str]] = None,
    ) -> None:
        """
        Public hook for non-core pipeline events (e.g., thermal spikes).
        Allows external engines to contribute causal nodes and optional
        directed links into the graph.
        """
        now = time.monotonic()
        payload = data or {}
        self._record_event(now, event_type, node_id, payload)
        for target in (link_to or []):
            self._add_or_update_edge(node_id, target, 0.6)

    def _record_event(self, timestamp: float, event_type: str, node_id: str, data: Dict[str, Any]) -> None:
        """Appends a timestamped event to the rolling log."""
        self.event_log.append({
            "timestamp": timestamp,
            "type": event_type,
            "node_id": node_id,
            "data": data
        })

    # ------------------------------------------------------------------ #
    #  Causal Linking (Temporal Analysis)                                  #
    # ------------------------------------------------------------------ #

    def _link_causes(self, current_time: float, target_spike: str) -> None:
        """
        When a spike occurs, look back in the event log (within the temporal window)
        and establish edges from processes to this spike.
        """
        # We need to look backwards through the deque
        # Deque is ordered oldest (left) to newest (right)
        log_list = list(self.event_log)
        
        for event in reversed(log_list):
            time_diff = current_time - event["timestamp"]
            
            # If we've gone too far back, stop looking
            if time_diff > self._TEMPORAL_WINDOW:
                break
                
            # Only consider PROCESS events as causes
            if event["type"] == "PROCESS":
                source_node = event["node_id"]
                process_data = event["data"]
                
                # Calculate linkage weight
                # Closer in time = stronger link
                time_weight = 1.0 - (time_diff / self._TEMPORAL_WINDOW)
                
                # Higher resource usage = stronger link
                # Normalize typical high usage to ~1.0
                if target_spike == "CPU_SPIKE":
                    mag_weight = min(process_data.get("cpu", 0.0) / 30.0, 1.0)
                else: # RAM_SPIKE
                    mag_weight = min(process_data.get("ram", 0.0) / 20.0, 1.0)
                    
                # Combined weight (favoring temporal proximity slightly)
                link_weight = (0.6 * time_weight) + (0.4 * mag_weight)
                
                # Only add meaningful links
                if link_weight > 0.1:
                    self._add_or_update_edge(source_node, target_spike, link_weight)

    def _add_or_update_edge(self, source: str, target: str, new_weight: float) -> None:
        """Adds a directed edge, using EMA to update existing weights."""
        if source not in self.edge_weights:
            self.edge_weights[source] = {}
        
        if target not in self.edge_weights[source]:
            self.edge_weights[source][target] = new_weight
        else:
            # Exponential Moving Average for weight stability
            current = self.edge_weights[source][target]
            self.edge_weights[source][target] = (0.3 * new_weight) + (0.7 * current)

    def _decay_graph(self) -> None:
        """Periodically degrades weights so old causal links don't persist forever."""
        # Called every cycle, but applies a very gentle decay
        decay_factor = 0.98
        threshold = 0.05
        
        to_delete = []
        for src, targets in self.edge_weights.items():
            for tgt, weight in list(targets.items()):
                new_w = weight * decay_factor
                if new_w < threshold:
                    del targets[tgt]
                else:
                    targets[tgt] = new_w
            
            if not targets:
                to_delete.append(src)
                
        for src in to_delete:
            del self.edge_weights[src]

    # ------------------------------------------------------------------ #
    #  Query / Traversal API                                               #
    # ------------------------------------------------------------------ #

    def get_root_cause(self) -> Dict[str, Any]:
        """
        Determines the primary root cause of current system stress by finding
        the node with the highest out-degree weight total.
        
        Returns:
            {
                "root_cause": str | None,
                "chain": list[str],
                "influence_score": float,
                "all_scores": dict[str, float]
            }
        """
        if not self.edge_weights:
            return {
                "root_cause": None,
                "chain": [],
                "influence_score": 0.0,
                "all_scores": {}
            }
            
        # Sum outgoing weights for each potential source process
        influence_scores = {}
        for source, targets in self.edge_weights.items():
            # Only consider processes as potential root causes, not intermediate spikes
            if not source.endswith("_SPIKE"):
                total_influence = sum(targets.values())
                influence_scores[source] = total_influence
                
        if not influence_scores:
            return {
                "root_cause": None,
                "chain": [],
                "influence_score": 0.0,
                "all_scores": {}
            }
            
        # Find the highest scoring process
        root_cause = max(influence_scores.items(), key=lambda x: x[1])
        top_process = root_cause[0]
        top_score = root_cause[1]
        
        if top_score < 0.1:
            return {
                "root_cause": None,
                "chain": [],
                "influence_score": 0.0,
                "all_scores": influence_scores
            }
            
        # Trace the chain from this root cause via BFS
        chain = self._trace_chain(top_process)
        
        return {
            "root_cause": top_process,
            "chain": chain,
            "influence_score": round(top_score, 3),
            "all_scores": {k: round(v, 3) for k, v in influence_scores.items()}
        }
        
    def _trace_chain(self, start_node: str) -> List[str]:
        """
        BFS to find the most heavily weighted path from the root cause
        to its ultimate effects.
        """
        chain = [start_node]
        current_node = start_node
        visited = {start_node}
        
        while current_node in self.edge_weights:
            targets = self.edge_weights[current_node]
            if not targets:
                break
                
            # Pick the strongest downstream link that we haven't visited
            unvisited_targets = {k: v for k, v in targets.items() if k not in visited}
            if not unvisited_targets:
                break
                
            best_target = max(unvisited_targets.items(), key=lambda x: x[1])[0]
            chain.append(best_target)
            visited.add(best_target)
            current_node = best_target
            
        return chain
