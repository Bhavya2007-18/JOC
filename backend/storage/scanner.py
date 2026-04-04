"""Filesystem scanner for storage intelligence phase 1."""

import os
import time

from .store_utils import bytes_to_human, get_file_category, is_safe_path


def _on_walk_error(error: OSError) -> None:
	"""Ignore walk errors like permission denied and keep scanning."""
	_ = error


def scan(path: str, max_files: int = 5000) -> dict:
	"""Scan a directory and return metadata for discovered files."""
	start_time = time.time()
	files = []

	if max_files <= 0 or not is_safe_path(path):
		return {"files": files, "total_files": 0, "scan_time": time.time() - start_time}

	for root, dirs, filenames in os.walk(path, onerror=_on_walk_error):
		if not is_safe_path(root):
			dirs[:] = []
			continue

		dirs[:] = [directory for directory in dirs if is_safe_path(os.path.join(root, directory))]

		for filename in filenames:
			if len(files) >= max_files:
				files.sort(key=lambda file_record: file_record["raw_size"], reverse=True)
				scan_time = time.time() - start_time
				return {"files": files, "total_files": len(files), "scan_time": scan_time}

			full_path = os.path.join(root, filename)
			if not is_safe_path(full_path):
				continue

			try:
				stat_result = os.stat(full_path)
			except (PermissionError, FileNotFoundError, OSError):
				continue

			extension = os.path.splitext(filename)[1].lower()
			record = {
				"path": full_path,
				"name": filename,
				"size": bytes_to_human(int(stat_result.st_size)),
				"raw_size": int(stat_result.st_size),
				"extension": extension,
				"category": get_file_category(extension),
				"modified_time": float(stat_result.st_mtime),
			}
			files.append(record)

	files.sort(key=lambda file_record: file_record["raw_size"], reverse=True)
	scan_time = time.time() - start_time
	return {"files": files, "total_files": len(files), "scan_time": scan_time}
