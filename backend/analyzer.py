import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("JOC.Analyzer")

# Thresholds for anomalies
CPU_THRESHOLD_PERCENT = 80.0
RAM_THRESHOLD_PERCENT = 85.0
HEAVY_PROCESS_CPU_THRESHOLD = 15.0
HEAVY_PROCESS_RAM_MB_THRESHOLD = 1024.0 # 1GB

def bytes_to_mb(bytes_val):
    return round(bytes_val / (1024 * 1024), 2)

def analyze_snapshot(snapshot):
    """
    Takes a system snapshot from monitor.py and returns an analysis dictionary
    containing detected issues, root causes, and explanations.
    """
    analysis = {
        "status": "Healthy",
        "issues": [],
        "root_cause": None,
        "explanation": "System is running smoothly.",
        "recommended_action": None
    }
    
    cpu_usage = snapshot.get("cpu", {}).get("cpu_percent", 0)
    ram_usage = snapshot.get("memory", {}).get("ram_percent", 0)
    top_processes = snapshot.get("top_processes", [])
    
    issues_detected = []
    
    # 1. Analyze CPU
    if cpu_usage > CPU_THRESHOLD_PERCENT:
        issues_detected.append("High CPU Usage")
        
    # 2. Analyze RAM
    if ram_usage > RAM_THRESHOLD_PERCENT:
        issues_detected.append("High Memory Usage")
        
    # 3. Analyze Processes (Root Cause Engine)
    heavy_cpu_procs = [p for p in top_processes if p.get("cpu", 0) > HEAVY_PROCESS_CPU_THRESHOLD]
    heavy_ram_procs = [p for p in top_processes if bytes_to_mb(p.get("memory", 0)) > HEAVY_PROCESS_RAM_MB_THRESHOLD]
    
    # Determine overall status
    if issues_detected:
        analysis["status"] = "Warning" if len(issues_detected) == 1 else "Critical"
        analysis["issues"] = issues_detected
        
        # Determine Root Cause and Explanation
        if "High Memory Usage" in issues_detected and heavy_ram_procs:
            culprit = heavy_ram_procs[0]['name']
            analysis["root_cause"] = f"{culprit} consuming massive RAM"
            analysis["explanation"] = f"{culprit} is using a lot of memory ({bytes_to_mb(heavy_ram_procs[0]['memory'])} MB), causing the system to run out of available RAM."
            analysis["recommended_action"] = {"type": "kill_process", "target": culprit, "pid": heavy_ram_procs[0]['pid']}
            
        elif "High CPU Usage" in issues_detected and heavy_cpu_procs:
            culprit = heavy_cpu_procs[0]['name']
            analysis["root_cause"] = f"{culprit} overloading CPU"
            analysis["explanation"] = f"{culprit} is consuming {heavy_cpu_procs[0]['cpu']}% of your CPU resources, causing system slowdowns."
            analysis["recommended_action"] = {"type": "kill_process", "target": culprit, "pid": heavy_cpu_procs[0]['pid']}
            
        elif "High Memory Usage" in issues_detected and "High CPU Usage" in issues_detected:
             analysis["root_cause"] = "Multiple heavy background tasks"
             analysis["explanation"] = "Your system is under heavy load from multiple background applications consuming both CPU and Memory."
             analysis["recommended_action"] = {"type": "enable_mode", "target": "Performance"}
             
        else:
             analysis["root_cause"] = "General system load"
             analysis["explanation"] = f"Overall system resource usage is high (CPU: {cpu_usage}%, RAM: {ram_usage}%)."
             analysis["recommended_action"] = {"type": "clear_ram", "target": "system"}

    return analysis

def determine_developer_mode(snapshot):
    """
    Detects if the user is in a heavy development session.
    """
    dev_processes = ["node", "code", "python", "docker", "java", "mysqld", "postgres"]
    active_dev_tools = []
    
    for p in snapshot.get("top_processes", []):
        name = p.get("name", "").lower()
        for dev_tool in dev_processes:
            if dev_tool in name and dev_tool not in active_dev_tools:
                active_dev_tools.append(dev_tool)
                
    if len(active_dev_tools) >= 2:
        return {
            "is_dev_session": True,
            "detected_tools": active_dev_tools,
            "message": f"Heavy development session detected ({', '.join(active_dev_tools)}). Optimizing for compilation and serving."
        }
    
    return {"is_dev_session": False}

if __name__ == "__main__":
    # Simple test with mock data
    mock_snapshot = {
        "cpu": {"cpu_percent": 85.5},
        "memory": {"ram_percent": 90.2},
        "top_processes": [
            {"pid": 1234, "name": "chrome", "cpu": 5.0, "memory": 2 * 1024 * 1024 * 1024}, # 2GB
            {"pid": 5678, "name": "code", "cpu": 25.0, "memory": 1 * 1024 * 1024 * 1024},  # 1GB
        ]
    }
    print(analyze_snapshot(mock_snapshot))
    print(determine_developer_mode(mock_snapshot))