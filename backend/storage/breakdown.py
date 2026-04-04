"""Category-level storage breakdown helpers."""

from .store_utils import bytes_to_human


def get_category_breakdown(files: list) -> dict:
	"""Group files by category and return sorted size totals."""
	category_totals = {}

	for file_record in files:
		category = file_record.get("category", "other")
		raw_size = int(file_record.get("raw_size", 0) or 0)
		category_totals[category] = category_totals.get(category, 0) + raw_size

	sorted_categories = sorted(
		category_totals.items(),
		key=lambda item: item[1],
		reverse=True,
	)

	breakdown = {}
	for category, total_raw_size in sorted_categories:
		breakdown[category] = {
			"size": bytes_to_human(total_raw_size),
			"raw_size": total_raw_size,
		}

	return breakdown
