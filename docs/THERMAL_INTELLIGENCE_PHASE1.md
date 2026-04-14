# Thermal Intelligence Layer — Phase 1

## What Was Added

- `intelligence/thermal_engine.py`
  - Synthetic temperature estimation (`40 + cpu_usage * 0.5`, clamped `40..95`)
  - Thermal state classification (`COOL`, `WARM`, `HOT`, `CRITICAL`)
  - Velocity detection (`stable`, `rising`, `spiking`)
  - Hysteresis transitions (anti-oscillation)
  - Thermal risk score (`0..100`)
  - Rolling history buffer (last 10 readings)
  - EMA smoothing for temperature stability

- `intelligence/monitor_loop.py`
  - Stage 6 integration with `thermal_engine.update(...)` each cycle
  - Thermal data included in unified intelligence payload
  - `THERMAL_SPIKE` event emission to causal graph on velocity spikes
  - Thermal-aware mode enforcement hook into `apply_system_mode(...)`

- `services/optimizer/power_mode.py`
  - Thermal guard before mode application
  - Blocks/downgrades unsafe mode (`beast` -> `smart`) when thermal is critical
  - Action logging for guard triggers via `ActionStore`

- `intelligence/causal_engine.py`
  - Public `emit_event(...)` hook for cross-engine causal injections

## Example Usage

```python
from intelligence.thermal_engine import ThermalEngine
from services.optimizer.power_mode import apply_system_mode

thermal_engine = ThermalEngine()
thermal_data = thermal_engine.update(cpu_usage=86.5, timestamp=1712345678.0)

result = apply_system_mode(
    mode="beast",
    force_live=False,
    thermal_data=thermal_data,
)

print(thermal_data)
print(result["mode"], result.get("thermal_guard_applied"))
```

## Sample Thermal Output

```json
{
  "temperature": 84.2,
  "raw_temperature": 83.6,
  "state": "HOT",
  "velocity": "rising",
  "score": 76.4,
  "is_critical": false,
  "delta_temp": 1.4,
  "history_size": 7
}
```

## Sample Guard Log Event

```json
{
  "event": "THERMAL_GUARD_TRIGGERED",
  "temp": 91.2,
  "state": "CRITICAL",
  "mode_before": "beast",
  "mode_after": "smart"
}
```
