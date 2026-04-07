from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.analyze import router as analyze_router
from api.fix import router as fix_router
from api.tweak import router as tweak_router
from api.action import router as action_router
from api.storage_routes import router as storage_router
from intelligence.monitor_loop import MonitorLoop

monitor = MonitorLoop(interval=5)
app = FastAPI()
@app.on_event("startup")
def start_monitor():
    monitor.start()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router)
app.include_router(fix_router)
app.include_router(tweak_router)
app.include_router(action_router)
app.include_router(storage_router)