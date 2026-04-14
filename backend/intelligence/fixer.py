# Fix engine for JOC

import time
import uuid

import psutil

from intelligence.action_store import ActionStore
from intelligence.config import DRY_RUN
from intelligence.constants import CRITICAL_PROCESSES
from intelligence.models import ActionRecord, ActionType
from services.optimizer.process_manager import kill_process_safe


class FixEngine:
    def kill_process_by_pid(self, pid: int) -> dict:
        result = kill_process_safe(pid=pid, dry_run=DRY_RUN)
        if not result.get("success", False):
            return {"error": result.get("message", f"Failed to terminate process {pid}")}

        response = {
            "action": "kill_process_pid",
            "pid": pid,
            "name": result.get("name", ""),
            "simulated": bool(result.get("dry_run", False)),
        }
        if result.get("action_id"):
            response["action_id"] = result["action_id"]
        return response
    def __init__(self) -> None:
        self.store = ActionStore()

    def _build_action_record(
        self,
        action_type: ActionType,
        target: str,
        reversible: bool,
        result: dict,
        parameters: dict,
    ) -> ActionRecord:
        result_status = str(result.get("status", "")).lower() if isinstance(result, dict) else ""
        if result_status in {"failed", "error", "blocked"}:
            status = "failed"
        else:
            status = "success"
        return ActionRecord(
            action_id=str(uuid.uuid4()),
            action_type=action_type,
            target=target,
            timestamp=time.time(),
            status=status,
            reversible=reversible,
            result=result,
            parameters=parameters,
        )

    def kill_process_by_name(self, process_name: str) -> dict:
        """
        Attempts to kill all processes matching the given name.
        """

        normalized_target = process_name.lower().replace(".exe", "")
        if normalized_target in CRITICAL_PROCESSES:
            result = {
                "error": f"Refusing to kill critical process: {process_name}"
            }
            record = self._build_action_record(
                action_type=ActionType.KILL_PROCESS,
                target=process_name,
                reversible=False,
                result=result,
                parameters={},
            )
            self.store.add_action(record)
            response = dict(result)
            response["action_id"] = record.action_id
            return response

        killed = []
        failed = []

        for proc in psutil.process_iter(["pid", "name"]):
            try:
                name = proc.info.get("name")

                if not name:
                    continue

                target = normalized_target
                proc_name = name.lower().replace(".exe", "")

                if proc_name in CRITICAL_PROCESSES:
                    continue

                if target == proc_name:
                    outcome = kill_process_safe(pid=proc.info["pid"], dry_run=DRY_RUN)
                    if outcome.get("success", False):
                        killed.append(proc.info["pid"])
                    else:
                        failed.append({
                            "pid": proc.info.get("pid"),
                            "error": outcome.get("message", "Failed to terminate process")
                        })

            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                failed.append({
                    "pid": proc.info.get("pid"),
                    "error": str(e)
                })

        if not killed:
            result = {
                "action": "kill_process",
                "target": process_name,
                "killed_pids": [],
                "failed": failed,
                "warning": "No matching process found"
            }
        else:
            result = {
                "action": "kill_process",
                "target": process_name,
                "killed_pids": killed,
                "failed": failed
            }
        record = self._build_action_record(
            action_type=ActionType.KILL_PROCESS,
            target=process_name,
            reversible=False,
            result=result,
            parameters={},
        )
        self.store.add_action(record)
        response = dict(result)
        response["action_id"] = record.action_id
        return response

    def execute_tweak(
        self,
        tweak_name: str,
        dry_run: bool = None,
        confirm_high_risk: bool = False,
    ) -> dict:
        from intelligence.tweaks.executor import execute_tweak
        from intelligence.tweaks.registry import get_tweak

        result = execute_tweak(
            tweak_name,
            dry_run=dry_run,
            confirm_high_risk=confirm_high_risk,
        )
        tweak = get_tweak(tweak_name)
        is_preview = bool(result.get("simulated", dry_run))
        is_reversible = bool(getattr(tweak, "reversible", False)) and not is_preview
        record = self._build_action_record(
            action_type=ActionType.SYSTEM_TWEAK,
            target=tweak_name,
            reversible=is_reversible,
            result=result,
            parameters={
                "requested_dry_run": dry_run,
                "confirm_high_risk": confirm_high_risk,
            },
        )
        self.store.add_action(record)
        return {
            "action_id": record.action_id,
            "result": result
        }

    def revert_action(self, action_id: str) -> dict:
        from intelligence.tweaks.executor import revert_tweak

        action = self.store.get_action_by_id(action_id)
        if action is None:
            return {"error": f"Action not found: {action_id}"}

        if not action.reversible:
            return {"error": f"Action is not reversible: {action_id}"}

        if action.action_type == ActionType.SYSTEM_TWEAK:
            result = revert_tweak(
                action.target,
                dry_run=False,
                revert_payload={
                    "original_result": action.result,
                    "original_parameters": action.parameters,
                },
            )
            record = self._build_action_record(
                action_type=ActionType.SYSTEM_TWEAK,
                target=action.target,
                reversible=False,
                result=result,
                parameters={"reverted_action_id": action_id},
            )
            self.store.add_action(record)
            return {
                "result": result,
                "action_id": record.action_id,
            }

        return {"error": f"Unsupported reversible action type: {action.action_type.value}"}
