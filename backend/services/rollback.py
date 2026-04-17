import uuid
import psutil
from typing import Dict, Any

import json
from utils.paths import get_persistent_path

class RollbackManager:
    """
    State safety interceptor. Snapshots system state before autonomous interventions.
    Allows for undo functionality if fixes generate instability.
    """
    def __init__(self):
        self._file_path = get_persistent_path("checkpoints.json", "storage")
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        self.snapshots_db: Dict[str, Dict[str, Any]] = {}
        self._load_checkpoints()

    def _load_checkpoints(self):
        try:
            if self._file_path.exists():
                with open(self._file_path, "r", encoding="utf-8") as f:
                    self.snapshots_db = json.load(f)
        except Exception:
            self.snapshots_db = {}

    def _save_checkpoints(self):
        try:
            with open(self._file_path, "w", encoding="utf-8") as f:
                json.dump(self.snapshots_db, f, indent=2)
        except Exception:
            pass

    def capture_pre_action_state(self, action_type: str, target: str, pid: int = None) -> str:
        """
        Captures the state of a target before it is modified.
        Returns a rollback ID.
        """
        snapshot = {
            "action_type": action_type,
            "target": target,
            "pid": pid,
            "state_data": {}
        }
        
        if action_type in ["priority_down", "priority_up", "suspend", "kill"]:
            if pid:
                try:
                    proc = psutil.Process(pid)
                    snapshot["state_data"]["priority"] = proc.nice()
                    snapshot["state_data"]["status"] = proc.status()
                except psutil.NoSuchProcess:
                    snapshot["state_data"]["error"] = "Process died before capture."
        
        # Handle system tweaks state capture
        elif action_type == "system_tweak":
            # Just an example stub, normally we would dump the registry or config state
            snapshot["state_data"]["previous_config"] = "ENABLED"
            
        rollback_id = str(uuid.uuid4())
        self.snapshots_db[rollback_id] = snapshot
        self._save_checkpoints()
        return rollback_id

    def capture_system_profile(self) -> str:
        """
        Captures a broad system checkpoint (Memory, Power, Active Process list).
        Recommended before high-risk tweaks.
        """
        from intelligence.tweaks.snapshot import SnapshotEngine
        snapshot_data = SnapshotEngine.capture().to_dict()
        
        rollback_id = f"CP-{str(uuid.uuid4())[:8]}"
        self.snapshots_db[rollback_id] = {
            "action_type": "checkpoint",
            "target": "full_system",
            "timestamp": snapshot_data.get("timestamp"),
            "state_data": snapshot_data
        }
        self._save_checkpoints()
        return rollback_id

    def execute_rollback(self, rollback_id: str) -> bool:
        """
        Executes a reverse procedure based on the captured pre-action state.
        """
        if rollback_id not in self.snapshots_db:
            return False
            
        snapshot = self.snapshots_db[rollback_id]
        action = snapshot["action_type"]
        pid = snapshot.get("pid")
        state = snapshot.get("state_data", {})
        
        try:
            if action in ["priority_down", "priority_up", "throttle_process"] and pid:
                original_priority = state.get("priority")
                if original_priority is not None:
                    # Windows nice values are different, but psutil obfuscates it somewhat.
                    proc = psutil.Process(pid)
                    proc.nice(original_priority)
                    return True
                    
            elif action == "suspend" and pid:
                proc = psutil.Process(pid)
                proc.resume()
                return True
                
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
        
        return False

# Global instance
rollback_manager = RollbackManager()
