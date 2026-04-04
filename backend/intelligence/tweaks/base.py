from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from ..models import RiskLevel


@dataclass
class SystemTweak:
	name: str
	description: str
	risk_level: RiskLevel
	reversible: bool

	def apply(self) -> Dict[str, object]:
		return {
			"status": "not_implemented",
			"action": "apply_tweak",
			"name": self.name,
			"message": "Tweak apply logic is not implemented yet.",
		}

	def revert(self) -> Dict[str, object]:
		return {
			"status": "not_implemented",
			"action": "revert_tweak",
			"name": self.name,
			"message": "Tweak revert logic is not implemented yet.",
		}
