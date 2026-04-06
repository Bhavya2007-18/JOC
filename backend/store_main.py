from fastapi import FastAPI
from pydantic import BaseModel
from typing import Literal
from .storage.breakdown import get_category_breakdown
from .storage.cleanup import EMPTY_CLEANUP_RESULT, delete_paths, extract_cleanup_paths
from .storage.cold_files import find_cold_files
from .storage.duplicate_finder import find_duplicates
from .storage.junk_cleaner import get_junk_files
from .storage.scanner import scan
from .storage.suggestions import generate_full_suggestions

app = FastAPI()
LAST_ANALYSIS = {
    "junk": {"junk_files": [], "total_junk_size": 0, "readable_size": "0 B"},
    "duplicates": {"duplicates": [], "total_duplicate_size": 0, "readable_size": "0 B"},
    "cold": {"cold_files": [], "total_cold_size": 0, "readable_size": "0 B", "threshold_days": 60},
}


class CleanupRequest(BaseModel):
    type: Literal["junk", "duplicates", "cold"]
    confirm: bool


def _strip_internal_fields(file_record: dict) -> dict:
    """Remove internal-only fields before API response."""
    return {key: value for key, value in file_record.items() if key != "path_lower"}


@app.get("/scan")
def scan_files(path: str = "C:/Users", max_files: int = 5000, cold_days: int = 60):
    result = scan(path, max_files=max_files)
    files = result["files"]

    breakdown = get_category_breakdown(files)
    junk = get_junk_files(files)
    duplicates = find_duplicates(files)
    cold = find_cold_files(files, days=cold_days)
    suggestions = generate_full_suggestions(
        files,
        junk=junk,
        duplicates=duplicates,
        cold=cold,
        cold_days=cold_days,
    )

    LAST_ANALYSIS["junk"] = junk
    LAST_ANALYSIS["duplicates"] = duplicates
    LAST_ANALYSIS["cold"] = cold

    public_files = [_strip_internal_fields(file_record) for file_record in files]
    public_junk_files = [_strip_internal_fields(file_record) for file_record in junk["junk_files"]]
    public_cold_files = [_strip_internal_fields(file_record) for file_record in cold["cold_files"]]

    return {
        "summary": {
            "total_files": result["total_files"],
            "scan_time": result["scan_time"],
        },
        "files": public_files[:50],
        "category_breakdown": breakdown,
        "junk": {
            "junk_files": public_junk_files,
            "total_junk_size": junk["total_junk_size"],
            "readable_size": junk["readable_size"],
        },
        "duplicates": duplicates,
        "cold_files": {
            "cold_files": public_cold_files,
            "total_cold_size": cold["total_cold_size"],
            "readable_size": cold["readable_size"],
            "threshold_days": cold["threshold_days"],
        },
        "suggestions": suggestions,
    }


@app.post("/cleanup")
def cleanup_files(payload: CleanupRequest):
    if not payload.confirm:
        return {"error": "Confirmation required"}

    cleanup_type = str(payload.type).lower().strip()
    if cleanup_type not in {"junk", "duplicates", "cold"}:
        return EMPTY_CLEANUP_RESULT.copy()

    junk = LAST_ANALYSIS.get("junk", {"junk_files": []})
    duplicates = LAST_ANALYSIS.get("duplicates", {"duplicates": []})
    cold = LAST_ANALYSIS.get("cold", {"cold_files": []})

    file_paths = extract_cleanup_paths(cleanup_type, junk, duplicates, cold)
    if not file_paths:
        return EMPTY_CLEANUP_RESULT.copy()

    return delete_paths(file_paths)