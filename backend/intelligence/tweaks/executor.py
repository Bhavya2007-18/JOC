from __future__ import annotations

from typing import Dict, Optional
import logging
import time

from .context import ExecutionContext
from .guard import GuardReport, ExecutionGuard
from .registry import get_tweak
from .snapshot import SnapshotEngine

logger = logging.getLogger(__name__)


def _normalized_status(raw_status: str, has_warnings: bool, has_failures: bool) -> str:
    status = (raw_status or "").lower()
    if status in {"error", "failed"}:
        return "failed"
    if status == "blocked":
        return "blocked"
    if has_failures or has_warnings:
        return "partial"
    return "success"


def _extract_targets(effects: Dict[str, object]) -> list:
    for key in (
        "processes_killed",
        "processes_suspended",
        "processes_lowered",
        "processes_cleaned",
    ):
        value = effects.get(key)
        if isinstance(value, list):
            return value
    return []


def _build_action_result(
    tweak_name: str,
    context: ExecutionContext,
    raw_result: Dict[str, object],
    guard: GuardReport,
) -> Dict[str, object]:
    duration_ms = int((time.time() - context.started_at) * 1000)
    effects = raw_result.get("effects", {})
    if not isinstance(effects, dict):
        effects = {}

    targets = _extract_targets(effects)
    failed_targets = raw_result.get("failed", [])
    has_failures = isinstance(failed_targets, list) and len(failed_targets) > 0
    status = _normalized_status(
        raw_status=str(raw_result.get("status", "success")),
        has_warnings=len(guard.warnings) > 0,
        has_failures=has_failures,
    )

    standardized = {
        "mode": context.mode,
        "tweak": tweak_name,
        "status": status,
        "simulated": context.simulated,
        "dry_run": context.dry_run,  # Backward compatibility
        "summary": raw_result.get("summary", ""),
        "message": raw_result.get("message", ""),
        "effects": {
            "targets": targets,
            "power_plan": effects.get("power_plan"),
            "memory_freed": effects.get("freed_mb"),
            "details": effects.get("details", []),
            "raw": effects,
        },
        "meta": {
            "duration_ms": duration_ms,
            "admin_required": guard.admin_required,
            "admin_used": guard.admin_used,
            "guard": guard.to_dict(),
            "request_id": context.request_id,
        },
    }
    if context.snapshot is not None:
        standardized["meta"]["snapshot"] = context.snapshot

    # Keep old top-level keys for existing frontend compatibility.
    standardized.update(effects)
    return standardized


def _blocked_result(
    tweak_name: str,
    context: ExecutionContext,
    guard: GuardReport,
    message: str,
) -> Dict[str, object]:
    return {
        "mode": context.mode,
        "tweak": tweak_name,
        "status": "blocked",
        "simulated": context.simulated,
        "dry_run": context.dry_run,
        "summary": message,
        "message": message,
        "effects": {
            "targets": [],
            "power_plan": None,
            "memory_freed": None,
            "details": [],
            "raw": {},
        },
        "meta": {
            "duration_ms": int((time.time() - context.started_at) * 1000),
            "admin_required": guard.admin_required,
            "admin_used": guard.admin_used,
            "guard": guard.to_dict(),
            "request_id": context.request_id,
        },
    }


def execute_tweak(
    tweak_name: str,
    dry_run: Optional[bool] = None,
    confirm_high_risk: bool = False,
) -> Dict[str, object]:
    context = ExecutionContext.from_request(
        dry_run=dry_run,
        mode=None,
        confirmed_high_risk=confirm_high_risk,
    )
    guard = ExecutionGuard().evaluate(tweak_name, context)
    logger.info(
        "PREPARING PROTOCOL: %s mode=%s dry_run=%s request_id=%s",
        tweak_name,
        context.mode,
        context.dry_run,
        context.request_id,
    )

    tweak = get_tweak(tweak_name)
    if tweak is None:
        logger.error("Tweak mapping failure: %s", tweak_name)
        return _blocked_result(tweak_name, context, guard, f"Tweak not found: {tweak_name}")

    if guard.blocked:
        logger.warning(
            "PROTOCOL BLOCKED: %s request_id=%s reasons=%s",
            tweak_name,
            context.request_id,
            ",".join(guard.reasons),
        )
        return _blocked_result(
            tweak_name,
            context,
            guard,
            "Execution blocked by safety guardrail checks.",
        )

    if context.mode == "execute" and not context.dry_run:
        # Snapshot is lightweight infrastructure for upcoming revert fidelity.
        context.snapshot = SnapshotEngine.capture().to_dict()

    try:
        raw = tweak.apply(context=context)
    except Exception as exc:
        logger.exception("FATAL PROTOCOL CRASH: %s request_id=%s", tweak_name, context.request_id)
        raw = {
            "status": "failed",
            "message": f"CRITICAL_DEPLOYMENT_ERROR: {str(exc)}",
            "effects": {},
        }

    response = _build_action_result(tweak_name, context, raw, guard)
    logger.info(
        "PROTOCOL COMPLETE: %s status=%s duration_ms=%s request_id=%s",
        tweak_name,
        response.get("status"),
        response.get("meta", {}).get("duration_ms"),
        context.request_id,
    )
    return response


def revert_tweak(
    tweak_name: str,
    dry_run: Optional[bool] = None,
    confirm_high_risk: bool = False,
    revert_payload: Optional[Dict[str, object]] = None,
) -> Dict[str, object]:
    context = ExecutionContext.from_request(
        dry_run=dry_run,
        mode="revert",
        confirmed_high_risk=confirm_high_risk,
    )
    guard = ExecutionGuard().evaluate(tweak_name, context)
    tweak = get_tweak(tweak_name)
    if tweak is None:
        return _blocked_result(tweak_name, context, guard, f"Tweak not found: {tweak_name}")

    if guard.blocked:
        return _blocked_result(tweak_name, context, guard, "Revert blocked by safety guardrail checks.")

    if isinstance(revert_payload, dict):
        context.snapshot = revert_payload

    try:
        raw = tweak.revert(context=context)
    except Exception as exc:
        logger.exception("REVERT FAILURE: %s request_id=%s", tweak_name, context.request_id)
        raw = {"status": "failed", "message": f"REVERT_FAILURE: {str(exc)}", "effects": {}}
    return _build_action_result(tweak_name, context, raw, guard)
