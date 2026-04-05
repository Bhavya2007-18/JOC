"""Storage optimization suggestion helpers."""

from .cold_files import find_cold_files
from .duplicate_finder import find_duplicates
from .junk_cleaner import get_junk_files
from .store_utils import bytes_to_human


def get_system_health(junk_size: int, duplicate_size: int, cold_size: int) -> dict:
	"""Calculate health score and status from storage inefficiencies."""
	score = 100
	one_gb = 1024 * 1024 * 1024
	two_gb = 2 * one_gb

	if junk_size > one_gb:
		score -= 10
	if duplicate_size > one_gb:
		score -= 15
	if cold_size > two_gb:
		score -= 10

	score = max(0, min(score, 100))

	if score >= 80:
		status = "Healthy"
	elif score >= 50:
		status = "Needs Optimization"
	else:
		status = "Critical"

	return {"system_health": score, "status": status}


def generate_full_suggestions(
	files: list,
	junk: dict = None,
	duplicates: dict = None,
	cold: dict = None,
	cold_days: int = 60,
) -> dict:
	"""Combine junk, duplicate, and cold-file insights into one output."""
	threshold_days = int(cold_days)
	if junk is None:
		junk = get_junk_files(files)
	if duplicates is None:
		duplicates = find_duplicates(files)
	if cold is None:
		cold = find_cold_files(files, days=threshold_days)

	junk_size = int(junk.get("total_junk_size", 0) or 0)
	duplicate_size = int(duplicates.get("total_duplicate_size", 0) or 0)
	cold_size = int(cold.get("total_cold_size", 0) or 0)

	raw_total = junk_size + duplicate_size + cold_size
	total_recoverable_space = bytes_to_human(raw_total)
	mb_500 = 500 * 1024 * 1024
	gb_2 = 2 * 1024 * 1024 * 1024

	if raw_total < mb_500:
		priority = "low"
		recommendation = "Cleanup is optional right now; focus on junk files first."
	elif raw_total <= gb_2:
		priority = "medium"
		recommendation = "Run a cleanup pass for junk and duplicate files soon."
	else:
		priority = "high"
		recommendation = "Start cleanup now and prioritize duplicate and cold files."

	actions = []

	if junk_size > 0:
		actions.append(
			{
				"type": "junk",
				"title": "Clear junk files",
				"description": "Remove temporary and cache files",
				"recoverable_space": bytes_to_human(junk_size),
			}
		)

	if duplicate_size > 0:
		actions.append(
			{
				"type": "duplicates",
				"title": "Remove duplicate files",
				"description": "Delete redundant copies of the same files",
				"recoverable_space": bytes_to_human(duplicate_size),
			}
		)

	if cold_size > 0:
		actions.append(
			{
				"type": "cold_files",
				"title": "Clean unused files",
				"description": "Remove files not used in a long time",
				"recoverable_space": bytes_to_human(cold_size),
			}
		)

	issue_sizes = {
		"junk": junk_size,
		"duplicates": duplicate_size,
		"cold_files": cold_size,
	}
	top_issue_type = max(issue_sizes, key=issue_sizes.get)

	if issue_sizes[top_issue_type] <= 0:
		top_issue = "No major storage issue detected"
	elif top_issue_type == "junk":
		top_issue = "Junk files are taking the most space"
	elif top_issue_type == "duplicates":
		top_issue = "Duplicate files are taking the most space"
	else:
		top_issue = "Unused files are occupying most storage"

	health_data = get_system_health(junk_size, duplicate_size, cold_size)

	return {
		"insight": f"You can free up {total_recoverable_space} of storage space",
		"top_issue": top_issue,
		"priority": priority,
		"recommendation": recommendation,
		"system_health": health_data["system_health"],
		"status": health_data["status"],
		"threshold_days": threshold_days,
		"total_recoverable_space": total_recoverable_space,
		"raw_total": raw_total,
		"actions": actions,
	}
