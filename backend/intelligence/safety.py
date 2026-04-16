from typing import Optional
from intelligence.config import DRY_RUN
from utils.execution_context import ExecutionContext


def allow_execution(context: Optional[ExecutionContext] = None) -> bool:
    if context:
        return not context.dry_run
    return not DRY_RUN


def enforce_safe_execution(context: Optional[ExecutionContext] = None) -> None:
    if context and context.dry_run:
        raise RuntimeError(f"Execution blocked: context {context.request_id} is in DRY_RUN mode")
    if not context and DRY_RUN:
        raise RuntimeError("Execution blocked: system is in global DRY_RUN mode")