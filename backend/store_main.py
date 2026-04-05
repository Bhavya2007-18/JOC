from fastapi import FastAPI
from .storage.breakdown import get_category_breakdown
from .storage.cold_files import find_cold_files
from .storage.duplicate_finder import find_duplicates
from .storage.junk_cleaner import get_junk_files
from .storage.scanner import scan
from .storage.suggestions import generate_full_suggestions

app = FastAPI()


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

    return {
        "summary": {
            "total_files": result["total_files"],
            "scan_time": result["scan_time"],
        },
        "files": files[:50],
        "category_breakdown": breakdown,
        "junk": junk,
        "duplicates": duplicates,
        "cold_files": cold,
        "suggestions": suggestions,
    }