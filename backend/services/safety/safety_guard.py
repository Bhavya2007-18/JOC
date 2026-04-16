from __future__ import annotations

from typing import Any, Iterable

import psutil


CRITICAL_PROCESSES = {
    "explorer.exe",
    "winlogon.exe",
    "csrss.exe",
    "services.exe",
    "lsass.exe",
}


def is_critical_process(process_name: str) -> bool:
    if not process_name:
        return False
    normalized = str(process_name).strip().lower()
    return normalized in CRITICAL_PROCESSES


def _process_value(process: Any, field: str) -> Any:
    if isinstance(process, dict):
        return process.get(field)

    value = getattr(process, field, None)
    if callable(value):
        try:
            return value()
        except TypeError:
            return None
    return value


def is_action_safe(action: dict, snapshot) -> bool:
    if action is None:
        return False

    action_type = action.get("action_type")
    if action_type == "kill_process":
        parameters = action.get("parameters", {}) or {}
        target_pid = parameters.get("pid")
        if target_pid is None:
            return True

        try:
            target_pid = int(target_pid)
        except (TypeError, ValueError):
            return True

        top_processes: Iterable[Any] = getattr(snapshot, "top_processes", []) or []
        matched_snapshot = False
        for process in top_processes:
            pid = _process_value(process, "pid")
            try:
                if int(pid) != target_pid:
                    continue
            except (TypeError, ValueError):
                continue

            matched_snapshot = True

            process_name = str(_process_value(process, "name") or "")
            if is_critical_process(process_name):
                return False

        # Fallback: snapshot can be partial, so validate directly with OS process table.
        if not matched_snapshot:
            try:
                proc = psutil.Process(target_pid)
                process_name = proc.name()
                if is_critical_process(process_name):
                    return False
            except Exception:
                pass

    return True
