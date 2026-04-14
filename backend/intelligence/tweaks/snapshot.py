from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Dict, List
import subprocess

import psutil


@dataclass
class SystemSnapshot:
    processes: List[dict]
    priorities: Dict[int, object]
    memory_state: Dict[str, object]
    power_plan: str
    timestamp: datetime

    def to_dict(self) -> Dict[str, object]:
        payload = asdict(self)
        payload["timestamp"] = self.timestamp.isoformat()
        return payload


class SnapshotEngine:
    @staticmethod
    def _get_power_plan() -> str:
        try:
            result = subprocess.run(
                ["powercfg", "/getactivescheme"],
                capture_output=True,
                text=True,
                timeout=3,
            )
            if result.returncode == 0:
                return (result.stdout or "").strip() or "unknown"
        except Exception:
            pass
        return "unknown"

    @staticmethod
    def capture() -> SystemSnapshot:
        processes: List[dict] = []
        priorities: Dict[int, object] = {}
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                pname = proc.info.get("name") or ""
                ppid = int(proc.info.get("pid"))
                priority = proc.nice()
                priorities[ppid] = priority
                processes.append({"pid": ppid, "name": pname})
            except Exception:
                continue

        vm = psutil.virtual_memory()
        memory_state = {
            "total": vm.total,
            "available": vm.available,
            "used": vm.used,
            "percent": vm.percent,
        }

        return SystemSnapshot(
            processes=processes,
            priorities=priorities,
            memory_state=memory_state,
            power_plan=SnapshotEngine._get_power_plan(),
            timestamp=datetime.now(timezone.utc),
        )

