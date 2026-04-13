"""Configuration constants for the Phase 1 security module."""

# Process classification
KNOWN_SAFE_PROCESSES = {
    "chrome.exe",
    "msedge.exe",
    "code.exe",
    "discord.exe",
    "spotify.exe",
    "postman.exe",
    "firefox.exe",
    "brave.exe",
    "opera.exe",
    "teams.exe",
    "zoom.exe",
    "slack.exe",
    "onedrive.exe",
    "steam.exe",
    "epicgameslauncher.exe",
    "vlc.exe",
    "winword.exe",
    "excel.exe",
    "powerpnt.exe",
    "outlook.exe",
    "notepad.exe",
    "taskmgr.exe",
    "cmd.exe",
    "powershell.exe",
    "mstsc.exe",
    "calc.exe",
    "git.exe",
    "git-bash.exe",
    "node.exe",
    "java.exe",
    "wmplayer.exe",
    "explorer.exe",
    "dwm.exe",
    "msmpeng.exe",
    "system",
    "system idle process",
    "svchost.exe",
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

IGNORE_SYSTEM_PROCESSES = {
    "memcompression",
    "system",
    "idle",
    "registry",
    "system idle process",
    "smss.exe",
    "csrss.exe",
    "winlogon.exe",
    "fontdrvhost.exe",
    "conhost.exe",
    "sihost.exe",
    "ctfmon.exe",
    "taskhostw.exe",
    "runtimebroker.exe",
    "dllhost.exe",
    "wudfhost.exe",
    "wmiapsrv.exe",
    "wmiprvse.exe",
    "sppsvc.exe",
    "searchindexer.exe",
    "searchprotocolhost.exe",
    "searchfilterhost.exe",
    "audiodg.exe",
    "spoolsv.exe",
    "lsm.exe",
    "werfault.exe",
    "wlanext.exe",
    "securityhealthservice.exe",
    "securityhealthsystray.exe",
    "wininit.exe",
    "services.exe",
    "lsass.exe",
    "svchost.exe",
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

