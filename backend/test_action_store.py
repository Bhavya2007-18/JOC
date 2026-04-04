from intelligence.action_store import ActionStore
from intelligence.models import ActionRecord, ActionType
import time
import uuid

store = ActionStore()

dummy_action = ActionRecord(
    action_id=str(uuid.uuid4()),
    action_type=ActionType.KILL_PROCESS,
    target="test.exe",
    timestamp=time.time(),
    status="success",
    reversible=False,
    result={"message": "test"},
    parameters={}
)

store.add_action(dummy_action)

print("Action added successfully")