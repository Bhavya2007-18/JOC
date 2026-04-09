"""Feedback loop connecting Red Team and Blue Team learning after each simulation."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from models.simulation_models import SimulationReport
from services.blue_team.adaptive_thresholds import AdaptiveThresholds
from services.blue_team.decision_optimizer import DecisionOptimizer
from services.blue_team.defense_memory import DefenseMemory
from services.blue_team.pattern_recognizer import PatternRecognizer
from services.red_team.attack_strategist import AttackStrategist
from services.red_team.multi_vector import AttackPlan
from utils.logger import get_logger

logger = get_logger("orchestration.feedback_loop")


@dataclass
class FeedbackResult:
    """Result of processing feedback after a simulation."""
    red_reward: float
    blue_detected: bool
    detection_latency: float
    blue_score: int
    red_evolution: Dict[str, Any] = field(default_factory=dict)
    blue_evolution: Dict[str, Any] = field(default_factory=dict)


class FeedbackLoop:
    """The bridge that connects Red and Blue learning after every simulation.

    After each simulation:
    1. Red Team records: was the attack detected? how fast? → Updates Q-table
    2. Blue Team records: was the response effective? → Updates baselines & patterns
    3. Both models improve for the next round
    """

    def __init__(self) -> None:
        self.strategist = AttackStrategist()
        self.defense_memory = DefenseMemory()
        self.thresholds = AdaptiveThresholds(self.defense_memory)
        self.pattern_recognizer = PatternRecognizer(self.defense_memory)
        self.decision_optimizer = DecisionOptimizer(self.defense_memory)

    def process_simulation_result(
        self,
        report: SimulationReport,
        attack_plan: Optional[AttackPlan] = None,
    ) -> FeedbackResult:
        """Process the result of a completed simulation and update both teams.

        Args:
            report: The completed simulation report
            attack_plan: The attack plan used (if ML-driven)
        """
        blue_score = report.evaluation.total_score
        detected = report.evaluation.verdict.value != "failed"
        detection_latency = report.metrics.detection_delay
        response_time = report.metrics.response_time

        # ── Red Team Feedback ─────────────────────────────────
        red_reward = 0.0
        if attack_plan:
            self.strategist.record_outcome(attack_plan, blue_score)
            red_reward = 1.0 - (blue_score / 100.0)

        # ── Blue Team Feedback ────────────────────────────────

        # 1. Update adaptive baselines with pre-attack system state
        #    (use the observation data to feed the EMA)
        for obs in report.observations:
            data = obs.get("data", {}) or obs.get("result", {})
            cpu = float(data.get("cpu_percent", 0.0))
            mem = float(data.get("memory_percent", 0.0))
            if cpu > 0 or mem > 0:
                self.thresholds.update(cpu, mem)

        # 2. Detection tracking
        self.defense_memory.record_detection(detected, detection_latency)

        # 3. Pattern recognition — fingerprint the anomalies
        anomalies = [
            obs for obs in report.observations
            if "type" in obs and obs.get("type") != "state_transition"
        ]
        fingerprint = self.pattern_recognizer.fingerprint(anomalies)

        # Determine best response from the decisions
        decisions = [
            obs for obs in report.observations
            if "decision" in obs
        ]
        best_response = decisions[0].get("decision", "investigate") if decisions else "investigate"

        self.pattern_recognizer.register_pattern(
            fingerprint=fingerprint,
            attack_type=report.simulation_type,
            blue_score=blue_score,
            best_response=best_response,
        )

        # 4. Decision outcome tracking
        effective = blue_score >= 60
        for decision in decisions:
            action = str(decision.get("decision", "investigate"))
            self.decision_optimizer.record_outcome(action, effective)

        # 5. Record Blue Team episode
        self.defense_memory.record_episode({
            "simulation_type": report.simulation_type,
            "blue_score": blue_score,
            "detected": detected,
            "detection_latency": round(detection_latency, 3),
            "response_time": round(response_time, 3),
            "fingerprint": fingerprint,
            "verdict": report.evaluation.verdict.value,
        })

        # ── Build result ──────────────────────────────────────
        result = FeedbackResult(
            red_reward=round(red_reward, 4),
            blue_detected=detected,
            detection_latency=round(detection_latency, 3),
            blue_score=blue_score,
            red_evolution=self.strategist.get_evolution_stats(),
            blue_evolution=self.defense_memory.get_stats(),
        )

        logger.info(
            "Feedback processed: blue_score=%d detected=%s latency=%.2f reward=%.2f",
            blue_score, detected, detection_latency, red_reward,
        )

        return result

    def get_evolution_stats(self) -> Dict[str, Any]:
        """Return combined evolution stats for both teams."""
        red_stats = self.strategist.get_evolution_stats()
        blue_stats = self.defense_memory.get_stats()

        # Calculate improvement trends
        red_win_rates = red_stats.get("win_rates", [])
        blue_latencies = blue_stats.get("recent_latencies", [])

        improving_blue = False
        if len(blue_latencies) >= 4:
            early = sum(blue_latencies[:len(blue_latencies)//2]) / max(1, len(blue_latencies)//2)
            late = sum(blue_latencies[len(blue_latencies)//2:]) / max(1, len(blue_latencies) - len(blue_latencies)//2)
            improving_blue = late < early

        return {
            "red_team": {
                "episodes_completed": red_stats["episodes_completed"],
                "exploration_rate": f"{red_stats['exploration_rate']}%",
                "top_strategies": red_stats["top_strategies"][:3],
                "current_best": red_stats["current_best"],
                "win_rates": red_win_rates,
            },
            "blue_team": {
                "detection_rate": f"{blue_stats['detection_rate']}%",
                "avg_detection_latency": f"{blue_stats['avg_detection_latency']}s",
                "patterns_known": blue_stats["patterns_known"],
                "best_action": blue_stats["best_action"],
                "action_stats": blue_stats["action_success_rates"],
                "baseline_cpu": blue_stats["baseline_cpu"],
                "baseline_memory": blue_stats["baseline_memory"],
                "improving": improving_blue,
            },
            "total_episodes": red_stats["episodes_completed"],
            "messages": self._generate_messages(red_stats, blue_stats),
        }

    def _generate_messages(self, red: Dict, blue: Dict) -> List[str]:
        """Generate human-readable evolution messages for the frontend."""
        messages = []
        episodes = red.get("episodes_completed", 0)

        if episodes == 0:
            messages.append("System ready for first training session")
            return messages

        if episodes >= 5:
            top = red.get("top_strategies", [])
            if top:
                messages.append(f"Red Team evolved: best strategy is '{top[0]['key']}' (Q={top[0]['q_value']:.2f})")

        det_rate = blue.get("detection_rate", 0.0)
        if det_rate > 80:
            messages.append(f"Blue Team is strong: {det_rate}% detection rate")
        elif det_rate > 50:
            messages.append(f"Blue Team improving: {det_rate}% detection rate")
        else:
            messages.append(f"Blue Team needs training: only {det_rate}% detection rate")

        avg_latency = blue.get("avg_detection_latency", 0.0)
        if avg_latency > 0:
            messages.append(f"Average detection speed: {avg_latency}s")

        patterns = blue.get("patterns_known", 0)
        if patterns > 0:
            messages.append(f"Blue Team recognizes {patterns} attack pattern{'s' if patterns > 1 else ''}")

        exploration = red.get("exploration_rate", 50)
        if exploration < 20:
            messages.append("Red Team has converged on optimal strategies")
        elif exploration > 40:
            messages.append("Red Team is still exploring new attack vectors")

        return messages

    def reset_all(self) -> None:
        """Reset both teams' learning data."""
        self.strategist.reset()
        self.defense_memory.reset()
        logger.info("All learning data reset")
