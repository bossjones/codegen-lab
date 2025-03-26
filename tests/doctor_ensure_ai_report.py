#!/usr/bin/env python3
"""Test script for ensure_ai_report function. Think of this like brew doctor.

This script tests the ensure_ai_report function from the prompt_library module.
"""

import json
import os
from typing import Any, Dict

from codegen_lab.prompt_library import ensure_ai_report


def main() -> None:
    """Test the ensure_ai_report function and print results."""
    # Get current working directory
    cwd = os.getcwd()
    print(f"Current working directory: {cwd}")

    # Check if ai_report.md exists in current directory
    report_path = "ai_report.md"
    exists = os.path.exists(report_path)

    # If not in current directory, check in parent directory (project root)
    if not exists and os.path.basename(cwd) == "tests":
        parent_dir = os.path.dirname(cwd)
        parent_report_path = os.path.join(parent_dir, "ai_report.md")
        if os.path.exists(parent_report_path):
            report_path = parent_report_path
            exists = True
            print(f"AI report found in parent directory: {report_path}")

    print(f"AI report exists: {exists}")

    # Run ensure_ai_report function
    print("Running ensure_ai_report function...")
    result = ensure_ai_report(report_path=report_path)

    # Print the result in a formatted way
    print("\nFunction result:")
    print(json.dumps(result, indent=2, default=str))

    # Check expected sections in the report if it exists
    if exists:
        print("\nChecking for expected sections in the report...")
        try:
            with open(report_path, encoding="utf-8") as f:
                content = f.read()

            expected_sections = [
                "Project Overview",
                "Repository Structure",
                "Technology Stack",
                "Application Structure",
                "Deployment",
                "Development Tools",
                "Conclusion",
            ]

            for section in expected_sections:
                if f"## {section}" in content:
                    print(f"✅ Found section: {section}")
                else:
                    print(f"❌ Missing section: {section}")
        except Exception as e:
            print(f"Error reading report: {e}")


if __name__ == "__main__":
    main()
