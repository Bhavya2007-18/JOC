"""Simple duplicate finder test script.

Manual setup (PowerShell) for a quick duplicate test:
1. New-Item -ItemType Directory -Force backend/duplicate_test_data | Out-Null
2. Set-Content -Path backend/duplicate_test_data/a.txt -Value "same-content"
3. Copy-Item backend/duplicate_test_data/a.txt backend/duplicate_test_data/b.txt
4. Set-Content -Path backend/duplicate_test_data/unique.txt -Value "different-content"
5. Run this script:
    c:/Users/UMA/Documents/GitHub/JOC/.venv/Scripts/python.exe backend/test_duplicate_finder.py
"""

import os
import sys

from storage.duplicate_finder import find_duplicates
from storage.scanner import scan


DEFAULT_TEST_FOLDER = os.path.join(os.path.dirname(__file__), "duplicate_test_data")


def print_manual_setup_instructions() -> None:
    """Print short instructions for creating known duplicate files."""
    print("Manual test setup (PowerShell):")
    print("1. New-Item -ItemType Directory -Force backend\\duplicate_test_data | Out-Null")
    print('2. Set-Content -Path backend\\duplicate_test_data\\a.txt -Value "same-content"')
    print("3. Copy-Item backend\\duplicate_test_data\\a.txt backend\\duplicate_test_data\\b.txt")
    print('4. Set-Content -Path backend\\duplicate_test_data\\unique.txt -Value "different-content"')
    print(
        "5. c:/Users/UMA/Documents/GitHub/JOC/.venv/Scripts/python.exe "
        "backend/test_duplicate_finder.py"
    )


def print_duplicate_report(result: dict) -> None:
    """Print duplicate summary and each duplicate group."""
    print(f"Total duplicate size: {result['readable_size']} ({result['total_duplicate_size']} bytes)")
    print(f"Debug duplicate groups count: {len(result['duplicates'])}")

    if not result["duplicates"]:
        print("No duplicate groups found.")
        return

    print("Duplicate groups:")
    for index, group in enumerate(result["duplicates"], start=1):
        print(f"\nGroup {index}")
        print(f"Size: {group['size']} ({group['raw_size']} bytes)")
        for file_path in group["files"]:
            print(f"- {file_path}")


def run_duplicate_test(test_folder: str) -> None:
    """Scan a folder and run duplicate detection."""
    if not os.path.isdir(test_folder):
        print(f"Test folder not found: {test_folder}")
        print_manual_setup_instructions()
        return

    scan_result = scan(test_folder, max_files=5000)
    duplicate_result = find_duplicates(scan_result["files"])

    print(f"Scanned folder: {test_folder}")
    print(f"Scanned files: {scan_result['total_files']}")
    print(f"Scan time: {scan_result['scan_time']:.2f} seconds")
    print_duplicate_report(duplicate_result)


if __name__ == "__main__":
    folder_arg = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TEST_FOLDER
    run_duplicate_test(folder_arg)
