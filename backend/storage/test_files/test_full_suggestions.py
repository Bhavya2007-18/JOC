"""Simple test script for full storage suggestions engine."""

import os
import shutil
import time

from storage.store_utils import bytes_to_human
from storage.suggestions import generate_full_suggestions


def _write_file(path: str, data: bytes) -> None:
    """Write binary data to a file path."""
    with open(path, "wb") as file_obj:
        file_obj.write(data)


def _build_record(path: str, modified_time: float) -> dict:
    """Build a file record in scanner-compatible format."""
    raw_size = os.path.getsize(path)
    extension = os.path.splitext(path)[1].lower()

    return {
        "path": path,
        "name": os.path.basename(path),
        "size": bytes_to_human(raw_size),
        "raw_size": raw_size,
        "extension": extension,
        "category": "other",
        "modified_time": modified_time,
    }


def run_full_suggestions_test() -> None:
    """Create fake data and validate full suggestions output."""
    now = time.time()
    test_dir = os.path.join(os.path.dirname(__file__), "full_suggestions_test_data")
    if os.path.isdir(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir, exist_ok=True)

    try:
        junk_path = os.path.join(test_dir, "junk.tmp")
        dup1_path = os.path.join(test_dir, "dup1.bin")
        dup2_path = os.path.join(test_dir, "dup2.bin")
        cold_path = os.path.join(test_dir, "cold.txt")

        _write_file(junk_path, b"J" * 150)
        _write_file(dup1_path, b"D" * 300)
        _write_file(dup2_path, b"D" * 300)
        _write_file(cold_path, b"C" * 500)

        files = [
            _build_record(junk_path, now - (10 * 86400)),
            _build_record(dup1_path, now - (10 * 86400)),
            _build_record(dup2_path, now - (10 * 86400)),
            _build_record(cold_path, now - (100 * 86400)),
        ]

        result = generate_full_suggestions(files)

        expected_junk = 150
        expected_duplicates = 300
        expected_cold = 500
        expected_total = expected_junk + expected_duplicates + expected_cold

        action_by_type = {action["type"]: action for action in result["actions"]}

        print("=== Full Suggestions Test ===")
        print(f"Total recoverable space: {result['total_recoverable_space']}")
        print(f"Raw total: {result['raw_total']} bytes")
        print("Actions:")
        for action in result["actions"]:
            print(f"- {action['type']}: {action['description']} ({action['recoverable_space']})")

        print("\n=== Debug Validation ===")
        print(f"Junk detected: {'junk' in action_by_type}")
        print(f"Duplicates detected: {'duplicates' in action_by_type}")
        print(f"Cold files detected: {'cold_files' in action_by_type}")
        print(f"Expected junk raw: {expected_junk}")
        print(f"Expected duplicates raw: {expected_duplicates}")
        print(f"Expected cold raw: {expected_cold}")
        print(f"Expected total raw: {expected_total}")
        print(f"Total correct: {result['raw_total'] == expected_total}")
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


if __name__ == "__main__":
    run_full_suggestions_test()
