#!/usr/bin/env python3
"""Script to validate frontmatter in cursor rule files."""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml


def validate_frontmatter(content: str) -> tuple[bool, list[str]]:
    """Validate frontmatter content against rules.

    Args:
        content: The full content of the MDC file

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Check if content starts with frontmatter delimiters
    if not content.startswith('---\n'):
        errors.append("Missing opening frontmatter delimiter '---'")
        return False, errors

    # Find the closing delimiter
    try:
        fm_end = content.index('\n---\n', 4)
    except ValueError:
        errors.append("Missing closing frontmatter delimiter '---'")
        return False, errors

    # Extract and parse frontmatter
    fm_content = content[4:fm_end]
    try:
        fm_data = yaml.safe_load(fm_content)
    except yaml.YAMLError as e:
        errors.append(f"Invalid YAML format: {e!s}")
        return False, errors

    if not isinstance(fm_data, dict):
        errors.append("Frontmatter must be a YAML dictionary")
        return False, errors

    # Check required fields
    required_fields = ['description', 'globs', 'alwaysApply']
    for field in required_fields:
        if field not in fm_data:
            errors.append(f"Missing required field: {field}")
        elif fm_data[field] is None or fm_data[field] == '':
            errors.append(f"Empty value for required field: {field}")

    # Validate description
    if 'description' in fm_data:
        if not isinstance(fm_data['description'], str):
            errors.append("Description must be a string")
        elif '\n' in fm_data['description']:
            errors.append("Description must be a single line")

    # Validate globs
    if 'globs' in fm_data:
        globs = fm_data['globs']
        if isinstance(globs, str):
            # Check for invalid glob formats
            if '"' in globs or "'" in globs:
                errors.append("Glob patterns should not be quoted")
            if '[' in globs or ']' in globs:
                errors.append("Glob patterns should not use array notation")
            if '{' in globs or '}' in globs:
                errors.append("Glob patterns should not use curly brace notation")
            # Check comma formatting
            if ',' in globs and not re.search(r', \w', globs):
                errors.append("Multiple globs should be separated by ', '")
        else:
            errors.append("Globs must be a string (comma-separated for multiple patterns)")

    # Validate alwaysApply
    if 'alwaysApply' in fm_data:
        if not isinstance(fm_data['alwaysApply'], bool):
            errors.append("alwaysApply must be a boolean (true/false)")

    return len(errors) == 0, errors

def validate_file(file_path: Path) -> tuple[bool, list[str]]:
    """Validate a single MDC file.

    Args:
        file_path: Path to the MDC file

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    try:
        content = file_path.read_text()
        return validate_frontmatter(content)
    except Exception as e:
        return False, [f"Error reading file: {e!s}"]

def main():
    """Validate all MDC files in the .cursor/rules directory."""
    rules_dir = Path('.cursor/rules')
    if not rules_dir.exists():
        print("Error: .cursor/rules directory not found")
        sys.exit(1)

    files = list(rules_dir.glob('*.mdc')) + list(rules_dir.glob('*.mdc.md'))
    if not files:
        print("No MDC files found in .cursor/rules")
        sys.exit(0)

    exit_code = 0
    for file_path in files:
        print(f"\nValidating {file_path}...")
        is_valid, errors = validate_file(file_path)

        if is_valid:
            print("✓ Valid frontmatter")
        else:
            exit_code = 1
            print("✗ Invalid frontmatter:")
            for error in errors:
                print(f"  - {error}")

    sys.exit(exit_code)

if __name__ == '__main__':
    main()
