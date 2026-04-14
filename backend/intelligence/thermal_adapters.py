"""
Thermal sensor adapters for Phase 2 hardware telemetry integration.

Design goals:
- Keep ThermalEngine source-agnostic
- Prefer real hardware sensors when available
- Graceful fallback to synthetic estimation
- Thread-safe caching to avoid expensive polling each cycle
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from threading import Lock
from typing import Optional, Tuple

from utils.logger import get_logger

logger = get_logger("thermal.adapters")


class BaseThermalAdapter(ABC):
    @abstractmethod
    def is_available(self) -> bool:
        ...

    @abstractmethod
    def get_cpu_temp(self) -> Optional[float]:
        ...

    @abstractmethod
    def get_gpu_temp(self) -> Optional[float]:
        ...


class SyntheticAdapter(BaseThermalAdapter):
    _MIN_TEMP = 40.0
    _MAX_TEMP = 95.0

    def __init__(self) -> None:
        self._last_cpu_usage: float = 0.0

    def is_available(self) -> bool:
        return True

    @staticmethod
    def _clamp(value: float, lo: float, hi: float) -> float:
        return max(lo, min(hi, value))

    def set_cpu_usage(self, cpu_usage: float) -> None:
        self._last_cpu_usage = self._clamp(float(cpu_usage), 0.0, 100.0)

    def get_cpu_temp(self) -> Optional[float]:
        estimated = 40.0 + (self._last_cpu_usage * 0.5)
        return round(self._clamp(estimated, self._MIN_TEMP, self._MAX_TEMP), 2)

    def get_gpu_temp(self) -> Optional[float]:
        return None


class LHMAdapter(BaseThermalAdapter):
    def __init__(self) -> None:
        self._wmi = None
        self._available = False
        self._init_client()

    def _init_client(self) -> None:
        try:
            import wmi  # type: ignore

            self._wmi = wmi.WMI(namespace=r"root\LibreHardwareMonitor")
            self._available = True
        except Exception:
            self._wmi = None
            self._available = False

    def is_available(self) -> bool:
        return self._available

    def _query_temperature_sensors(self):
        if not self._available or self._wmi is None:
            return []
        try:
            return self._wmi.Sensor()
        except Exception:
            self._available = False
            return []

    def get_cpu_temp(self) -> Optional[float]:
        sensors = self._query_temperature_sensors()
        if not sensors:
            return None

        cpu_values = []
        for sensor in sensors:
            try:
                sensor_type = str(getattr(sensor, "SensorType", ""))
                name = str(getattr(sensor, "Name", ""))
                value = getattr(sensor, "Value", None)
                if sensor_type != "Temperature" or value is None:
                    continue
                name_upper = name.upper()
                if "CPU PACKAGE" in name_upper or "CPU CORE" in name_upper:
                    cpu_values.append(float(value))
            except Exception:
                continue

        if not cpu_values:
            return None
        return round(sum(cpu_values) / len(cpu_values), 2)

    def get_gpu_temp(self) -> Optional[float]:
        sensors = self._query_temperature_sensors()
        if not sensors:
            return None

        gpu_values = []
        for sensor in sensors:
            try:
                sensor_type = str(getattr(sensor, "SensorType", ""))
                name = str(getattr(sensor, "Name", ""))
                value = getattr(sensor, "Value", None)
                if sensor_type != "Temperature" or value is None:
                    continue
                if "GPU CORE" in name.upper():
                    gpu_values.append(float(value))
            except Exception:
                continue

        if not gpu_values:
            return None
        return round(sum(gpu_values) / len(gpu_values), 2)


class NvidiaAdapter(BaseThermalAdapter):
    def __init__(self) -> None:
        self._nvml = None
        self._available = False
        self._init_nvml()

    def _init_nvml(self) -> None:
        try:
            import pynvml  # type: ignore

            self._nvml = pynvml
            self._nvml.nvmlInit()
            self._available = True
        except Exception:
            self._nvml = None
            self._available = False

    def is_available(self) -> bool:
        return self._available

    def get_cpu_temp(self) -> Optional[float]:
        return None

    def get_gpu_temp(self) -> Optional[float]:
        if not self._available or self._nvml is None:
            return None
        try:
            handle = self._nvml.nvmlDeviceGetHandleByIndex(0)
            value = self._nvml.nvmlDeviceGetTemperature(
                handle, self._nvml.NVML_TEMPERATURE_GPU
            )
            return round(float(value), 2)
        except Exception:
            self._available = False
            return None


class ThermalAdapterManager:
    _instance: Optional["ThermalAdapterManager"] = None

    def __init__(self, cache_ttl_seconds: float = 1.5) -> None:
        self.adapters = [LHMAdapter(), NvidiaAdapter(), SyntheticAdapter()]
        self._cache_ttl = max(1.0, float(cache_ttl_seconds))
        self._cache_lock = Lock()
        self._cached_at = 0.0
        self._cached_value: Optional[Tuple[float, Optional[float], str, str]] = None
        self._last_source: Optional[str] = None

    @classmethod
    def get_instance(cls) -> "ThermalAdapterManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_best_temp(self, cpu_usage: float) -> Tuple[float, Optional[float], str, str]:
        now = time.time()
        with self._cache_lock:
            if self._cached_value and (now - self._cached_at) < self._cache_ttl:
                return self._cached_value

        cpu = max(0.0, min(100.0, float(cpu_usage)))
        best_cpu: Optional[float] = None
        best_gpu: Optional[float] = None
        best_source = "SyntheticAdapter"
        best_confidence = "low"

        for adapter in self.adapters:
            try:
                if isinstance(adapter, SyntheticAdapter):
                    adapter.set_cpu_usage(cpu)

                if not adapter.is_available():
                    continue

                cpu_temp = adapter.get_cpu_temp()
                gpu_temp = adapter.get_gpu_temp()

                if cpu_temp is not None:
                    best_cpu = float(cpu_temp)
                    best_gpu = float(gpu_temp) if gpu_temp is not None else None
                    best_source = adapter.__class__.__name__
                    best_confidence = "high" if best_source != "SyntheticAdapter" else "low"
                    break
            except Exception:
                continue

        if best_cpu is None:
            synthetic = self.adapters[-1]
            if isinstance(synthetic, SyntheticAdapter):
                synthetic.set_cpu_usage(cpu)
                fallback_temp = synthetic.get_cpu_temp()
                best_cpu = float(fallback_temp) if fallback_temp is not None else 40.0
            else:
                best_cpu = 40.0
            best_gpu = None
            best_source = "SyntheticAdapter"
            best_confidence = "low"

        result = (round(best_cpu, 2), best_gpu, best_source, best_confidence)

        with self._cache_lock:
            self._cached_value = result
            self._cached_at = now
            previous = self._last_source
            self._last_source = best_source

        if previous and previous != best_source:
            logger.info(
                'THERMAL_SOURCE_SWITCH {"event":"THERMAL_SOURCE_SWITCH","from":"%s","to":"%s"}',
                previous,
                best_source,
            )

        return result
