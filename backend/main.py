from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from storage.db import init_db
from api.analyze import router as analyze_router
from api.fix import router as fix_router
from api.tweak import router as tweak_router
from api.action import router as action_router
from api.storage_routes import router as storage_router
from api.system_routes import router as system_router
from api.optimizer_routes import router as optimizer_router
from api.intelligence_routes import router as intelligence_router
from api.simulation_routes import router as simulation_router
from api.sentinel_routes import router as sentinel_router, start_broadcast_task
from api.autonomy_routes import router as autonomy_router
from intelligence.config import DRY_RUN
from intelligence.monitor_loop import MonitorLoop
from utils.logger import get_logger

monitor = MonitorLoop(interval=5)
logger = get_logger("api")
app = FastAPI()


@app.middleware("http")
async def add_error_handling(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as exc:
        logger.exception("Unhandled error")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.on_event("startup")
def startup_event():
    print(f"SYSTEM RUNNING IN DRY MODE: {DRY_RUN}")
    if DRY_RUN:
        print("WARNING: ALL SYSTEM ACTIONS ARE IN DRY RUN MODE")
        print("=" * 50)
        print("SYSTEM RUNNING IN SAFE SIMULATION MODE")
        print("No real system changes will occur")
        print("=" * 50)
    init_db()


@app.on_event("startup")
def start_monitor():
    monitor.start()

@app.on_event("startup")
def start_sentinel_ws():
    start_broadcast_task()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router)
app.include_router(fix_router)
app.include_router(tweak_router)
app.include_router(action_router)
app.include_router(storage_router)
app.include_router(system_router)
app.include_router(optimizer_router)
app.include_router(intelligence_router)
app.include_router(simulation_router)
app.include_router(sentinel_router)
app.include_router(autonomy_router)
