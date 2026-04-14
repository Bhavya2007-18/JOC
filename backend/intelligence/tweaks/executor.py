from __future__ import annotations

from typing import Dict

from intelligence.config import DRY_RUN
from .registry import get_tweak


def execute_tweak(tweak_name: str, dry_run: bool = None) -> Dict[str, object]:
	# Use provided dry_run override, otherwise fallback to global DRY_RUN config
	effective_dry_run = dry_run if dry_run is not None else DRY_RUN
	
	tweak = get_tweak(tweak_name)
	if tweak is None:
		return {"error": f"Tweak not found: {tweak_name}"}

	# Inject dry_run into the tweak apply context
	import intelligence.config
	original_dry_run = intelligence.config.DRY_RUN
	intelligence.config.DRY_RUN = effective_dry_run
	
	try:
		result = tweak.apply()
	finally:
		intelligence.config.DRY_RUN = original_dry_run

	response = {
		"mode": "preview" if effective_dry_run else "execute",
		"tweak_id": tweak_name,
		"status": result.get("status", "success"),
		"dry_run": effective_dry_run,
		"summary": result.get("summary", ""),
		"action_id": None
	}
	response.update(result.get("effects", {}))
	return response


def revert_tweak(tweak_name: str) -> Dict[str, object]:
	tweak = get_tweak(tweak_name)
	if tweak is None:
		return {"error": f"Tweak not found: {tweak_name}"}
	return {
		"action": "revert",
		"tweak": tweak_name,
		"type": "system_tweak",
		"result": tweak.revert(),
	}
