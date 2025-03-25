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
    # This function will be implemented in a later phase
    # For now, it's a placeholder that references the original implementation
    from codegen_lab.promptlib import parse_cursor_rule as original_parse_cursor_rule

    return original_parse_cursor_rule(content)


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
    # This function will be implemented in a later phase
    # For now, it's a placeholder that references the original implementation
    from codegen_lab.promptlib import generate_cursor_rule as original_generate_cursor_rule

    return original_generate_cursor_rule(
        rule_name=rule_name,
        description=description,
        file_patterns=file_patterns,
        content_patterns=content_patterns,
        action_message=action_message,
        examples=examples,
        tags=tags,
        priority=priority,
    )
