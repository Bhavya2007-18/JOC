from intelligence.config import DRY_RUN


def allow_execution() -> bool:
    return not DRY_RUN


def enforce_safe_execution() -> None:
    if DRY_RUN:
        raise RuntimeError("Execution blocked: system is in DRY_RUN mode")