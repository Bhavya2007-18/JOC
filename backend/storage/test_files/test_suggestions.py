"""Simple test script for storage suggestions engine."""

import os

from storage.junk_cleaner import get_junk_files
from storage.scanner import scan
from storage.suggestions import generate_suggestions


def print_suggestions_report(title: str, suggestions: dict) -> None:
    """Print suggestion summary and actions."""
    print(f"\n=== {title} ===")
    print(f"Total recoverable space: {suggestions['total_recoverable_space']}")
    print(f"Debug raw_total: {suggestions['raw_total']} bytes")

    print("Suggested actions:")
    for action in suggestions["actions"]:
        print(f"- {action['type']}: {action['description']} ({action['recoverable_space']})")


def run_real_data_test() -> None:
    """Run full flow with real scanned files."""
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    scan_result = scan(base_path, max_files=1000)
    junk_data = get_junk_files(scan_result["files"])
    suggestions = generate_suggestions(scan_result["files"], junk_data)

    print(f"Scanned files: {scan_result['total_files']}")
    print(f"Scan time: {scan_result['scan_time']:.2f} seconds")
    print(f"Debug junk raw size: {junk_data['total_junk_size']} bytes")
    print_suggestions_report("Real Data Suggestions", suggestions)


def run_fake_data_test() -> None:
    """Run calculation checks with fake data."""
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
            "path": "C:/demo/video/movie.mkv",
            "name": "movie.mkv",
            "size": "5.00 GB",
            "raw_size": 5 * 1024 * 1024 * 1024,
            "extension": ".mkv",
            "category": "video",
            "modified_time": 0.0,
        },
        {
            "path": "C:/demo/docs/report.pdf",
            "name": "report.pdf",
            "size": "100.00 MB",
            "raw_size": 100 * 1024 * 1024,
            "extension": ".pdf",
            "category": "document",
            "modified_time": 0.0,
        },
    ]

    junk_data = get_junk_files(fake_files)
    suggestions = generate_suggestions(fake_files, junk_data)

    print(f"\nDebug fake junk raw size: {junk_data['total_junk_size']} bytes")
    print_suggestions_report("Fake Data Suggestions", suggestions)


if __name__ == "__main__":
    run_real_data_test()
    run_fake_data_test()
