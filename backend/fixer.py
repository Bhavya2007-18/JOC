# Fix engine for JOC

import psutil


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
    def kill_process_by_name(self, process_name: str) -> dict:
        """
        Attempts to kill all processes matching the given name.
        """

        if process_name.lower() in CRITICAL_PROCESSES:
            return {
                "error": f"Refusing to kill critical process: {process_name}"
            }

        killed = []
        failed = []

        for proc in psutil.process_iter(["pid", "name"]):
            try:
                if proc.info["name"] == process_name:
                    proc.kill()
                    killed.append(proc.info["pid"])
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                failed.append({
                    "pid": proc.info.get("pid"),
                    "error": str(e)
                })

        return {
            "action": "kill_process",
            "target": process_name,
            "killed_pids": killed,
            "failed": failed
        }