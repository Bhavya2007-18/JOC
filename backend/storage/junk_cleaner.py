"""Junk file detection helpers."""

from .store_utils import bytes_to_human


def get_junk_files(files: list) -> dict:
	"""Return junk files and total reclaimable size."""
	junk_extensions = {".tmp", ".log", ".cache"}
	path_keywords = ("temp", "cache")

	junk_files = []
	total_junk_size = 0

	for file_record in files:
		extension = str(file_record.get("extension", "")).lower()
		file_path = str(file_record.get("path", "")).lower()

		is_junk_by_extension = extension in junk_extensions
		is_junk_by_path = any(keyword in file_path for keyword in path_keywords)

		if not (is_junk_by_extension or is_junk_by_path):
			continue

		junk_files.append(file_record)
		total_junk_size += int(file_record.get("raw_size", 0) or 0)

	junk_files.sort(key=lambda file_record: int(file_record.get("raw_size", 0) or 0), reverse=True)

	return {
		"junk_files": junk_files,
		"total_junk_size": total_junk_size,
		"readable_size": bytes_to_human(total_junk_size),
	}
