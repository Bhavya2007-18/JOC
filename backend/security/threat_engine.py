"""Rule-based threat detection from process signals."""

from backend.security.sec_models import ProcessInfo, ThreatItem, ThreatSeverity


def detect_threats(processes: list[ProcessInfo]) -> list[ThreatItem]:
    """Convert analyzed processes into structured threat items."""
    threats: list[ThreatItem] = []
    seen_ids: set[str] = set()

    for proc in processes:
        if proc.classification == "suspicious":
            category = "suspicious_process"
            threat_id = f"{proc.pid}_{category}"
            if threat_id not in seen_ids:
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
                seen_ids.add(threat_id)

        if proc.classification == "unknown":
            category = "unknown_process"
            threat_id = f"{proc.pid}_{category}"
            if threat_id not in seen_ids:
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
                seen_ids.add(threat_id)

        if proc.is_idle:
            category = "idle_resource_hog"
            threat_id = f"{proc.pid}_{category}"
            if threat_id not in seen_ids:
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
                seen_ids.add(threat_id)

        if proc.is_background and proc.classification == "suspicious":
            category = "background_suspicious"
            threat_id = f"{proc.pid}_{category}"
            if threat_id not in seen_ids:
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
                seen_ids.add(threat_id)

    return threats
