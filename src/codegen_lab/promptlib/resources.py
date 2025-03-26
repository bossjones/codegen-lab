"""Resources for cursor rules.

This module contains MCP resource endpoints for cursor rules, including:
- list_cursor_rules: List all available cursor rules
- get_cursor_rule: Get a parsed cursor rule by name
- get_cursor_rule_raw: Get the raw markdown content of a cursor rule by name

Migration Plan for resources.py:
- [x] Import all necessary dependencies
- [x] Update type imports to use models and utils modules
- [x] Implement list_cursor_rules function:
  - [x] Use get_cursor_rule_names from utils
  - [x] Iterate through rule names and create list entries
  - [x] Add error handling for file system operations
  - [x] Return formatted list of rules
- [x] Implement get_cursor_rule function:
  - [x] Use read_cursor_rule and parse_cursor_rule from utils
  - [x] Add error handling for missing rules
  - [x] Return parsed rule structure
- [x] Implement get_cursor_rule_raw function:
  - [x] Use read_cursor_rule from utils
  - [x] Add error handling for missing rules
  - [x] Return raw rule content
- [x] Add proper docstrings and type hints
- [x] Add logging for debugging and error tracking
- [ ] Update __init__.py to re-export resources
- [ ] Verify functionality through manual testing
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

# Use local imports to avoid circular dependencies
if TYPE_CHECKING:
    from codegen_lab.promptlib.models import CursorRule

# Direct imports for actually used functions
from codegen_lab.promptlib import mcp
from codegen_lab.promptlib.utils import get_cursor_rule_names, parse_cursor_rule, read_cursor_rule

# Set up logging
logger = logging.getLogger(__name__)


@mcp.resource(
    "cursor-rules://list",
    name="list_cursor_rules",
    description="List all available cursor rules with their names and descriptions",
)
def list_cursor_rules() -> list[dict[str, str]] | dict[str, Any]:
    """List all available cursor rules with their names and descriptions.

    Returns:
        Union[List[Dict[str, str]], Dict[str, Any]]: List of cursor rules with names and descriptions,
            or an error message if the operation fails.

    """
    try:
        logger.debug("Listing all cursor rules")
        rule_names = get_cursor_rule_names()
        result = []

        for name in rule_names:
            logger.debug(f"Processing rule: {name}")
            rule_content = read_cursor_rule(name)
            if rule_content:
                rule_data = parse_cursor_rule(rule_content)
                result.append({"name": name, "description": rule_data.get("description", "No description available")})
            else:
                logger.warning(f"Could not read content for rule: {name}")
                result.append({"name": name, "description": "Description unavailable"})

        logger.debug(f"Found {len(result)} cursor rules")
        return result
    except Exception as e:
        logger.error(f"Error listing cursor rules: {e!s}", exc_info=True)
        return {"error": "Failed to list cursor rules", "message": str(e)}


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
        Dict[str, Any]: Structured representation of the cursor rule,
            or an error message if the rule doesn't exist or can't be parsed.

    """
    try:
        logger.debug(f"Getting cursor rule: {name}")
        rule_content = read_cursor_rule(name)

        if not rule_content:
            logger.warning(f"Cursor rule not found: {name}")
            return {"error": "Rule not found", "message": f"Cursor rule '{name}' does not exist or could not be read."}

        logger.debug(f"Parsing cursor rule: {name}")
        rule_data = parse_cursor_rule(rule_content)

        if not rule_data:
            logger.warning(f"Failed to parse cursor rule: {name}")
            return {
                "error": "Parsing failure",
                "message": f"Failed to parse cursor rule '{name}'. The file may be malformed.",
            }

        logger.debug(f"Successfully retrieved cursor rule: {name}")
        return rule_data
    except Exception as e:
        logger.error(f"Error getting cursor rule '{name}': {e!s}", exc_info=True)
        return {"error": "Failed to get cursor rule", "message": str(e)}


@mcp.resource(
    "cursor-rule-raw://{name}",
    name="get_cursor_rule_raw",
    description="Get the raw markdown content of a cursor rule by name",
)
def get_cursor_rule_raw(name: str) -> str | dict[str, str]:
    """Get the raw markdown content of a cursor rule by name.

    Args:
        name: The name of the cursor rule

    Returns:
        Union[str, Dict[str, str]]: The raw markdown content of the cursor rule,
            or an error message if the rule doesn't exist.

    """
    try:
        logger.debug(f"Getting raw cursor rule content: {name}")
        rule_content = read_cursor_rule(name)

        if not rule_content:
            logger.warning(f"Cursor rule not found: {name}")
            return {"error": "Rule not found", "message": f"Cursor rule '{name}' does not exist or could not be read."}

        logger.debug(f"Successfully retrieved raw cursor rule content: {name}")
        return rule_content
    except Exception as e:
        logger.error(f"Error getting raw cursor rule '{name}': {e!s}", exc_info=True)
        return {"error": "Failed to get cursor rule content", "message": str(e)}
