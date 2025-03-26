"""Utilities for cursor rules.

This module contains utility functions for working with cursor rules, including:
- get_cursor_rule_files: Get all cursor rule files
- get_cursor_rule_names: Get all cursor rule names
- read_cursor_rule: Read a cursor rule file by name
- parse_cursor_rule: Parse cursor rule content into a structured format
- generate_cursor_rule: Generate a cursor rule based on provided parameters
"""

from __future__ import annotations

import glob
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, TypedDict, Union

if TYPE_CHECKING:
    from codegen_lab.promptlib.models import (
        CursorRule,
        CursorRuleAction,
        CursorRuleExample,
        CursorRuleFilter,
        CursorRuleMetadata,
    )

# Define paths
CURSOR_RULES_DIR = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../hack/drafts/cursor_rules")))


def get_cursor_rule_files() -> list[Path]:
    """Get all cursor rule files from the cursor rules directory.

    Returns:
        List[Path]: List of paths to cursor rule files

    """
    return list(CURSOR_RULES_DIR.glob("*.mdc.md"))


def get_cursor_rule_names() -> list[str]:
    """Get all cursor rule names from the cursor rules directory.

    Returns:
        List[str]: List of cursor rule names (without extension)

    """
    return [file.stem.replace(".mdc", "") for file in get_cursor_rule_files()]


def read_cursor_rule(rule_name: str) -> str | None:
    """Read a cursor rule file by name.

    Args:
        rule_name: The name of the cursor rule (without extension)

    Returns:
        Optional[str]: The content of the cursor rule file, or None if not found

    """
    rule_path = CURSOR_RULES_DIR / f"{rule_name}.mdc.md"
    if rule_path.exists():
        return rule_path.read_text()
    return None


def parse_cursor_rule(content: str) -> dict[str, Any]:
    """Parse cursor rule content into a structured format.

    Args:
        content: The content of the cursor rule file

    Returns:
        Dict[str, Any]: Structured representation of the cursor rule

    """
    # Extract frontmatter
    frontmatter = {}
    frontmatter_match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
    if frontmatter_match:
        frontmatter_text = frontmatter_match.group(1)
        for line in frontmatter_text.strip().split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                frontmatter[key.strip()] = value.strip()

    # Extract title and description
    title_match = re.search(r"# (.*?)\n", content)
    title = title_match.group(1) if title_match else ""

    description = ""
    description_match = re.search(r"# .*?\n\n(.*?)\n\n", content, re.DOTALL)
    if description_match:
        description = description_match.group(1).strip()

    # Extract rule content
    rule_content = {}
    rule_match = re.search(r"<rule>(.*?)</rule>", content, re.DOTALL)
    if rule_match:
        rule_text = rule_match.group(1)

        # Extract name
        name_match = re.search(r"name: (.*?)$", rule_text, re.MULTILINE)
        if name_match:
            rule_content["name"] = name_match.group(1).strip()

        # Extract description
        desc_match = re.search(r"description: (.*?)$", rule_text, re.MULTILINE)
        if desc_match:
            rule_content["description"] = desc_match.group(1).strip()

        # Extract filters section
        filters_match = re.search(r"filters:(.*?)(?:actions:|examples:|metadata:)", rule_text, re.DOTALL)
        if filters_match:
            filters_text = filters_match.group(1).strip()
            filters = []
            for filter_match in re.finditer(r"- type: (.*?)\n\s+pattern: \"(.*?)\"", filters_text, re.DOTALL):
                filters.append({"type": filter_match.group(1).strip(), "pattern": filter_match.group(2).strip()})
            rule_content["filters"] = filters

        # Extract actions section
        actions_match = re.search(r"actions:(.*?)(?:examples:|metadata:|$)", rule_text, re.DOTALL)
        if actions_match:
            actions_text = actions_match.group(1).strip()
            actions = []
            for action_match in re.finditer(
                r"- type: (.*?)\n\s+message: \|(.*?)(?:\n\s+-|\n\nexamples|\n\nmetadata|$)", actions_text, re.DOTALL
            ):
                actions.append({"type": action_match.group(1).strip(), "message": action_match.group(2).strip()})
            rule_content["actions"] = actions

        # Extract examples section
        examples_match = re.search(r"examples:(.*?)(?:metadata:|$)", rule_text, re.DOTALL)
        if examples_match:
            examples_text = examples_match.group(1).strip()
            examples = []
            for example_match in re.finditer(
                r"- input: \|(.*?)\n\s+output: \|(.*?)(?:\n\s+-|$)", examples_text, re.DOTALL
            ):
                examples.append({"input": example_match.group(1).strip(), "output": example_match.group(2).strip()})
            rule_content["examples"] = examples

        # Extract metadata section
        metadata_match = re.search(r"metadata:(.*?)$", rule_text, re.DOTALL)
        if metadata_match:
            metadata_text = metadata_match.group(1).strip()
            metadata = {}

            # Extract priority
            priority_match = re.search(r"priority: (.*?)$", metadata_text, re.MULTILINE)
            if priority_match:
                metadata["priority"] = priority_match.group(1).strip()

            # Extract version
            version_match = re.search(r"version: (.*?)$", metadata_text, re.MULTILINE)
            if version_match:
                metadata["version"] = version_match.group(1).strip()

            # Extract tags
            tags_match = re.search(r"tags:(.*?)(?:\n\s*[a-z]|$)", metadata_text, re.DOTALL)
            if tags_match:
                tags_text = tags_match.group(1).strip()
                tags = []
                for tag_match in re.finditer(r"- (.*?)$", tags_text, re.MULTILINE):
                    tags.append(tag_match.group(1).strip())
                metadata["tags"] = tags

            rule_content["metadata"] = metadata

    return rule_content


def generate_cursor_rule(
    rule_name: str,
    description: str,
    file_patterns: list[str],
    content_patterns: list[str],
    action_message: str,
    examples: list[dict[str, str]],
    tags: list[str],
    priority: str = "medium",
) -> str:
    """Generate a cursor rule based on provided parameters.

    Args:
        rule_name: The name of the rule
        description: The description of the rule
        file_patterns: List of file patterns to match
        content_patterns: List of content patterns to match
        action_message: The message to display for the action
        examples: List of examples for the rule
        tags: List of tags for the rule
        priority: The priority of the rule (default: "medium")

    Returns:
        str: The generated cursor rule content

    """
    # Generate frontmatter
    frontmatter = {
        "description": description,
        "globs": "*.{" + ",".join(file_patterns) + "}",
        "alwaysApply": False,
    }

    # Generate rule content
    rule_content = {
        "name": rule_name,
        "description": description,
        "filters": [{"type": "file_extension", "pattern": f"\\.{pattern}$"} for pattern in file_patterns],
        "actions": [{"type": "suggest", "message": action_message}],
        "examples": [{"input": ex["input"], "output": ex["output"]} for ex in examples],
        "metadata": {
            "priority": priority,
            "version": "1.0",
            "tags": tags,
        },
    }

    # Add content patterns if provided
    if content_patterns:
        rule_content["filters"].extend([{"type": "content", "pattern": pattern} for pattern in content_patterns])

    # Format frontmatter as YAML
    frontmatter_str = "---\n"
    for key, value in frontmatter.items():
        frontmatter_str += f"{key}: {value}\n"
    frontmatter_str += "---\n\n"

    # Format title and description
    title_str = f"# {rule_name.replace('-', ' ').title()}\n\n{description}\n\n"

    # Format rule content
    rule_str = "<rule>\n"

    # Add name and description
    rule_str += f"name: {rule_content['name']}\n"
    rule_str += f"description: {rule_content['description']}\n\n"

    # Add filters
    rule_str += "filters:\n"
    for filter_item in rule_content["filters"]:
        rule_str += f"  - type: {filter_item['type']}\n"
        rule_str += f'    pattern: "{filter_item["pattern"]}"\n'

    # Add actions
    rule_str += "\nactions:\n"
    for action in rule_content["actions"]:
        rule_str += f"  - type: {action['type']}\n"
        rule_str += "    message: |\n"
        # Indent each line of the message
        for line in action["message"].split("\n"):
            rule_str += f"      {line}\n"

    # Add examples if provided
    if examples:
        rule_str += "\nexamples:\n"
        for example in rule_content["examples"]:
            rule_str += "  - input: |\n"
            # Indent each line of the input
            for line in example["input"].split("\n"):
                rule_str += f"      {line}\n"
            rule_str += "    output: |\n"
            # Indent each line of the output
            for line in example["output"].split("\n"):
                rule_str += f"      {line}\n"

    # Add metadata
    rule_str += "\nmetadata:\n"
    metadata = rule_content["metadata"]
    rule_str += f"  priority: {metadata['priority']}\n"
    rule_str += f"  version: {metadata['version']}\n"
    if metadata.get("tags"):
        rule_str += "  tags:\n"
        for tag in metadata["tags"]:
            rule_str += f"    - {tag}\n"

    rule_str += "</rule>\n"

    # Combine all sections
    return frontmatter_str + title_str + rule_str
