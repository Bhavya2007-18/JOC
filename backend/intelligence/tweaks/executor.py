from __future__ import annotations

from typing import Dict

from .registry import get_tweak


def execute_tweak(tweak_name: str) -> Dict[str, object]:
	tweak = get_tweak(tweak_name)
	if tweak is None:
		return {"error": f"Tweak not found: {tweak_name}"}
	return {
        "status": "success",
		"tweak": tweak_name,
		"type": "system_tweak",
		"result": tweak.apply(),
	}


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
