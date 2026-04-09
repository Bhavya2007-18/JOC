"""Multi-vector attack combiner for Red Team."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from utils.logger import get_logger

logger = get_logger("red_team.multi_vector")


@dataclass
class AttackVector:
    """One component of a multi-vector attack."""
    simulation_type: str
    difficulty: str = "medium"
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AttackPlan:
    """Complete plan produced by the Red Team strategist."""
    plan_id: str
    vectors: List[AttackVector]
    strategy_name: str
    difficulty: str
    expected_difficulty_score: float  # 0-1, how hard this should be for Blue Team
    history_based: bool  # whether this was chosen by ML or randomly
    metadata: Dict[str, Any] = field(default_factory=dict)

    def primary_type(self) -> str:
        """Return the first vector's simulation type (for compatibility)."""
        return self.vectors[0].simulation_type if self.vectors else "cpu_spike"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "strategy_name": self.strategy_name,
            "vectors": [
                {"simulation_type": v.simulation_type, "difficulty": v.difficulty, "parameters": v.parameters}
                for v in self.vectors
            ],
            "difficulty": self.difficulty,
            "expected_difficulty_score": self.expected_difficulty_score,
            "history_based": self.history_based,
        }


# Pre-defined multi-vector templates
COMBO_TEMPLATES: Dict[str, List[AttackVector]] = {
    "stealth_memory": [
        AttackVector("cpu_spike", "easy"),       # small CPU distraction
        AttackVector("memory_stress", "hard"),    # main payload: heavy RAM hit
    ],
    "process_flood": [
        AttackVector("process_simulator", "medium"),
        AttackVector("cpu_spike", "medium"),
    ],
    "network_distract": [
        AttackVector("network_burst", "medium"),  # saturate network first
        AttackVector("cpu_spike", "hard"),         # then spike CPU
    ],
    "slow_bleed": [
        AttackVector("memory_stress", "stealth"),  # very slow memory leak
        AttackVector("process_simulator", "easy"),  # light background process
    ],
    "full_assault": [
        AttackVector("cpu_spike", "hard"),
        AttackVector("memory_stress", "medium"),
        AttackVector("network_burst", "medium"),
    ],
}

# Single-vector templates (for backward compatibility and simple runs)
SINGLE_TEMPLATES: Dict[str, AttackVector] = {
    "cpu_spike": AttackVector("cpu_spike"),
    "memory_stress": AttackVector("memory_stress"),
    "process_simulator": AttackVector("process_simulator"),
    "network_burst": AttackVector("network_burst"),
}


class MultiVectorCombiner:
    """Produces attack plans — either single or multi-vector."""

    def build_single(
        self,
        simulation_type: str,
        difficulty: str = "medium",
        parameters: Dict[str, Any] | None = None,
    ) -> List[AttackVector]:
        """Build a single-vector attack."""
        vec = AttackVector(
            simulation_type=simulation_type,
            difficulty=difficulty,
            parameters=parameters or {},
        )
        return [vec]

    def build_combo(self, combo_name: str) -> List[AttackVector]:
        """Build a multi-vector attack from a named template."""
        if combo_name not in COMBO_TEMPLATES:
            logger.warning("Unknown combo %s, falling back to cpu_spike", combo_name)
            return self.build_single("cpu_spike")
        return list(COMBO_TEMPLATES[combo_name])

    @staticmethod
    def available_combos() -> List[str]:
        return list(COMBO_TEMPLATES.keys())

    @staticmethod
    def combo_description(name: str) -> str:
        """Human-readable description of a combo for the frontend."""
        descriptions = {
            "stealth_memory": "Distract with light CPU spike, then hit RAM hard",
            "process_flood": "Spawn suspicious process + CPU stress",
            "network_distract": "Network saturation followed by CPU spike",
            "slow_bleed": "Slow memory leak with background process (hard to detect)",
            "full_assault": "CPU + Memory + Network simultaneously",
        }
        return descriptions.get(name, name)
