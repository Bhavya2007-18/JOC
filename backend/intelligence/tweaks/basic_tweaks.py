from __future__ import annotations

from typing import Dict

from ..models import RiskLevel
from .base import SystemTweak
from .registry import register_tweak


class ReduceVisualEffects(SystemTweak):
	def apply(self) -> Dict[str, object]:
		return {
			"status": "success",
			"message": "Visual effects reduced (simulated)",
			"impact": "Improved UI responsiveness",
		}

	def revert(self) -> Dict[str, object]:
		return {
			"status": "success",
			"message": "Visual effects restored (simulated)",
		}


class HighPerformanceMode(SystemTweak):
	def apply(self) -> Dict[str, object]:
		return {
			"status": "success",
			"message": "High performance mode enabled (simulated)",
			"impact": "Better CPU performance",
		}

	def revert(self) -> Dict[str, object]:
		return {
			"status": "success",
			"message": "Power mode restored (simulated)",
		}


register_tweak(
	ReduceVisualEffects(
		name="reduce_visual_effects",
		description="Reduce system animations to improve performance",
		risk_level=RiskLevel.SAFE,
		reversible=True,
	)
)

register_tweak(
	HighPerformanceMode(
		name="high_performance_mode",
		description="Switch system to high performance power mode",
		risk_level=RiskLevel.MODERATE,
		reversible=True,
	)
)
