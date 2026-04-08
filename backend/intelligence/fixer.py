# Fix engine for JOC

import time
import uuid

import psutil

from intelligence.action_store import ActionStore
from intelligence.models import ActionRecord, ActionType

from config import DRY_RUN


CRITICAL_PROCESSES = [
    "explorer.exe",
    "winlogon.exe",
    "csrss.exe",
    "services.exe",
    "lsass.exe",
    "system",
    "svchost.exe",
]


class FixEngine:
    def kill_process_by_pid(self, pid: int) -> dict:
        try:
            proc = psutil.Process(pid)
            name = proc.name()

            if name.lower() in CRITICAL_PROCESSES:
                return {"error": f"Refusing to kill critical process: {name}"}

            if DRY_RUN:
                result = {
                    "action": "kill_process_pid",
                    "pid": pid,
                    "name": name,
                    "simulated": True
                }
            else:
                proc.kill()
                result = {
                    "action": "kill_process_pid",
                    "pid": pid,
                    "name": name,
                    "simulated": False
                }

            record = self._build_action_record(
                action_type=ActionType.KILL_PROCESS,
                target=name,
                reversible=False,
                result=result,
                parameters={"pid": pid},
            )

            self.store.add_action(record)

            response = dict(result)
            response["action_id"] = record.action_id
            return response

        except psutil.NoSuchProcess:
            return {"error": f"No process found with PID {pid}"}
        except psutil.AccessDenied:
            return {"error": f"Access denied to process {pid}"}
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
        status = "failed" if "error" in result else "success"
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

        if process_name.lower() in CRITICAL_PROCESSES:
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

                target = process_name.lower().replace(".exe", "")
                proc_name = name.lower().replace(".exe", "")

                if target in proc_name:
                    if DRY_RUN:
                        killed.append(proc.info["pid"])
                    else:
                        proc.kill()
                        killed.append(proc.info["pid"])

            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                failed.append({
                    "pid": proc.info.get("pid"),
                    "error": str(e)
                })

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

    def execute_tweak(self, tweak_name: str) -> dict:
        from intelligence.tweaks.executor import execute_tweak

        result = execute_tweak(tweak_name)
        record = self._build_action_record(
            action_type=ActionType.SYSTEM_TWEAK,
            target=tweak_name,
            reversible=True,
            result=result,
            parameters={},
        )
        self.store.add_action(record)
        response = dict(result)
        response["action_id"] = record.action_id
        return response

    def revert_action(self, action_id: str) -> dict:
        from intelligence.tweaks.executor import revert_tweak

        action = self.store.get_action_by_id(action_id)
        if action is None:
            return {"error": f"Action not found: {action_id}"}

        if not action.reversible:
            return {"error": f"Action is not reversible: {action_id}"}

        if action.action_type == ActionType.SYSTEM_TWEAK:
            result = revert_tweak(action.target)
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