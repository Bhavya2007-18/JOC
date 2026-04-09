"""Dynamic intensity profiles for Red Team simulations."""
from __future__ import annotations

from typing import Any, Dict

from utils.logger import get_logger

logger = get_logger("red_team.intensity_controller")


# Base intensity profiles — parameters for each simulation type at each difficulty
_PROFILES: Dict[str, Dict[str, Dict[str, Any]]] = {
    "cpu_spike": {
        "easy":   {"duration": 3,  "intensity": 1, "throttle_seconds": 0.01},
        "medium": {"duration": 5,  "intensity": 2, "throttle_seconds": 0.005},
        "hard":   {"duration": 8,  "intensity": 4, "throttle_seconds": 0.001},
        "stealth": {"duration": 10, "intensity": 1, "throttle_seconds": 0.02},
    },
    "memory_stress": {
        "easy":   {"chunk_mb": 8,  "steps": 3, "pause_seconds": 0.5, "hold_seconds": 2},
        "medium": {"chunk_mb": 16, "steps": 5, "pause_seconds": 0.3, "hold_seconds": 3},
        "hard":   {"chunk_mb": 32, "steps": 8, "pause_seconds": 0.2, "hold_seconds": 4},
        "stealth": {"chunk_mb": 4, "steps": 10, "pause_seconds": 1.0, "hold_seconds": 5},
    },
    "process_simulator": {
        "easy":   {"lifespan": 3, "cpu_burst": False},
        "medium": {"lifespan": 5, "cpu_burst": True},
        "hard":   {"lifespan": 8, "cpu_burst": True},
        "stealth": {"lifespan": 12, "cpu_burst": False},
    },
    "network_burst": {
        "easy":   {"packet_size": 512,  "packet_count": 200, "delay_seconds": 0.005},
        "medium": {"packet_size": 1024, "packet_count": 500, "delay_seconds": 0.002},
        "hard":   {"packet_size": 2048, "packet_count": 1000, "delay_seconds": 0.001},
        "stealth": {"packet_size": 256, "packet_count": 100, "delay_seconds": 0.02},
    },
}

VALID_DIFFICULTIES = {"easy", "medium", "hard", "stealth", "auto"}


class IntensityController:
    """Selects and adapts intensity parameters for Red Team simulations."""

    def get_parameters(
        self,
        simulation_type: str,
        difficulty: str = "medium",
        adaptive_override: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """Return parameters for a given simulation + difficulty.

        If adaptive_override is provided (from the strategist), merge it on top.
        """
        sim_profiles = _PROFILES.get(simulation_type, {})
        if difficulty not in sim_profiles:
            difficulty = "medium"

        base_params = dict(sim_profiles[difficulty])

        if adaptive_override:
            base_params.update(adaptive_override)

        logger.info(
            "Intensity: type=%s difficulty=%s params=%s",
            simulation_type,
            difficulty,
            base_params,
        )
        return base_params

    def escalate(self, current_params: Dict[str, Any], factor: float = 1.3) -> Dict[str, Any]:
        """Increase intensity by a factor (used when Blue Team detects too easily)."""
        escalated = {}
        for k, v in current_params.items():
            if isinstance(v, (int, float)) and k not in {"cpu_burst"}:
                escalated[k] = type(v)(v * factor)
            else:
                escalated[k] = v
        return escalated

    def deescalate(self, current_params: Dict[str, Any], factor: float = 0.7) -> Dict[str, Any]:
        """Decrease intensity (used for stealth mode when Blue Team is weak)."""
        deescalated = {}
        for k, v in current_params.items():
            if isinstance(v, (int, float)) and k not in {"cpu_burst"}:
                deescalated[k] = type(v)(max(1, v * factor))
            else:
                deescalated[k] = v
        return deescalated

    @staticmethod
    def available_profiles() -> Dict[str, list]:
        """Return all available simulation types and their difficulty levels."""
        return {sim: list(profiles.keys()) for sim, profiles in _PROFILES.items()}
