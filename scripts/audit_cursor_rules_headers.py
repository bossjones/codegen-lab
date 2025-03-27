#!/usr/bin/env python3
"""
Script to audit cursor rule files in hack/drafts/cursor_rules or .cursor/rules directory
for proper YAML frontmatter headers.

This script checks for:
1. Presence of YAML frontmatter (enclosed by ---)
2. Required fields: description, globs, and alwaysApply
3. Correct combinations of fields based on rule type
4. Proper formatting of fields
5. Absence of quotes around glob patterns
"""

import argparse
import os
import re
from typing import Any, Dict, List, Optional, Tuple

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


def determine_rule_type(description: str, globs: str, always_apply: bool) -> tuple[str, list[str]]:
    """
    Determine the type of cursor rule based on frontmatter fields.

    Args:
        description: Content of the description field
        globs: Content of the globs field
        always_apply: Value of the alwaysApply field

    Returns:
        Tuple containing:
        - String indicating the rule type
        - List of issues if the combination is invalid
    """
    issues = []

    # Check for Always rule
    if always_apply:
        rule_type = "Always"
        if description.strip():
            issues.append("Always rules should have empty description field")
        if globs.strip():
            issues.append("Always rules should have empty globs field")

    # Check for Agent Selected rule
    elif description.strip() and not globs.strip():
        rule_type = "Agent Selected"

    # Check for Auto Select rule
    elif not description.strip() and globs.strip():
        rule_type = "Auto Select"

    # Check for Auto Select+desc rule
    elif description.strip() and globs.strip():
        rule_type = "Auto Select+desc"

    # Check for Manual rule
    elif not description.strip() and not globs.strip() and not always_apply:
        rule_type = "Manual"

    else:
        rule_type = "Unknown"
        issues.append("Invalid combination of frontmatter fields")

    return rule_type, issues


def check_for_quoted_globs(globs: str) -> list[str]:
    """
    Check if glob patterns are surrounded by quotes, which is incorrect.

    Args:
        globs: Content of the globs field

    Returns:
        List of issues found (empty if no quotes detected)
    """
    issues = []

    # Check for entire field being quoted
    if globs.strip().startswith('"') and globs.strip().endswith('"'):
        issues.append("Glob patterns should not be enclosed in double quotes")
    elif globs.strip().startswith("'") and globs.strip().endswith("'"):
        issues.append("Glob patterns should not be enclosed in single quotes")

    # Check for individual patterns being quoted
    if re.search(r'["\'][^,]*["\']', globs):
        issues.append("Individual glob patterns should not be quoted")

    return issues


def check_yaml_header(file_path: str) -> tuple[bool, list[str], dict[str, Any]]:
    """
    Check if a file has the correct YAML frontmatter header.

    Args:
        file_path: Path to the file to check

    Returns:
        Tuple containing:
        - Boolean indicating if the header is valid
        - List of issues found (empty if valid)
        - Dictionary of extracted frontmatter fields
    """
    issues = []
    frontmatter = {
        "description": "",
        "globs": "",
        "alwaysApply": False,
        "rule_type": "Unknown"
    }

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Check if the file starts with ---
        if not content.strip().startswith("---"):
            issues.append("Missing opening YAML delimiter '---'")
            return False, issues, frontmatter

        # Extract the YAML frontmatter
        match = re.match(r"---\s*(.*?)\s*---", content, re.DOTALL)
        if not match:
            issues.append("Missing closing YAML delimiter '---'")
            return False, issues, frontmatter

        yaml_content = match.group(1)

        # Check for required fields
        if "description:" not in yaml_content:
            issues.append("Missing 'description' field")
        else:
            # Use a better regex that stops at the next field or end of content
            description_match = re.search(r"description:(.*?)(?=\n[a-zA-Z][a-zA-Z0-9_]*:|$)", yaml_content, re.DOTALL)
            if description_match:
                # Get the content and strip leading/trailing whitespace (including newlines)
                description = description_match.group(1).strip()
                frontmatter["description"] = description

        if "globs:" not in yaml_content:
            issues.append("Missing 'globs' field")
        else:
            # Use a better regex for glob patterns
            globs_match = re.search(r"globs:(.*?)(?=\n[a-zA-Z][a-zA-Z0-9_]*:|$)", yaml_content, re.DOTALL)
            if globs_match:
                globs = globs_match.group(1).strip()
                frontmatter["globs"] = globs

                # Check glob formatting
                if globs and (globs.startswith("[") or globs.startswith("{")):
                    issues.append("Incorrect glob format, should not use array or curly brace notation")

                # Check for missing spaces after commas
                if globs and "," in globs and not re.search(r",\s+", globs):
                    issues.append("Missing spaces after commas in glob list")

                # Check for quoted globs
                issues.extend(check_for_quoted_globs(globs))

        if "alwaysApply:" not in yaml_content:
            issues.append("Missing 'alwaysApply' field")
        else:
            # Use a better regex for alwaysApply
            always_apply_match = re.search(r"alwaysApply:(.*?)(?=\n[a-zA-Z][a-zA-Z0-9_]*:|$)", yaml_content, re.DOTALL)
            if always_apply_match:
                always_apply_value = always_apply_match.group(1).strip().lower()
                frontmatter["alwaysApply"] = always_apply_value == "true"

                # Fix for incorrectly capturing "alwaysApply: false" as a glob pattern
                if "alwaysApply:" in frontmatter["globs"]:
                    frontmatter["globs"] = ""

        # Check for empty lines in frontmatter
        if "\n\n" in yaml_content:
            issues.append("Empty lines between frontmatter fields")

        # Determine rule type and check for valid combinations
        rule_type, type_issues = determine_rule_type(
            frontmatter["description"],
            frontmatter["globs"],
            frontmatter["alwaysApply"]
        )
        frontmatter["rule_type"] = rule_type
        issues.extend(type_issues)

        return len(issues) == 0, issues, frontmatter

    except Exception as e:
        issues.append(f"Error reading file: {e!s}")
        return False, issues, frontmatter


def audit_cursor_rules(directory: str) -> tuple[dict[str, list[str]], dict[str, dict[str, Any]]]:
    """
    Audit cursor rule files in the specified directory.

    Args:
        directory: Directory containing cursor rule files

    Returns:
        Tuple containing:
        - Dictionary mapping file paths to lists of issues
        - Dictionary mapping file paths to frontmatter info
    """
    results = {}
    frontmatter_info = {}

    if not os.path.exists(directory):
        return {directory: [f"Directory not found: {directory}"]}, {}

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".mdc.md") or file.endswith(".mdc"):
                file_path = os.path.join(root, file)
                is_valid, issues, frontmatter = check_yaml_header(file_path)

                frontmatter_info[file_path] = frontmatter
                if not is_valid:
                    results[file_path] = issues

    return results, frontmatter_info


def get_rule_type_color(rule_type: str) -> str:
    """
    Get a color for a rule type for consistent coloring.

    Args:
        rule_type: The type of rule

    Returns:
        A color string for rich
    """
    colors = {
        "Agent Selected": "cyan",
        "Always": "magenta",
        "Auto Select": "green",
        "Auto Select+desc": "blue",
        "Manual": "yellow",
        "Unknown": "red"
    }
    return colors.get(rule_type, "white")


def print_rule_type_examples(console: Console) -> None:
    """
    Print examples of valid headers for each rule type using rich formatting,
    including information about how each rule type works.

    Args:
        console: Rich console instance for output
    """
    console.print("\n[bold]Summary of required header format by rule type:[/bold]")

    rule_types = [
        ("Agent Selected", "cyan", "Agent sees description and chooses when to apply. Description field is critical."),
        ("Always", "magenta", "Applied to every chat and cmd-k request automatically. No need for description or globs."),
        ("Auto Select", "green", "Applied to matching existing files. Glob pattern is critical."),
        ("Auto Select+desc", "blue", "Better for new files. Includes description with critical glob pattern."),
        ("Manual", "yellow", "User must explicitly reference in chat. Not automatically applied.")
    ]

    for rule_type, color, description in rule_types:
        example_text = ""
        field_notes = ""

        if rule_type == "Agent Selected":
            example_text = "---\ndescription: Description of the cursor rule\nglobs:\nalwaysApply: false\n---"
            field_notes = "description: [bold green]CRITICAL[/bold green] - Agent uses this to decide when to apply\nglobs: [bold red]BLANK[/bold red]\nalwaysApply: must be false"
        elif rule_type == "Always":
            example_text = "---\ndescription:\nglobs:\nalwaysApply: true\n---"
            field_notes = "description: [bold red]BLANK[/bold red]\nglobs: [bold red]BLANK[/bold red]\nalwaysApply: must be true"
        elif rule_type == "Auto Select":
            example_text = "---\ndescription:\nglobs: *.py, *.js\nalwaysApply: false\n---"
            field_notes = "description: [bold red]BLANK[/bold red]\nglobs: [bold green]CRITICAL[/bold green] - Must be valid glob pattern(s)\nalwaysApply: must be false"
        elif rule_type == "Auto Select+desc":
            example_text = "---\ndescription: Description of the cursor rule\nglobs: *.py, *.js\nalwaysApply: false\n---"
            field_notes = "description: Included to help users understand the rule\nglobs: [bold green]CRITICAL[/bold green] - Must be valid glob pattern(s)\nalwaysApply: must be false"
        elif rule_type == "Manual":
            example_text = "---\ndescription:\nglobs:\nalwaysApply: false\n---"
            field_notes = "description: [bold red]BLANK[/bold red]\nglobs: [bold red]BLANK[/bold red]\nalwaysApply: must be false"

        panel_content = Text()
        panel_content.append(f"{description}\n\n", style="italic")
        panel_content.append("YAML Header Example:\n", style="bold")
        panel_content.append(f"{example_text}\n\n")
        panel_content.append("Field Requirements:\n", style="bold")
        panel_content.append(field_notes)

        panel = Panel(
            panel_content,
            title=f"[bold]{rule_type}[/bold]",
            border_style=color,
            padding=(1, 2)
        )
        console.print(panel)

    # Add note about glob patterns format
    console.print("\n[bold yellow]Note about glob patterns:[/bold yellow]")
    console.print(" • Glob patterns should be comma-separated with spaces: '*.py, *.js'")
    console.print(" • Do not use quotes around patterns: '*.py' is incorrect")
    console.print(" • Do not use array notation: [*.py, *.js] is incorrect")


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Audit cursor rule files for proper YAML frontmatter headers."
    )
    parser.add_argument(
        "--prod",
        action="store_true",
        help="Check production directory (.cursor/rules) instead of staging (hack/drafts/cursor_rules)"
    )
    parser.add_argument(
        "--desc",
        action="store_true",
        help="Include the description field in the output table"
    )
    return parser.parse_args()


def main() -> None:
    """Main function to audit cursor rule headers."""
    args = parse_arguments()

    # Set directory based on args
    if args.prod:
        directory = ".cursor/rules"
        env_name = "production"
    else:
        directory = "hack/drafts/cursor_rules"
        env_name = "staging"

    console = Console()
    console.print(f"[bold]Auditing cursor rule headers in [blue]{directory}[/blue] ({env_name} environment)...[/bold]")

    results, frontmatter_info = audit_cursor_rules(directory)

    # Handle directory not found
    if directory in results:
        console.print(f"[bold red]Error:[/bold red] {results[directory][0]}")
        return

    # Create a table for rule types
    rule_table = Table(title=f"Cursor Rule Types in {env_name} environment", box=box.ROUNDED, show_lines=True)
    rule_table.add_column("File", style="dim")
    rule_table.add_column("Rule Type")
    rule_table.add_column("Glob Patterns")

    # Add description column if requested
    if args.desc:
        rule_table.add_column("Description")

    # Count rule types for summary
    rule_type_counts = {"Agent Selected": 0, "Always": 0, "Auto Select": 0, "Auto Select+desc": 0, "Manual": 0, "Unknown": 0}

    for file_path, frontmatter in frontmatter_info.items():
        relative_path = os.path.relpath(file_path)
        rule_type = frontmatter["rule_type"]

        # Fix for displaying glob patterns
        if not frontmatter["globs"] or frontmatter["globs"].strip() == "":
            glob_patterns = "<none>"
        else:
            glob_patterns = frontmatter["globs"]

        rule_type_counts[rule_type] = rule_type_counts.get(rule_type, 0) + 1

        color = get_rule_type_color(rule_type)

        # Prepare row data
        row_data = [
            relative_path,
            f"[{color}]{rule_type}[/{color}]",
            glob_patterns
        ]

        # Add description if requested
        if args.desc:
            description = frontmatter["description"].strip() if frontmatter["description"] else "<none>"
            row_data.append(description)

        rule_table.add_row(*row_data)

    console.print(rule_table)

    # Create a summary table
    summary_table = Table(title="Rule Type Summary", box=box.ROUNDED)
    summary_table.add_column("Rule Type")
    summary_table.add_column("Count", justify="right")

    for rule_type, count in rule_type_counts.items():
        if count > 0:
            color = get_rule_type_color(rule_type)
            summary_table.add_row(f"[{color}]{rule_type}[/{color}]", str(count))

    console.print(summary_table)

    # Report issues if any
    if not results:
        console.print("\n[bold green]✅ All cursor rule files have valid headers![/bold green]")
    else:
        console.print(f"\n[bold red]❌ Found issues in {len(results)} files:[/bold red]")

        for file_path, issues in results.items():
            relative_path = os.path.relpath(file_path)
            rule_type = frontmatter_info[file_path]["rule_type"]
            color = get_rule_type_color(rule_type)

            issue_text = Text()
            issue_text.append(f"\n{relative_path} ", style="bold")
            issue_text.append(f"({rule_type})", style=color)
            issue_text.append(":")

            console.print(issue_text)

            for issue in issues:
                console.print(f"  [red]•[/red] {issue}")

        # Print examples of valid headers
        print_rule_type_examples(console)


if __name__ == "__main__":
    main()
