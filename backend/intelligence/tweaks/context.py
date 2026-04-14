from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import time
import uuid

from intelligence import config


@dataclass
class ExecutionContext:
    dry_run: bool
    mode: str
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    started_at: float = field(default_factory=time.time)
    confirmed_high_risk: bool = False
    snapshot: Optional[Dict[str, Any]] = None

    @classmethod
    def from_request(
        cls,
        dry_run: Optional[bool] = None,
        mode: Optional[str] = None,
        confirmed_high_risk: bool = False,
    ) -> "ExecutionContext":
        effective_dry_run = config.DRY_RUN if dry_run is None else bool(dry_run)
        effective_mode = mode or ("preview" if effective_dry_run else "execute")
        return cls(
            dry_run=effective_dry_run,
            mode=effective_mode,
            confirmed_high_risk=confirmed_high_risk,
        )

    @property
    def simulated(self) -> bool:
        return self.mode == "preview" or self.dry_run

