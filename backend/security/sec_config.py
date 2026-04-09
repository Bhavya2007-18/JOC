"""Configuration constants for the Phase 1 security module."""

# Process classification
KNOWN_SAFE_PROCESSES = {
    "system",
    "system idle process",
    "svchost.exe",
    "explorer.exe",
    "wininit.exe",
    "services.exe",
    "python.exe",
    "pythonw.exe",
}

FOREGROUND_APPS = {
    "chrome.exe",
    "msedge.exe",
    "firefox.exe",
    "code.exe",
    "devenv.exe",
    "notepad.exe",
    "teams.exe",
}

KNOWN_NETWORK_APPS = {
    "chrome.exe",
    "msedge.exe",
    "firefox.exe",
    "code.exe",
    "teams.exe",
    "discord.exe",
    "onedrive.exe",
}

# Thresholds
CPU_SPIKE_THRESHOLD = 80.0
RAM_HOG_THRESHOLD_MB = 1024.0
IDLE_CPU_THRESHOLD = 1.0
IDLE_RAM_THRESHOLD_MB = 300.0

# Risk weights
RISK_WEIGHTS = {
    "suspicious_process": 25,
    "high_cpu_process": 20,
    "high_ram_process": 20,
    "idle_resource_hog": 15,
    "unknown_network_access": 20,
}

