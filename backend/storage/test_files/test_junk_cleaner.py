"""Simple test script for junk file detection."""

import os

from storage.junk_cleaner import get_junk_files
from storage.scanner import scan


def print_junk_report(title: str, junk_result: dict, top_n: int = 5) -> None:
    """Print junk size summary and top junk files."""
    print(f"\n=== {title} ===")
    print(f"Total junk size: {junk_result['readable_size']} ({junk_result['total_junk_size']} bytes)")

    top_files = junk_result["junk_files"][:top_n]
    if not top_files:
        print("No junk files found.")
        return

    print(f"Top {len(top_files)} junk files:")
    for file_record in top_files:
        print(f"- {file_record['name']} | {file_record['size']} | {file_record['path']}")


def run_real_scan_test() -> None:
    """Run junk detection on real scanned files."""
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    scan_result = scan(base_path, max_files=1000)
    junk_result = get_junk_files(scan_result["files"])

    print(f"Scanned files: {scan_result['total_files']}")
    print(f"Scan time: {scan_result['scan_time']:.2f} seconds")
    print_junk_report("Real Scan Junk Report", junk_result)


def run_fake_dataset_test() -> None:
    """Run junk detection on a small fake dataset."""
    fake_files = [
        {
            "path": "C:/demo/temp/session.tmp",
            "name": "session.tmp",
            "size": "2.00 MB",
            "raw_size": 2 * 1024 * 1024,
            "extension": ".tmp",
            "category": "other",
            "modified_time": 0.0,
        },
        {
            "path": "C:/demo/logs/app.log",
            "name": "app.log",
            "size": "500.00 KB",
            "raw_size": 500 * 1024,
            "extension": ".log",
            "category": "document",
            "modified_time": 0.0,
        },
        {
            "path": "C:/demo/docs/report.pdf",
            "name": "report.pdf",
            "size": "1.00 MB",
            "raw_size": 1 * 1024 * 1024,
            "extension": ".pdf",
            "category": "document",
            "modified_time": 0.0,
        },
        {
            "path": "C:/demo/cache/image.png",
            "name": "image.png",
            "size": "300.00 KB",
            "raw_size": 300 * 1024,
            "extension": ".png",
            "category": "image",
            "modified_time": 0.0,
        },
    ]

    junk_result = get_junk_files(fake_files)
    print_junk_report("Fake Dataset Junk Report", junk_result)


if __name__ == "__main__":
    run_real_scan_test()
    run_fake_dataset_test()
