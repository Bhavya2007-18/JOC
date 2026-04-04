import os
import platform
import subprocess
import shutil
import psutil
import logging

logger = logging.getLogger("JOC.Fixer")

# ==========================================
# 1. SAFE EXECUTION LAYER (CRITICAL)
# ==========================================

# List of critical processes that must NEVER be killed
PROTECTED_PROCESSES = {
    # Windows
    "system", "idle", "wininit.exe", "csrss.exe", "services.exe", "lsass.exe", 
    "smss.exe", "explorer.exe", "winlogon.exe", "taskmgr.exe", "spoolsv.exe",
    # Linux
    "systemd", "init", "kthreadd", "sshd", "bash", "zsh", "gnome-shell",
    # Mac
    "kernel_task", "launchd", "WindowServer", "sysmond"
}

def is_safe_process(process_name: str) -> bool:
    """
    Checks if a process is safe to terminate.
    Returns False if it's a critical system process.
    """
    if not process_name:
        return False
    return process_name.lower() not in PROTECTED_PROCESSES


# ==========================================
# 2. PERMISSION-BASED EXECUTION WRAPPER
# ==========================================

def execute_action(action_name: str, payload: dict, confirm: bool = False) -> dict:
    """
    Wrapper for all actions. Enforces confirmation before execution.
    """
    if not confirm:
        return {
            "status": "confirmation_required",
            "action": action_name,
            "details": "This action needs user approval before execution."
        }
        
    # Route to the correct action based on name
    if action_name == "kill_process_by_pid":
        return _kill_process(payload.get("pid"))
    elif action_name == "kill_process_by_name":
        return _kill_process_by_name(payload.get("name"))
    elif action_name == "clear_temp_files":
        return _clear_temp_files()
    elif action_name == "apply_mode":
        return _apply_mode(payload.get("mode"))
    else:
        return {
            "status": "failed",
            "action": action_name,
            "details": f"Unknown action: {action_name}"
        }


# ==========================================
# 3. PROCESS CONTROL SYSTEM
# ==========================================

def _kill_process(pid: int) -> dict:
    """Internal function to kill a process by PID using OS commands."""
    try:
        # 1. Validate safety using psutil before running OS commands
        proc = psutil.Process(pid)
        proc_name = proc.name()
        
        if not is_safe_process(proc_name):
            return {
                "status": "blocked",
                "action": "kill_process",
                "details": f"Cannot kill protected system process: {proc_name} (PID: {pid})"
            }

        # 2. Execute OS-specific kill command
        sys_os = platform.system()
        if sys_os == "Windows":
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], check=True, capture_output=True)
        else: # Linux/Mac
            subprocess.run(["kill", "-9", str(pid)], check=True, capture_output=True)
            
        return {
            "status": "success",
            "action": "kill_process",
            "details": f"Successfully terminated process {proc_name} (PID: {pid})"
        }
        
    except psutil.NoSuchProcess:
        return {"status": "failed", "action": "kill_process", "details": f"Process PID {pid} not found."}
    except subprocess.CalledProcessError as e:
        return {"status": "failed", "action": "kill_process", "details": f"OS failed to kill PID {pid}: {e.stderr.decode('utf-8', errors='ignore') if e.stderr else str(e)}"}
    except Exception as e:
        return {"status": "failed", "action": "kill_process", "details": f"Error: {str(e)}"}


def _kill_process_by_name(name: str) -> dict:
    """Internal function to kill all processes matching a name using OS commands."""
    if not name:
        return {"status": "failed", "action": "kill_process_by_name", "details": "No process name provided."}
        
    if not is_safe_process(name):
        return {
            "status": "blocked",
            "action": "kill_process_by_name",
            "details": f"Cannot kill protected system process: {name}"
        }

    sys_os = platform.system()
    try:
        if sys_os == "Windows":
            # Add .exe if missing for Windows
            target_name = name if name.lower().endswith(".exe") else f"{name}.exe"
            subprocess.run(["taskkill", "/F", "/IM", target_name], check=True, capture_output=True)
        else: # Linux/Mac
            subprocess.run(["pkill", "-9", name], check=True, capture_output=True)
            
        return {
            "status": "success",
            "action": "kill_process_by_name",
            "details": f"Successfully terminated all processes named {name}"
        }
    except subprocess.CalledProcessError:
        # taskkill/pkill returns error if process isn't found, which is fine
        return {"status": "success", "action": "kill_process_by_name", "details": f"No active processes found named {name}"}
    except Exception as e:
        return {"status": "failed", "action": "kill_process_by_name", "details": f"Error: {str(e)}"}


# ==========================================
# 4. SYSTEM CLEANUP (BASIC)
# ==========================================

def _clear_temp_files() -> dict:
    """Safely clears OS temporary directories."""
    sys_os = platform.system()
    temp_dirs = []
    
    if sys_os == "Windows":
        temp_dirs = [
            os.environ.get('TEMP', 'C:\\Temp'),
            os.environ.get('TMP', 'C:\\Windows\\Temp')
        ]
    else:
        temp_dirs = ['/tmp']
        
    files_deleted = 0
    bytes_freed = 0
    
    for temp_dir in temp_dirs:
        if not os.path.exists(temp_dir):
            continue
            
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    # Safety check: don't delete files modified in the last 24 hours
                    import time
                    if time.time() - os.path.getmtime(file_path) < 86400:
                        continue
                        
                    size = os.path.getsize(file_path)
                    os.remove(file_path)
                    bytes_freed += size
                    files_deleted += 1
                except (OSError, PermissionError):
                    # Silently skip files we can't touch (in use, locked, etc)
                    pass
                    
    mb_freed = round(bytes_freed / (1024 * 1024), 2)
    return {
        "status": "success",
        "action": "clear_temp_files",
        "details": f"Cleaned up {files_deleted} old temp files, freeing {mb_freed} MB."
    }


# ==========================================
# 5. MODE SYSTEM
# ==========================================

def _apply_mode(mode_name: str) -> dict:
    """Applies grouped actions based on the requested mode."""
    if not mode_name:
        return {"status": "failed", "action": "apply_mode", "details": "Mode name not provided."}
        
    mode = mode_name.lower()
    
    if mode == "gaming":
        # Example gaming logic: clear temp files to free space, kill known heavy non-essential background apps
        _clear_temp_files()
        _kill_process_by_name("chrome") # Example: kill browser
        return {
            "status": "success",
            "action": "apply_mode",
            "details": "Gaming Mode applied: Background apps cleared, memory freed for maximum performance."
        }
        
    elif mode == "performance":
        # Example performance logic: clear temp files
        _clear_temp_files()
        return {
            "status": "success",
            "action": "apply_mode",
            "details": "Performance Mode applied: System cleaned and balanced for heavy workloads."
        }
        
    elif mode == "battery":
        # Example battery logic: kill known power-hungry background updaters
        _kill_process_by_name("OneDrive")
        _kill_process_by_name("Dropbox")
        return {
            "status": "success",
            "action": "apply_mode",
            "details": "Battery Saver applied: Background sync and heavy apps restricted."
        }
        
    else:
        return {
            "status": "failed",
            "action": "apply_mode",
            "details": f"Unknown mode: {mode_name}"
        }


# ==========================================
# 6. LOCAL TESTING BLOCK
# ==========================================

if __name__ == "__main__":
    import json
    
    print("\n--- JOC Fixer Engine Local Test ---\n")
    
    # Test 1: Action without confirmation
    print("1. Testing unconfirmed action:")
    res1 = execute_action("clear_temp_files", {}, confirm=False)
    print(json.dumps(res1, indent=2))
    
    # Test 2: Try killing protected process
    print("\n2. Testing protected process block:")
    res2 = execute_action("kill_process_by_name", {"name": "explorer.exe"}, confirm=True)
    print(json.dumps(res2, indent=2))
    
    # Test 3: Clear temp files
    print("\n3. Testing temp file cleanup:")
    res3 = execute_action("clear_temp_files", {}, confirm=True)
    print(json.dumps(res3, indent=2))
    
    # Test 4: Apply Mode
    print("\n4. Testing Mode application:")
    res4 = execute_action("apply_mode", {"mode": "gaming"}, confirm=True)
    print(json.dumps(res4, indent=2))
    
    print("\n--- Test Complete ---")