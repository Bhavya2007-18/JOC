import random
from state.system_state import SystemState
from debug.debug_manager import get_debug_manager
from events.event_manager import Event

class RedAgent:
    def __init__(self):
        self.tick_count = 0
        self.current_wave = "idle"
        
    def reset(self):
        self.tick_count = 0
        self.current_wave = "idle"
    
    async def act(self, state: SystemState, rng: random.Random) -> Event:
        self.tick_count += 1
        # Phase 4 Multi-wave scenario logic
        if self.tick_count < 10:
            self.current_wave = "cpu_probe"
            impact_cpu = rng.uniform(5.0, 15.0)
            impact_ram = rng.uniform(0.0, 2.0)
        elif self.tick_count < 25:
            self.current_wave = "memory_leak_wave"
            impact_cpu = rng.uniform(2.0, 8.0)
            # Escalating memory leak
            impact_ram = rng.uniform(15.0, 30.0)
        elif self.tick_count < 40:
            self.current_wave = "cpu_flood_wave"
            impact_cpu = rng.uniform(30.0, 50.0)
            impact_ram = rng.uniform(5.0, 10.0)
        else:
            self.current_wave = "multi_vector_assault"
            impact_cpu = rng.uniform(25.0, 45.0)
            impact_ram = rng.uniform(25.0, 45.0)
            
        intensity = (impact_cpu + impact_ram) / 100.0
        
        await get_debug_manager().log(
            component="red_agent",
            message="Attack vector selected",
            data={
                "wave": self.current_wave,
                "tick_count": self.tick_count,
                "intensity": intensity,
                "cpu_impact": impact_cpu,
                "ram_impact": impact_ram,
                "current_state_cpu": getattr(state, 'cpu_usage', 0),
            }
        )
        
        return Event(
            type="red_action",
            action=self.current_wave,
            source="red_agent",
            impact={"cpu": impact_cpu, "ram": impact_ram},
            metadata={"intensity": intensity, "tick_count": self.tick_count}
        )
