import gc
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Tuple

from utils.execution_context import ExecutionContext
from utils.logger import get_logger


logger = get_logger("optimizer.cleanup")
_action_store = ActionStore()


def _log_cleanup_action(result: Dict[str, Any], parameters: Dict[str, Any]) -> str:
    action_id = f"cleanup-{int(result['timestamp'] * 1000)}"
    record = ActionRecord(
        action_id=action_id,
        action_type=ActionType.SYSTEM_TWEAK,
        target="cleanup",
        timestamp=result["timestamp"],
        status="completed" if result["success"] else "failed",
        reversible=False,
        result=result,
        parameters=parameters,
    )
    _action_store.add_action(record)
    return action_id


def _collect_safe_cache_dirs() -> List[Path]:
    home = Path.home()
    candidates = [
        home / ".joc" / "cache",
        home / ".cache" / "joc",
    ]
    existing = [path for path in candidates if path.exists()]
    return existing


def _cleanup_path(path: Path, dry_run: bool) -> Tuple[int, bool]:
    if not path.exists():
        return 0, False

    freed = 0
    simulated = False

    if dry_run:
        simulated = True
        if path.is_file():
            try:
                freed = path.stat().st_size
            except OSError:
                freed = 0
        else:
            for root, _, files in os.walk(path):
                for name in files:
                    file_path = Path(root) / name
                    try:
                        freed += file_path.stat().st_size
                    except OSError:
                        continue
        return freed, simulated

    if path.is_file():
        try:
            size = path.stat().st_size
        except OSError:
            size = 0
        try:
            path.unlink()
            freed = size
        except OSError:
            freed = 0
        return freed, simulated

    try:
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                file_path = Path(root) / name
                try:
                    size = file_path.stat().st_size
                except OSError:
                    size = 0
                try:
                    file_path.unlink()
                    freed += size
                except OSError:
                    continue
            for name in dirs:
                dir_path = Path(root) / name
                try:
                    dir_path.rmdir()
                except OSError:
                    continue
    except OSError:
        return freed, simulated

    return freed, simulated


def run_cleanup(context: Optional[ExecutionContext] = None, dry_run: bool = False) -> Dict[str, Any]:
    if context is None:
        context = ExecutionContext.from_request(dry_run=dry_run)
    
    effective_dry_run = context.simulated
    temp_dir = Path(tempfile.gettempdir())
    cache_dirs = _collect_safe_cache_dirs()

    items: List[Dict[str, Any]] = []
    total_freed = 0

    temp_freed, temp_sim = _cleanup_path(temp_dir, dry_run=effective_dry_run)
    items.append(
        {
            "path": str(temp_dir),
            "bytes_freed": int(temp_freed),
            "simulated": temp_sim or effective_dry_run,
        }
    )
    total_freed += int(temp_freed)

    for cache_dir in cache_dirs:
        freed, sim = _cleanup_path(cache_dir, dry_run=effective_dry_run)
        items.append(
            {
                "path": str(cache_dir),
                "bytes_freed": int(freed),
                "simulated": sim or effective_dry_run,
            }
        )
        total_freed += int(freed)

    before_gc = gc.get_stats()
    gc.collect()
    after_gc = gc.get_stats()

    risk = "low"
    confidence = 0.8
    if not dry_run and total_freed > 0:
        risk = "medium"
        confidence = 0.85

    result = {
        "success": True,
        "message": "Cleanup completed" if not effective_dry_run else "Dry-run: cleanup simulated",
        "dry_run": effective_dry_run,
        "total_bytes_freed": int(total_freed),
        "items": items,
        "gc_before": before_gc,
        "gc_after": after_gc,
        "timestamp": float(__import__("time").time()),
        "risk": risk,
        "confidence": confidence,
    }

    _log_cleanup_action(result, {"dry_run": effective_dry_run})

    context.log_action("run_cleanup", {"total_bytes_freed": total_freed, "items_count": len(items)})

    return result
