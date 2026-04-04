"""Storage optimization suggestion helpers."""

from .cold_files import find_cold_files
from .duplicate_finder import find_duplicates
from .junk_cleaner import get_junk_files
from .store_utils import bytes_to_human


def generate_suggestions(files: list, junk_data: dict) -> dict:
	"""Generate simple, actionable storage suggestions."""
	junk_raw = int(junk_data.get("total_junk_size", 0) or 0)

	sorted_files = sorted(
		files,
		key=lambda file_record: int(file_record.get("raw_size", 0) or 0),
		reverse=True,
	)

	top_10_largest = sorted_files[:10]
	large_files_raw = sum(int(file_record.get("raw_size", 0) or 0) for file_record in top_10_largest)

	raw_total = junk_raw + large_files_raw

	actions = [
		{
			"type": "junk_cleanup",
			"description": "Clear junk files",
			"recoverable_space": bytes_to_human(junk_raw),
		},
		{
			"type": "large_files",
			"description": "Review large files",
			"recoverable_space": bytes_to_human(large_files_raw),
		},
	]

	return {
		"total_recoverable_space": bytes_to_human(raw_total),
		"raw_total": raw_total,
		"actions": actions,
		"top_large_files": top_10_largest[:3],
	}


def generate_full_suggestions(files: list) -> dict:
	"""Combine junk, duplicate, and cold-file insights into one output."""
	junk = get_junk_files(files)
	duplicates = find_duplicates(files)
	cold = find_cold_files(files, days=60)

	junk_size = int(junk.get("total_junk_size", 0) or 0)
	duplicate_size = int(duplicates.get("total_duplicate_size", 0) or 0)
	cold_size = int(cold.get("total_cold_size", 0) or 0)

	raw_total = junk_size + duplicate_size + cold_size
	actions = []

	if junk_size > 0:
		actions.append(
			{
				"type": "junk",
				"description": "Clear junk files",
				"recoverable_space": bytes_to_human(junk_size),
			}
		)

	if duplicate_size > 0:
		actions.append(
			{
				"type": "duplicates",
				"description": "Remove duplicate files",
				"recoverable_space": bytes_to_human(duplicate_size),
			}
		)

	if cold_size > 0:
		actions.append(
			{
				"type": "cold_files",
				"description": "Clean unused files",
				"recoverable_space": bytes_to_human(cold_size),
			}
		)

	return {
		"total_recoverable_space": bytes_to_human(raw_total),
		"raw_total": raw_total,
		"actions": actions,
	}
