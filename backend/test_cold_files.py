"""Simple test script for cold file detection using fake data."""

import time

from storage.cold_files import find_cold_files


def run_fake_cold_file_test() -> None:
    """Validate that only old files are detected and size math is correct."""
    now = time.time()

    fake_files = [
        {
            "path": "C:/demo/archive/old_report.pdf",
            "name": "old_report.pdf",
            "size": "10.00 MB",
            "raw_size": 10 * 1024 * 1024,
            "extension": ".pdf",
            "category": "document",
            "modified_time": now - (100 * 86400),
        },
        {
            "path": "C:/demo/work/new_notes.txt",
            "name": "new_notes.txt",
            "size": "2.00 MB",
            "raw_size": 2 * 1024 * 1024,
            "extension": ".txt",
            "category": "document",
            "modified_time": now - (10 * 86400),
        },
    ]

    result = find_cold_files(fake_files, days=60)

    expected_total = 10 * 1024 * 1024
    detected_names = [file_record["name"] for file_record in result["cold_files"]]

    print("=== Cold File Test ===")
    print(f"Threshold days: {result['threshold_days']}")
    print(f"Total cold size: {result['readable_size']} ({result['total_cold_size']} bytes)")
    print(f"Detected files: {', '.join(detected_names) if detected_names else 'None'}")

    print("\n=== Debug Checks ===")
    print(f"Only old file detected: {detected_names == ['old_report.pdf']}")
    print(f"Size calculation correct: {result['total_cold_size'] == expected_total}")


if __name__ == "__main__":
    run_fake_cold_file_test()
