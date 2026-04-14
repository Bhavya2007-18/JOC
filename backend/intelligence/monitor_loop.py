import time
import threading

from intelligence.snapshot_provider import collect_snapshot
from intelligence.engine import IntelligenceEngine
from storage.db import save_snapshot
from utils.logger import get_logger

# Phase 2 Core Engines
from intelligence.baseline_engine import BaselineEngine
from intelligence.threat_engine import ThreatEngine
from intelligence.causal_engine import CausalEngine
from intelligence.predictive_engine import PredictiveEngine
from intelligence.xai_engine import XAIEngine
from intelligence.thermal_engine import ThermalEngine

# Phase 3 Autonomy Layer
from autonomy.orchestrator import AutonomyOrchestrator
from services.optimizer.power_mode import get_current_mode, apply_system_mode

from state.system_state import get_state
import asyncio

logger = get_logger("monitor")

class MonitorLoop:
    _instance = None

    def __init__(self, interval: int = 5):
        self.interval = interval
        self.engine = IntelligenceEngine()
        self._thread = None
        self._running = False
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._stop_event = threading.Event()
        self.latest_snapshot = None
        self.latest_analysis = None
        self._iteration_count = 0
        
        # Instantiate Intelligence Layer
        self.baseline_engine = BaselineEngine(window_size=60)
        self.threat_engine = ThreatEngine()
        self.causal_engine = CausalEngine()
        self.predictive_engine = PredictiveEngine()
        self.xai_engine = XAIEngine()
        self.thermal_engine = ThermalEngine()
        
        # Instantiate Autonomy Layer
        self.autonomy_orchestrator = AutonomyOrchestrator()
        
        self.latest_intelligence = {
            "threat": {},
            "prediction": {},
            "explanation": {},
            "baseline": {}
        }
        self.latest_autonomy_state = {}
        MonitorLoop._instance = self

    @classmethod
    def get_instance(cls):
        return cls._instance

    def start(self):
        with self._lock:
            if self._running:
                return

            self._running = True
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()

    def stop(self):
        with self._lock:
            self._running = False
            self._stop_event.set()

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=self.interval + 1)
        self._thread = None

    def nudge(self):
        """Force an immediate snapshot + analysis cycle (called by simulation engine)."""
        try:
            logger.info("Nudge: forced immediate snapshot")
            snapshot = collect_snapshot()
            save_snapshot(snapshot)
            self.engine.analyze(snapshot)
        except Exception as e:
            logger.error(f"[MonitorLoop Nudge Error] {e}")

    def run(self):
        self._run_loop()

    def _run_loop(self):
        while not self._stop_event.is_set():
            try:
                logger.info("Loop running")

                snapshot = collect_snapshot()
                self.latest_snapshot = snapshot

                # Stage 0: Process Data Extraction
                cpu = snapshot.cpu_percent
                ram = snapshot.memory_percent
                processes = [
                    {"name": p.name, "pid": p.pid, "cpu_percent": p.cpu_percent, "memory_percent": p.memory_percent} 
                    for p in snapshot.top_processes
                ]
                
                # Execute original analysis logic for diagnostic issues
                analysis = self.engine.analyze(snapshot)
                self.latest_analysis = analysis

                # --- Phase 2 Intelligence Pipeline ---
                
                # Stage 1: Baseline
                baseline_data = self.baseline_engine.analyze(cpu, ram)
                cpu_z = baseline_data.get("cpu_z_score")
                ram_z = baseline_data.get("ram_z_score")
                
                # Stage 2: Threat
                threat_data = self.threat_engine.compute(cpu, ram, cpu_z, ram_z)
                
                # Stage 3: Causal
                self.causal_engine.ingest_snapshot(cpu, ram, processes, cpu_z, ram_z)
                causal_data = self.causal_engine.get_root_cause()
                
                # Stage 4: Prediction
                self.predictive_engine.observe(cpu, ram, snapshot.timestamp)
                pred_data = self.predictive_engine.forecast()
                
                # Stage 5: XAI Narrative Generation
                explanation = self.xai_engine.generate(
                    cpu, ram, baseline_data, threat_data, causal_data, pred_data
                )

                # Stage 6: Thermal Intelligence
                thermal_data = self.thermal_engine.update(cpu_usage=cpu, timestamp=snapshot.timestamp)
                if thermal_data.get("velocity") == "spiking":
                    # Hook thermal spikes into causal graph.
                    self.causal_engine.emit_event(
                        event_type="THERMAL",
                        node_id="THERMAL_SPIKE",
                        data={
                            "temperature": thermal_data.get("temperature"),
                            "delta_temp": thermal_data.get("delta_temp"),
                            "state": thermal_data.get("state"),
                            "score": thermal_data.get("score"),
                        },
                        link_to=["CPU_SPIKE", "PROCESS_ACTIVITY"],
                    )
                    # Refresh causal root-cause after thermal event enrichment.
                    causal_data = self.causal_engine.get_root_cause()
                
                # Compile Unified Intelligence Object
                self.latest_intelligence = {
                    "threat": threat_data,
                    "prediction": pred_data,
                    "explanation": explanation,
                    "baseline": baseline_data,
                    "causal_graph": causal_data,
                    "thermal": thermal_data,
                }
                
                # Phase 3: Autonomy Loop
                autonomy_result = self.autonomy_orchestrator.tick(self.latest_intelligence)
                self.latest_autonomy_state = autonomy_result
                
                # Periodic System Mode Enforcement (every 10 ticks / approx 50s)
                self._iteration_count += 1
                if self._iteration_count % 10 == 0:
                    current_mode = get_current_mode()
                    logger.info(f"Enforcing system mode policy: {current_mode.upper()}")
                    apply_system_mode(current_mode, force_live=True, thermal_data=thermal_data)
                
                # Broadcast Threat Score to SystemState directly
                try:
                    # Async task wrapper since monitor is running loop in separate thread
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                         asyncio.run_coroutine_threadsafe(
                             get_state().update({"threat_level": threat_data["threat_score"]}),
                             loop
                         )
                except RuntimeError:
                    # No loop, ignore
                    pass

                save_snapshot(snapshot)
            except Exception as e:
                logger.error(f"[MonitorLoop Error] {e}")

            self._stop_event.wait(self.interval)
