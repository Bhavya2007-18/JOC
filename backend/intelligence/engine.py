from __future__ import annotations

import time
from typing import List
from intelligence.state_manager import StateManager
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

		IntelligenceEngine.state_manager.add_snapshot(snapshot)
		history = IntelligenceEngine.state_manager.get_recent()

		avg_cpu = sum(item.cpu_percent for item in history) / len(history)
		avg_memory = sum(item.memory_percent for item in history) / len(history)
		
		cpu_values = [item.cpu_percent for item in history]
		memory_values = [item.memory_percent for item in history]

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
			cpu_suggested_actions: List[ActionSuggestion] = []
			if affected_cpu_processes:
				cpu_suggested_actions.append(
					ActionSuggestion(
						action_type=ActionType.KILL_PROCESS,
						target=affected_cpu_processes[0],
						description=f"Close {affected_cpu_processes[0]} to reduce CPU usage",
						risk_level=RiskLevel.MODERATE,
						reversible=False,
						parameters={},
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
				memory_suggested_actions.append(
					ActionSuggestion(
						action_type=ActionType.KILL_PROCESS,
						target=affected_memory_processes[0],
						description=f"Close {affected_memory_processes[0]} to free memory",
						risk_level=RiskLevel.MODERATE,
						reversible=False,
						parameters={},
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

		health_score = max(0.0, min(100.0, 100.0 - (20.0 * len(issues))))

		snapshot_summary = {
			"cpu_percent": snapshot.cpu_percent,
			"memory_percent": snapshot.memory_percent,
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

		return DiagnosticReport(
			timestamp=time.time(),
			snapshot_summary=snapshot_summary,
			issues=issues,
			system_health_score=health_score,
			changes_detected=changes_detected,
			anomalies_detected=[],
		)
