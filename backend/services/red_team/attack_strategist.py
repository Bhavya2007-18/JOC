"""ε-greedy Reinforcement Learning attack strategist for Red Team."""
from __future__ import annotations

import random
import uuid
from typing import Any, Dict, List, Optional

from utils.logger import get_logger

from .intensity_controller import IntensityController
from .multi_vector import AttackPlan, AttackVector, MultiVectorCombiner, COMBO_TEMPLATES
from .strategy_memory import StrategyMemory

logger = get_logger("red_team.attack_strategist")

# All possible action keys for the Q-table
_SIMULATION_TYPES = ["cpu_spike", "memory_stress", "process_simulator", "network_burst"]
_DIFFICULTIES = ["easy", "medium", "hard", "stealth"]
_COMBO_NAMES = list(COMBO_TEMPLATES.keys())


def _make_key(sim_type: str, difficulty: str) -> str:
    return f"{sim_type}|{difficulty}"


class AttackStrategist:
    """Main Red Team brain — selects attacks using ε-greedy RL.

    Algorithm:
    - With probability ε → explore (random attack)
    - With probability 1-ε → exploit (pick highest Q-value attack)
    - After each episode, update Q-value: Q += α(reward - Q)
    - Reward = 1 - (blue_score / 100) → undetected attacks get high reward
    - ε decays after each episode: ε *= 0.98 (min 0.1)
    """

    def __init__(self) -> None:
        self.memory = StrategyMemory()
        self.combiner = MultiVectorCombiner()
        self.intensity = IntensityController()

    def select_attack(self, difficulty: str = "auto") -> AttackPlan:
        """Select the next attack using ε-greedy strategy.

        Args:
            difficulty: 'easy', 'medium', 'hard', 'auto' (ML-chosen)
        """
        plan_id = str(uuid.uuid4())[:8]
        epsilon = self.memory.epsilon
        is_exploring = random.random() < epsilon

        if is_exploring:
            plan = self._explore(plan_id, difficulty)
            logger.info("Exploring: %s (ε=%.2f)", plan.strategy_name, epsilon)
        else:
            plan = self._exploit(plan_id, difficulty)
            logger.info("Exploiting: %s (ε=%.2f)", plan.strategy_name, epsilon)

        plan.history_based = not is_exploring
        return plan

    def record_outcome(self, plan: AttackPlan, blue_score: int) -> None:
        """Record the result of an attack and update Q-values.

        Args:
            plan: The attack plan that was executed
            blue_score: Blue Team's total score (0-100)
        """
        reward = 1.0 - (blue_score / 100.0)
        reward = max(0.0, min(1.0, reward))

        detected = blue_score >= 50

        # Update Q-value for each vector in the plan
        for vector in plan.vectors:
            key = _make_key(vector.simulation_type, vector.difficulty)
            self.memory.update_q_value(key, reward)

        # Also update combo key if multi-vector
        if plan.strategy_name in _COMBO_NAMES:
            combo_key = f"combo|{plan.strategy_name}"
            self.memory.update_q_value(combo_key, reward)

        # Record episode
        self.memory.record_episode({
            "plan_id": plan.plan_id,
            "strategy_name": plan.strategy_name,
            "attack_type": plan.primary_type(),
            "difficulty": plan.difficulty,
            "vectors": [v.simulation_type for v in plan.vectors],
            "blue_score": blue_score,
            "reward": round(reward, 4),
            "detected": detected,
            "history_based": plan.history_based,
        })

        # Decay exploration rate
        self.memory.decay_epsilon()

        logger.info(
            "Outcome recorded: plan=%s blue=%d reward=%.2f detected=%s ε=%.2f",
            plan.plan_id, blue_score, reward, detected, self.memory.epsilon,
        )

    def get_evolution_stats(self) -> Dict[str, Any]:
        """Return stats for frontend visualization."""
        top = self.memory.get_top_strategies(5)
        win_rates = self.memory.get_recent_win_rates(window=5)
        history = self.memory.history

        # Calculate detection rate trend
        recent = history[-20:] if history else []
        detection_rate = (
            sum(1 for ep in recent if ep.get("detected", True)) / len(recent)
            if recent else 0.0
        )

        return {
            "episodes_completed": self.memory.episode_count,
            "exploration_rate": round(self.memory.epsilon * 100, 1),
            "top_strategies": top,
            "win_rates": win_rates,
            "recent_detection_rate": round(detection_rate * 100, 1),
            "q_table_size": len(self.memory.q_table),
            "current_best": top[0]["key"] if top else "none",
        }

    def reset(self) -> None:
        """Wipe all learned strategies."""
        self.memory.reset()

    # ── private ───────────────────────────────────────────────

    def _explore(self, plan_id: str, difficulty: str) -> AttackPlan:
        """Random attack selection (exploration)."""
        use_combo = random.random() < 0.3  # 30% chance of combo

        if use_combo and _COMBO_NAMES:
            combo_name = random.choice(_COMBO_NAMES)
            vectors = self.combiner.build_combo(combo_name)
            diff = difficulty if difficulty != "auto" else random.choice(_DIFFICULTIES)
            # Apply intensity to each vector
            for v in vectors:
                if difficulty != "auto":
                    v.difficulty = diff
                v.parameters = self.intensity.get_parameters(v.simulation_type, v.difficulty)
            return AttackPlan(
                plan_id=plan_id,
                vectors=vectors,
                strategy_name=combo_name,
                difficulty=diff,
                expected_difficulty_score=0.5,
                history_based=False,
            )
        else:
            sim_type = random.choice(_SIMULATION_TYPES)
            diff = difficulty if difficulty != "auto" else random.choice(_DIFFICULTIES)
            params = self.intensity.get_parameters(sim_type, diff)
            vectors = self.combiner.build_single(sim_type, diff, params)
            return AttackPlan(
                plan_id=plan_id,
                vectors=vectors,
                strategy_name=sim_type,
                difficulty=diff,
                expected_difficulty_score=0.5,
                history_based=False,
            )

    def _exploit(self, plan_id: str, difficulty: str) -> AttackPlan:
        """Pick the best known attack (exploitation)."""
        q_table = self.memory.q_table

        if not q_table:
            return self._explore(plan_id, difficulty)

        # Find the highest Q-value action
        best_key = max(q_table, key=q_table.get)
        best_q = q_table[best_key]

        if best_key.startswith("combo|"):
            combo_name = best_key.split("|", 1)[1]
            vectors = self.combiner.build_combo(combo_name)
            diff = difficulty if difficulty != "auto" else "hard"
            for v in vectors:
                v.parameters = self.intensity.get_parameters(v.simulation_type, v.difficulty)
            return AttackPlan(
                plan_id=plan_id,
                vectors=vectors,
                strategy_name=combo_name,
                difficulty=diff,
                expected_difficulty_score=best_q,
                history_based=True,
            )
        else:
            parts = best_key.split("|")
            sim_type = parts[0] if len(parts) > 0 else "cpu_spike"
            diff_from_q = parts[1] if len(parts) > 1 else "medium"
            actual_diff = difficulty if difficulty != "auto" else diff_from_q
            params = self.intensity.get_parameters(sim_type, actual_diff)
            vectors = self.combiner.build_single(sim_type, actual_diff, params)
            return AttackPlan(
                plan_id=plan_id,
                vectors=vectors,
                strategy_name=sim_type,
                difficulty=actual_diff,
                expected_difficulty_score=best_q,
                history_based=True,
            )
