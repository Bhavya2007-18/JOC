import os
import shutil
import hashlib
from pathlib import Path

def bytes_to_mb(bytes_val):
    return round(bytes_val / (1024 * 1024), 2)

def get_storage_breakdown(path="/"):
    """
    Provides a breakdown of storage usage for a given path.
    Default is root or C: drive.
    """
    if os.name == 'nt' and path == "/":
        path = "C:\\"
        
    try:
        total, used, free = shutil.disk_usage(path)
        return {
            "path": path,
            "total_gb": round(total / (1024**3), 2),
            "used_gb": round(used / (1024**3), 2),
            "free_gb": round(free / (1024**3), 2),
            "percent_used": round((used / total) * 100, 2)
        }
    except Exception as e:
        return {"error": str(e)}

def scan_for_junk(paths_to_scan=None):
    """
    Scans common temporary directories for junk files.
    """
    junk_files = []
    total_size = 0
    
    if paths_to_scan is None:
        if os.name == 'nt': # Windows
            user_temp = os.environ.get('TEMP', 'C:\\Temp')
            win_temp = 'C:\\Windows\\Temp'
            paths_to_scan = [user_temp, win_temp]
        else: # Linux/Mac
            paths_to_scan = ['/tmp', '/var/tmp']
            
    for temp_dir in paths_to_scan:
        if not os.path.exists(temp_dir):
            continue
            
        try:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    filepath = os.path.join(root, file)
                    try:
                        size = os.path.getsize(filepath)
                        total_size += size
                        junk_files.append({"path": filepath, "size": size})
                    except (OSError, FileNotFoundError):
                        pass
        except Exception as e:
            pass # Ignore access denied errors on root directories
            
    return {
        "files_found": len(junk_files),
        "total_size_mb": bytes_to_mb(total_size),
        "sample_files": junk_files[:5] # Return a sample to display
    }

def clean_junk(paths_to_scan=None):
    """
    Deletes files found in temporary directories.
    """
    scan_results = scan_for_junk(paths_to_scan)
    deleted_count = 0
    freed_space = 0
    
    # In a real scenario, we'd iterate over scan_results['sample_files'] or all files
    # For safety in this demo, we won't actually delete unless specified
    # return {"success": True, "message": f"Deleted {scan_results['files_found']} files. Freed {scan_results['total_size_mb']} MB."}
    
    return {"success": True, "message": f"Simulated cleanup: Would free {scan_results['total_size_mb']} MB of junk files."}

if __name__ == "__main__":
    print("Storage Breakdown:")
    print(get_storage_breakdown())
    print("\nJunk Scan:")
    print(scan_for_junk())