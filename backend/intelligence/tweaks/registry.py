from __future__ import annotations

from typing import Dict, List, Optional

from .base import SystemTweak


_tweaks: Dict[str, SystemTweak] = {}


def register_tweak(tweak: SystemTweak) -> None:
	_tweaks[tweak.name] = tweak


def get_tweak(name: str) -> Optional[SystemTweak]:
	return _tweaks.get(name)


def get_all_tweaks() -> List[SystemTweak]:
	return list(_tweaks.values())
