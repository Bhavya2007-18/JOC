from fastapi import FastAPI
from .storage.breakdown import get_category_breakdown
from .storage.cold_files import find_cold_files
from .storage.duplicate_finder import find_duplicates
from .storage.junk_cleaner import get_junk_files
from .storage.scanner import scan
from .storage.suggestions import generate_full_suggestions

app = FastAPI()


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