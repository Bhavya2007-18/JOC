from __future__ import annotations

import time
from typing import List

from .models import DiagnosticReport, Issue, SystemSnapshot


class IntelligenceEngine:
	def analyze(self, snapshot: SystemSnapshot) -> DiagnosticReport:
		issues: List[Issue] = []

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

		if snapshot.cpu_percent > 80:
			top_cpu_processes = sorted(
				snapshot.top_processes,
				key=lambda process: process.cpu_percent,
				reverse=True,
			)[:2]
			affected_cpu_processes = _unique_process_names(
				[process.name for process in top_cpu_processes]
			)
			cpu_suggestion = _build_suggestion(
				affected_cpu_processes,
				"Close heavy applications or background processes",
			)
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
				evidence={"cpu_percent": snapshot.cpu_percent},
			)
			cpu_issue.clamp_confidence()
			issues.append(cpu_issue)

		if snapshot.memory_percent > 80:
			top_memory_processes = sorted(
				snapshot.top_processes,
				key=lambda process: process.memory_mb,
				reverse=True,
			)[:2]
			affected_memory_processes = _unique_process_names(
				[process.name for process in top_memory_processes]
			)
			memory_suggestion = _build_suggestion(
				affected_memory_processes,
				"Close memory-intensive applications or restart unused services",
			)
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
				evidence={"memory_percent": snapshot.memory_percent},
			)
			memory_issue.clamp_confidence()
			issues.append(memory_issue)

		health_score = max(0.0, min(100.0, 100.0 - (20.0 * len(issues))))

		snapshot_summary = {
			"cpu_percent": snapshot.cpu_percent,
			"memory_percent": snapshot.memory_percent,
			"process_count": snapshot.process_count,
		}

		return DiagnosticReport(
			timestamp=time.time(),
			snapshot_summary=snapshot_summary,
			issues=issues,
			system_health_score=health_score,
			changes_detected=[],
			anomalies_detected=[],
		)
