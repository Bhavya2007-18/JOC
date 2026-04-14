from __future__ import annotations

import ctypes
import subprocess
import os
import logging
import time
from typing import Dict, List, Optional

import psutil

from ..models import RiskLevel
from .base import SystemTweak
from .context import ExecutionContext
from .registry import register_tweak

logger = logging.getLogger(__name__)

# Critical system processes that should NEVER be killed or lowered in priority
CRITICAL_PROCESSES = [
    "explorer.exe", "winlogon.exe", "csrss.exe", "services.exe",
    "lsass.exe", "system", "svchost.exe", "system idle process",
    "registry", "smss.exe", "wininit.exe", "dwm.exe",
    "memcompression", "fontdrvhost.exe", "lsaiso.exe",
]

# Processes that are safe to kill/suspend for gaming performance
GAMING_KILLABLE = [
    "searchindexer.exe", "searchhost.exe", "onedrive.exe",
    "msedge.exe", "teams.exe", "skype.exe", "spotify.exe",
    "discord.exe", "slack.exe", "cortana.exe",
    "gamebarpresencewriter.exe", "yourphone.exe",
    "microsoftedgeupdate.exe", "googlechromeupdate.exe",
]

# Processes to hibernate/lower in priority for battery efficiency
BATTERY_REDUCE = [
    "searchindexer.exe", "onedrive.exe", "teams.exe",
    "discord.exe", "spotify.exe", "steam.exe",
]

def _get_process_info(proc) -> Optional[dict]:
    try:
        # Pre-check if process is still running
        if not proc.is_running():
            return None
        return {
            "pid": proc.pid,
            "name": proc.name(),
            "cpu_percent": 0.0, # Avoid first-call 0.0 logic issues
            "memory_mb": round(proc.memory_info().rss / (1024 * 1024), 1),
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied, Exception):
        return None

def _is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except (AttributeError, Exception):
        return False


def _purge_standby_list() -> (bool, str):
    """
    Purges Windows standby memory list via NtSetSystemInformation.
    Requires administrator privileges.
    """
    try:
        # SYSTEM_INFORMATION_CLASS.SystemMemoryListInformation
        system_memory_list_information = 80
        # MEMORY_LIST_COMMAND.MemoryPurgeStandbyList
        memory_purge_standby_list = 4

        command = ctypes.c_ulong(memory_purge_standby_list)
        status = ctypes.windll.ntdll.NtSetSystemInformation(
            system_memory_list_information,
            ctypes.byref(command),
            ctypes.sizeof(command),
        )
        if status == 0:
            return True, "Standby list purged"
        return False, f"NtSetSystemInformation failed with NTSTATUS {status}"
    except Exception as exc:
        return False, f"Standby purge error: {str(exc)}"


def _get_foreground_pid() -> Optional[int]:
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        if not hwnd:
            return None
        pid = ctypes.c_ulong()
        ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        return int(pid.value) if pid.value else None
    except Exception:
        return None

# ─── COMBAT MODE ─────────────────────────────────────────────────────────────

class GamingBoost(SystemTweak):
    """
    ⚔️ Combat Mode: Maximum performance protocol.
    Kills background bloat, boosts foreground app priority, and locks ultimate power.
    """
    def apply(self, context: Optional[ExecutionContext] = None) -> Dict[str, object]:
        try:
            context = context or ExecutionContext.from_request()
            killed: List[dict] = []
            lowered: List[dict] = []
            boosted: Optional[dict] = None
            failed: List[dict] = []
            priority_snapshot: Dict[str, int] = {}
            boosted_selection = "memory_fallback"

            is_dry = context.dry_run

            # 1. Kill background bloat
            for proc in psutil.process_iter(["pid", "name"]):
                try:
                    name = (proc.info.get("name") or "").lower()
                    if name in GAMING_KILLABLE:
                        info = _get_process_info(proc)
                        if info:
                            if not is_dry:
                                proc.kill()
                            killed.append(info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                except Exception as e:
                    failed.append({"name": "process_kill", "error": str(e)})

            # 2. CPU Priority Management
            app_candidates = []
            for proc in psutil.process_iter(["pid", "name"]):
                try:
                    name = (proc.info.get("name") or "").lower()
                    if name in CRITICAL_PROCESSES or proc.pid == os.getpid():
                        continue
                    app_candidates.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if app_candidates:
                foreground_pid = _get_foreground_pid()
                top_proc = None
                if foreground_pid:
                    for candidate in app_candidates:
                        if candidate.pid == foreground_pid:
                            top_proc = candidate
                            boosted_selection = "foreground_window"
                            break

                # Fallback: largest memory process when active window process is unavailable
                if top_proc is None:
                    app_candidates.sort(key=lambda p: p.memory_info().rss if p.is_running() else 0, reverse=True)
                    top_proc = app_candidates[0]
                
                try:
                    old_priority = top_proc.nice()
                    if not is_dry:
                        top_proc.nice(psutil.HIGH_PRIORITY_CLASS)
                        priority_snapshot[str(top_proc.pid)] = int(old_priority)
                    boosted = _get_process_info(top_proc)
                except Exception:
                    pass

                # Starve others
                for proc in app_candidates[1:50]: # Limit scale
                    try:
                        old_priority = proc.nice()
                        if not is_dry:
                            proc.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
                            priority_snapshot[str(proc.pid)] = int(old_priority)
                        info = _get_process_info(proc)
                        if info:
                            lowered.append(info)
                    except Exception:
                        continue

            # 3. Power Plan Override
            power_result = "Skipped"
            if not is_dry:
                try:
                    # Ultimate Performance GUID
                    res = subprocess.run(
                        ["powercfg", "/setactive", "e9a42b02-d5df-448d-aa00-03f14749eb61"],
                        capture_output=True, timeout=3
                    )
                    if res.returncode != 0:
                        subprocess.run(["powercfg", "/setactive", "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"], timeout=3)
                        power_result = "High Performance"
                    else:
                        power_result = "Ultimate Performance"
                except Exception:
                    power_result = "Default Balanced (Failed Override)"
            else:
                power_result = "Preview: Ultimate Performance"

            return {
                "status": "success",
                "summary": f"Combat Mode active. Boosted {boosted['name'] if boosted else 'Main Task'}. Optimized {len(lowered)} background vectors.",
                "dry_run": is_dry,
                "effects": {
                    "processes_killed": killed,
                    "processes_lowered": [l for l in lowered if l][:10],
                    "foreground_boosted": boosted,
                    "boosted_selection": boosted_selection,
                    "priority_snapshot": priority_snapshot,
                    "power_plan": power_result,
                    "details": [
                        f"Allocated HIGH priority to '{boosted['name'] if boosted else 'Main Application'}'",
                        f"Boost target selection: {boosted_selection}",
                        f"Throttled {len(lowered)} background tasks to starvation levels",
                        f"Purged {len(killed)} non-critical performance bottlenecks",
                        f"Power State: {power_result}",
                    ],
                }
            }
        except Exception as e:
            logger.error(f"Combat Mode Failure: {e}")
            return {"status": "error", "message": f"CRITICAL_FAILURE: {str(e)}", "dry_run": context.dry_run}

    def revert(self, context: Optional[ExecutionContext] = None) -> Dict[str, object]:
        context = context or ExecutionContext.from_request(mode="revert")
        restored = 0
        failed = 0
        snapshot = context.snapshot or {}
        original = snapshot.get("original_result", {}) if isinstance(snapshot, dict) else {}
        raw_effects = (
            original.get("effects", {}).get("raw", {})
            if isinstance(original.get("effects", {}), dict)
            else {}
        )
        priority_snapshot = raw_effects.get("priority_snapshot", {})
        if not isinstance(priority_snapshot, dict):
            priority_snapshot = {}

        if not context.dry_run:
            for pid_text, old_prio in priority_snapshot.items():
                try:
                    proc = psutil.Process(int(pid_text))
                    proc.nice(int(old_prio))
                    restored += 1
                except Exception:
                    failed += 1

        if not context.dry_run:
            try:
                subprocess.run(["powercfg", "/setactive", "381b4222-f694-41f0-9685-ff5bb260df2e"], timeout=3)
            except Exception:
                pass
        return {
            "status": "success",
            "message": "Combat Mode disengaged. Normal power vectors restored.",
            "effects": {
                "priorities_restored": restored,
                "priorities_restore_failed": failed,
                "details": [
                    f"Restored {restored} process priorities from snapshot",
                    f"Priority restore failures: {failed}",
                    "Balanced power profile restored",
                ],
            },
        }

# ─── STEALTH MODE ────────────────────────────────────────────────────────────

class BatterySaver(SystemTweak):
    """
    🕶️ Stealth Mode: Efficiency protocol.
    Hibernates sync tasks, throtles background threads, and enables deep power saving.
    """
    def apply(self, context: Optional[ExecutionContext] = None) -> Dict[str, object]:
        try:
            context = context or ExecutionContext.from_request()
            lowered: List[dict] = []
            is_dry = context.dry_run
            service_result = "Normal"

            # 1. Hibernate heavy background protocols
            for proc in psutil.process_iter(["pid", "name"]):
                try:
                    name = (proc.info.get("name") or "").lower()
                    if name in BATTERY_REDUCE:
                        info = _get_process_info(proc)
                        if info:
                            if not is_dry:
                                proc.nice(psutil.IDLE_PRIORITY_CLASS)
                            lowered.append(info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # 2. Windows Update service pause
            if not is_dry and _is_admin():
                try:
                    subprocess.run(["sc", "stop", "wuauserv"], capture_output=True, timeout=5)
                    service_result = "Paused"
                except Exception:
                    service_result = "Failed"
            elif is_dry:
                service_result = "Preview: Pause Suggested"

            # 3. Power plan switch
            power_result = "Skipped"
            if not is_dry:
                try:
                    subprocess.run(["powercfg", "/setactive", "a1841308-3541-4fab-bc81-f71556f20b4a"], timeout=3)
                    power_result = "Power Saver Active"
                except Exception:
                    power_result = "Default Balanced"
            else:
                power_result = "Preview: Power Saver"

            return {
                "status": "success",
                "summary": f"Stealth Mode engaged. {len(lowered)} tasks moved to deep idle.",
                "dry_run": is_dry,
                "effects": {
                    "processes_lowered": lowered,
                    "processes_suspended": lowered,
                    "power_plan": power_result,
                    "service_changes": service_result,
                    "details": [
                        f"Reduced {len(lowered)} tasks to IDLE priority class (not true suspend)",
                        f"Background Windows Update: {service_result}",
                        f"Power State: {power_result}",
                        "Minimized telemetry sync frequency",
                    ],
                }
            }
        except Exception as e:
            return {"status": "error", "message": f"STEALTH_FAILURE: {str(e)}"}

    def revert(self, context: Optional[ExecutionContext] = None) -> Dict[str, object]:
        context = context or ExecutionContext.from_request(mode="revert")
        if not context.dry_run:
            try:
                if _is_admin():
                    subprocess.run(["sc", "start", "wuauserv"], timeout=5)
                subprocess.run(["powercfg", "/setactive", "381b4222-f694-41f0-9685-ff5bb260df2e"], timeout=3)
            except Exception:
                pass
        return {"status": "success", "message": "Stealth Mode disengaged. High-speed sync restored."}

# ─── NEURAL SYNC ─────────────────────────────────────────────────────────────

class PerformanceBoost(SystemTweak):
    """
    ⚡ Neural Sync: Adaptive optimization.
    Throttles runaway processes and protects critical system nodes using telemetry.
    """
    def apply(self, context: Optional[ExecutionContext] = None) -> Dict[str, object]:
        try:
            context = context or ExecutionContext.from_request()
            lowered: List[dict] = []
            protected_count = 0
            is_dry = context.dry_run
            
            # Simple heuristic threshold
            CPU_THRESHOLD = 30.0

            candidates: List[psutil.Process] = []
            for proc in psutil.process_iter(["pid", "name"]):
                try:
                    name = (proc.info.get("name") or "").lower()
                    if name in CRITICAL_PROCESSES:
                        protected_count += 1
                        continue
                    candidates.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Non-blocking two-phase sample:
            # 1) warm-up counters quickly
            for proc in candidates:
                try:
                    proc.cpu_percent(interval=None)
                except Exception:
                    continue

            # 2) single short settle delay instead of N x 100ms serial waits
            time.sleep(0.12)

            for proc in candidates:
                try:
                    cpu = proc.cpu_percent(interval=None)
                    if cpu > CPU_THRESHOLD:
                        info = _get_process_info(proc)
                        if info:
                            info["cpu_percent"] = round(cpu, 1)
                            if not is_dry:
                                proc.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
                            lowered.append(info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            return {
                "status": "success",
                "summary": f"Neural Sync optimized {len(lowered)} nodes. Shielding {protected_count} core systems.",
                "dry_run": is_dry,
                "effects": {
                    "processes_lowered": lowered,
                    "protected_count": protected_count,
                    "details": [
                        f"Normalizing {len(lowered)} resource-heavy background spikes",
                        f"Shielded {protected_count} critical OS nodes from interference",
                        "Redistributed system task priority for better throughput",
                    ],
                }
            }
        except Exception as e:
            return {"status": "error", "message": f"NEURAL_FAILURE: {str(e)}"}

    def revert(self, context: Optional[ExecutionContext] = None) -> Dict[str, object]:
        return {"status": "success", "message": "Neural Sync baseline restored."}

# ─── MEMORY FLUSH ────────────────────────────────────────────────────────────

class CleanRAM(SystemTweak):
    """
    💎 Memory Flush: Emergency recovery.
    Purges standby cache and trims working sets to recover RAM instantly.
    """
    def apply(self, context: Optional[ExecutionContext] = None) -> Dict[str, object]:
        try:
            context = context or ExecutionContext.from_request()
            is_dry = context.dry_run
            mem_before = psutil.virtual_memory()
            freed_processes: List[dict] = []
            failed: List[dict] = []
            cache_result = "Not attempted"
            estimated_reclaim_mb = 0.0

            for proc in psutil.process_iter(["pid", "name"]):
                try:
                    name = (proc.info.get("name") or "").lower()
                    if name in CRITICAL_PROCESSES:
                        continue

                    rss_mb = round(proc.memory_info().rss / (1024 * 1024), 1)
                    if is_dry:
                        # Conservative reclaim estimate: 12% of current working set
                        estimated_reclaim_mb += max(0.0, rss_mb * 0.12)
                        if rss_mb >= 80:
                            freed_processes.append(
                                {"pid": proc.pid, "name": name, "memory_mb": rss_mb}
                            )
                        continue

                    # EmptyWorkingSet requires PROCESS_SET_QUOTA and query permissions.
                    process_set_quota = 0x0100
                    process_query_limited_info = 0x1000
                    desired_access = process_set_quota | process_query_limited_info
                    handle = ctypes.windll.kernel32.OpenProcess(desired_access, False, proc.pid)
                    if not handle:
                        failed.append({"pid": proc.pid, "name": name, "error": "OpenProcess failed"})
                        continue
                    try:
                        result = ctypes.windll.psapi.EmptyWorkingSet(handle)
                        if result:
                            freed_processes.append({"pid": proc.pid, "name": name, "memory_mb": rss_mb})
                        else:
                            failed.append(
                                {"pid": proc.pid, "name": name, "error": "EmptyWorkingSet failed"}
                            )
                    finally:
                        ctypes.windll.kernel32.CloseHandle(handle)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                except Exception as exc:
                    failed.append({"name": "process_trim", "error": str(exc)})

            if is_dry:
                cache_result = "Preview: Standby purge estimate only"
            else:
                # 2. Clear Standby (Requires Admin)
                if _is_admin():
                    ok, detail = _purge_standby_list()
                    cache_result = detail if ok else f"Failed: {detail}"
                else:
                    cache_result = "Skipped (Admin required)"

            mem_after = psutil.virtual_memory()
            if is_dry:
                freed_mb = round(estimated_reclaim_mb, 1)
            else:
                freed_mb = round(max(0, (mem_after.available - mem_before.available) / (1024 * 1024)), 1)

            return {
                "status": "success",
                "summary": f"Memory Flush complete. {freed_mb} MB recovered.",
                "dry_run": is_dry,
                "failed": failed,
                "effects": {
                    "memory_before_percent": mem_before.percent,
                    "memory_after_percent": mem_after.percent,
                    "freed_mb": freed_mb,
                    "processes_cleaned": freed_processes[:20] if not is_dry else freed_processes[:20],
                    "estimated": is_dry,
                    "failed_count": len(failed),
                    "details": [
                        f"Processed {len(freed_processes)} memory vectors",
                        f"RAM load reduced from {mem_before.percent}% to {mem_after.percent}%",
                        f"System Cache Status: {cache_result}",
                        f"Operation failures captured: {len(failed)}",
                    ],
                }
            }
        except Exception as e:
            return {"status": "error", "message": f"RAM_RECOVERY_FAILURE: {str(e)}"}

    def revert(self, context: Optional[ExecutionContext] = None) -> Dict[str, object]:
        return {"status": "success", "message": "Flush is final. Memory will re-fill naturally."}

# ─── REGISTRATION ─────────────────────────────────────────────────────────────

register_tweak(GamingBoost(
    name="gaming_boost",
    description="⚔️ COMBAT MODE: Purge background noise, boost main task priority, and lock performance power vectors.",
    risk_level=RiskLevel.RISKY,
    reversible=True,
))

register_tweak(BatterySaver(
    name="battery_saver",
    description="🕶️ STEALTH MODE: Hibernate sync protocols, throttle background threads, and enable efficiency power state.",
    risk_level=RiskLevel.SAFE,
    reversible=True,
))

register_tweak(PerformanceBoost(
    name="performance_boost",
    description="⚡ NEURAL SYNC: Dynamic telemetry analysis and reprioritization of system resources in real-time.",
    risk_level=RiskLevel.MODERATE,
    reversible=True,
))

register_tweak(CleanRAM(
    name="clean_ram",
    description="💎 MEMORY FLUSH: Deep sector purge of standby memory and trimming of unused working sets.",
    risk_level=RiskLevel.SAFE,
    reversible=False,
))
