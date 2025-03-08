#!/usr/bin/env python3
"""
Script to audit cursor rule files in hack/drafts/cursor_rules directory for proper YAML frontmatter headers.

This script checks for:
1. Presence of YAML frontmatter (enclosed by ---)
2. Required fields: description and globs
"""

import os
import re
from typing import Dict, List, Optional, Tuple


def check_yaml_header(file_path: str) -> tuple[bool, list[str]]:
    """
    Check if a file has the correct YAML frontmatter header.

    Args:
        file_path: Path to the file to check

    Returns:
        Tuple containing:
        - Boolean indicating if the header is valid
        - List of issues found (empty if valid)
    """
    issues = []

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Check if the file starts with ---
        if not content.strip().startswith("---"):
            issues.append("Missing opening YAML delimiter '---'")
            return False, issues

        # Extract the YAML frontmatter
        match = re.match(r"---\s*(.*?)\s*---", content, re.DOTALL)
        if not match:
            issues.append("Missing closing YAML delimiter '---'")
            return False, issues

        yaml_content = match.group(1)

        # Check for required fields
        if "description:" not in yaml_content:
            issues.append("Missing 'description' field")

        if "globs:" not in yaml_content:
            issues.append("Missing 'globs' field")

        return len(issues) == 0, issues

    except Exception as e:
        issues.append(f"Error reading file: {str(e)}")
        return False, issues


def audit_cursor_rules(directory: str) -> dict[str, list[str]]:
    """
    Audit cursor rule files in the specified directory.

    Args:
        directory: Directory containing cursor rule files

    Returns:
        Dictionary mapping file paths to lists of issues
    """
    results = {}

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".mdc.md"):
                file_path = os.path.join(root, file)
                is_valid, issues = check_yaml_header(file_path)

                if not is_valid:
                    results[file_path] = issues

    return results


def main() -> None:
    """Main function to audit cursor rule headers."""
    directory = "hack/drafts/cursor_rules"

    print(f"Auditing cursor rule headers in {directory}...")
    results = audit_cursor_rules(directory)

    if not results:
        print("✅ All cursor rule files have valid headers!")
    else:
        print(f"❌ Found issues in {len(results)} files:")
        for file_path, issues in results.items():
            relative_path = os.path.relpath(file_path)
            print(f"\n{relative_path}:")
            for issue in issues:
                print(f"  - {issue}")

        print("\nSummary of required header format:")
        print("---")
        print("description: Description of the cursor rule")
        print("globs: *")
        print("---")


if __name__ == "__main__":
    main()
