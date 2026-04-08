from __future__ import annotations

import subprocess
import sys
import time
from typing import Any, Dict, Optional

from utils.logger import get_logger

from .base_simulation import BaseSimulation


logger = get_logger("validation.red.process_simulator")


class ProcessSimulation(BaseSimulation):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._process: Optional[subprocess.Popen] = None

    def setup(self) -> None:
        self.safety_guard.ensure_within_limits()

    def execute(self) -> Dict[str, Any]:
        lifespan = float(self.parameters.get("lifespan", 5))
        simulated_name = str(self.parameters.get("name", "simulated_suspicious_process"))
        cpu_burst = bool(self.parameters.get("cpu_burst", True))

        if self.dry_run:
            return {
                "simulation": "process_simulator",
                "dry_run": True,
                "name": simulated_name,
                "lifespan": lifespan,
                "cpu_burst": cpu_burst,
            }

        if cpu_burst:
            python_code = (
                "import time\n"
                "end=time.time()+%s\n"
                "while time.time()<end:\n"
                "    sum(i*i for i in range(4000))\n"
            ) % lifespan
        else:
            python_code = "import time; time.sleep(%s)" % lifespan

        self._process = subprocess.Popen(
            [sys.executable, "-c", python_code, "--sim-name", simulated_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        start = time.time()
        while time.time() - start < lifespan:
            self.safety_guard.raise_if_abort_requested()
            self.safety_guard.ensure_within_limits()
            if self._process.poll() is not None:
                break
            time.sleep(0.1)

        return {
            "simulation": "process_simulator",
            "dry_run": False,
            "name": simulated_name,
            "lifespan": lifespan,
            "pid": self._process.pid if self._process else None,
        }

    def cleanup(self) -> None:
        if self._process and self._process.poll() is None:
            try:
                self._process.terminate()
            except OSError:
                pass
        logger.info("Process simulation cleaned up id=%s", self.simulation_id)

    def metadata(self) -> Dict[str, Any]:
        return {
            "type": "process_simulator",
            "simulation_id": self.simulation_id,
            "correlation_id": self.correlation_id,
            "parameters": self.parameters,
        }

