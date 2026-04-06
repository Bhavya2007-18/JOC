"""Duplicate file detection helpers."""

import hashlib

from .store_utils import bytes_to_human


def _compute_file_hash(file_path: str, chunk_size: int = 1024 * 1024) -> str:
	"""Compute file hash using chunked reads."""
	hasher = hashlib.md5()
	try:
		with open(file_path, "rb") as file_obj:
			while True:
				chunk = file_obj.read(chunk_size)
				if not chunk:
					break
				hasher.update(chunk)
	except Exception:
		return ""
	return hasher.hexdigest()


def _compute_prefix_hash(file_path: str, prefix_size: int = 4096) -> str:
	"""Compute hash for file prefix to avoid unnecessary full reads."""
	hasher = hashlib.md5()
	try:
		with open(file_path, "rb") as file_obj:
			prefix = file_obj.read(prefix_size)
	except Exception:
		return ""
	hasher.update(prefix)
	return hasher.hexdigest()


def find_duplicates(files: list) -> dict:
	"""Find duplicate files and estimate wasted space."""
	files = [file_record for file_record in files if int(file_record.get("raw_size", 0) or 0) > 0]

	size_groups = {}
	for file_record in files:
		raw_size = int(file_record.get("raw_size", 0) or 0)
		size_groups.setdefault(raw_size, []).append(file_record)

	duplicate_groups = []
	total_duplicate_size = 0

	for raw_size, same_size_files in size_groups.items():
		if len(same_size_files) < 2:
			continue

		prefix_groups = {}
		for file_record in same_size_files:
			file_path = str(file_record.get("path", ""))
			if not file_path:
				continue

			prefix_hash = _compute_prefix_hash(file_path)
			if not prefix_hash:
				continue

			prefix_groups.setdefault(prefix_hash, []).append(file_path)

		for prefix_matched_paths in prefix_groups.values():
			if len(prefix_matched_paths) < 2:
				continue

			hash_groups = {}
			for file_path in prefix_matched_paths:
				file_hash = _compute_file_hash(file_path)
				if not file_hash:
					continue

				hash_groups.setdefault(file_hash, []).append(file_path)

			for matched_paths in hash_groups.values():
				if len(matched_paths) < 2:
					continue

				duplicate_groups.append(
					{
						"size": bytes_to_human(raw_size),
						"raw_size": raw_size,
						"files": matched_paths,
					}
				)
				total_duplicate_size += (len(matched_paths) - 1) * raw_size

	duplicate_groups.sort(key=lambda group: group["raw_size"], reverse=True)

	return {
		"duplicates": duplicate_groups,
		"total_duplicate_size": total_duplicate_size,
		"readable_size": bytes_to_human(total_duplicate_size),
	}
