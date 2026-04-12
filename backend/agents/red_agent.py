import random
from state.system_state import SystemState
from debug.debug_manager import get_debug_manager
from events.event_manager import Event

class RedAgent:
    ACTIONS = ["cpu_spike", "memory_stress"]
    
    async def act(self, state: SystemState, rng: random.Random) -> Event:
        action = rng.choice(self.ACTIONS)
        intensity = rng.uniform(0.1, 0.8)
        
        # Calculate impact based on intensity
        impact_cpu = intensity * 30.0 if action == "cpu_spike" else intensity * 10.0
        impact_ram = intensity * 20.0 if action == "memory_stress" else intensity * 5.0
        
        await get_debug_manager().log(
            component="red_agent",
            message="Attack vector selected",
            data={
                "action": action,
                "intensity": intensity,
                "cpu_impact": impact_cpu,
                "ram_impact": impact_ram,
                "current_state_cpu": getattr(state, 'cpu_usage', 0),
            }
        )
        
        return Event(
            type="red_action",
            action=action,
            source="red_agent",
            impact={"cpu": impact_cpu, "ram": impact_ram},
            metadata={"intensity": intensity}
        )
