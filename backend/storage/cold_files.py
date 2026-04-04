"""Cold file detection helpers."""

import time

from .store_utils import bytes_to_human


def find_cold_files(files: list, days: int = 60) -> dict:
	"""Return files that have not been modified for the given number of days."""
	current_time = time.time()
	allowed_thresholds = {30, 60, 90}
	threshold_days = int(days)
	if threshold_days not in allowed_thresholds:
		threshold_days = 60
	threshold_seconds = threshold_days * 86400

	cold_files = []
	total_cold_size = 0

	for file_record in files:
		modified_time = float(file_record.get("modified_time", 0.0) or 0.0)
		if current_time - modified_time <= threshold_seconds:
			continue

		cold_files.append(file_record)
		total_cold_size += int(file_record.get("raw_size", 0) or 0)

	cold_files.sort(key=lambda file_record: int(file_record.get("raw_size", 0) or 0), reverse=True)

	return {
		"cold_files": cold_files,
		"total_cold_size": total_cold_size,
		"readable_size": bytes_to_human(total_cold_size),
		"threshold_days": threshold_days,
	}
