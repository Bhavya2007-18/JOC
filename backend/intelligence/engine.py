from __future__ import annotations
import time
from typing import List
from intelligence.constants import CRITICAL_PROCESSES
from intelligence.state_manager import StateManager
from intelligence.utils.anomaly import compute_z_score, is_anomaly
from .models import (
	ActionSuggestion,
	ActionType,
	DiagnosticReport,
	Issue,
	RiskLevel,
	SystemSnapshot,
	Severity,
)

class IntelligenceEngine:
	state_manager = StateManager()

	def analyze(self, snapshot: SystemSnapshot) -> DiagnosticReport:
		issues: List[Issue] = []
		anomalies: List[Issue] = []

		IntelligenceEngine.state_manager.add_snapshot(snapshot)
		history = IntelligenceEngine.state_manager.get_recent()

		avg_cpu = sum(item.cpu_percent for item in history) / len(history)
		avg_memory = sum(item.memory_percent for item in history) / len(history)
		
		cpu_history = [item.cpu_percent for item in history]
		memory_history = [item.memory_percent for item in history]
		disk_history = [item.disk_percent for item in history]

		cpu_values = cpu_history
		memory_values = memory_history
		cpu_z = compute_z_score(snapshot.cpu_percent, cpu_history)
		memory_z = compute_z_score(snapshot.memory_percent, memory_history)
		disk_z_score = compute_z_score(snapshot.disk_percent, disk_history)
		_ = disk_z_score  # Placeholder for future disk anomaly issue generation.

		cpu_increasing = all(x < y for x, y in zip(cpu_values, cpu_values[1:]))
		memory_increasing = all(x < y for x, y in zip(memory_values, memory_values[1:]))
		history_ready = IntelligenceEngine.state_manager.has_enough_data()
		cpu_consistently_high = all(x > 75 for x in cpu_values) if history_ready else False
		memory_consistently_high = all(x > 75 for x in memory_values) if history_ready else False


		def _unique_process_names(process_names: List[str]) -> List[str]:
			unique_names: List[str] = []
			for name in process_names:
				if name not in unique_names:
					unique_names.append(name)
			return unique_names

		def _join_with_or(names: List[str]) -> str:
			if not names:
				return ""
			if len(names) == 1:
				return names[0]
			if len(names) == 2:
				return f"{names[0]} or {names[1]}"
			return f"{', '.join(names[:-1])}, or {names[-1]}"

		def _build_suggestion(affected_processes: List[dict], generic_suggestion: str) -> str:
			if affected_processes:
				names = [p["name"] for p in affected_processes]
				if len(names) == 1:
					return f"Consider closing {names[0]}"
				if len(names) == 2:
					return f"Consider closing {names[0]} or {names[1]}"
				return f"Consider closing {', '.join(names[:-1])}, or {names[-1]}"
			return generic_suggestion

		top_cpu_processes = sorted(
			snapshot.top_processes,
			key=lambda process: process.cpu_percent,
			reverse=True,
		)[:2]
		affected_cpu_processes = [
			{"name": process.name, "pid": process.pid}
			for process in top_cpu_processes
		]
		affected_cpu_process_names = _unique_process_names(
			[process.name for process in top_cpu_processes]
		)

		top_memory_processes = sorted(
			snapshot.top_processes,
			key=lambda process: process.memory_mb,
			reverse=True,
		)[:2]
		affected_memory_processes = [
			{"name": process.name, "pid": process.pid}
			for process in top_memory_processes
		]

		if is_anomaly(cpu_z):
			cpu_anomaly_issue = Issue(
				id="CPU_ANOMALY",
				category="cpu",
				severity=Severity.MEDIUM,
				title="Abnormal CPU Usage Detected",
				cause="CPU usage deviates significantly from recent baseline",
				explanation="CPU usage is significantly higher than usual behavior",
				confidence=min(1.0, abs(cpu_z) / 3.0),
				affected_processes=affected_cpu_processes,
				suggestion="Inspect recent workload spikes and high-CPU processes",
				evidence={
					"current": snapshot.cpu_percent,
					"z_score": cpu_z,
				},
				suggested_actions=[],
			)
			cpu_anomaly_issue.clamp_confidence()
			issues.append(cpu_anomaly_issue)
			anomalies.append(cpu_anomaly_issue)

		if is_anomaly(memory_z):
			memory_anomaly_issue = Issue(
				id="MEMORY_ANOMALY",
				category="memory",
				severity=Severity.MEDIUM,
				title="Abnormal Memory Usage Detected",
				cause="Memory usage deviates significantly from recent baseline",
				explanation="Memory usage is significantly higher than usual behavior",
				confidence=min(1.0, abs(memory_z) / 3.0),
				affected_processes=affected_memory_processes,
				suggestion="Inspect recent memory growth and high-memory processes",
				evidence={
					"current": snapshot.memory_percent,
					"z_score": memory_z,
				},
				suggested_actions=[],
			)
			memory_anomaly_issue.clamp_confidence()
			issues.append(memory_anomaly_issue)
			anomalies.append(memory_anomaly_issue)

		if snapshot.cpu_percent > 80:
			cpu_suggestion = _build_suggestion(
				affected_cpu_processes,
				"Close heavy applications or background processes",
			)
			cpu_suggested_actions: List[ActionSuggestion] = []
			if affected_cpu_processes:
				process = top_cpu_processes[0]
				process_name = process.name
				process_pid = process.pid	
				normalized_process_name = process_name.lower().replace(".exe", "")

				if normalized_process_name not in CRITICAL_PROCESSES:
					cpu_suggested_actions.append(
						ActionSuggestion(
							action_type=ActionType.KILL_PROCESS,
							target=process_name,
							description=f"Close {process_name} to reduce CPU usage",
							risk_level=RiskLevel.MODERATE,
							reversible=False,
							parameters={"pid": process.pid},
							estimated_impact="Immediate CPU usage reduction",
						)
					)
			cpu_suggested_actions.append(
				ActionSuggestion(
					action_type=ActionType.SYSTEM_TWEAK,
					target="high_performance_mode",
					description="Enable high performance mode to improve CPU performance",
					risk_level=RiskLevel.MODERATE,
					reversible=True,
					parameters={},
					estimated_impact="Improves CPU performance under load",
				)
			)
			cpu_evidence = {"cpu_percent": snapshot.cpu_percent}
			if top_cpu_processes:
				process = top_cpu_processes[0]
				normalized_process_name = process.name.lower().replace(".exe", "")
				if normalized_process_name not in CRITICAL_PROCESSES:
					cpu_evidence["fix_action"] = {
						"action": "kill_process",
						"target": process.name,
						"pid": process.pid,
					}
			if top_cpu_processes:
				cpu_process_details = " and ".join(
					f"{process.name} ({process.cpu_percent:.0f}%)" for process in top_cpu_processes	
				)
				cpu_cause = f"CPU usage is high due to {cpu_process_details}"
				cpu_explanation = (
					"Your system is experiencing high CPU usage, and specific applications are "
					"contributing heavily to the load."
				)
			else:
				cpu_cause = "CPU usage is above 80%"
				cpu_explanation = (
					"Your system is experiencing high CPU usage which may slow down performance."
				)

			cpu_issue = Issue(
				id="HIGH_CPU",
				category="cpu",
				severity=Severity.MEDIUM,
				title="High CPU Usage",
				cause=cpu_cause,
				explanation=cpu_explanation,
				confidence=min(1.0, snapshot.cpu_percent / 100),
				affected_processes=affected_cpu_processes,
				suggestion=cpu_suggestion,
				evidence=cpu_evidence,
				suggested_actions=cpu_suggested_actions,
			)
			cpu_issue.clamp_confidence()
			issues.append(cpu_issue)

		if cpu_consistently_high:
			cpu_sustained_issue = Issue(
				id="CPU_SUSTAINED_HIGH",
				category="cpu",
				severity=Severity.HIGH,
				title="Sustained High CPU Usage",
				cause="CPU usage has remained consistently high over multiple checks",
				explanation="This indicates prolonged system stress, not just a temporary spike.",
				confidence=0.9,
				affected_processes=affected_cpu_processes,
				suggestion="Consider closing heavy applications or restarting system",
				evidence={"cpu_history": cpu_values},
				suggested_actions=[],
			)
			issues.append(cpu_sustained_issue)

		if snapshot.memory_percent > 80:
			memory_suggestion = _build_suggestion(
				affected_memory_processes,
				"Close memory-intensive applications or restart unused services",
			)
			memory_suggested_actions: List[ActionSuggestion] = []
			if affected_memory_processes:
				safe_process = None
				for p in affected_memory_processes:
					process_name = p["name"].lower().replace(".exe", "")
					if process_name not in CRITICAL_PROCESSES:
						safe_process = p
						break

				if safe_process:
					process_name = safe_process["name"]
					process_pid = safe_process["pid"]
					memory_suggested_actions.append(
						ActionSuggestion(
							action_type=ActionType.KILL_PROCESS,
							target=process_name,
							description=f"Close {process_name} to free memory",
							risk_level=RiskLevel.MODERATE,
							reversible=False,
							parameters={"pid": process_pid},
							estimated_impact="Immediate memory usage reduction",
						)
					)
			memory_suggested_actions.append(
				ActionSuggestion(
					action_type=ActionType.SYSTEM_TWEAK,
					target="reduce_visual_effects",
					description="Reduce UI animations to lower memory usage",
					risk_level=RiskLevel.SAFE,
					reversible=True,
					parameters={},
					estimated_impact="Reduces RAM usage and improves responsiveness",
				)
			)
			memory_evidence = {"memory_percent": snapshot.memory_percent}
			if affected_memory_processes:
				safe_process = None
				for p in affected_memory_processes:
					process_name = p["name"].lower().replace(".exe", "")
					if process_name not in CRITICAL_PROCESSES:
						safe_process = p
						break

				if safe_process:
					process_name = safe_process["name"]
					process_pid = safe_process["pid"]
					memory_evidence["fix_action"] = {
						"action": "kill_process",
						"target": process_name,
						"pid": process_pid
					}
			if top_memory_processes:
				memory_process_details = " and ".join(
					f"{process.name} ({process.memory_mb:.0f} MB)" for process in top_memory_processes
				)
				memory_cause = f"Memory usage is high due to {memory_process_details}"
				memory_explanation = (
					"Your system is experiencing high memory usage, and specific applications are "
					"consuming significant RAM."
				)
			else:
				memory_cause = "Memory usage is above 80%"
				memory_explanation = (
					"Your system is experiencing high memory usage which may slow down performance."
				)

			memory_issue = Issue(
				id="HIGH_MEMORY",
				category="memory",
				severity=Severity.HIGH,
				title="High Memory Usage",
				cause=memory_cause,
				explanation=memory_explanation,
				confidence=min(1.0, snapshot.memory_percent / 100),
				affected_processes=affected_memory_processes,
				suggestion=memory_suggestion,
				evidence=memory_evidence,
				suggested_actions=memory_suggested_actions,
			)
			memory_issue.clamp_confidence()
			issues.append(memory_issue)

		if memory_increasing and history_ready:
			memory_leak_issue = Issue(
				id="MEMORY_LEAK_PATTERN",
				category="memory",
				severity=Severity.MEDIUM,
				title="Memory Usage Increasing Over Time",
				cause="Memory usage shows a steady upward trend",
				explanation="This may indicate a memory leak or accumulating background processes.",
				confidence=0.85,
				affected_processes=affected_memory_processes,
				suggestion="Monitor or restart high memory applications",
				evidence={"memory_history": memory_values},
				suggested_actions=[],
			)
			issues.append(memory_leak_issue)

		if snapshot.disk_percent > 85:
			top_disk_processes = sorted(
				snapshot.disk_heavy_processes,
				key=lambda process: (process.io_read_bytes or 0) + (process.io_write_bytes or 0),
				reverse=True,
			)[:2]
			affected_disk_processes = [
				{"name": process.name, "pid": process.pid}
				for process in top_disk_processes
			]

			disk_suggested_actions: List[ActionSuggestion] = []
			if affected_disk_processes:
				safe_process = None
				for p in affected_disk_processes:
					process_name = p["name"].lower().replace(".exe", "")
					if process_name not in CRITICAL_PROCESSES:
						safe_process = p
						break

				if safe_process:
					process_name = safe_process["name"]
					process_pid = safe_process["pid"]
					disk_suggested_actions.append(
						ActionSuggestion(
							action_type=ActionType.KILL_PROCESS,
							target=process_name,
							description=f"Close {process_name} to reduce disk pressure",
							risk_level=RiskLevel.MODERATE,
							reversible=False,
							parameters={"pid": process_pid},
							estimated_impact="Immediate reduction in disk I/O contention",
						)
					)

			disk_suggested_actions.append(
				ActionSuggestion(
					action_type=ActionType.SYSTEM_TWEAK,
					target="disk_cleanup",
					description="Run disk cleanup to free up storage and reduce pressure",
					risk_level=RiskLevel.SAFE,
					reversible=True,
					parameters={},
					estimated_impact="Improves available disk space and may reduce disk pressure",
				)
			)

			if top_disk_processes:
				disk_process_details = " and ".join(
					f"{process.name} ({((process.io_read_bytes or 0) + (process.io_write_bytes or 0)):.0f} B)"
					for process in top_disk_processes
				)
				disk_cause = f"Disk usage is high with heavy I/O from {disk_process_details}"
				disk_explanation = (
					"Your system is experiencing high disk utilization, and specific processes "
					"are generating significant disk I/O."
				)
			else:
				disk_cause = "Disk usage is above 85%"
				disk_explanation = (
					"Your system is experiencing high disk usage which can degrade responsiveness."
				)

			disk_issue = Issue(
				id="HIGH_DISK_USAGE",
				category="disk",
				severity=Severity.HIGH,
				title="High Disk Usage",
				cause=disk_cause,
				explanation=disk_explanation,
				confidence=min(1.0, snapshot.disk_percent / 100),
				affected_processes=affected_disk_processes,
				suggestion="Consider closing disk-heavy processes and running disk cleanup",
				evidence={
					"disk_percent": snapshot.disk_percent,
					"top_disk_processes": [
						{
							"name": process.name,
							"pid": process.pid,
							"io_read_bytes": process.io_read_bytes or 0,
							"io_write_bytes": process.io_write_bytes or 0,
							"io_read_mb": (process.io_read_bytes or 0) / (1024.0 * 1024.0),
							"io_write_mb": (process.io_write_bytes or 0) / (1024.0 * 1024.0),
						}
						for process in top_disk_processes
					],
				},
				suggested_actions=disk_suggested_actions,
			)
			disk_issue.clamp_confidence()
			issues.append(disk_issue)

		process_count_threshold = max(250, int(len(snapshot.top_processes) * 60))
		if snapshot.process_count > process_count_threshold:
			affected_background_processes = [
				{"name": process.name, "pid": process.pid}
				for process in snapshot.top_processes[:3]
			]

			process_count_actions: List[ActionSuggestion] = []
			safe_process = None
			for process in snapshot.top_processes:
				process_name = process.name.lower().replace(".exe", "")
				if process_name not in CRITICAL_PROCESSES:
					safe_process = process
					break

			if safe_process is not None:
				process_count_actions.append(
					ActionSuggestion(
						action_type=ActionType.KILL_PROCESS,
						target=safe_process.name,
						description=f"Close {safe_process.name} to reduce background load",
						risk_level=RiskLevel.MODERATE,
						reversible=False,
						parameters={"pid": safe_process.pid},
						estimated_impact="Immediate reduction in process count pressure",
					)
				)

			process_count_actions.append(
				ActionSuggestion(
					action_type=ActionType.SYSTEM_TWEAK,
					target="disable_startup_apps",
					description="Disable unnecessary startup applications",
					risk_level=RiskLevel.SAFE,
					reversible=True,
					parameters={},
					estimated_impact="Reduces background process load over time",
				)
			)

			high_process_count_issue = Issue(
				id="HIGH_PROCESS_COUNT",
				category="system",
				severity=Severity.MEDIUM,
				title="Too Many Background Processes",
				cause="System is running a high number of background processes",
				explanation="Excessive background processes can slow down performance and increase memory/CPU usage",
				confidence=0.8,
				affected_processes=affected_background_processes,
				suggestion="Disable unnecessary startup apps and close non-essential background processes",
					evidence={
						"process_count": snapshot.process_count,
						"threshold": process_count_threshold,
					},
				suggested_actions=process_count_actions,
			)
			high_process_count_issue.clamp_confidence()
			issues.append(high_process_count_issue)

		process_frequency: dict[str, int] = {}
		for historical_snapshot in history:
			seen_in_snapshot = set()
			for process in historical_snapshot.top_processes:
				if process.name in seen_in_snapshot:
					continue
				process_frequency[process.name] = process_frequency.get(process.name, 0) + 1
				seen_in_snapshot.add(process.name)

		candidate_processes_by_pid = {
			process.pid: process
			for process in (snapshot.top_processes + snapshot.disk_heavy_processes)
		}
		startup_threshold_time = snapshot.boot_time + 15 * 60
		startup_candidates = []

		for process in candidate_processes_by_pid.values():
			normalized_name = process.name.lower().replace(".exe", "")
			if normalized_name in CRITICAL_PROCESSES:
				continue

			frequency = process_frequency.get(process.name, 0)
			started_near_boot = process.create_time <= startup_threshold_time
			if started_near_boot or frequency >= 2:
				startup_candidates.append((process, started_near_boot, frequency))

		startup_candidates.sort(key=lambda item: (item[1], item[2]), reverse=True)
		selected_startup_candidates = startup_candidates[:3]
		affected_startup_processes = [
			{"name": process.name, "pid": process.pid}
			for process, _, _ in selected_startup_candidates
		]

		if affected_startup_processes:
			startup_count = len(affected_startup_processes)
			has_near_boot_process = any(started_near_boot for _, started_near_boot, _ in selected_startup_candidates)
			has_multi_snapshot_process = any(frequency >= 2 for _, _, frequency in selected_startup_candidates)
			startup_confidence = 0.5 + (0.1 * startup_count)
			if has_near_boot_process:
				startup_confidence += 0.1
			if has_multi_snapshot_process:
				startup_confidence += 0.1
			startup_confidence = min(1.0, startup_confidence)

			startup_issue = Issue(
				id="STARTUP_LOAD",
				category="system",
				severity=Severity.MEDIUM,
				title="Startup Applications Impacting Performance",
				cause="Multiple applications are running from system startup",
				explanation="Startup applications can slow boot time and consume resources continuously",
				confidence=startup_confidence,
				affected_processes=affected_startup_processes,
				suggestion="Disable unnecessary startup applications",
				evidence={
					"startup_processes": affected_startup_processes,
					"startup_count": startup_count,
					"startup_threshold_time": startup_threshold_time,
				},
				suggested_actions=[
					ActionSuggestion(
						action_type=ActionType.SYSTEM_TWEAK,
						target="disable_startup_apps",
						description="Disable unnecessary startup applications",
						risk_level=RiskLevel.SAFE,
						reversible=True,
						parameters={},
						estimated_impact="Reduces startup and background resource load",
					)
				],
			)
			if any(issue.id in {"HIGH_MEMORY", "HIGH_CPU"} for issue in issues):
				startup_issue.severity = Severity.HIGH
			startup_issue.clamp_confidence()
			issues.append(startup_issue)

		running_services = [
			service for service in snapshot.services
			if service.get("status") == "running"
		]
		running_service_count = len(running_services)

		if running_service_count > 120:
			high_service_count_issue = Issue(
				id="HIGH_SERVICE_COUNT",
				category="system",
				severity=Severity.MEDIUM,
				title="Too Many Running Services",
				cause="System has a high number of active background services",
				explanation="Too many services can consume resources and slow down performance",
				confidence=0.75,
				affected_processes=[
					{"name": service.get("name", "unknown"), "pid": None}
					for service in running_services[:3]
				],
				suggestion="Review and optimize running services",
				evidence={"service_count": running_service_count},
				suggested_actions=[
					ActionSuggestion(
						action_type=ActionType.SYSTEM_TWEAK,
						target="disable_service",
						description="Disable unnecessary running services",
						risk_level=RiskLevel.MODERATE,
						reversible=True,
						parameters={},
						estimated_impact="Reduces service-related background resource usage",
					),
					ActionSuggestion(
						action_type=ActionType.SYSTEM_TWEAK,
						target="optimize_services",
						description="Optimize service startup and runtime behavior",
						risk_level=RiskLevel.SAFE,
						reversible=True,
						parameters={},
						estimated_impact="Improves background service efficiency",
					),
				],
			)
			high_service_count_issue.clamp_confidence()
			issues.append(high_service_count_issue)

		service_frequency: dict[str, int] = {}
		for historical_snapshot in history:
			seen_services = set()
			for service in historical_snapshot.services:
				service_name = service.get("name")
				if not service_name or service_name in seen_services:
					continue
				if service.get("status") != "running":
					continue
				service_frequency[service_name] = service_frequency.get(service_name, 0) + 1
				seen_services.add(service_name)

		heavy_service_candidates: dict[str, tuple[bool, int]] = {}
		min_frequent_presence = max(2, int(len(history) * 0.6))
		for service in running_services:
			service_name = service.get("name")
			if not service_name:
				continue

			frequency = service_frequency.get(service_name, 0)
			always_running = len(history) > 0 and frequency == len(history)
			frequently_present = frequency >= min_frequent_presence
			if not (always_running or frequently_present):
				continue

			existing = heavy_service_candidates.get(service_name)
			candidate_score = (always_running, frequency)
			if existing is None or candidate_score > existing:
				heavy_service_candidates[service_name] = candidate_score

		top_heavy_services = sorted(
			heavy_service_candidates.items(),
			key=lambda item: (item[1][0], item[1][1]),
			reverse=True,
		)[:3]

		if top_heavy_services:
			heavy_service_names = [name for name, _ in top_heavy_services]
			heavy_services_issue = Issue(
				id="HEAVY_SERVICES",
				category="system",
				severity=Severity.MEDIUM,
				title="Potentially Heavy Services Detected",
				cause="Several services appear to be continuously active across snapshots",
				explanation="Services that are always running and frequently present may contribute to persistent background load",
				confidence=min(1.0, 0.6 + (0.1 * len(heavy_service_names))),
				affected_processes=[{"name": name, "pid": None} for name in heavy_service_names],
				suggestion="Review and disable unnecessary services",
				evidence={
					"top_services": heavy_service_names,
					"service_frequency": {
						name: score[1] for name, score in top_heavy_services
					},
				},
				suggested_actions=[
					ActionSuggestion(
						action_type=ActionType.SYSTEM_TWEAK,
						target="disable_service",
						description="Disable unnecessary services after review",
						risk_level=RiskLevel.MODERATE,
						reversible=True,
						parameters={"service_name": heavy_service_names[0]},
						estimated_impact="Reduces continuous service background load",
					),
					ActionSuggestion(
						action_type=ActionType.SYSTEM_TWEAK,
						target="optimize_services",
						description="Optimize service startup behavior",
						risk_level=RiskLevel.SAFE,
						reversible=True,
						parameters={},
						estimated_impact="Improves long-term service resource usage",
					),
				],
			)
			heavy_services_issue.clamp_confidence()
			issues.append(heavy_services_issue)

		def _safe_percent(primary_attr: str, nested_attr: str) -> float:
			"""Safely fetch percent metrics from flat or nested snapshot shapes."""
			try:
				value = getattr(snapshot, primary_attr, None)
				if value is None:
					nested = getattr(snapshot, nested_attr, None)
					if nested is not None:
						value = getattr(nested, primary_attr, None)
						if value is None and isinstance(nested, dict):
							value = nested.get(primary_attr, None)
				if value is None:
					return 0.0
				return float(value)
			except (TypeError, ValueError):
				return 0.0

		cpu_percent_for_health = _safe_percent("cpu_percent", "cpu")
		memory_percent_for_health = _safe_percent("memory_percent", "memory")
		health_score = 100.0 - (cpu_percent_for_health * 0.5 + memory_percent_for_health * 0.5)
		health_score = max(0.0, min(100.0, health_score))

		snapshot_summary = {
			"cpu_percent": snapshot.cpu_percent,
			"memory_percent": snapshot.memory_percent,
			"disk_percent": snapshot.disk_percent,
			"process_count": snapshot.process_count,
		}

		changes_detected: List[dict] = []
		history = IntelligenceEngine.state_manager.get_recent()
		previous_snapshot = history[-2] if len(history) >= 2 else None
		change_time = time.time()

		if previous_snapshot is not None:
			current_process_names = _unique_process_names(
				[process.name for process in snapshot.top_processes]
			)
			previous_process_names = _unique_process_names(
				[process.name for process in previous_snapshot.top_processes]
			)

			previous_process_set = set(previous_process_names)
			current_process_set = set(current_process_names)

			for process_name in current_process_names:
				if process_name not in previous_process_set:
					changes_detected.append(
						{
							"type": "process_started",
							"name": process_name,
							"pid": next((p.pid for p in snapshot.top_processes if p.name == process_name), None),
							"time": change_time,
						}
					)

			for process_name in previous_process_names:
				if process_name not in current_process_set:
					changes_detected.append(
						{
							"type": "process_stopped",
							"name": process_name,
							"pid": None,
							"time": change_time,
						}
					)

			if history_ready:
				cpu_spike_value = snapshot.cpu_percent - avg_cpu
				if cpu_spike_value > 15:
					changes_detected.append(
						{
							"type": "cpu_spike",
							"value": cpu_spike_value,
							"likely_caused_by": affected_cpu_process_names,
							"severity": "high" if cpu_spike_value > 30 else "medium",
							"time": change_time,
						}
					)

				memory_spike_value = snapshot.memory_percent - avg_memory
				if memory_spike_value > 10:
					changes_detected.append(
						{
							"type": "memory_spike",
							"value": memory_spike_value,
							"likely_caused_by": [p["name"] for p in affected_memory_processes],
							"severity": "high" if memory_spike_value > 30 else "medium",
							"time": change_time,
						}
					)

		high_memory_issue = next((issue for issue in issues if issue.id == "HIGH_MEMORY"), None)
		if high_memory_issue and changes_detected:
			latest_process_started = next(
				(change for change in reversed(changes_detected) if change.get("type") == "process_started"),
				None,
			)
			latest_memory_spike = next(
				(change for change in reversed(changes_detected) if change.get("type") == "memory_spike"),
				None,
			)

			if top_memory_processes:
				likely_due_to = " and ".join(
					f"{process.name} ({process.memory_mb:.0f} MB)" for process in top_memory_processes
				)
			else:
				likely_due_to = "recent memory-intensive activity"

			if latest_process_started and latest_memory_spike:
				high_memory_issue.cause = (
					f"Memory usage increased after {latest_process_started['name']} started, "
					f"causing a {latest_memory_spike['value']:.1f}% spike likely due to {likely_due_to}"
				)
				high_memory_issue.explanation = (
					"Recent change analysis shows a process start followed by a memory spike "
					f"of {latest_memory_spike['value']:.1f}% above baseline."
				)
			elif latest_process_started:
				high_memory_issue.cause = (
					f"Memory usage increased after {latest_process_started['name']} started, "
					f"likely due to {likely_due_to}"
				)
			elif latest_memory_spike:
				high_memory_issue.cause = (
					f"Memory usage increased with a {latest_memory_spike['value']:.1f}% spike, "
					f"likely due to {likely_due_to}"
				)
				high_memory_issue.explanation = (
					"Recent change analysis detected a memory spike "
					f"of {latest_memory_spike['value']:.1f}% above baseline."
				)

		high_disk_issue = next((issue for issue in issues if issue.id == "HIGH_DISK_USAGE"), None)
		if high_disk_issue and changes_detected:
			latest_process_started = next(
				(change for change in reversed(changes_detected) if change.get("type") == "process_started"),
				None,
			)
			latest_disk_spike = next(
				(change for change in reversed(changes_detected) if change.get("type") == "disk_spike"),
				None,
			)

			top_disk_evidence = high_disk_issue.evidence.get("top_disk_processes", [])
			top_disk_names = [p.get("name", "unknown") for p in top_disk_evidence if isinstance(p, dict)]
			if top_disk_names:
				heavy_io_sources = " and ".join(top_disk_names[:2])
			else:
				heavy_io_sources = "recent disk-heavy processes"

			if latest_process_started:
				high_disk_issue.cause = (
					f"Disk usage increased after {latest_process_started['name']} started, "
					f"likely due to heavy disk I/O from {heavy_io_sources}"
				)
			elif latest_disk_spike:
				high_disk_issue.cause = (
					f"Disk usage increased with a {latest_disk_spike['value']:.1f}% spike, "
					f"likely due to heavy disk I/O from {heavy_io_sources}"
				)

		for issue in issues:
			if not issue.suggested_actions:
				continue

			def _action_score(action: ActionSuggestion) -> float:
				if action.action_type == ActionType.KILL_PROCESS:
					base_score = 3
				elif action.action_type == ActionType.SYSTEM_TWEAK:
					base_score = 2
				else:
					base_score = 0

				if action.risk_level == RiskLevel.SAFE:
					safety_bonus = 2
				elif action.risk_level == RiskLevel.MODERATE:
					safety_bonus = 1
				else:
					safety_bonus = 0

				return (base_score + safety_bonus) * issue.confidence

			best_suggestion = max(issue.suggested_actions, key=_action_score)

			if best_suggestion.action_type == ActionType.KILL_PROCESS:
				reason = "Highest impact action to immediately reduce resource usage"
			elif best_suggestion.action_type == ActionType.SYSTEM_TWEAK:
				reason = "Safe optimization with moderate performance improvement"
			else:
				reason = "Recommended action based on current issue confidence"

			best_action = {
				"action_type": best_suggestion.action_type.value,
				"target": best_suggestion.target,
				"parameters": best_suggestion.parameters,
				"reason": reason,
				"confidence": issue.confidence,
			}
			pid = best_suggestion.parameters.get("pid")
			if pid is not None:
				best_action["pid"] = pid
			issue.best_action = best_action

		return DiagnosticReport(
			timestamp=time.time(),
			snapshot_summary=snapshot_summary,
			issues=issues,
			system_health_score=health_score,
			changes_detected=changes_detected,
			anomalies_detected=anomalies,
		)
