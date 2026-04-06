"""Cleanup helpers for removing files from analysis outputs."""

import os


EMPTY_CLEANUP_RESULT = {
    "deleted": [],
    "failed": [],
    "total_deleted": 0,
    "total_failed": 0,
}


def extract_cleanup_paths(cleanup_type: str, junk: dict, duplicates: dict, cold: dict) -> list[str]:
    """Extract deletable file paths from existing analysis outputs."""
    paths = []

    if cleanup_type == "junk":
        for file_record in junk.get("junk_files", []):
            file_path = str(file_record.get("path", ""))
            if file_path:
                paths.append(file_path)

    elif cleanup_type == "cold":
        for file_record in cold.get("cold_files", []):
            file_path = str(file_record.get("path", ""))
            if file_path:
                paths.append(file_path)

    elif cleanup_type == "duplicates":
        for group in duplicates.get("duplicates", []):
            group_files = [str(path) for path in group.get("files", []) if str(path)]
            if len(group_files) <= 1:
                continue
            # Keep one file per duplicate group and delete the rest.
            paths.extend(group_files[1:])

    deduped_paths = []
    seen = set()
    for file_path in paths:
        if file_path in seen:
            continue
        seen.add(file_path)
        deduped_paths.append(file_path)

    return deduped_paths


def delete_paths(file_paths: list[str]) -> dict:
    """Delete provided file paths safely without recursive behavior."""
    deleted = []
    failed = []

    for file_path in file_paths:
        if not os.path.isfile(file_path):
            failed.append(file_path)
            continue

        try:
            os.remove(file_path)
            deleted.append(file_path)
        except Exception:
            failed.append(file_path)

    return {
        "deleted": deleted,
        "failed": failed,
        "total_deleted": len(deleted),
        "total_failed": len(failed),
    }
