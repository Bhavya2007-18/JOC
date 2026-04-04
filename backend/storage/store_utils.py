"""Utility helpers for storage scanning."""

import os


def bytes_to_human(size: int) -> str:
	"""Convert bytes to a readable KB/MB/GB string."""
	if size < 0:
		size = 0

	units = ["B", "KB", "MB", "GB", "TB"]
	value = float(size)
	unit_index = 0

	while value >= 1024 and unit_index < len(units) - 1:
		value /= 1024
		unit_index += 1

	if unit_index == 0:
		return f"{int(value)} {units[unit_index]}"
	return f"{value:.2f} {units[unit_index]}"


def get_file_category(extension: str) -> str:
	"""Map a file extension to a high-level category."""
	ext = extension.lower().strip()
	if ext.startswith("."):
		ext = ext[1:]

	video = {"mp4", "mkv", "avi", "mov", "wmv", "flv", "webm", "m4v"}
	image = {"jpg", "jpeg", "png", "gif", "bmp", "webp", "svg", "tiff"}
	document = {"pdf", "doc", "docx", "txt", "ppt", "pptx", "xls", "xlsx", "csv", "md"}
	audio = {"mp3", "wav", "aac", "flac", "ogg", "m4a", "wma"}
	archive = {"zip", "rar", "7z", "tar", "gz", "bz2", "xz"}

	if ext in video:
		return "video"
	if ext in image:
		return "image"
	if ext in document:
		return "document"
	if ext in audio:
		return "audio"
	if ext in archive:
		return "archive"
	return "other"


def is_safe_path(path: str) -> bool:
	"""Block scanning of protected Windows system folders."""
	protected_paths = [
		r"C:\Windows",
		r"C:\Program Files",
		r"C:\Program Files (x86)",
	]

	try:
		candidate = os.path.normcase(os.path.abspath(path))
	except (OSError, ValueError):
		return False

	for protected in protected_paths:
		normalized_protected = os.path.normcase(os.path.abspath(protected))
		if candidate == normalized_protected or candidate.startswith(normalized_protected + os.sep):
			return False

	return True
