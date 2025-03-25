"""Models for cursor rules.

This module contains the data structures for cursor rules, including:
- CursorRuleMetadata: Metadata for a cursor rule
- CursorRuleExample: Example for a cursor rule
- CursorRuleFilter: Filter for a cursor rule
- CursorRuleAction: Action for a cursor rule
- CursorRule: Complete cursor rule structure
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict, Union


class CursorRuleMetadata(TypedDict, total=False):
    """Metadata for a cursor rule.

    Attributes:
        priority: The priority of the rule (high, medium, low)
        version: The version of the rule
        tags: List of tags associated with the rule

    """

    priority: str
    version: str
    tags: list[str]


class CursorRuleExample(TypedDict):
    """Example for a cursor rule.

    Attributes:
        input: The input example
        output: The expected output

    """

    input: str
    output: str


class CursorRuleFilter(TypedDict):
    """Filter for a cursor rule.

    Attributes:
        type: The type of filter (file_extension, content, etc.)
        pattern: The pattern to match

    """

    type: str
    pattern: str


class CursorRuleAction(TypedDict):
    """Action for a cursor rule.

    Attributes:
        type: The type of action (suggest, etc.)
        message: The message to display

    """

    type: str
    message: str


class CursorRule(TypedDict):
    """Complete cursor rule structure.

    Attributes:
        name: The name of the rule
        description: The description of the rule
        filters: List of filters for the rule
        actions: List of actions for the rule
        examples: List of examples for the rule
        metadata: Metadata for the rule

    """

    name: str
    description: str
    filters: list[CursorRuleFilter]
    actions: list[CursorRuleAction]
    examples: list[CursorRuleExample]
    metadata: CursorRuleMetadata
