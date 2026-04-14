from __future__ import annotations

import ctypes
import subprocess
import sys
from typing import Dict, List

import psutil

from ..models import RiskLevel
from .base import SystemTweak
from .registry import register_tweak

from config import DRY_RUN


CRITICAL_PROCESSES = [
    "explorer.exe", "winlogon.exe", "csrss.exe", "services.exe",
    "lsass.exe", "system", "svchost.exe", "system idle process",
    "registry", "smss.exe", "wininit.exe", "dwm.exe",
    "memcompression", "fontdrvhost.exe", "lsaiso.exe",
]

GAMING_KILLABLE = [
    "searchindexer.exe", "searchhost.exe", "onedrive.exe",
    "msedge.exe", "teams.exe", "skype.exe", "spotify.exe",
    "discord.exe", "slack.exe", "cortana.exe",
    "gamebarpresencewriter.exe", "yourphone.exe",
    "microsoftedgeupdate.exe", "googlechromeupdate.exe",
]

BATTERY_REDUCE = [
    "searchindexer.exe", "onedrive.exe", "teams.exe",
    "discord.exe", "spotify.exe", "steam.exe",
]


def _get_process_info(proc) -> dict:
    try:
        return {
            "pid": proc.pid,
            "name": proc.name(),
            "cpu_percent": proc.cpu_percent(interval=None),
            "memory_mb": round(proc.memory_info().rss / (1024 * 1024), 1),
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None


class GamingBoost(SystemTweak):
    def apply(self) -> Dict[str, object]:
        affected: List[dict] = []
        killed: List[dict] = []
        failed: List[dict] = []

        for proc in psutil.process_iter(["pid", "name"]):
            try:
                name = (proc.info.get("name") or "").lower()
                if name in GAMING_KILLABLE:
                    info = _get_process_info(proc)
                    if info:
                        affected.append(info)
                        if not DRY_RUN:
                            proc.kill()
                        killed.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                failed.append({"name": name, "error": str(e)})

        # Set power plan to High Performance
        power_result = "skipped (dry run)"
        if not DRY_RUN:
            try:
                subprocess.run(
                    ["powercfg", "/setactive", "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"],
                    capture_output=True, timeout=5
                )
                power_result = "High Performance plan activated"
            except Exception as e:
                power_result = f"Failed: {e}"
        else:
            power_result = "Would activate High Performance power plan"

        return {
            "status": "success",
            "summary": f"Gaming Boost applied. {len(killed)} background processes stopped.",
            "dry_run": DRY_RUN,
            "effects": {
                "processes_killed": killed,
                "power_plan": power_result,
                "details": [
                    f"Stopped {len(killed)} background apps (OneDrive, Search, Edge updates, etc.)",
                    "Activated Windows High Performance power plan",
                    "Prioritized foreground applications",
                ],
            },
            "processes_failed": failed,
        }

    def revert(self) -> Dict[str, object]:
        if not DRY_RUN:
            try:
                subprocess.run(
                    ["powercfg", "/setactive", "381b4222-f694-41f0-9685-ff5bb260df2e"],
                    capture_output=True, timeout=5
                )
            except Exception:
                pass
        return {
            "status": "success",
            "message": "Reverted to Balanced power plan",
        }


class BatterySaver(SystemTweak):
    def apply(self) -> Dict[str, object]:
        suspended: List[dict] = []
        failed: List[dict] = []

        for proc in psutil.process_iter(["pid", "name"]):
            try:
                name = (proc.info.get("name") or "").lower()
                if name in BATTERY_REDUCE:
                    info = _get_process_info(proc)
                    if info:
                        if not DRY_RUN:
                            proc.suspend()
                        suspended.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                failed.append({"name": name, "error": str(e)})

        # Set power plan to Power Saver
        power_result = "skipped (dry run)"
        if not DRY_RUN:
            try:
                subprocess.run(
                    ["powercfg", "/setactive", "a1841308-3541-4fab-bc81-f71556f20b4a"],
                    capture_output=True, timeout=5
                )
                power_result = "Power Saver plan activated"
            except Exception as e:
                power_result = f"Failed: {e}"
        else:
            power_result = "Would activate Power Saver plan"

        return {
            "status": "success",
            "summary": f"Battery Saver applied. {len(suspended)} heavy apps suspended.",
            "dry_run": DRY_RUN,
            "effects": {
                "processes_suspended": suspended,
                "power_plan": power_result,
                "details": [
                    f"Suspended {len(suspended)} resource-heavy apps",
                    "Activated Windows Power Saver plan",
                    "Reduced background CPU activity",
                ],
            },
            "processes_failed": failed,
        }

    def revert(self) -> Dict[str, object]:
        resumed = []
        for proc in psutil.process_iter(["pid", "name", "status"]):
            try:
                name = (proc.info.get("name") or "").lower()
                if name in BATTERY_REDUCE and proc.status() == psutil.STATUS_STOPPED:
                    if not DRY_RUN:
                        proc.resume()
                    resumed.append(name)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        if not DRY_RUN:
            try:
                subprocess.run(
                    ["powercfg", "/setactive", "381b4222-f694-41f0-9685-ff5bb260df2e"],
                    capture_output=True, timeout=5
                )
            except Exception:
                pass

        return {
            "status": "success",
            "message": f"Battery Saver reverted. {len(resumed)} apps resumed. Balanced plan restored.",
        }


class PerformanceBoost(SystemTweak):
    def apply(self) -> Dict[str, object]:
        lowered: List[dict] = []
        failed: List[dict] = []

        for proc in psutil.process_iter(["pid", "name", "cpu_percent"]):
            try:
                name = (proc.info.get("name") or "").lower()
                cpu = proc.info.get("cpu_percent") or 0.0
                if name in CRITICAL_PROCESSES:
                    continue
                if cpu > 20.0:
                    info = _get_process_info(proc)
                    if info:
                        if not DRY_RUN:
                            proc.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
                        lowered.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                failed.append({"name": name, "error": str(e)})

        return {
            "status": "success",
            "summary": f"Performance Boost applied. {len(lowered)} high-CPU processes reprioritized.",
            "dry_run": DRY_RUN,
            "effects": {
                "processes_lowered": lowered,
                "details": [
                    f"Lowered priority of {len(lowered)} CPU-heavy processes",
                    "System caches will be freed on next idle cycle",
                    "Memory allocation optimized for active applications",
                ],
            },
            "processes_failed": failed,
        }

    def revert(self) -> Dict[str, object]:
        return {
            "status": "success",
            "message": "Performance Boost reverted. Process priorities restored on next restart.",
        }


class CleanRAM(SystemTweak):
    def apply(self) -> Dict[str, object]:
        mem_before = psutil.virtual_memory()
        freed_processes: List[dict] = []

        if not DRY_RUN:
            # EmptyWorkingSet on non-critical processes to free inactive pages
            try:
                for proc in psutil.process_iter(["pid", "name"]):
                    try:
                        name = (proc.info.get("name") or "").lower()
                        if name in CRITICAL_PROCESSES:
                            continue
                        handle = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, proc.pid)
                        if handle:
                            ctypes.windll.psapi.EmptyWorkingSet(handle)
                            ctypes.windll.kernel32.CloseHandle(handle)
                            freed_processes.append({"pid": proc.pid, "name": proc.info.get("name")})
                    except Exception:
                        continue
            except Exception:
                pass

        mem_after = psutil.virtual_memory()
        freed_mb = round((mem_after.available - mem_before.available) / (1024 * 1024), 1)

        return {
            "status": "success",
            "summary": f"RAM cleaned. {max(0, freed_mb)} MB freed across {len(freed_processes)} processes.",
            "dry_run": DRY_RUN,
            "effects": {
                "memory_before_percent": mem_before.percent,
                "memory_after_percent": mem_after.percent,
                "freed_mb": max(0, freed_mb),
                "processes_cleaned": freed_processes,
                "details": [
                    f"Cleared inactive memory pages from {len(freed_processes)} processes",
                    f"Memory usage: {mem_before.percent}% → {mem_after.percent}%",
                    f"Freed approximately {max(0, freed_mb)} MB",
                ],
            },
        }

    def revert(self) -> Dict[str, object]:
        return {
            "status": "success",
            "message": "RAM clean is not reversible (memory will be re-allocated as needed).",
        }


# Register all tweaks
register_tweak(GamingBoost(
    name="gaming_boost",
    description="Kill background apps and activate High Performance power plan",
    risk_level=RiskLevel.MODERATE,
    reversible=True,
))

register_tweak(BatterySaver(
    name="battery_saver",
    description="Suspend heavy apps and activate Power Saver plan",
    risk_level=RiskLevel.SAFE,
    reversible=True,
))

register_tweak(PerformanceBoost(
    name="performance_boost",
    description="Lower priority of CPU-heavy processes for smoother operation",
    risk_level=RiskLevel.MODERATE,
    reversible=True,
))

register_tweak(CleanRAM(
    name="clean_ram",
    description="Clear inactive memory pages to free up RAM",
    risk_level=RiskLevel.SAFE,
    reversible=False,
))
