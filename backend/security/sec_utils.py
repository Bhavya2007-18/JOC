"""Small shared utility functions for the security module."""

from typing import Any


def format_bytes(n: int) -> str:
    """Convert bytes to a human-readable string."""
    value = float(max(n, 0))
    units = ["B", "KB", "MB", "GB", "TB", "PB"]

    for unit in units:
        if value < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(value)} B"
            return f"{value:.2f} {unit}"
        value /= 1024

    return "0 B"


def safe_proc_attr(proc: Any, attr: str, default: Any = None) -> Any:
    """Safely access psutil process attributes."""
    try:
        if hasattr(proc, "info") and isinstance(proc.info, dict):
            return proc.info.get(attr, default)
        return getattr(proc, attr, default)
    except Exception:
        return default


# Backward-compatible alias used by downstream modules.
safe_process_attr = safe_proc_attr

