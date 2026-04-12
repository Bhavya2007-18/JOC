import asyncio
import random
from typing import Optional
from state.system_state import get_state
from events.event_manager import get_event_manager
from agents.red_agent import RedAgent
from agents.blue_agent import BlueAgent

class SimulationEngine:
    def __init__(self):
        self._task: Optional[asyncio.Task] = None
        self._status: str = "stopped"  # stopped | running | paused
        self._interval: float = 1.0  # seconds between ticks
        self._seed: Optional[int] = None
        self._rng: random.Random = random.Random()
        
        self.red_agent = RedAgent()
        self.blue_agent = BlueAgent()
        self.state_manager = get_state()
        self.event_manager = get_event_manager()

    def _compute_threat(self, cpu: float, ram: float) -> int:
        score = (cpu * 0.6) + (ram * 0.4)
        return min(max(int(score), 0), 100)

    async def _loop(self):
        while True:
            if self._status == "paused":
                await asyncio.sleep(1.0)
                continue
                
            if self._status == "stopped":
                break
                
            # Wait for next tick
            await asyncio.sleep(self._interval)
            
            # --- TICK ---
            current_state = self.state_manager.to_dict()
            mock_state_obj = type('MockState', (object,), current_state)()
            
            # Red acts
            red_event = await self.red_agent.act(mock_state_obj, self._rng)
            
            # Update state with red's action temporarily
            mock_state_obj.cpu_usage += red_event.impact.get("cpu", 0.0)
            mock_state_obj.ram_usage += red_event.impact.get("ram", 0.0)
            
            # Blue responds
            blue_event = await self.blue_agent.respond(red_event, mock_state_obj)
            
            # Log events
            await self.event_manager.log_event(red_event)
            await self.event_manager.log_event(blue_event)
            
            # Update and broadcast state
            new_cpu = min(max(current_state["cpu_usage"] + red_event.impact.get("cpu", 0) + blue_event.impact.get("cpu", 0), 0.0), 100.0)
            new_ram = min(max(current_state["ram_usage"] + red_event.impact.get("ram", 0) + blue_event.impact.get("ram", 0), 0.0), 100.0)
            
            await self.state_manager.update({
                "cpu_usage": new_cpu,
                "ram_usage": new_ram,
                "threat_level": self._compute_threat(new_cpu, new_ram),
                "simulation_status": "running"
            })

    async def start(self, seed: Optional[int] = None, interval: Optional[float] = None) -> None:
        if self._status == "running":
            return
            
        if seed is None:
            self._seed = random.randint(0, 9999)
        else:
            self._seed = seed
            
        self._rng.seed(self._seed)
        print(f"Simulation Engine starting with seed: {self._seed} and interval {self._interval}")
        
        if interval is not None:
            self._interval = interval
            
        self._status = "running"
        await self.state_manager.update({"simulation_status": "running"})
        
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._loop())

    async def pause(self) -> None:
        if self._status == "running":
            self._status = "paused"
            await self.state_manager.update({"simulation_status": "paused"})

    async def resume(self) -> None:
        if self._status == "paused":
            self._status = "running"
            await self.state_manager.update({"simulation_status": "running"})

    async def reset(self) -> None:
        self._status = "stopped"
        await self.state_manager.update({
            "cpu_usage": 0.0,
            "ram_usage": 0.0,
            "threat_level": 0,
            "simulation_status": "stopped"
        })
        if self._task and not self._task.done():
            self._task.cancel()
        self._task = None

    async def set_speed(self, interval: float) -> None:
        self._interval = max(0.1, interval)
        
# Singleton
_engine_instance = SimulationEngine()

def get_engine() -> SimulationEngine:
    return _engine_instance
