import time
from typing import Any, Dict, Optional, Tuple

import psutil

from intelligence.action_store import ActionStore
from intelligence.models import ActionRecord, ActionType
from utils.logger import get_logger


logger = get_logger("optimizer.process_manager")
_action_store = ActionStore()


_PROTECTED_PIDS = {0, 1}
_PROTECTED_NAMES = {
    "system",
    "system idle process",
    "idle",
    "init",
    "systemd",
    "csrss.exe",
    "wininit.exe",
    "services.exe",
    "lsass.exe",
}


def _is_protected_process(proc: psutil.Process) -> bool:
    try:
        if proc.pid in _PROTECTED_PIDS:
            return True
        name = (proc.name() or "").lower()
        if name in _PROTECTED_NAMES:
            return True
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return True
    return False


def _ensure_protected_set() -> None:
    try:
        current = psutil.Process()
        _PROTECTED_PIDS.add(current.pid)
        _PROTECTED_PIDS.add(current.ppid())
    except psutil.Error:
        return


def _log_action(
    action_type: ActionType,
    target: str,
    status: str,
    reversible: bool,
    result: Dict[str, Any],
    parameters: Dict[str, Any],
) -> str:
    action_id = f"opt-{int(time.time() * 1000)}-{target}"
    record = ActionRecord(
        action_id=action_id,
        action_type=action_type,
        target=target,
        timestamp=time.time(),
        status=status,
        reversible=reversible,
        result=result,
        parameters=parameters,
    )
    _action_store.add_action(record)
    return action_id


def _compute_risk(action: str, protected: bool, cpu_percent: Optional[float] = None) -> Dict[str, Any]:
    if protected:
        return {"risk": "high", "confidence": 0.95}
    if cpu_percent is None:
        return {"risk": "medium", "confidence": 0.7}
    if cpu_percent < 20:
        return {"risk": "low", "confidence": 0.8}
    if cpu_percent < 60:
        return {"risk": "medium", "confidence": 0.85}
    return {"risk": "high", "confidence": 0.9}


def _prepare_process(pid: int) -> Tuple[Optional[psutil.Process], bool, str]:
    _ensure_protected_set()
    try:
        proc = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return None, False, "Process does not exist"
    except psutil.AccessDenied:
        return None, False, "Access denied to process"
    protected = _is_protected_process(proc)
    if protected:
        return proc, True, "Process is protected and cannot be modified"
    return proc, False, ""


def kill_process_safe(pid: int, dry_run: bool = False) -> Dict[str, Any]:
    proc, protected, reason = _prepare_process(pid)
    if proc is None:
        logger.warning("Kill rejected for pid=%s: %s", pid, reason)
        return {
            "pid": pid,
            "name": "",
            "action": "kill",
            "success": False,
            "message": reason,
            "dry_run": dry_run,
            "protected": False,
            "action_id": None,
            "risk": "medium",
            "confidence": 0.7,
        }

    try:
        name = proc.name() or ""
        cpu_percent = proc.cpu_percent(interval=None)
    except psutil.Error:
        name = ""
        cpu_percent = None

    risk_info = _compute_risk("kill", protected, cpu_percent)

    if protected:
        logger.warning("Kill rejected for protected process pid=%s name=%s", pid, name)
        return {
            "pid": pid,
            "name": name,
            "action": "kill",
            "success": False,
            "message": "Protected process; kill not allowed",
            "dry_run": dry_run,
            "protected": True,
            "action_id": None,
            **risk_info,
        }

    if dry_run:
        logger.info("Dry-run kill for pid=%s name=%s", pid, name)
        return {
            "pid": pid,
            "name": name,
            "action": "kill",
            "success": True,
            "message": "Dry-run: process would be terminated",
            "dry_run": True,
            "protected": False,
            "action_id": None,
            **risk_info,
        }

    try:
        proc.terminate()
        logger.info("Requested terminate for pid=%s name=%s", pid, name)
        action_id = _log_action(
            action_type=ActionType.KILL_PROCESS,
            target=str(pid),
            status="requested",
            reversible=False,
            result={"pid": pid, "name": name},
            parameters={"action": "terminate"},
        )
        return {
            "pid": pid,
            "name": name,
            "action": "kill",
            "success": True,
            "message": "Terminate signal sent",
            "dry_run": False,
            "protected": False,
            "action_id": action_id,
            **risk_info,
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as exc:
        logger.error("Failed to terminate pid=%s: %s", pid, exc)
        return {
            "pid": pid,
            "name": name,
            "action": "kill",
            "success": False,
            "message": "Failed to terminate process",
            "dry_run": False,
            "protected": False,
            "action_id": None,
            **risk_info,
        }


def _map_priority_for_platform(priority: int) -> Any:
    if psutil.WINDOWS:
        if priority <= -10:
            return psutil.HIGH_PRIORITY_CLASS
        if priority < 0:
            return psutil.ABOVE_NORMAL_PRIORITY_CLASS
        if priority == 0:
            return psutil.NORMAL_PRIORITY_CLASS
        if priority <= 10:
            return psutil.BELOW_NORMAL_PRIORITY_CLASS
        return psutil.IDLE_PRIORITY_CLASS
    return priority


def change_process_priority_safe(pid: int, priority: int, dry_run: bool = False) -> Dict[str, Any]:
    proc, protected, reason = _prepare_process(pid)
    if proc is None:
        logger.warning("Priority change rejected for pid=%s: %s", pid, reason)
        return {
            "pid": pid,
            "name": "",
            "action": "priority",
            "success": False,
            "message": reason,
            "dry_run": dry_run,
            "protected": False,
            "action_id": None,
            "risk": "medium",
            "confidence": 0.7,
        }

    try:
        name = proc.name() or ""
        old_nice = proc.nice()
        cpu_percent = proc.cpu_percent(interval=None)
    except psutil.Error:
        name = ""
        old_nice = None
        cpu_percent = None

    risk_info = _compute_risk("priority", protected, cpu_percent)

    if protected:
        logger.warning("Priority change rejected for protected process pid=%s name=%s", pid, name)
        return {
            "pid": pid,
            "name": name,
            "action": "priority",
            "success": False,
            "message": "Protected process; priority change not allowed",
            "dry_run": dry_run,
            "protected": True,
            "action_id": None,
            **risk_info,
        }

    new_nice_value = _map_priority_for_platform(priority)

    if dry_run:
        logger.info(
            "Dry-run priority change for pid=%s name=%s from=%s to=%s",
            pid,
            name,
            old_nice,
            new_nice_value,
        )
        return {
            "pid": pid,
            "name": name,
            "action": "priority",
            "success": True,
            "message": "Dry-run: priority would be changed",
            "dry_run": True,
            "protected": False,
            "action_id": None,
            **risk_info,
        }

    try:
        proc.nice(new_nice_value)
        logger.info(
            "Changed priority for pid=%s name=%s from=%s to=%s",
            pid,
            name,
            old_nice,
            new_nice_value,
        )
        action_id = _log_action(
            action_type=ActionType.SYSTEM_TWEAK,
            target=str(pid),
            status="completed",
            reversible=False,
            result={"pid": pid, "name": name, "old_nice": old_nice, "new_nice": new_nice_value},
            parameters={"action": "priority_change", "requested_priority": priority},
        )
        return {
            "pid": pid,
            "name": name,
            "action": "priority",
            "success": True,
            "message": "Priority updated",
            "dry_run": False,
            "protected": False,
            "action_id": action_id,
            **risk_info,
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, ValueError) as exc:
        logger.error("Failed to change priority for pid=%s: %s", pid, exc)
        return {
            "pid": pid,
            "name": name,
            "action": "priority",
            "success": False,
            "message": "Failed to change priority",
            "dry_run": False,
            "protected": False,
            "action_id": None,
            **risk_info,
        }


def suspend_process_safe(pid: int, dry_run: bool = False) -> Dict[str, Any]:
    proc, protected, reason = _prepare_process(pid)
    if proc is None:
        logger.warning("Suspend rejected for pid=%s: %s", pid, reason)
        return {
            "pid": pid,
            "name": "",
            "action": "suspend",
            "success": False,
            "message": reason,
            "dry_run": dry_run,
            "protected": False,
            "action_id": None,
            "risk": "medium",
            "confidence": 0.7,
        }

    try:
        name = proc.name() or ""
        cpu_percent = proc.cpu_percent(interval=None)
    except psutil.Error:
        name = ""
        cpu_percent = None

    risk_info = _compute_risk("suspend", protected, cpu_percent)

    if protected:
        logger.warning("Suspend rejected for protected process pid=%s name=%s", pid, name)
        return {
            "pid": pid,
            "name": name,
            "action": "suspend",
            "success": False,
            "message": "Protected process; suspend not allowed",
            "dry_run": dry_run,
            "protected": True,
            "action_id": None,
            **risk_info,
        }

    if dry_run:
        logger.info("Dry-run suspend for pid=%s name=%s", pid, name)
        return {
            "pid": pid,
            "name": name,
            "action": "suspend",
            "success": True,
            "message": "Dry-run: process would be suspended",
            "dry_run": True,
            "protected": False,
            "action_id": None,
            **risk_info,
        }

    try:
        proc.suspend()
        logger.info("Suspended pid=%s name=%s", pid, name)
        action_id = _log_action(
            action_type=ActionType.SYSTEM_TWEAK,
            target=str(pid),
            status="completed",
            reversible=True,
            result={"pid": pid, "name": name},
            parameters={"action": "suspend"},
        )
        return {
            "pid": pid,
            "name": name,
            "action": "suspend",
            "success": True,
            "message": "Process suspended",
            "dry_run": False,
            "protected": False,
            "action_id": action_id,
            **risk_info,
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, AttributeError) as exc:
        logger.error("Failed to suspend pid=%s: %s", pid, exc)
        return {
            "pid": pid,
            "name": name,
            "action": "suspend",
            "success": False,
            "message": "Failed to suspend process",
            "dry_run": False,
            "protected": False,
            "action_id": None,
            **risk_info,
        }


def resume_process_safe(pid: int, dry_run: bool = False) -> Dict[str, Any]:
    proc, protected, reason = _prepare_process(pid)
    if proc is None:
        logger.warning("Resume rejected for pid=%s: %s", pid, reason)
        return {
            "pid": pid,
            "name": "",
            "action": "resume",
            "success": False,
            "message": reason,
            "dry_run": dry_run,
            "protected": False,
            "action_id": None,
            "risk": "medium",
            "confidence": 0.7,
        }

    try:
        name = proc.name() or ""
        cpu_percent = proc.cpu_percent(interval=None)
    except psutil.Error:
        name = ""
        cpu_percent = None

    risk_info = _compute_risk("resume", protected, cpu_percent)

    if protected:
        logger.warning("Resume allowed for protected process pid=%s name=%s", pid, name)

    if dry_run:
        logger.info("Dry-run resume for pid=%s name=%s", pid, name)
        return {
            "pid": pid,
            "name": name,
            "action": "resume",
            "success": True,
            "message": "Dry-run: process would be resumed",
            "dry_run": True,
            "protected": protected,
            "action_id": None,
            **risk_info,
        }

    try:
        proc.resume()
        logger.info("Resumed pid=%s name=%s", pid, name)
        action_id = _log_action(
            action_type=ActionType.SYSTEM_TWEAK,
            target=str(pid),
            status="completed",
            reversible=False,
            result={"pid": pid, "name": name},
            parameters={"action": "resume"},
        )
        return {
            "pid": pid,
            "name": name,
            "action": "resume",
            "success": True,
            "message": "Process resumed",
            "dry_run": False,
            "protected": protected,
            "action_id": action_id,
            **risk_info,
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, AttributeError) as exc:
        logger.error("Failed to resume pid=%s: %s", pid, exc)
        return {
            "pid": pid,
            "name": name,
            "action": "resume",
            "success": False,
            "message": "Failed to resume process",
            "dry_run": False,
            "protected": protected,
            "action_id": None,
            **risk_info,
        }
