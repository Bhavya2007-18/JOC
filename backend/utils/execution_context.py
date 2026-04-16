from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from intelligence import config

logger = logging.getLogger(__name__)

@dataclass
class ExecutionContext:
    dry_run: bool
    mode: str
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    started_at: float = field(default_factory=time.time)
    confirmed_high_risk: bool = False
    snapshot: Optional[Dict[str, Any]] = None
    user: Optional[str] = None

    def __post_init__(self):
        # Extra safety as requested by user
        assert isinstance(self.dry_run, bool), f"ExecutionContext error: dry_run must be bool, got {type(self.dry_run)}"
        
    @classmethod
    def from_request(
        cls,
        dry_run: Optional[bool] = None,
        mode: Optional[str] = None,
        confirmed_high_risk: bool = False,
        user: Optional[str] = None,
    ) -> "ExecutionContext":
        # Fallback to config only if not provided in request
        effective_dry_run = config.DRY_RUN if dry_run is None else bool(dry_run)
        effective_mode = mode or ("preview" if effective_dry_run else "execute")
        
        return cls(
            dry_run=effective_dry_run,
            mode=effective_mode,
            confirmed_high_risk=confirmed_high_risk,
            user=user,
        )

    @property
    def simulated(self) -> bool:
        return self.mode == "preview" or self.dry_run

    def log_action(self, action_name: str, details: Dict[str, Any]):
        status = "SIMULATED" if self.simulated else "EXECUTED"
        logger.info(
            f"[{status}] {action_name} | dry_run={self.dry_run} | "
            f"request_id={self.request_id} | user={self.user} | details={details}"
        )
