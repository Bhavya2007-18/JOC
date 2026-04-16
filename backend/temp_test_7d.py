import time
from intelligence.sensors.etw_adapter import ETWAdapter

adapter = ETWAdapter()
print(f'ETW lib: {adapter._etw_lib}')
print(f'Is admin: {adapter._is_admin}')
print(f'ETW active: {adapter._etw_active}')

time.sleep(6)   # let psutil thread run one poll cycle

events = adapter.poll()
print(f'Events captured: {len(events)}')
for e in events[:5]:
    print(f'  {e["type"]} — {e["name"]} (pid={e["pid"]})')

adapter.stop()
print('OK')
