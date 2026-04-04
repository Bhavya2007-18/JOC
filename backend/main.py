from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import time

# Import our JOC modules
import monitor
import analyzer
import fixer
import storage

app = FastAPI(title="JOC Sentinel Engine API", version="1.0.0")

# Enable CORS for the React frontend (running on port 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"], # Allow Vite/React dev ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# Models
# ---------------------------------------------------------
class ProcessActionRequest(BaseModel):
    pid: int
    name: str

class ModeActionRequest(BaseModel):
    mode: str

# ---------------------------------------------------------
# Routes
# ---------------------------------------------------------

@app.on_event("startup")
async def startup_event():
    """Initialize system monitoring on startup."""
    print("Starting JOC Sentinel Engine...")
    monitor.initialize_monitoring()

@app.get("/api/health")
def health_check():
    """Simple API health check."""
    return {"status": "online", "message": "JOC Engine is active."}

@app.get("/api/system/snapshot")
def get_full_snapshot():
    """
    Returns a complete system snapshot including raw metrics and intelligent analysis.
    This is the primary endpoint for the dashboard.
    """
    # 1. Observation Layer: Get raw data
    raw_data = monitor.get_system_snapshot()
    
    # 2. Intelligence Layer: Analyze data
    analysis = analyzer.analyze_snapshot(raw_data)
    dev_status = analyzer.determine_developer_mode(raw_data)
    
    # 3. Storage Layer: Get quick disk usage
    disk_info = storage.get_storage_breakdown()
    
    # Combine into a single payload
    return {
        "timestamp": raw_data["timestamp"],
        "metrics": {
            "cpu": raw_data["cpu"],
            "memory": raw_data["memory"],
            "disk": disk_info
        },
        "processes": raw_data["top_processes"],
        "intelligence": {
            "analysis": analysis,
            "developer_mode": dev_status
        }
    }

@app.post("/api/actions/kill_process")
def action_kill_process(req: ProcessActionRequest):
    """Action Layer: Safely terminate a process."""
    result = fixer.kill_process(req.pid, req.name)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.post("/api/actions/clear_ram")
def action_clear_ram():
    """Action Layer: Attempt to clear system RAM caches."""
    result = fixer.clear_ram()
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.post("/api/actions/set_mode")
def action_set_mode(req: ModeActionRequest):
    """Action Layer: Apply a specific operation mode."""
    result = fixer.apply_mode(req.mode)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.get("/api/storage/scan")
def storage_scan_junk():
    """Storage Module: Scan for junk files."""
    return storage.scan_for_junk()

@app.post("/api/storage/clean")
def storage_clean_junk():
    """Storage Module: Clean found junk files."""
    return storage.clean_junk()

# ---------------------------------------------------------
# Entry Point
# ---------------------------------------------------------
if __name__ == "__main__":
    print("Initializing JOC Backend Server...")
    # Run the API server locally on port 8000
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)