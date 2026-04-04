from __future__ import annotations

import json
from dataclasses import asdict
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import ActionRecord, ActionType


class ActionStore:
	def __init__(self) -> None:
		self._file_path = Path(__file__).parent / "action_history.json"
		self._file_path.parent.mkdir(parents=True, exist_ok=True)
		self._actions: List[ActionRecord] = []
		self._load_history()

	def add_action(self, action_record: ActionRecord) -> None:
		self._actions.append(action_record)
		self._save_history()

	def get_all_actions(self) -> List[ActionRecord]:
		return list(self._actions)

	def get_action_by_id(self, action_id: str) -> Optional[ActionRecord]:
		for action in self._actions:
			if action.action_id == action_id:
				return action
		return None

	def _load_history(self) -> None:
		try:
			with self._file_path.open("r", encoding="utf-8") as history_file:
				raw_data = json.load(history_file)
		except FileNotFoundError:
			self._actions = []
			return
		except (json.JSONDecodeError, OSError):
			self._actions = []
			return

		if not isinstance(raw_data, list):
			self._actions = []
			return

		loaded_actions: List[ActionRecord] = []
		for item in raw_data:
			action_record = self._deserialize_action_record(item)
			if action_record is not None:
				loaded_actions.append(action_record)
		self._actions = loaded_actions

	def _save_history(self) -> None:
		serialized = [self._serialize_action_record(action) for action in self._actions]
		try:
			with self._file_path.open("w", encoding="utf-8") as history_file:
				json.dump(serialized, history_file, indent=2)
		except OSError:
			return

	def _serialize_action_record(self, action_record: ActionRecord) -> Dict[str, Any]:
		return self._serialize_value(asdict(action_record))

	def _serialize_value(self, value: Any) -> Any:
		if isinstance(value, Enum):
			return value.value
		if isinstance(value, dict):
			return {str(key): self._serialize_value(item) for key, item in value.items()}
		if isinstance(value, list):
			return [self._serialize_value(item) for item in value]
		return value

	def _deserialize_action_record(self, raw_action: Any) -> Optional[ActionRecord]:
		if not isinstance(raw_action, dict):
			return None

		try:
			return ActionRecord(
				action_id=str(raw_action["action_id"]),
				action_type=ActionType(raw_action["action_type"]),
				target=str(raw_action["target"]),
				timestamp=float(raw_action["timestamp"]),
				status=str(raw_action["status"]),
				reversible=bool(raw_action["reversible"]),
				result=raw_action.get("result", {}) if isinstance(raw_action.get("result", {}), dict) else {},
				parameters=raw_action.get("parameters", {})
				if isinstance(raw_action.get("parameters", {}), dict)
				else {},
			)
		except (KeyError, TypeError, ValueError):
			return None
