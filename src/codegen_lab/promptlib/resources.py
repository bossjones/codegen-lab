"""Resources for cursor rules.

This module contains MCP resource endpoints for cursor rules, including:
- list_cursor_rules: List all available cursor rules
- get_cursor_rule: Get a parsed cursor rule by name
- get_cursor_rule_raw: Get the raw markdown content of a cursor rule by name
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

# Use local imports to avoid circular dependencies
if TYPE_CHECKING:
    from codegen_lab.promptlib.models import CursorRule
    from codegen_lab.promptlib.utils import get_cursor_rule_names, parse_cursor_rule, read_cursor_rule

from codegen_lab.promptlib import mcp


@mcp.resource(
    "cursor-rules://list",
    name="list_cursor_rules",
    description="List all available cursor rules with their names and descriptions",
)
def list_cursor_rules() -> list[dict[str, str]] | dict[str, Any]:
    """List all available cursor rules with their names and descriptions.

    Returns:
        Union[List[Dict[str, str]], Dict[str, Any]]: List of cursor rules with names and descriptions

    """
    # This function will be implemented in a later phase
    # For now, it's a placeholder that references the original implementation
    from codegen_lab.promptlib import list_cursor_rules as original_list_cursor_rules

    return original_list_cursor_rules()


@mcp.resource(
    "cursor-rule://{name}",
    name="get_cursor_rule",
    description="Get a parsed cursor rule by name with structured content",
)
def get_cursor_rule(name: str) -> dict[str, Any]:
    """Get a parsed cursor rule by name with structured content.

    Args:
        name: The name of the cursor rule

    Returns:
        Dict[str, Any]: Structured representation of the cursor rule

    """
    # This function will be implemented in a later phase
    # For now, it's a placeholder that references the original implementation
    from codegen_lab.promptlib import get_cursor_rule as original_get_cursor_rule

    return original_get_cursor_rule(name)


@mcp.resource(
    "cursor-rule-raw://{name}",
    name="get_cursor_rule_raw",
    description="Get the raw markdown content of a cursor rule by name",
)
def get_cursor_rule_raw(name: str) -> str:
    """Get the raw markdown content of a cursor rule by name.

    Args:
        name: The name of the cursor rule

    Returns:
        str: The raw markdown content of the cursor rule

    """
    # This function will be implemented in a later phase
    # For now, it's a placeholder that references the original implementation
    from codegen_lab.promptlib import get_cursor_rule_raw as original_get_cursor_rule_raw

    return original_get_cursor_rule_raw(name)
