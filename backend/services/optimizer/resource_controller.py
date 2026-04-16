from typing import Any, Dict, List, Optional, Tuple

import psutil

from utils.execution_context import ExecutionContext
from models.optimizer_models import ActionType
from services.system_monitor import get_cpu_stats, get_memory_stats
from utils.logger import get_logger

from .process_manager import change_process_priority_safe, _map_priority_for_platform, _prepare_process, _is_protected_process


logger = get_logger("optimizer.resource")
_action_store = ActionStore()


def _calculate_optimization_score() -> float:
    cpu = get_cpu_stats()
    mem = get_memory_stats()

    cpu_percent = float(cpu.get("usage_percent", 0.0))
    mem_percent = float(mem.get("percent", 0.0))

    cpu_score = max(0.0, 100.0 - cpu_percent)
    mem_score = max(0.0, 100.0 - mem_percent)

    return round((cpu_score * 0.6 + mem_score * 0.4), 2)


def analyze_system_load(cpu_threshold: float, max_processes: int) -> List[Dict[str, Any]]:
    processes: List[Dict[str, Any]] = []

    for proc in psutil.process_iter(attrs=["pid", "name", "cpu_percent", "nice"]):
        try:
            info = proc.info
            cpu_percent = info.get("cpu_percent")
            if cpu_percent is None:
                cpu_percent = proc.cpu_percent(interval=None)

            if float(cpu_percent) < cpu_threshold:
                continue

            protected = _is_protected_process(proc)
            processes.append(
                {
                    "pid": int(info["pid"]),
                    "name": info.get("name") or "unknown",
                    "cpu_percent": float(cpu_percent),
                    "current_priority": info.get("nice"),
                    "protected": protected,
                }
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    processes.sort(key=lambda item: item["cpu_percent"], reverse=True)
    return processes[:max_processes]


def boost_system_performance(cpu_threshold: float, max_processes: int, context: Optional[ExecutionContext] = None, dry_run: bool = False) -> Dict[str, Any]:
    if context is None:
        context = ExecutionContext.from_request(dry_run=dry_run)
    
    effective_dry_run = context.simulated
    heavy_processes = analyze_system_load(cpu_threshold=cpu_threshold, max_processes=max_processes)
    score_before = _calculate_optimization_score()

    boosted: List[Dict[str, Any]] = []

    for proc_info in heavy_processes:
        pid = proc_info["pid"]
        name = proc_info["name"]
        protected = proc_info["protected"]
        current_nice = proc_info.get("current_priority")

        suggested_priority = 10 if not psutil.WINDOWS else 0

        if protected:
            logger.info("Skipping boost for protected process pid=%s name=%s", pid, name)
            boosted.append(
                {
                    "pid": pid,
                    "name": name,
                    "cpu_percent": proc_info["cpu_percent"],
                    "old_priority": current_nice,
                    "new_priority": current_nice,
                    "changed": False,
                    "protected": True,
                    "dry_run": effective_dry_run,
                    "action_id": None,
                }
            )
            continue

        if effective_dry_run:
            logger.info(
                "Dry-run boost for pid=%s name=%s cpu=%s current_priority=%s suggested=%s",
                pid,
                name,
                proc_info["cpu_percent"],
                current_nice,
                suggested_priority,
            )
            boosted.append(
                {
                    "pid": pid,
                    "name": name,
                    "cpu_percent": proc_info["cpu_percent"],
                    "old_priority": current_nice,
                    "new_priority": _map_priority_for_platform(suggested_priority),
                    "changed": True,
                    "protected": False,
                    "dry_run": True,
                    "action_id": None,
                }
            )
            context.log_action("boost_system", {"pid": pid, "name": name, "suggested": suggested_priority})
            continue

        result = change_process_priority_safe(pid=pid, priority=suggested_priority, context=context)

        boosted.append(
            {
                "pid": pid,
                "name": name,
                "cpu_percent": proc_info["cpu_percent"],
                "old_priority": current_nice,
                "new_priority": _map_priority_for_platform(suggested_priority),
                "changed": bool(result.get("success", False)),
                "protected": False,
                "dry_run": effective_dry_run,
                "action_id": result.get("action_id"),
            }
        )

    score_after = _calculate_optimization_score()

    logger.info(
        "Boost finished dry_run=%s score_before=%s score_after=%s processes=%s",
        effective_dry_run,
        score_before,
        score_after,
        len(boosted),
    )

    risk = "low"
    confidence = 0.8
    if not dry_run and score_after < score_before:
        risk = "medium"
        confidence = 0.85

    return {
        "success": True,
        "message": "Boost executed" if not effective_dry_run else "Dry-run: boost simulated",
        "dry_run": effective_dry_run,
        "optimization_score_before": score_before,
        "optimization_score_after": score_after,
        "processes": boosted,
        "risk": risk,
        "confidence": confidence,
    }


def get_optimization_suggestions(cpu_threshold: float, max_processes: int) -> Dict[str, Any]:
    heavy_processes = analyze_system_load(cpu_threshold=cpu_threshold, max_processes=max_processes)
    score = _calculate_optimization_score()

    high_cpu_suggestions: List[Dict[str, Any]] = []
    actions: List[Dict[str, Any]] = []

    for proc_info in heavy_processes:
        pid = proc_info["pid"]
        name = proc_info["name"]
        cpu_percent = proc_info["cpu_percent"]
        current_priority = proc_info.get("current_priority")
        protected = proc_info["protected"]

        suggested_priority = 10 if not psutil.WINDOWS else 0
        reason = f"Process uses {cpu_percent:.1f}% CPU"

        high_cpu_suggestions.append(
            {
                "pid": pid,
                "name": name,
                "cpu_percent": cpu_percent,
                "current_priority": current_priority,
                "suggested_priority": suggested_priority if not protected else None,
                "reason": reason,
                "protected": protected,
            }
        )

        if not protected:
            actions.append(
                {
                    "action_type": "lower_priority",
                    "target": str(pid),
                    "reason": reason,
                    "dry_run_only": True,
                }
            )

    logger.info(
        "Generated optimization suggestions score=%s high_cpu=%s",
        score,
        len(high_cpu_suggestions),
    )

    return {
        "optimization_score": score,
        "high_cpu_processes": high_cpu_suggestions,
        "recommended_actions": actions,
    }
