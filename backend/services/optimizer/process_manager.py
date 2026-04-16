import time
import uuid
from types import SimpleNamespace
from typing import Any, Dict, Optional, Tuple

import psutil

from intelligence.action_store import ActionStore
from intelligence.config import DRY_RUN
from intelligence.constants import CRITICAL_PROCESSES
from intelligence.models import ActionRecord, ActionType
from utils.execution_context import ExecutionContext
from utils.logger import get_logger

# Removed global DRY_RUN reliance to ensure thread safety
# logger = get_logger("optimizer.process_manager")


logger = get_logger("optimizer.process_manager")
_action_store = ActionStore()


_PROTECTED_PIDS = {0, 1}
_PROTECTED_NAMES = {
    name.lower().replace(".exe", "")
    for name in CRITICAL_PROCESSES
} | {
    "init",
    "systemd",
    "system",
    "system idle process",
    "idle",
    "csrss",
    "wininit",
    "services",
    "lsass",
    "winlogon",
    "explorer",
    "svchost",
    "dwm",
    "smss",
    "memcompression",
    "registry",
    "fontdrvhost",
    "lsaiso",
    "conhost",
    "runtimebroker",
    "searchui",
    "sihost",
    "taskhostw",
    "ctfmon",
    "audiodg",
    "spoolsv",
    "wudfhost",
}

def _is_protected_process(proc: psutil.Process) -> bool:
    try:
        if proc.pid in _PROTECTED_PIDS:
            return True
        name = (proc.name() or "").lower().replace(".exe", "")
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
    action_id = f"opt-{uuid.uuid4()}"
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


def kill_process_safe(pid: int, context: Optional[ExecutionContext] = None, dry_run: bool = False) -> Dict[str, Any]:
    if context is None:
        context = ExecutionContext.from_request(dry_run=dry_run)
    
    effective_dry_run = context.simulated
    start_time = time.time()
    proc, protected, reason = _prepare_process(pid)
    if proc is None:
        logger.warning("Kill rejected for pid=%s: %s", pid, reason)
        message = "Simulated action (DRY RUN)" if effective_dry_run else reason
        return {
            "pid": pid,
            "name": "",
            "action": "kill",
            "success": True if effective_dry_run else False,
            "message": message,
            "dry_run": effective_dry_run,
            "protected": False,
            "action_id": None,
            "execution_time_ms": int((time.time() - start_time) * 1000),
            "risk": "medium",
            "confidence": 0.7,
        }

    try:
        name = proc.name() or ""
        cpu_percent = proc.cpu_percent(interval=None)
    except psutil.Error:
        name = ""
        cpu_percent = None

    action = {"action_type": "kill_process", "parameters": {"pid": pid}}
    snapshot = SimpleNamespace(top_processes=[SimpleNamespace(pid=pid, name=name)])
    if not is_action_safe(action, snapshot):
        logger.warning(f"[BLOCKED] Unsafe action prevented: {action}")
        return {
            "pid": pid,
            "name": name,
            "action": "kill",
            "success": False,
            "message": "Unsafe action blocked by safety guard",
            "dry_run": effective_dry_run,
            "protected": True,
            "action_id": None,
            "execution_time_ms": int((time.time() - start_time) * 1000),
            "risk": "high",
            "confidence": 0.95,
        }

    risk_info = _compute_risk("kill", protected, cpu_percent)

    if protected:
        logger.warning("Kill rejected for protected process pid=%s name=%s", pid, name)
        message = "Simulated action (DRY RUN)" if effective_dry_run else "Protected process; kill not allowed"
        return {
            "pid": pid,
            "name": name,
            "action": "kill",
            "success": True if effective_dry_run else False,
            "message": message,
            "dry_run": effective_dry_run,
            "protected": True,
            "action_id": None,
            "execution_time_ms": int((time.time() - start_time) * 1000),
            **risk_info,    
        }

    if effective_dry_run:
        context.log_action("kill_process", {"pid": pid, "name": name})
        return {
            "pid": pid,
            "name": name,
            "action": "kill",
            "success": True,
            "message": "Dry-run: process would be terminated",
            "dry_run": effective_dry_run,
            "protected": False,
            "action_id": None,
            "execution_time_ms": int((time.time() - start_time) * 1000),
            **risk_info,
        }

    try:
        if not execution_allowed:
            enforce_safe_execution()
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except psutil.TimeoutExpired:
            proc.kill()
        
        context.log_action("kill_process", {"pid": pid, "name": name})
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
            "dry_run": effective_dry_run,
            "protected": False,
            "action_id": action_id,
            "execution_time_ms": int((time.time() - start_time) * 1000),
            **risk_info,
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as exc:
        logger.error("Failed to terminate pid=%s: %s", pid, exc)
        message = "Simulated action (DRY RUN)" if effective_dry_run else "Failed to terminate process"
        return {
            "pid": pid,
            "name": name,
            "action": "kill",
            "success": True if effective_dry_run else False,
            "message": message,
            "dry_run": effective_dry_run,
            "protected": False,
            "action_id": None,
            "execution_time_ms": int((time.time() - start_time) * 1000),
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


def change_process_priority_safe(pid: int, priority: int, context: Optional[ExecutionContext] = None, dry_run: bool = False) -> Dict[str, Any]:
    if context is None:
        context = ExecutionContext.from_request(dry_run=dry_run)
    
    effective_dry_run = context.simulated
    start_time = time.time()
    proc, protected, reason = _prepare_process(pid)
    if proc is None:
        risk_info = _compute_risk("priority", False, None)
        logger.warning("Priority change rejected for pid=%s: %s", pid, reason)
        message = "Simulated action (DRY RUN)" if effective_dry_run else reason
        return {
            "pid": pid,
            "name": "",
            "action": "priority",
            "success": True if effective_dry_run else False,
            "message": message,
            "dry_run": effective_dry_run,
            "protected": False,
            "action_id": None,
            "execution_time_ms": int((time.time() - start_time) * 1000),
            **risk_info,
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
        message = "Simulated action (DRY RUN)" if effective_dry_run else "Protected process; priority change not allowed"
        return {
            "pid": pid,
            "name": name,
            "action": "priority",
            "success": True if effective_dry_run else False,
            "message": message,
            "dry_run": effective_dry_run,
            "protected": True,
            "action_id": None,
            "execution_time_ms": int((time.time() - start_time) * 1000),
            **risk_info,
        }

    new_nice_value = _map_priority_for_platform(priority)

    if effective_dry_run:
        context.log_action("change_priority", {"pid": pid, "name": name, "from": old_nice, "to": new_nice_value})
        return {
            "pid": pid,
            "name": name,
            "action": "priority",
            "success": True,
            "message": "Dry-run: priority would be changed",
            "dry_run": effective_dry_run,
            "protected": False,
            "action_id": None,
            "execution_time_ms": int((time.time() - start_time) * 1000),
            **risk_info,
        }

    try:
        if not execution_allowed:
            enforce_safe_execution()
        proc.nice(new_nice_value)
        context.log_action("change_priority", {"pid": pid, "name": name, "from": old_nice, "to": new_nice_value})
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
            "dry_run": effective_dry_run,
            "protected": False,
            "action_id": action_id,
            "execution_time_ms": int((time.time() - start_time) * 1000),
            **risk_info,
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, ValueError) as exc:
        logger.error("Failed to change priority for pid=%s: %s", pid, exc)
        message = "Simulated action (DRY RUN)" if effective_dry_run else "Failed to change priority"
        return {
            "pid": pid,
            "name": name,
            "action": "priority",
            "success": True if effective_dry_run else False,
            "message": message,
            "dry_run": effective_dry_run,
            "protected": False,
            "action_id": None,
            "execution_time_ms": int((time.time() - start_time) * 1000),
            **risk_info,
        }


def suspend_process_safe(pid: int, context: Optional[ExecutionContext] = None, dry_run: bool = False) -> Dict[str, Any]:
    if context is None:
        context = ExecutionContext.from_request(dry_run=dry_run)
    
    effective_dry_run = context.simulated
    start_time = time.time()
    proc, protected, reason = _prepare_process(pid)
    if proc is None:
        risk_info = _compute_risk("suspend", False, None)
        logger.warning("Suspend rejected for pid=%s: %s", pid, reason)
        message = "Simulated action (DRY RUN)" if effective_dry_run else reason
        return {
            "pid": pid,
            "name": "",
            "action": "suspend",
            "success": True if effective_dry_run else False,
            "message": message,
            "dry_run": effective_dry_run,
            "protected": False,
            "action_id": None,
            "execution_time_ms": int((time.time() - start_time) * 1000),
            **risk_info,
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
        message = "Simulated action (DRY RUN)" if effective_dry_run else "Protected process; suspend not allowed"
        return {
            "pid": pid,
            "name": name,
            "action": "suspend",
            "success": True if effective_dry_run else False,
            "message": message,
            "dry_run": effective_dry_run,
            "protected": True,
            "action_id": None,
            "execution_time_ms": int((time.time() - start_time) * 1000),
            **risk_info,
        }

    if effective_dry_run:
        context.log_action("suspend_process", {"pid": pid, "name": name})
        return {
            "pid": pid,
            "name": name,
            "action": "suspend",
            "success": True,
            "message": "Dry-run: process would be suspended",
            "dry_run": effective_dry_run,
            "protected": False,
            "action_id": None,
            "execution_time_ms": int((time.time() - start_time) * 1000),
            **risk_info,
        }

    try:
        if not execution_allowed:
            enforce_safe_execution()
        proc.suspend()
        context.log_action("suspend_process", {"pid": pid, "name": name})
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
            "dry_run": effective_dry_run,
            "protected": False,
            "action_id": action_id,
            "execution_time_ms": int((time.time() - start_time) * 1000),
            **risk_info,
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, AttributeError) as exc:
        logger.error("Failed to suspend pid=%s: %s", pid, exc)
        message = "Simulated action (DRY RUN)" if effective_dry_run else "Failed to suspend process"
        return {
            "pid": pid,
            "name": name,
            "action": "suspend",
            "success": True if effective_dry_run else False,
            "message": message,
            "dry_run": effective_dry_run,
            "protected": False,
            "action_id": None,
            "execution_time_ms": int((time.time() - start_time) * 1000),
            **risk_info,
        }


def resume_process_safe(pid: int, context: Optional[ExecutionContext] = None, dry_run: bool = False) -> Dict[str, Any]:
    if context is None:
        context = ExecutionContext.from_request(dry_run=dry_run)
    
    effective_dry_run = context.simulated
    start_time = time.time()
    proc, protected, reason = _prepare_process(pid)
    if proc is None:
        risk_info = _compute_risk("resume", False, None)
        logger.warning("Resume rejected for pid=%s: %s", pid, reason)
        message = "Simulated action (DRY RUN)" if effective_dry_run else reason
        return {
            "pid": pid,
            "name": "",
            "action": "resume",
            "success": True if effective_dry_run else False,
            "message": message,
            "dry_run": effective_dry_run,
            "protected": False,
            "action_id": None,
            "execution_time_ms": int((time.time() - start_time) * 1000),
            **risk_info,
        }

    try:
        name = proc.name() or ""
        cpu_percent = proc.cpu_percent(interval=None)
    except psutil.Error:
        name = ""
        cpu_percent = None

    risk_info = _compute_risk("resume", protected, cpu_percent)

    if protected:
        logger.warning("Resume attempted on protected process pid=%s name=%s", pid, name)

    if effective_dry_run:
        context.log_action("resume_process", {"pid": pid, "name": name})
        return {
            "pid": pid,
            "name": name,
            "action": "resume",
            "success": True,
            "message": "Dry-run: process would be resumed",
            "dry_run": effective_dry_run,
            "protected": protected,
            "action_id": None,
            "execution_time_ms": int((time.time() - start_time) * 1000),
            **risk_info,
        }

    try:
        if not execution_allowed:
            enforce_safe_execution()
        proc.resume()
        context.log_action("resume_process", {"pid": pid, "name": name})
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
            "dry_run": effective_dry_run,
            "protected": protected,
            "action_id": action_id,
            "execution_time_ms": int((time.time() - start_time) * 1000),
            **risk_info,
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, AttributeError) as exc:
        logger.error("Failed to resume pid=%s: %s", pid, exc)
        message = "Simulated action (DRY RUN)" if effective_dry_run else "Failed to resume process"
        return {
            "pid": pid,
            "name": name,
            "action": "resume",
            "success": True if effective_dry_run else False,
            "message": message,
            "dry_run": effective_dry_run,
            "protected": protected,
            "action_id": None,
            "execution_time_ms": int((time.time() - start_time) * 1000),
            **risk_info,
        }
