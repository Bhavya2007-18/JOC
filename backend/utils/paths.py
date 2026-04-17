import os
import sys
from pathlib import Path

def get_persistent_dir(subfolder=""):
    """
    Returns a Path object pointing to a persistent directory for JOC_Sentinel.
    If running as a PyInstaller EXE, it uses %APPDATA%/JOC_Sentinel.
    Otherwise, it uses the local backend directory to stay self-contained in dev.
    """
    if getattr(sys, 'frozen', False):
        base = Path(os.environ.get("APPDATA", os.path.expanduser("~"))) / "JOC_Sentinel"
    else:
        # Resolve to backend/
        base = Path(__file__).resolve().parent.parent

    if subfolder:
        base = base / subfolder

    base.mkdir(parents=True, exist_ok=True)
    return base

def get_persistent_path(filename, subfolder="storage"):
    return get_persistent_dir(subfolder) / filename
