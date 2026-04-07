import psutil
import time
import os
from storage.db import save_snapshot
# Optional: Set a global flag if initialization is required
_is_initialized = False

def _bytes_to_mb(bytes_val):
    """Utility function to convert bytes to Megabytes."""
    return round(bytes_val / (1024 * 1024), 2)

def initialize_monitoring():
    """
    Initialize process tracking for CPU percentage calculations.
    psutil.cpu_percent() returns 0.0 on the first call because it needs an interval.
    Calling it once with interval=None stores the baseline.
    """
    global _is_initialized
    psutil.cpu_percent(interval=None)
    _is_initialized = True

def get_cpu_info():
    """Returns CPU usage statistics."""
    if not _is_initialized:
        initialize_monitoring()
        
    return {
        "cpu_percent": psutil.cpu_percent(interval=0.1), # Short interval for accurate reading
        "cpu_count": psutil.cpu_count(logical=True)
    }

def get_memory_info():
    """Returns Memory usage statistics."""
    mem = psutil.virtual_memory()
    return {
        "ram_percent": mem.percent,
        "ram_used": mem.used,
        "ram_total": mem.total,
        "ram_available": mem.available
    }

def get_top_processes(n=5):
    """
    Returns the top N processes sorted by memory usage (primary) and CPU usage (secondary).
    """
    processes = []
    
    # Iterate over all running processes
    for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
        try:
            # Fetch process details
            proc_info = proc.info
            
            # Filter out processes with missing critical data
            if proc_info['name'] is None or proc_info['memory_info'] is None:
                continue
                
            # The first call to cpu_percent for a process returns 0.0,
            # but in a continuous loop it will become accurate.
            # Using memory as the primary sort is more stable for immediate snapshots.
            mem_usage = proc_info['memory_info'].rss
            
            processes.append({
                "pid": proc_info['pid'],
                "name": proc_info['name'],
                "cpu": proc_info['cpu_percent'],
                "memory": mem_usage
            })
            
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # Safe handling: Process might have terminated or we don't have permissions
            pass

    # Sort primarily by memory (descending), then by CPU (descending)
    sorted_processes = sorted(
        processes, 
        key=lambda x: (x['memory'], x['cpu']), 
        reverse=True
    )
    
    return sorted_processes[:n]

def get_system_snapshot():
    """
    MAIN OUTPUT FUNCTION:
    Collects all system data and returns a structured dictionary.
    """
    # Ensure initialization has happened
    if not _is_initialized:
        initialize_monitoring()
        
    snapshot = {
        "timestamp": time.time(),
        "cpu": get_cpu_info(),
        "memory": get_memory_info(),
        "top_processes": get_top_processes()
    }
    
    return snapshot

# ---------------------------------------------------------
# LOCAL TESTING BLOCK (Removable)
# ---------------------------------------------------------
if __name__ == "__main__":
    import json
    
    print("Starting JOC System Monitor Test...")
    print("Press Ctrl+C to stop.")
    
    # Initialize first to get accurate CPU readings
    initialize_monitoring()
    time.sleep(0.5) # Give it a moment to baseline
    
    try:
        while True:
            # Clear screen for cleaner output (works on Windows/Linux)
            os.system('cls' if os.name == 'nt' else 'clear')
            
            snapshot = get_system_snapshot()
            save_snapshot(snapshot)
            # Print formatted output for easy reading
            print(f"=== System Snapshot at {time.strftime('%H:%M:%S', time.localtime(snapshot['timestamp']))} ===")
            print(f"CPU: {snapshot['cpu']['cpu_percent']}% ({snapshot['cpu']['cpu_count']} cores)")
            
            mem = snapshot['memory']
            print(f"RAM: {mem['ram_percent']}% | Used: {_bytes_to_mb(mem['ram_used'])} MB / {_bytes_to_mb(mem['ram_total'])} MB")
            print("\nTop 5 Processes:")
            print(f"{'PID':<8} | {'Name':<25} | {'RAM (MB)':<10} | {'CPU %':<8}")
            print("-" * 60)
            
            for p in snapshot['top_processes']:
                print(f"{p['pid']:<8} | {p['name']:<25} | {_bytes_to_mb(p['memory']):<10} | {p['cpu']:<8}")
                
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")