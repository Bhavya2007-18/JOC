"""Junk file detection helpers."""

import os

from .store_utils import bytes_to_human


JUNK_EXTENSIONS = {".tmp", ".log", ".cache", ".bak"}
JUNK_FOLDERS = ["/temp/", "/cache/", "/logs/"]


def get_junk_files(files: list) -> dict:
	"""Return junk files and total reclaimable size."""
	junk_files = []
	total_junk_size = 0

	for file_record in files:
		extension = str(file_record.get("extension", "")).lower()
		file_path_lower = str(file_record.get("path_lower", str(file_record.get("path", "")).lower()))
		normalized_path = "/" + os.path.normpath(file_path_lower).replace("\\", "/").strip("/") + "/"

		is_junk_by_extension = extension in JUNK_EXTENSIONS
		is_junk_by_path = any(folder in normalized_path for folder in JUNK_FOLDERS)

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
