from __future__ import annotations

import json
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from core.config import ValidationConfig, get_validation_config
from models.simulation_models import (
    EvaluationData,
    MetricsData,
    SimulationQueueItem,
    SimulationReport,
    SimulationRunRequest,
    SimulationRunResponse,
    SimulationState,
    SimulationType,
    TimelineData,
    Verdict,
)
from services.blue_team import IntelligenceBridge, ResponseAnalyzer, ScoringEngine
from services.intelligence import append_log_entry
from services.orchestration.simulation_scheduler import SimulationScheduler
from services.orchestration.state_manager import RuntimeControl, RuntimeStateManager, SafetyGuard
from services.red_team import (
    BaseSimulation,
    CpuSpikeSimulation,
    MemoryStressSimulation,
    NetworkBurstSimulation,
    ProcessSimulation,
)
from services.system_monitor import get_cpu_stats, get_memory_stats, get_top_processes
from intelligence.config import DRY_RUN
from services.red_team.attack_strategist import AttackStrategist
from services.red_team.multi_vector import AttackPlan
from services.orchestration.feedback_loop import FeedbackLoop
from intelligence.monitor_loop import MonitorLoop
from utils.execution_context import ExecutionContext
from utils.logger import get_logger


logger = get_logger("validation.integrity_engine")


class IntegrityEngine:
    def __init__(
        self,
        config: Optional[ValidationConfig] = None,
        bridge: Optional[IntelligenceBridge] = None,
        analyzer: Optional[ResponseAnalyzer] = None,
        scheduler: Optional[SimulationScheduler] = None,
    ) -> None:
        self.config = config or get_validation_config()
        self.bridge = bridge or IntelligenceBridge()
        self.analyzer = analyzer or ResponseAnalyzer()
        self.scorer = ScoringEngine(self.config)
        self.scheduler = scheduler or SimulationScheduler()
        self.state_manager = RuntimeStateManager()
        self.runtime_control = RuntimeControl()
        self.safety_guard = SafetyGuard(self.config, self.runtime_control)

        self._run_lock = threading.Lock()
        self._history: List[SimulationReport] = []

        # ML-driven components
        self.strategist = AttackStrategist()
        self.feedback_loop = FeedbackLoop()
        self._current_attack_plan: Optional[AttackPlan] = None

    def run(self, request: SimulationRunRequest) -> SimulationRunResponse:
        if self._run_lock.locked():
            if request.queue_if_busy:
                queued_id = str(uuid.uuid4())
                queued_item = SimulationQueueItem(
                    simulation_id=queued_id,
                    simulation_type=request.simulation_type,
                    parameters=request.parameters,
                    dry_run=request.dry_run,
                    observation_window_seconds=request.observation_window_seconds,
                    correlation_id=queued_id,
                )
                self.scheduler.enqueue(queued_item)
                self._log_event(
                    correlation_id=queued_id,
                    event="queued",
                    payload={"simulation_type": request.simulation_type.value},
                )
                return SimulationRunResponse(
                    queued=True,
                    report=None,
                    simulation_id=queued_id,
                    message="Simulation queued; another run is in progress",
                )
            return SimulationRunResponse(
                queued=False,
                report=None,
                simulation_id="",
                message="Simulation engine busy",
            )

        with self._run_lock:
            self.runtime_control.clear_kill_switch()
            report = self._execute_request(request)
            self._history.append(report)

        self._run_next_queued()

        return SimulationRunResponse(
            queued=False,
            report=report,
            simulation_id=report.simulation_id,
            message="Simulation completed",
        )

    def stop(self, reason: str) -> Dict[str, Any]:
        self.runtime_control.trigger_kill_switch()
        self._log_event(correlation_id="global", event="stop_requested", payload={"reason": reason})
        return {"success": True, "message": "Emergency stop requested", "reason": reason}

    def get_report(self, simulation_id: str) -> Optional[SimulationReport]:
        for report in reversed(self._history):
            if report.simulation_id == simulation_id:
                return report
        return None

    def get_history(self) -> List[SimulationReport]:
        return list(self._history)

    def _run_next_queued(self) -> None:
        queued = self.scheduler.dequeue()
        if queued is None:
            return

        synthetic_request = SimulationRunRequest(
            simulation_type=queued.simulation_type,
            parameters=queued.parameters,
            dry_run=queued.dry_run,
            observation_window_seconds=queued.observation_window_seconds,
            chain=[],
            queue_if_busy=False,
        )
        with self._run_lock:
            self.runtime_control.clear_kill_switch()
            report = self._execute_request(synthetic_request, fixed_ids=(queued.simulation_id, queued.correlation_id))
            self._history.append(report)

    def _execute_request(
        self,
        request: SimulationRunRequest,
        fixed_ids: Optional[Tuple[str, str]] = None,
    ) -> SimulationReport:
        simulation_id = fixed_ids[0] if fixed_ids else str(uuid.uuid4())
        correlation_id = fixed_ids[1] if fixed_ids else str(uuid.uuid4())
        context = ExecutionContext.from_request(dry_run=request.dry_run)
        start = time.time()

        # ── ML Attack Selection ───────────────────────────────
        attack_plan: Optional[AttackPlan] = None
        difficulty = getattr(request, "difficulty", "auto")

        if request.simulation_type == SimulationType.auto:
            # Let the strategist choose the attack
            attack_plan = self.strategist.select_attack(difficulty=difficulty)
            self._current_attack_plan = attack_plan
            requested_types = [
                SimulationType(v.simulation_type) for v in attack_plan.vectors
            ]
            # Use intensity-controlled parameters from the plan
            if attack_plan.vectors:
                request.parameters = attack_plan.vectors[0].parameters
            logger.info(
                "ML-selected attack: %s (plan=%s, difficulty=%s, history=%s)",
                attack_plan.strategy_name,
                attack_plan.plan_id,
                attack_plan.difficulty,
                attack_plan.history_based,
            )
        else:
            requested_types = [request.simulation_type]
            requested_types.extend(request.chain)

        if request.replay_simulation_id:
            previous = self.get_report(request.replay_simulation_id)
            if previous is not None:
                requested_types = [SimulationType(previous.simulation_type)]
                request.parameters = previous.parameters

        timeline = TimelineData(start=start, transitions=[])
        observations: List[Dict[str, Any]] = []

        try:
            self._transition(SimulationState.initializing, correlation_id, "Initializing simulation run", timeline)
            self._assert_not_timeout(start)

            # Nudge the monitor to collect fresh data immediately
            monitor = MonitorLoop.get_instance()
            if monitor:
                monitor.nudge()

            for simulation_type in requested_types:
                simulation = self._build_simulation(
                    simulation_type=simulation_type,
                    simulation_id=simulation_id,
                    correlation_id=correlation_id,
                    parameters=request.parameters,
                    context=context,
                )
                self._run_single_simulation(simulation, observations, start, timeline)

            self._transition(SimulationState.observing, correlation_id, "Observation window started", timeline)
            observation_window = request.observation_window_seconds or self.config.observation_window_seconds
            self._observe(observation_window=observation_window, start_time=start)

            intelligence = self.bridge.fetch_intelligence_outputs(window_seconds=observation_window)
            timeline.anomaly_detected_at = intelligence.get("anomaly_detected_at")
            timeline.decision_made_at = intelligence.get("decision_made_at")

            self._transition(SimulationState.analyzing, correlation_id, "Analyzing responses", timeline)

            # Use primary type for analysis (first vector if multi-vector)
            primary_type = attack_plan.primary_type() if attack_plan else request.simulation_type.value

            analysis = self.analyzer.analyze(
                simulation_type=primary_type,
                anomalies=intelligence.get("anomalies", []),
                decisions=intelligence.get("decisions", []),
            )

            completed = time.time()
            timeline.completed_at = completed
            response_time = completed - start
            detection_delay = (
                (timeline.anomaly_detected_at - start)
                if timeline.anomaly_detected_at is not None
                else response_time
            )

            evaluation_raw = self.scorer.score(
                analysis=analysis,
                response_time=response_time,
                detection_delay=detection_delay,
            )

            metrics = MetricsData(response_time=response_time, detection_delay=detection_delay)
            evaluation = EvaluationData(
                detection_score=evaluation_raw["detection_score"],
                decision_score=evaluation_raw["decision_score"],
                time_score=evaluation_raw["time_score"],
                total_score=evaluation_raw["total_score"],
                false_negatives=evaluation_raw["false_negatives"],
                false_positives=evaluation_raw["false_positives"],
                verdict=Verdict(evaluation_raw["verdict"]),
            )

            # ── Feedback Loop ─────────────────────────────────
            feedback_data = None
            try:
                feedback_result = self.feedback_loop.process_simulation_result(
                    report=SimulationReport(
                        simulation_id=simulation_id,
                        simulation_type=primary_type,
                        parameters=request.parameters,
                        timeline=timeline,
                        metrics=metrics,
                        evaluation=evaluation,
                        observations=observations + intelligence.get("anomalies", []) + intelligence.get("decisions", []),
                        logs_ref=self._resolve_log_ref(),
                        state=SimulationState.completed,
                        correlation_id=correlation_id,
                    ),
                    attack_plan=attack_plan,
                )
                feedback_data = {
                    "red_reward": feedback_result.red_reward,
                    "blue_detected": feedback_result.blue_detected,
                    "detection_latency": feedback_result.detection_latency,
                    "red_evolution": feedback_result.red_evolution,
                    "blue_evolution": feedback_result.blue_evolution,
                }
            except Exception as fb_err:
                logger.error("Feedback loop error: %s", fb_err)

            self._transition(SimulationState.completed, correlation_id, "Simulation completed", timeline)
            report = SimulationReport(
                simulation_id=simulation_id,
                simulation_type=primary_type,
                parameters=request.parameters,
                timeline=timeline,
                metrics=metrics,
                evaluation=evaluation,
                observations=observations + intelligence.get("anomalies", []) + intelligence.get("decisions", []),
                logs_ref=self._resolve_log_ref(),
                state=SimulationState.completed,
                correlation_id=correlation_id,
                feedback=feedback_data,
                attack_plan=attack_plan.to_dict() if attack_plan else None,
            )
            self._persist_report(report)
            return report

        except Exception as exc:
            self._transition(SimulationState.failed, correlation_id, f"Simulation failed: {exc}", timeline)
            failure_time = time.time()
            timeline.completed_at = failure_time

            failed_report = SimulationReport(
                simulation_id=simulation_id,
                simulation_type=request.simulation_type.value,
                parameters=request.parameters,
                timeline=timeline,
                metrics=MetricsData(response_time=failure_time - start, detection_delay=0.0),
                evaluation=EvaluationData(
                    detection_score=0,
                    decision_score=0,
                    time_score=0,
                    total_score=0,
                    false_negatives=1,
                    false_positives=0,
                    verdict=Verdict.failed,
                ),
                observations=observations,
                logs_ref=self._resolve_log_ref(),
                state=SimulationState.failed,
                correlation_id=correlation_id,
            )
            self._persist_report(failed_report)
            return failed_report

        finally:
            self.runtime_control.clear_kill_switch()
            self._transition(SimulationState.idle, correlation_id, "Engine returned to IDLE", timeline)

    def _build_simulation(
        self,
        simulation_type: SimulationType,
        simulation_id: str,
        correlation_id: str,
        parameters: Dict[str, Any],
        context: ExecutionContext,
    ) -> BaseSimulation:
        mapping = {
            SimulationType.cpu_spike: CpuSpikeSimulation,
            SimulationType.memory_stress: MemoryStressSimulation,
            SimulationType.process_simulator: ProcessSimulation,
            SimulationType.network_burst: NetworkBurstSimulation,
        }
        simulation_class = mapping[simulation_type]
        return simulation_class(
            simulation_id=simulation_id,
            correlation_id=correlation_id,
            parameters=parameters,
            safety_guard=self.safety_guard,
            context=context,
        )

    def _run_single_simulation(
        self,
        simulation: BaseSimulation,
        observations: List[Dict[str, Any]],
        start_time: float,
        timeline: TimelineData,
    ) -> None:
        self._transition(
            SimulationState.running,
            simulation.correlation_id,
            f"Running {simulation.metadata().get('type')}",
            timeline,
        )
        self._assert_not_timeout(start_time)
        simulation.setup()
        try:
            result = simulation.execute()
            observations.append({"metadata": simulation.metadata(), "result": result, "timestamp": time.time()})
        finally:
            simulation.cleanup()

    def _observe(self, observation_window: int, start_time: float) -> None:
        # Nudge again at the start of observation to capture post-attack state
        monitor = MonitorLoop.get_instance()
        if monitor:
            monitor.nudge()

        observe_start = time.time()
        while time.time() - observe_start < observation_window:
            self._assert_not_timeout(start_time)
            self.safety_guard.raise_if_abort_requested()

            cpu = get_cpu_stats()
            memory = get_memory_stats()
            processes = get_top_processes(limit=5)
            append_log_entry(
                cpu_percent=float(cpu.get("usage_percent", 0.0)),
                memory_percent=float(memory.get("percent", 0.0)),
                top_processes=processes,
            )
            time.sleep(1.0)

    def _assert_not_timeout(self, start_time: float) -> None:
        elapsed = time.time() - start_time
        if elapsed > self.config.simulation_timeout_seconds:
            raise TimeoutError("Simulation timeout exceeded")

    def _resolve_log_ref(self) -> str:
        return str(self._logs_path())

    def _persist_report(self, report: SimulationReport) -> None:
        self._log_event(
            correlation_id=report.correlation_id,
            event="report_persisted",
            payload=report.model_dump(),
        )

    def _transition(
        self,
        state: SimulationState,
        correlation_id: str,
        note: str,
        timeline: TimelineData,
    ) -> None:
        self.state_manager.transition(state, correlation_id=correlation_id, note=note)
        transition = {
            "timestamp": time.time(),
            "state": state.value,
            "note": note,
        }
        timeline.transitions.append(transition)
        self._log_event(correlation_id=correlation_id, event="state_transition", payload=transition)

    def _logs_path(self) -> Path:
        backend_root = Path(__file__).resolve().parents[2]
        configured = Path(self.config.log_file_path)
        path = configured if configured.is_absolute() else backend_root / configured
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text("[]", encoding="utf-8")
        return path

    def _log_event(self, correlation_id: str, event: str, payload: Dict[str, Any]) -> None:
        path = self._logs_path()
        try:
            raw = path.read_text(encoding="utf-8")
            data = json.loads(raw)
            if not isinstance(data, list):
                data = []
        except (OSError, json.JSONDecodeError):
            data = []

        data.append(
            {
                "timestamp": time.time(),
                "correlation_id": correlation_id,
                "event": event,
                "payload": payload,
            }
        )
        try:
            path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except OSError:
            logger.error("Failed to write simulation log event")
