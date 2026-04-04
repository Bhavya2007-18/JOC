from __future__ import annotations

import time
from typing import List

from .models import (
	ActionSuggestion,
	ActionType,
	DiagnosticReport,
	Issue,
	RiskLevel,
	SystemSnapshot,
)


class IntelligenceEngine:
	_previous_snapshot = None
	_snapshot_history: List[SystemSnapshot] = []

	def analyze(self, snapshot: SystemSnapshot) -> DiagnosticReport:
		issues: List[Issue] = []

		IntelligenceEngine._snapshot_history.append(snapshot)
		if len(IntelligenceEngine._snapshot_history) > 5:
			IntelligenceEngine._snapshot_history = IntelligenceEngine._snapshot_history[-5:]

		avg_cpu = sum(item.cpu_percent for item in IntelligenceEngine._snapshot_history) / len(
			IntelligenceEngine._snapshot_history
		)
		avg_memory = sum(item.memory_percent for item in IntelligenceEngine._snapshot_history) / len(
			IntelligenceEngine._snapshot_history
		)
		history_ready = len(IntelligenceEngine._snapshot_history) >= 3

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

		def _build_suggestion(affected_processes: List[str], generic_suggestion: str) -> str:
			if affected_processes:
				return f"Consider closing {_join_with_or(affected_processes)}"
			return generic_suggestion

		top_cpu_processes = sorted(
			snapshot.top_processes,
			key=lambda process: process.cpu_percent,
			reverse=True,
		)[:2]
		affected_cpu_processes = _unique_process_names(
			[process.name for process in top_cpu_processes]
		)

		top_memory_processes = sorted(
			snapshot.top_processes,
			key=lambda process: process.memory_mb,
			reverse=True,
		)[:2]
		affected_memory_processes = _unique_process_names(
			[process.name for process in top_memory_processes]
		)

		if snapshot.cpu_percent > 80:
			cpu_suggestion = _build_suggestion(
				affected_cpu_processes,
				"Close heavy applications or background processes",
			)
			cpu_evidence = {"cpu_percent": snapshot.cpu_percent}
			if affected_cpu_processes:
				cpu_evidence["fix_action"] = {
					"action": "kill_process",
					"target": affected_cpu_processes[0],
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
				severity="warning",
				title="High CPU Usage",
				cause=cpu_cause,
				explanation=cpu_explanation,
				confidence=min(1.0, snapshot.cpu_percent / 100),
				affected_processes=affected_cpu_processes,
				suggestion=cpu_suggestion,
				evidence=cpu_evidence,
			)
			cpu_issue.clamp_confidence()
			issues.append(cpu_issue)

		if snapshot.memory_percent > 80:
			memory_suggestion = _build_suggestion(
				affected_memory_processes,
				"Close memory-intensive applications or restart unused services",
			)
			memory_evidence = {"memory_percent": snapshot.memory_percent}
			if affected_memory_processes:
				memory_evidence["fix_action"] = {
					"action": "kill_process",
					"target": affected_memory_processes[0],
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
				severity="warning",
				title="High Memory Usage",
				cause=memory_cause,
				explanation=memory_explanation,
				confidence=min(1.0, snapshot.memory_percent / 100),
				affected_processes=affected_memory_processes,
				suggestion=memory_suggestion,
				evidence=memory_evidence,
			)
			memory_issue.clamp_confidence()
			issues.append(memory_issue)

		health_score = max(0.0, min(100.0, 100.0 - (20.0 * len(issues))))

		snapshot_summary = {
			"cpu_percent": snapshot.cpu_percent,
			"memory_percent": snapshot.memory_percent,
			"process_count": snapshot.process_count,
		}

		changes_detected: List[dict] = []
		previous_snapshot = IntelligenceEngine._previous_snapshot
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
						{"type": "process_started", "name": process_name, "time": change_time}
					)

			for process_name in previous_process_names:
				if process_name not in current_process_set:
					changes_detected.append(
						{"type": "process_stopped", "name": process_name, "time": change_time}
					)

			if history_ready:
				cpu_spike_value = snapshot.cpu_percent - avg_cpu
				if cpu_spike_value > 15:
					changes_detected.append(
						{
							"type": "cpu_spike",
							"value": cpu_spike_value,
							"likely_caused_by": affected_cpu_processes,
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
							"likely_caused_by": affected_memory_processes,
							"severity": "high" if memory_spike_value > 30 else "medium",
							"time": change_time,
						}
					)

		IntelligenceEngine._previous_snapshot = snapshot

		return DiagnosticReport(
			timestamp=time.time(),
			snapshot_summary=snapshot_summary,
			issues=issues,
			system_health_score=health_score,
			changes_detected=changes_detected,
			anomalies_detected=[],
		)
