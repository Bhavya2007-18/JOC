from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

from services.orchestration.state_manager import SafetyGuard
from utils.execution_context import ExecutionContext


class BaseSimulation(ABC):
    """Abstract base class for deterministic stress simulations."""

    def __init__(
        self,
        simulation_id: str,
        correlation_id: str,
        parameters: Dict[str, Any],
        safety_guard: SafetyGuard,
        context: ExecutionContext,
    ) -> None:
        self.simulation_id = simulation_id
        self.correlation_id = correlation_id
        self.parameters = parameters
        self.safety_guard = safety_guard
        self.context = context
        self.dry_run = context.dry_run

    @abstractmethod
    def setup(self) -> None:
        """Prepare resources needed before stress execution."""

    @abstractmethod
    def execute(self) -> Dict[str, Any]:
        """Execute the simulation and return structured observations."""

    @abstractmethod
    def cleanup(self) -> None:
        """Release resources regardless of success/failure."""

    @abstractmethod
    def metadata(self) -> Dict[str, Any]:
        """Return simulation metadata for traceability."""

