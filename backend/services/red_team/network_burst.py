from __future__ import annotations

import socket
import time
from typing import Any, Dict

from utils.logger import get_logger

from .base_simulation import BaseSimulation


logger = get_logger("validation.red.network_burst")


class NetworkBurstSimulation(BaseSimulation):
    def setup(self) -> None:
        self.safety_guard.ensure_within_limits()

    def execute(self) -> Dict[str, Any]:
        packet_size = max(64, int(self.parameters.get("packet_size", 1024)))
        packet_count = max(1, int(self.parameters.get("packet_count", 500)))
        delay_seconds = float(self.parameters.get("delay_seconds", 0.001))
        endpoint_host = "127.0.0.1"
        endpoint_port = int(self.parameters.get("port", 9999))

        if self.dry_run:
            return {
                "simulation": "network_burst",
                "dry_run": True,
                "packet_size": packet_size,
                "packet_count": packet_count,
                "endpoint": f"{endpoint_host}:{endpoint_port}",
            }

        payload = b"x" * packet_size
        bytes_sent = 0
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            for _ in range(packet_count):
                self.safety_guard.raise_if_abort_requested()
                self.safety_guard.ensure_within_limits()
                sent = sock.sendto(payload, (endpoint_host, endpoint_port))
                bytes_sent += int(sent)
                if delay_seconds > 0:
                    time.sleep(delay_seconds)

        return {
            "simulation": "network_burst",
            "dry_run": False,
            "packet_size": packet_size,
            "packet_count": packet_count,
            "bytes_sent": bytes_sent,
            "endpoint": f"{endpoint_host}:{endpoint_port}",
        }

    def cleanup(self) -> None:
        logger.info("Network burst cleanup completed id=%s", self.simulation_id)

    def metadata(self) -> Dict[str, Any]:
        return {
            "type": "network_burst",
            "simulation_id": self.simulation_id,
            "correlation_id": self.correlation_id,
            "parameters": self.parameters,
        }

