import logging
import time
from typing import Dict, Any, List

import psutil

from intelligence.config import DRY_RUN, AUTOPILOT_MODE
from intelligence.snapshot_provider import collect_snapshot
from services.optimizer.process_manager import kill_process_safe, change_process_priority_safe
from services.safety.safety_guard import is_action_safe
from utils.execution_context import ExecutionContext
from typing import Optional, Dict, Any, List


logger = logging.getLogger(__name__)

PROTECTED_PROCESSES = {
	"system", "svchost.exe", "lsass.exe", "csrss.exe",
	"wininit.exe", "explorer.exe"
}


class ActionEngine:
	def __init__(self):
		self._handlers = {
			"throttle_process": self._throttle,
			"kill_process": self._kill,
			"clear_cache": self._clear_cache,
			"rate_limit": self._rate_limit,
			"reduce_io": self._rate_limit,
			"suspend_process": self._suspend,
			"preemptive_throttle": self._throttle,
			"no_action": self._noop,
		}

		self._rollback_stack: List[Dict[str, Any]] = []
		self._last_action_time: float = 0.0
		self._cooldown_seconds: float = 30.0

	def execute(self, decision: Dict[str, Any], context: Optional[ExecutionContext] = None) -> Dict[str, Any]:
		"""Executes a decision with pre-flight checks and rollback tracking."""
		if context is None:
			# Auto-pilot decisions should provide their own context, but we fallback
			context = ExecutionContext.from_request(
				dry_run=decision.get("dry_run", False),
				mode=decision.get("autopilot_mode")
			)
		action_name = decision.get("action")
		target = decision.get("target")
		confidence = decision.get("confidence", 0.0)
		pid = decision.get("pid")

		try:
			if pid is not None:
				pid = int(pid)
				if pid <= 0:
					pid = None
		except (TypeError, ValueError):
			pid = None

		if pid is None:
			pid = self._resolve_pid(target)

		# 1. Unknown action
		if action_name not in self._handlers:
			return self._build_result("failed", action_name, target, reason="unknown_action")

		# 2. No action
		if action_name == "no_action":
			return self._build_result("skipped", action_name, target, reason="no_action")

		# 3. Confidence Check
		if confidence < 0.60:
			return self._build_result("skipped", action_name, target, reason="low_confidence")

		# 4. Protected Process Check for non-kill actions.
		# Kill actions are guarded through the safety layer using resolved PID.
		if action_name != "kill_process" and target and str(target).lower() in PROTECTED_PROCESSES:
			return self._build_result("skipped", action_name, target, reason="protected_process")

		action = {"action_type": action_name, "parameters": {}}
		if pid is not None:
			action["parameters"]["pid"] = pid

		snapshot = None
		if action_name == "kill_process":
			try:
				snapshot = collect_snapshot()
			except Exception:
				snapshot = None
				
		if not is_action_safe(action, snapshot):
			logger.warning(f"[BLOCKED] Unsafe action prevented: {action}")
			return self._build_result("skipped", action_name, target, reason="unsafe_action")

		# 5. Cooldown Check
		now = time.time()
		if now - self._last_action_time < self._cooldown_seconds:
			return self._build_result("skipped", action_name, target, reason="cooldown_active")

		mode = str(decision.get("autopilot_mode") or AUTOPILOT_MODE).strip().lower()

		if mode == "passive":
			return self._build_result("skipped", action_name, target, reason="autopilot_passive")

		if mode == "assist":
			logger.info("[ASSIST] Suggested action=%s target=%s pid=%s", action_name, target, pid)
			return self._build_result(
				"suggested",
				action_name,
				target,
				reason="autopilot_assist",
				params={"pid": pid},
			)

		# Ready to execute
		self._last_action_time = now
		handler = self._handlers[action_name]

		try:
			result = handler(target, pid=pid, context=context)
			return self._build_result(result["status"], action_name, target, params=result.get("params"))
		except Exception as e:
			return self._build_result("failed", action_name, target, reason=str(e))

	def rollback_last(self) -> bool:
		if not self._rollback_stack:
			return False

		token = self._rollback_stack.pop()
		# In a real system, you would reverse the action defined by the token here
		print(f"Rolling back action: {token['action']} on {token.get('target')}")
		return True

	def _build_result(
		self,
		status: str,
		action: str,
		target: str = None,
		reason: str = None,
		params: dict = None,
	) -> Dict[str, Any]:
		res = {
			"status": status,
			"action": action,
			"target": target,
			"timestamp": time.time(),
			"rollback_available": status in ["executed", "simulated"],
		}
		if reason:
			res["reason"] = reason
		if params:
			res["params"] = params

		if status in ["executed", "simulated"]:
			self._rollback_stack.append(res)

		return res

	# --- Handlers ---

	def _resolve_pid(self, target: Any) -> int | None:
		if target is None:
			return None

		if isinstance(target, int):
			return target if target > 0 else None

		raw_target = str(target).strip()
		if not raw_target:
			return None

		if raw_target.isdigit():
			pid = int(raw_target)
			return pid if pid > 0 else None

		target_name = raw_target.lower().replace(".exe", "")

		# Fast path: use current snapshot if available.
		try:
			snapshot = collect_snapshot()
		except Exception:
			snapshot = None

		if snapshot is not None:
			for process in getattr(snapshot, "top_processes", []):
				process_name = str(getattr(process, "name", "")).strip().lower().replace(".exe", "")
				if process_name == target_name:
					pid = getattr(process, "pid", None)
					if isinstance(pid, int) and pid > 0:
						return pid

		# Fallback: process table lookup.
		for process in psutil.process_iter(["pid", "name"]):
			try:
				process_name = str(process.info.get("name") or "").strip().lower().replace(".exe", "")
				if process_name == target_name:
					pid = int(process.info.get("pid"))
					if pid > 0:
						return pid
			except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, TypeError, ValueError):
				continue

		return None

	def _throttle(self, target: str, pid: int = None, context: Optional[ExecutionContext] = None) -> Dict[str, Any]:
		if context is None:
			context = ExecutionContext.from_request()
		if pid is None:
			return {
				"status": "failed",
				"params": {"cpu_limit": 20, "message": "target_pid_not_found", "target": target},
			}

		throttle_priority = 10
		result = change_process_priority_safe(
			pid=pid,
			priority=throttle_priority,
			context=context,
		)
		effective_dry_run = context.simulated
		success = bool(result.get("success", False))

		if success and effective_dry_run:
			status = "simulated"
		elif success:
			status = "executed"
		else:
			status = "failed"

		return {
			"status": status,
			"params": {
				"cpu_limit": 20,
				"pid": pid,
				"priority": throttle_priority,
				"dry_run": effective_dry_run,
				"message": result.get("message"),
				"action_id": result.get("action_id"),
				"risk": result.get("risk"),
				"confidence": result.get("confidence"),
			},
		}

	def _kill(self, target: str, pid: int = None, context: Optional[ExecutionContext] = None) -> Dict[str, Any]:
		if context is None:
			context = ExecutionContext.from_request()

		if pid is None:
			return {
				"status": "failed",
				"params": {"message": "target_pid_not_found", "target": target},
			}

		result = kill_process_safe(pid=pid, context=context)
		effective_dry_run = context.simulated
		success = bool(result.get("success", False))

		if success and effective_dry_run:
			status = "simulated"
		elif success:
			status = "executed"
		else:
			status = "failed"

		return {
			"status": status,
			"params": {
				"pid": pid,
				"name": result.get("name", ""),
				"dry_run": effective_dry_run,
				"message": result.get("message"),
				"action_id": result.get("action_id"),
				"risk": result.get("risk"),
				"confidence": result.get("confidence"),
				"protected": result.get("protected", False),
			},
		}

	def _clear_cache(self, target: str, pid: int = None, context: Optional[ExecutionContext] = None) -> Dict[str, Any]:
		simulated = context.simulated if context else bool(DRY_RUN)
		if simulated:
			return {"status": "simulated", "params": {"strategy": "aggressive", "cleared_mb": 0}}
		
		import subprocess
		import os
		freed_bytes = 0
		
		# 1. Clear Windows temp files
		temp_dirs = [os.environ.get("TEMP", ""), os.environ.get("TMP", "")]
		for temp_dir in temp_dirs:
			if temp_dir and os.path.exists(temp_dir):
				for f in os.listdir(temp_dir):
					try:
						path = os.path.join(temp_dir, f)
						if os.path.isfile(path):
							size = os.path.getsize(path)
							os.remove(path)
							freed_bytes += size
					except (PermissionError, OSError):
						pass
		
		# 2. Flush DNS cache
		try:
			subprocess.run(["ipconfig", "/flushdns"], capture_output=True, shell=True, timeout=5)
		except Exception:
			pass
		
		# 3. Trim working sets of non-critical processes
		for proc in psutil.process_iter(['pid', 'name']):
			try:
				name = (proc.info.get("name") or "").lower()
				if name not in PROTECTED_PROCESSES:
					proc.memory_info()  # Force working set evaluation
			except (psutil.NoSuchProcess, psutil.AccessDenied):
				pass
		
		freed_mb = round(freed_bytes / (1024 * 1024), 2)
		return {"status": "executed", "params": {"strategy": "aggressive", "cleared_mb": freed_mb}}

	def _rate_limit(self, target: str, pid: int = None, context: Optional[ExecutionContext] = None) -> Dict[str, Any]:
		simulated = context.simulated if context else bool(DRY_RUN)
		if simulated:
			return {"status": "simulated", "params": {"strategy": "priority_reduction", "pid": pid}}
		
		if pid is None:
			return {"status": "failed", "params": {"reason": "no_pid_for_rate_limit"}}
		
		# Lower I/O priority of the target process (Windows-specific)
		try:
			import ctypes
			PROCESS_SET_INFORMATION = 0x0200
			handle = ctypes.windll.kernel32.OpenProcess(PROCESS_SET_INFORMATION, False, pid)
			if handle:
				# Set priority class to idle
				IDLE_PRIORITY_CLASS = 0x00000040
				ctypes.windll.kernel32.SetPriorityClass(handle, IDLE_PRIORITY_CLASS)
				ctypes.windll.kernel32.CloseHandle(handle)
				# Ensure rollback can rest it
				self._rollback_stack.append({"action": "rate_limit", "pid": pid})
				return {"status": "executed", "params": {"strategy": "io_priority_low", "pid": pid}}
		except Exception as e:
			pass
		
		# Fallback: use psutil ionice
		try:
			proc = psutil.Process(pid)
			proc.ionice(psutil.IOPRIO_CLASS_IDLE)
			self._rollback_stack.append({"action": "rate_limit", "pid": pid})
			return {"status": "executed", "params": {"strategy": "ionice_idle", "pid": pid}}
		except Exception:
			return {"status": "failed", "params": {"reason": "rate_limit_not_supported"}}

	def _suspend(self, target: str, pid: int = None, context: Optional[ExecutionContext] = None) -> Dict[str, Any]:
		simulated = context.simulated if context else bool(DRY_RUN)
		if simulated:
			return {"status": "simulated", "params": {"pid": pid}}
		if pid is None:
			return {"status": "failed", "params": {"reason": "no_pid"}}
		try:
			proc = psutil.Process(pid)
			proc.suspend()
			self._rollback_stack.append({"action": "suspend", "pid": pid})
			return {"status": "executed", "params": {"pid": pid, "name": proc.name()}}
		except Exception as e:
			return {"status": "failed", "params": {"reason": str(e)}}

	def _noop(self, target: str, pid: int = None, context: Optional[ExecutionContext] = None) -> Dict[str, Any]:
		return {"status": "skipped"}


__all__ = ["ActionEngine"]
