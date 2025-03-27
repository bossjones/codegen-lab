#!/usr/bin/env python3

"""Check cursor rule .mdc files for line count limits.

USAGE EXAMPLES:

# Check a single file
python3 check_rule_lines.py path/to/rule.mdc

# Check a directory of rules
python3 check_rule_lines.py .cursor/rules/

# Set custom line limit
python3 check_rule_lines.py .cursor/rules/ --max-lines 25

# Show details for all files
python3 check_rule_lines.py .cursor/rules/ -v
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, NamedTuple, Tuple


class LineCountLimits(NamedTuple):
    """Line count limits for cursor rule files."""

    target: int = 120  # Target line count (recommended)
    maximum: int = 250  # Maximum allowed line count


def check_rule_file(file_path: Path, limits: LineCountLimits) -> tuple[bool, bool, int]:
    """Check if a cursor rule file exceeds the target and maximum line counts.

    Args:
        file_path: Path to the .mdc file
        limits: LineCountLimits tuple with target and maximum values

    Returns:
        Tuple of (within_target: bool, within_max: bool, actual_line_count: int)

    """
    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()
            line_count = len(lines)
            return (line_count <= limits.target, line_count <= limits.maximum, line_count)
    except OSError as e:
        print(f"Error reading file {file_path}: {e}", file=sys.stderr)
        return False, False, 0


def find_mdc_files(directory: Path) -> list[Path]:
    """Find all .mdc files in the given directory and its subdirectories.

    Args:
        directory: Root directory to search in

    Returns:
        List of paths to .mdc files

    """
    mdc_files = []
    try:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".mdc"):
                    mdc_files.append(Path(root) / file)
    except OSError as e:
        print(f"Error walking directory {directory}: {e}", file=sys.stderr)
    return mdc_files


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check cursor rule .mdc files for line count limits",
        epilog="Note: The recommended target is 120 lines, with a maximum of 250 lines.",
    )
    parser.add_argument("path", type=str, help="Path to .mdc file or directory containing .mdc files")
    parser.add_argument(
        "--target-lines", type=int, default=120, help="Target number of lines (default: 120, recommended)"
    )
    parser.add_argument("--max-lines", type=int, default=250, help="Maximum allowed number of lines (default: 250)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show details for all files")
    parser.add_argument(
        "--strict", "-s", action="store_true", help="Exit with error if any files exceed the target (not just maximum)"
    )

    args = parser.parse_args()
    path = Path(args.path)
    limits = LineCountLimits(args.target_lines, args.max_lines)

    if not path.exists():
        print(f"Error: Path does not exist: {path}", file=sys.stderr)
        sys.exit(1)

    files_to_check = []
    if path.is_file():
        if not path.name.endswith(".mdc"):
            print(f"Error: File must be a .mdc file: {path}", file=sys.stderr)
            sys.exit(1)
        files_to_check = [path]
    else:
        files_to_check = find_mdc_files(path)
        if not files_to_check:
            print(f"No .mdc files found in directory: {path}", file=sys.stderr)
            sys.exit(1)

    exceeded_target = []
    exceeded_maximum = []

    for file_path in files_to_check:
        within_target, within_max, line_count = check_rule_file(file_path, limits)

        if not within_max:
            exceeded_maximum.append((file_path, line_count))
        elif not within_target:
            exceeded_target.append((file_path, line_count))
        elif args.verbose:
            print(f"✅ {file_path}: {line_count} lines")

    if exceeded_target or exceeded_maximum:
        if exceeded_maximum:
            print("\nFiles exceeding maximum line count:")
            for file_path, line_count in exceeded_maximum:
                print(f"❌ {file_path}: {line_count} lines (exceeds maximum of {limits.maximum})")

        if exceeded_target:
            print("\nFiles exceeding target line count:")
            for file_path, line_count in exceeded_target:
                print(f"⚠️  {file_path}: {line_count} lines (exceeds target of {limits.target})")

        # Exit with error if any files exceed maximum, or if strict mode and files exceed target
        if exceeded_maximum or (args.strict and exceeded_target):
            sys.exit(1)
    elif not args.verbose:
        total_files = len(files_to_check)
        print(f"✅ All {total_files} files are within limits ({limits.target} target, {limits.maximum} maximum)")


if __name__ == "__main__":
    main()
