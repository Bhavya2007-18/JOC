from dataclasses import dataclass
from typing import Dict, List

from utils.logger import get_logger


logger = get_logger("optimizer.startup")


@dataclass
class StartupEntry:
    id: str
    name: str
    enabled: bool
    impact: str
    critical: bool
    simulated_only: bool = True


_STARTUP_ENTRIES: Dict[str, StartupEntry] = {
    "browser-sync": StartupEntry(
        id="browser-sync",
        name="Browser Sync Helper",
        enabled=True,
        impact="medium",
        critical=False,
    ),
    "cloud-drive": StartupEntry(
        id="cloud-drive",
        name="Cloud Drive Client",
        enabled=True,
        impact="high",
        critical=False,
    ),
    "security-suite": StartupEntry(
        id="security-suite",
        name="Security Suite",
        enabled=True,
        impact="medium",
        critical=True,
    ),
}


def list_startup_entries() -> List[StartupEntry]:
    return list(_STARTUP_ENTRIES.values())


def set_startup_enabled(entry_id: str, enabled: bool) -> StartupEntry:
    entry = _STARTUP_ENTRIES.get(entry_id)
    if entry is None:
        raise KeyError("Startup entry not found")

    if entry.critical and not enabled:
        logger.warning("Attempt to disable critical startup entry id=%s name=%s", entry.id, entry.name)
        return entry

    logger.info("Simulated set startup enabled id=%s enabled=%s", entry.id, enabled)
    entry.enabled = enabled
    return entry

