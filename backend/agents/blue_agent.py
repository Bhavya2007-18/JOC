from state.system_state import SystemState
from events.event_manager import Event

class BlueAgent:
    CPU_THRESHOLD = 70.0
    RAM_THRESHOLD = 80.0
    
    async def respond(self, red_event: Event, state: SystemState) -> Event:
        # Simple rule-based response (no ML yet)
        if state.cpu_usage > self.CPU_THRESHOLD:
            action = "throttle_process"
            impact_cpu = -5.0
            impact_ram = -1.0
        elif state.ram_usage > self.RAM_THRESHOLD:
            action = "flush_cache"
            impact_cpu = -1.0
            impact_ram = -3.0
        else:
            action = "log_only"
            impact_cpu = 0.0
            impact_ram = 0.0
        
        return Event(
            type="blue_action",
            action=action,
            source="blue_agent",
            impact={"cpu": impact_cpu, "ram": impact_ram},
            metadata={"responding_to": red_event.id}
        )
