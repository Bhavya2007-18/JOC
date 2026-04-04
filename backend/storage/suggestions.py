"""Storage optimization suggestion helpers."""

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
