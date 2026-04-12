import asyncio
from typing import Optional, List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from state.system_state import get_state
from events.event_manager import get_event_manager, Event
from simulation.engine import get_engine

router = APIRouter(prefix="/api", tags=["sentinel"])

# --- Models ---
class SimStartRequest(BaseModel):
    seed: Optional[int] = None
    interval: Optional[float] = None

class SimSpeedRequest(BaseModel):
    interval: float

# --- REST Endpoints ---
@router.get("/state")
def get_current_state():
    return get_state().to_dict()

@router.get("/status")
def get_current_status():
    return {"status": get_state().to_dict().get("simulation_status", "stopped")}

@router.get("/events")
def get_recent_events(limit: int = 100):
    return [ev.dict() for ev in get_event_manager().get_events(limit)]

@router.post("/simulation/start")
async def start_sim(req: SimStartRequest = SimStartRequest()):
    await get_engine().start(seed=req.seed, interval=req.interval)
    return {"status": "running"}

@router.post("/simulation/pause")
async def pause_sim():
    await get_engine().pause()
    return {"status": "paused"}

@router.post("/simulation/resume")
async def resume_sim():
    await get_engine().resume()
    return {"status": "running"}

@router.post("/simulation/reset")
async def reset_sim():
    await get_engine().reset()
    return {"status": "stopped"}

@router.post("/simulation/speed")
async def set_sim_speed(req: SimSpeedRequest):
    await get_engine().set_speed(req.interval)
    return {"interval": req.interval}

# --- WebSocket ---
class ConnectionManager:
    def __init__(self):
        self.active_connections = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)

    async def broadcast(self, message: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)

manager = ConnectionManager()

async def broadcast_state_task():
    while True:
        try:
            state_dict = get_state().to_dict()
            await manager.broadcast({
                "type": "state_update",
                "data": state_dict
            })
            
            # Broadcast the complete intelligent threat/pred/xai payload
            from intelligence.monitor_loop import MonitorLoop
            monitor = MonitorLoop.get_instance()
            if monitor and hasattr(monitor, 'latest_intelligence') and monitor.latest_intelligence:
                await manager.broadcast({
                    "type": "intelligence_update",
                    "data": monitor.latest_intelligence
                })
                
            if monitor and hasattr(monitor, 'latest_autonomy_state') and monitor.latest_autonomy_state:
                await manager.broadcast({
                    "type": "autonomy_update",
                    "data": monitor.latest_autonomy_state
                })
                
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Error broadcasting state: {e}")
        
        await asyncio.sleep(1.0)

_state_task = None

def start_broadcast_task():
    global _state_task
    if _state_task is None or _state_task.done():
        _state_task = asyncio.create_task(broadcast_state_task())
        
        async def on_event(event: Event):
            await manager.broadcast({
                "type": "event",
                "data": event.dict()
            })
            
        get_event_manager().subscribe(on_event)

@router.websocket("/ws/live")
async def websocket_live(websocket: WebSocket):
    await manager.connect(websocket)
    start_broadcast_task()
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)
