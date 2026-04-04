from fastapi import FastAPI
from .storage.scanner import scan

app = FastAPI()

@app.get("/scan")
def scan_files(path: str = "C:/Users"):
    result = scan(path)
    return {
        "summary": {
            "total_files": result["total_files"],
            "scan_time": result["scan_time"],
        },
        "files": result["files"][:50],
    }