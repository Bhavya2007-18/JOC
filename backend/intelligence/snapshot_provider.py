from __future__ import annotations

import time
from typing import Dict, List, Optional

import psutil

from .models import ProcessInfo, SystemSnapshot


_BYTES_PER_MB = 1024.0 * 1024.0
_previous_disk = None
_previous_net = None
_previous_time = None


def _bytes_to_mb(value: int) -> float:
	return float(value) / _BYTES_PER_MB


def _safe_username(proc: psutil.Process) -> Optional[str]:
	try:
		return proc.username()
	except (psutil.AccessDenied, psutil.NoSuchProcess):
		return None


def _safe_io_counters(proc: psutil.Process) -> tuple[Optional[int], Optional[int]]:
	try:
		io = proc.io_counters()
		if io is None:
			return None, None
		return io.read_bytes, io.write_bytes
	except (psutil.AccessDenied, psutil.NoSuchProcess, AttributeError):
		return None, None


def _collect_services() -> List[Dict[str, str]]:
	services: List[Dict[str, str]] = []
	if not hasattr(psutil, "win_service_iter"):
		return services

	try:
		for service in psutil.win_service_iter():
			try:
				services.append(
					{
						"name": service.name(),
						"status": service.status(),
						"display_name": service.display_name(),
					}
				)
			except (psutil.AccessDenied, psutil.NoSuchProcess, OSError):
				continue
	except (psutil.AccessDenied, NotImplementedError, OSError, AttributeError):
		return []

	return services


def collect_snapshot() -> SystemSnapshot:
	global _previous_disk, _previous_net, _previous_time

	process_handles = list(
		psutil.process_iter(
			attrs=[
				"pid",
				"name",
				"memory_info",
				"memory_percent",
				"status",
				"create_time",
				"num_threads",
			]
		)
	)

	for proc in process_handles:
		try:
			proc.cpu_percent(interval=None)
		except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
			continue

	cpu_percent = psutil.cpu_percent(interval=0.5)
	cpu_per_core = psutil.cpu_percent(interval=None, percpu=True)

	vm = psutil.virtual_memory()
	disk_usage = psutil.disk_usage("/")
	services = _collect_services()

	processes: List[ProcessInfo] = []
	for proc in process_handles:
		try:
			memory_info = proc.info["memory_info"]
			if memory_info is None:
				continue
			read_bytes, write_bytes = _safe_io_counters(proc)

			processes.append(
				ProcessInfo(
					pid=proc.info["pid"],
					name=proc.info["name"] or "unknown",
					cpu_percent=proc.cpu_percent(interval=None),
					memory_mb=_bytes_to_mb(memory_info.rss),
					memory_percent=float(proc.info["memory_percent"] or 0.0),
					status=proc.info["status"] or "unknown",
					create_time=float(proc.info["create_time"] or 0.0),
					num_threads=int(proc.info["num_threads"] or 0),
					io_read_bytes=read_bytes,
					io_write_bytes=write_bytes,
					username=_safe_username(proc),
				)
			)
		except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
			continue

	top_processes = sorted(processes, key=lambda process: process.memory_mb, reverse=True)[:5]
	disk_heavy_processes = sorted(
		processes,
		key=lambda process: (process.io_read_bytes or 0) + (process.io_write_bytes or 0),
		reverse=True,
	)[:5]

	current_time = time.time()
	disk_counters = psutil.disk_io_counters()
	net_counters = psutil.net_io_counters()
	current_disk = None
	current_net = None

	if disk_counters is not None:
		current_disk = (float(disk_counters.read_bytes), float(disk_counters.write_bytes))
	if net_counters is not None:
		current_net = (float(net_counters.bytes_sent), float(net_counters.bytes_recv))

	disk_read_rate = 0.0
	disk_write_rate = 0.0
	net_sent_rate = 0.0
	net_recv_rate = 0.0

	if _previous_time is not None:
		time_diff = current_time - _previous_time
		if time_diff <= 0:
			disk_read_rate = 0.0
			disk_write_rate = 0.0
			net_sent_rate = 0.0
			net_recv_rate = 0.0
		else:
			if _previous_disk is not None and current_disk is not None:
				prev_read, prev_write = _previous_disk
				curr_read, curr_write = current_disk
				disk_read_delta = max(0.0, curr_read - prev_read)
				disk_write_delta = max(0.0, curr_write - prev_write)
				disk_read_rate = disk_read_delta / time_diff
				disk_write_rate = disk_write_delta / time_diff
			if _previous_net is not None and current_net is not None:
				prev_sent, prev_recv = _previous_net
				curr_sent, curr_recv = current_net
				net_sent_delta = max(0.0, curr_sent - prev_sent)
				net_recv_delta = max(0.0, curr_recv - prev_recv)
				net_sent_rate = net_sent_delta / time_diff
				net_recv_rate = net_recv_delta / time_diff

	_previous_disk = current_disk
	_previous_net = current_net
	_previous_time = current_time

	return SystemSnapshot(
		timestamp=current_time,
		cpu_percent=cpu_percent,
		cpu_per_core=cpu_per_core,
		memory_total_mb=_bytes_to_mb(vm.total),
		memory_used_mb=_bytes_to_mb(vm.used),
		memory_percent=vm.percent,
		swap_percent=psutil.swap_memory().percent,
		disk_total=int(disk_usage.total),
		disk_used=int(disk_usage.used),
		disk_percent=float(disk_usage.percent),
		disk_read_bytes_per_sec=disk_read_rate,
		disk_write_bytes_per_sec=disk_write_rate,
		net_bytes_sent_per_sec=net_sent_rate,
		net_bytes_recv_per_sec=net_recv_rate,
		process_count=len(process_handles),
		top_processes=top_processes,
		disk_heavy_processes=disk_heavy_processes,
		boot_time=psutil.boot_time(),
		services=services,
	)
