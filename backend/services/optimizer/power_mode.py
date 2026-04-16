"""System power-mode controller for JOC.

Implements three operating modes that adjust Windows power plans,
process scheduling priorities, and background service throttling.

Modes:
    CHILL  – Power-saving / silent-running
    SMART  – Balanced / adaptive
    BEAST  – Maximum performance / uncaged
"""

import json
import subprocess
import time
from typing import Any, Dict, List, Optional

import psutil

from intelligence.action_store import ActionStore
from intelligence.config import DRY_RUN
from intelligence.models import ActionRecord, ActionType
from services.system_monitor import get_cpu_stats, get_memory_stats
from utils.logger import get_logger

from .process_manager import (
    _is_protected_process,
    change_process_priority_safe,
)
from storage.db import get_setting, set_setting

logger = get_logger("optimizer.power_mode")
_action_store = ActionStore()

# ------------------------------------------------------------------
# Windows built-in power plan GUIDs
# ------------------------------------------------------------------
_POWER_PLANS = {
    "chill": "a1841308-3541-4fab-bc81-f71556f20b4a",   # Power Saver
    "smart": "381b4222-f694-41f0-9685-ff5bb260df2e",    # Balanced
    "beast": "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",   # High Performance
}

# Priority values for Windows (psutil nice values)
_PRIORITY_MAP = {
    "chill": psutil.BELOW_NORMAL_PRIORITY_CLASS,
    "smart": psutil.NORMAL_PRIORITY_CLASS,
    "beast": psutil.ABOVE_NORMAL_PRIORITY_CLASS,
}

# CPU-threshold: processes above this threshold get priority adjustment
_CPU_THRESHOLDS = {
    "chill": 15.0,   # aggressively throttle anything above 15%
    "smart": 40.0,   # moderate — only touch heavy hitters
    "beast": 0.0,    # boost everything visible
}

_MAX_AFFECTED_PROCESSES = {
    "chill": 20,
    "smart": 10,
    "beast": 15,
}

# Current active mode (initialized from DB or default)
try:
    _current_mode: str = get_setting("system_mode", "smart")
except Exception:
    _current_mode = "smart"

# ------------------------------------------------------------------
# Thermal Cooldown Lock — prevents rapid re-escalation after events
# ------------------------------------------------------------------
_THERMAL_COOLDOWN_SECONDS: float = 30.0
_thermal_cooldown_until: Optional[float] = None


def _is_thermal_cooldown_active(current_time: float) -> bool:
    if _thermal_cooldown_until is None:
        return False
    return current_time < _thermal_cooldown_until


def _enter_thermal_cooldown(cooldown_seconds: float = _THERMAL_COOLDOWN_SECONDS) -> None:
    global _thermal_cooldown_until
    _thermal_cooldown_until = time.time() + cooldown_seconds


def get_current_mode() -> str:
    """Return the currently active system mode."""
    return _current_mode


def _set_power_plan(mode: str, dry_run: bool) -> Dict[str, Any]:
    """Set the Windows power plan via powercfg."""
    guid = _POWER_PLANS.get(mode)
    if not guid:
        return {"success": False, "message": f"Unknown mode: {mode}"}

    plan_names = {
        "chill": "Power Saver",
        "smart": "Balanced",
        "beast": "High Performance",
    }

    if dry_run:
        return {
            "success": True,
            "simulated": True,
            "plan": plan_names.get(mode, mode),
            "guid": guid,
            "message": f"DRY RUN: Would set power plan to {plan_names.get(mode)}",
        }

    try:
        result = subprocess.run(
            ["powercfg", "/setactive", guid],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return {
                "success": True,
                "simulated": False,
                "plan": plan_names.get(mode, mode),
                "guid": guid,
                "message": f"Power plan set to {plan_names.get(mode)}",
            }
        return {
            "success": False,
            "simulated": False,
            "message": f"powercfg failed: {result.stderr.strip()}",
        }
    except Exception as exc:
        logger.error("Failed to set power plan: %s", exc)
        return {"success": False, "simulated": False, "message": str(exc)}


def _adjust_process_priorities(
    mode: str, dry_run: bool
) -> List[Dict[str, Any]]:
    """Adjust process priorities based on mode profile."""
    threshold = _CPU_THRESHOLDS[mode]
    max_procs = _MAX_AFFECTED_PROCESSES[mode]
    target_priority = _PRIORITY_MAP[mode]
    cpu_count = psutil.cpu_count(logical=True) or 1

    affected: List[Dict[str, Any]] = []

    processes = []
    for proc in psutil.process_iter(attrs=["pid", "name", "cpu_percent"]):
        try:
            info = proc.info
            cpu = info.get("cpu_percent")
            if cpu is None:
                cpu = proc.cpu_percent(interval=None)
            cpu = round(float(cpu) / cpu_count, 1)

            if _is_protected_process(proc):
                continue

            if mode == "beast":
                # In beast mode, boost everything that's meaningful
                if cpu >= 1.0:
                    processes.append({"pid": info["pid"], "name": info.get("name", "unknown"), "cpu": cpu})
            elif cpu >= threshold:
                processes.append({"pid": info["pid"], "name": info.get("name", "unknown"), "cpu": cpu})
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    processes.sort(key=lambda p: p["cpu"], reverse=True)
    processes = processes[:max_procs]

    for proc_info in processes:
        if dry_run:
            affected.append({
                "pid": proc_info["pid"],
                "name": proc_info["name"],
                "cpu_percent": proc_info["cpu"],
                "action": f"Would set priority to {target_priority}",
                "simulated": True,
            })
        else:
            result = change_process_priority_safe(
                pid=proc_info["pid"],
                priority=target_priority,
                dry_run=False,
            )
            affected.append({
                "pid": proc_info["pid"],
                "name": proc_info["name"],
                "cpu_percent": proc_info["cpu"],
                "action": f"Priority set to {target_priority}",
                "success": result.get("success", False),
                "simulated": False,
            })

    return affected


def _get_mode_description(mode: str) -> Dict[str, str]:
    """Return human-readable metadata for the mode."""
    descriptions = {
        "chill": {
            "label": "CHILL",
            "subtitle": "Power Saving",
            "description": "Reduced CPU frequency, limited background processes, battery saving, low thermals.",
            "icon": "💤",
        },
        "smart": {
            "label": "SMART",
            "subtitle": "Balanced",
            "description": "Dynamic performance adjustment, resource allocation on demand, speed and efficiency balance.",
            "icon": "🧠",
        },
        "beast": {
            "label": "BEAST",
            "subtitle": "Max Performance",
            "description": "Maximum CPU/GPU push, no throttling limits, performance over power, increased thermal tolerance.",
            "icon": "⚡",
        },
    }
    return descriptions.get(mode, descriptions["smart"])

def _record_thermal_guard_event(
    thermal_data: Dict[str, Any],
    mode_before: str,
    mode_after: str,
    reason: str,
) -> str:
    event_payload = {
        "event": "THERMAL_GUARD_TRIGGERED",
        "temp": thermal_data.get("temperature"),
        "state": thermal_data.get("state"),
        "velocity": thermal_data.get("velocity"),
        "score": thermal_data.get("score"),
        "mode_before": mode_before,
        "mode_after": mode_after,
        "reason": reason,
        "timestamp": time.time(),
    }
    action_id = f"thermal-guard-{int(time.time() * 1000)}"
    record = ActionRecord(
        action_id=action_id,
        action_type=ActionType.SYSTEM_TWEAK,
        target="thermal_guard",
        timestamp=time.time(),
        status="completed",
        reversible=False,
        result=event_payload,
        parameters={"event_type": "THERMAL_GUARD_TRIGGERED"},
    )
    _action_store.add_action(record)
    logger.warning("THERMAL_GUARD_TRIGGERED %s", json.dumps(event_payload))
    return action_id


def apply_system_mode(
    mode: str,
    force_live: bool = False,
    thermal_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Apply a system operating mode.

    Args:
        mode: One of 'chill', 'smart', 'beast'
        force_live: If True, bypasses the global DRY_RUN flag for this action.

    Returns:
        Result dict with power plan status, affected processes,
        system metrics, and mode metadata.
    """
    global _current_mode
    effective_dry_run = bool(DRY_RUN) and not force_live
    if effective_dry_run:
        logger.info("[DRY RUN ACTIVE] No real system changes will be applied.")
    mode = mode.lower().strip()

    if mode not in _POWER_PLANS:
        return {
            "success": False,
            "message": f"Invalid mode: {mode}. Must be chill, smart, or beast.",
        }

    guard_action_id = None
    guard_downgraded = False
    requested_mode = mode
    current_time = time.time()

    if thermal_data:
        temp = thermal_data.get("temperature", 0)
        velocity = thermal_data.get("velocity", "stable")
        state = thermal_data.get("state", "COOL")
        is_critical = thermal_data.get("is_critical", False)

        if mode == "beast":
            if _is_thermal_cooldown_active(current_time):
                mode = "smart"
                guard_downgraded = True
                guard_action_id = _record_thermal_guard_event(
                    thermal_data=thermal_data,
                    mode_before=requested_mode,
                    mode_after=mode,
                    reason="thermal_cooldown_lock",
                )
                _enter_thermal_cooldown()
            elif is_critical:
                mode = "smart"
                guard_downgraded = True
                guard_action_id = _record_thermal_guard_event(
                    thermal_data=thermal_data,
                    mode_before=requested_mode,
                    mode_after=mode,
                    reason="critical_thermal_state",
                )
                _enter_thermal_cooldown()
            elif state == "HOT" and velocity == "rising":
                mode = "smart"
                guard_downgraded = True
                guard_action_id = _record_thermal_guard_event(
                    thermal_data=thermal_data,
                    mode_before=requested_mode,
                    mode_after=mode,
                    reason="hot_rising_thermal",
                )
                _enter_thermal_cooldown()
        elif mode == "smart" and state == "HOT" and velocity == "rising":
            mode = "chill"
            guard_downgraded = True
            guard_action_id = _record_thermal_guard_event(
                thermal_data=thermal_data,
                mode_before=requested_mode,
                mode_after=mode,
                reason="hot_rising_smart_to_chill",
            )

    # Capture before-metrics
    cpu_before = get_cpu_stats()
    mem_before = get_memory_stats()

    # 1. Set power plan
    power_result = _set_power_plan(mode, dry_run=effective_dry_run)

    # 2. Adjust process priorities
    affected_processes = _adjust_process_priorities(mode, dry_run=effective_dry_run)

    # 3. Update internal state and persistence
    previous_mode = _current_mode
    _current_mode = mode

    if not effective_dry_run:
        set_setting("system_mode", mode)

    # 4. Capture after-metrics
    cpu_after = get_cpu_stats()
    mem_after = get_memory_stats()

    mode_info = _get_mode_description(mode)

    result = {
        "success": power_result.get("success", False),
        "dry_run": effective_dry_run,
        "mode": mode,
        "requested_mode": requested_mode,
        "previous_mode": previous_mode,
        "thermal_guard_applied": guard_downgraded,
        "mode_info": mode_info,
        "power_plan": power_result,
        "affected_processes": len(affected_processes),
        "processes": affected_processes[:10],  # Limit response size
        "metrics": {
            "cpu_before": cpu_before.get("usage_percent", 0),
            "cpu_after": cpu_after.get("usage_percent", 0),
            "memory_before": mem_before.get("percent", 0),
            "memory_after": mem_after.get("percent", 0),
        },
        "message": (
            f"{'[DRY RUN] ' if effective_dry_run else ''}"
            f"{'[THERMAL_GUARD] ' if guard_downgraded else ''}"
            f"Mode switched: {previous_mode.upper()} -> {mode.upper()}. "
            f"Power plan: {power_result.get('plan', 'N/A')}. "
            f"{len(affected_processes)} processes adjusted."
        ),
        "timestamp": time.time(),
    }
    if thermal_data:
        result["thermal"] = {
            "temperature": thermal_data.get("temperature"),
            "state": thermal_data.get("state"),
            "velocity": thermal_data.get("velocity"),
            "score": thermal_data.get("score"),
            "is_critical": thermal_data.get("is_critical"),
        }
    if guard_action_id:
        result["thermal_guard_action_id"] = guard_action_id

    # Log the action
    action_id = f"mode-{mode}-{int(time.time() * 1000)}"
    record = ActionRecord(
        action_id=action_id,
        action_type=ActionType.SYSTEM_TWEAK,
        target=f"system_mode_{mode}",
        timestamp=time.time(),
        status="completed",
        reversible=True,
        result=result,
        parameters={"mode": mode, "previous_mode": previous_mode},
    )
    _action_store.add_action(record)
    result["action_id"] = action_id

    logger.info(
        "Mode applied mode=%s dry_run=%s processes=%s",
        mode,
        effective_dry_run,
        len(affected_processes),
    )

    return result
