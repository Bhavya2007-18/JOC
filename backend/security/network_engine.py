"""Network collection and behavior analysis stage."""

import importlib

from .sec_utils import current_timestamp, safe_connection_pid


def collect_network_connections() -> list[dict]:
    """Collect network connection snapshots from psutil."""
    try:
        psutil = importlib.import_module("psutil")
    except Exception:
        return []

    items: list[dict] = []
    for conn in psutil.net_connections(kind="inet"):
        items.append(
            {
                "pid": safe_connection_pid(conn),
                "status": getattr(conn, "status", "UNKNOWN"),
            }
        )
    return items


def analyze_network(process_analysis: dict) -> dict:
    """Find unknown processes that also use network connections."""
    connections = collect_network_connections()
    unknown_pids = {
        process.get("pid")
        for process in process_analysis.get("unknown_processes", [])
        if process.get("pid") is not None
    }

    unknown_network_apps = [
        conn
        for conn in connections
        if conn.get("pid") in unknown_pids and conn.get("status") != "NONE"
    ]

    return {
        "timestamp": current_timestamp(),
        "connections": connections,
        "unknown_network_apps": unknown_network_apps,
    }
