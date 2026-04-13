"""Rule-based threat detection from process signals."""

from backend.security.sec_config import IGNORE_SYSTEM_PROCESSES
from backend.security.sec_models import ProcessInfo, ThreatItem, ThreatSeverity


def detect_threats(processes: list[ProcessInfo]) -> list[ThreatItem]:
    """Convert analyzed processes into structured threat items."""
    threats: list[ThreatItem] = []
    seen: set[tuple[str, str]] = set()

    for proc in processes:
        name = (proc.name or "unknown").lower()
        if name in IGNORE_SYSTEM_PROCESSES:
            continue

        if proc.classification == "known_safe":
            continue

        process_name = name

        if proc.classification == "suspicious":
            category = "suspicious_process"
            threat_id = f"{proc.pid}_{category}".lower()
            key = (process_name, category)
            if key not in seen:
                threats.append(
                    ThreatItem(
                        id=threat_id,
                        category=category,
                        severity=ThreatSeverity.HIGH,
                        title="Suspicious Process Detected",
                        description=(
                            f"Process {proc.name} flagged as suspicious "
                            f"(CPU: {proc.cpu_percent:.1f}%, RAM: {proc.ram_mb:.1f} MB)."
                        ),
                        pid=proc.pid,
                        process_name=proc.name,
                    )
                )
                seen.add(key)

        if proc.classification == "unknown" and proc.cpu_percent > 1:
            category = "unknown_process"
            threat_id = f"{proc.pid}_{category}".lower()
            key = (process_name, category)
            if key not in seen:
                threats.append(
                    ThreatItem(
                        id=threat_id,
                        category=category,
                        severity=ThreatSeverity.MEDIUM,
                        title="Unknown Process",
                        description=(
                            f"Process {proc.name} (PID {proc.pid}) is not recognized."
                        ),
                        pid=proc.pid,
                        process_name=proc.name,
                    )
                )
                seen.add(key)

        if proc.is_idle:
            category = "idle_resource_hog"
            threat_id = f"{proc.pid}_{category}".lower()
            key = (process_name, category)
            if key not in seen:
                threats.append(
                    ThreatItem(
                        id=threat_id,
                        category=category,
                        severity=ThreatSeverity.MEDIUM,
                        title="Idle Resource Usage",
                        description=(
                            f"Process {proc.name} is mostly idle with low CPU but "
                            f"high RAM usage ({proc.ram_mb:.1f} MB)."
                        ),
                        pid=proc.pid,
                        process_name=proc.name,
                    )
                )
                seen.add(key)

        if proc.is_background and proc.classification == "suspicious":
            category = "background_suspicious"
            threat_id = f"{proc.pid}_{category}".lower()
            key = (process_name, category)
            if key not in seen:
                threats.append(
                    ThreatItem(
                        id=threat_id,
                        category=category,
                        severity=ThreatSeverity.HIGH,
                        title="Suspicious Background Activity",
                        description=(
                            f"Suspicious background process {proc.name} detected "
                            f"(PID {proc.pid})."
                        ),
                        pid=proc.pid,
                        process_name=proc.name,
                    )
                )
                seen.add(key)

    return threats
