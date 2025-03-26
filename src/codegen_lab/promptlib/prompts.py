"""Prompts for cursor rules.

This module contains MCP prompt functions for cursor rule generation, including:
- repo_analysis_prompt: Analyze a repository to gather information for cursor rule creation
- generate_cursor_rule_prompt: Generate a custom cursor rule based on repository information

Migration Plan for prompts.py:
- [ ] Import all necessary dependencies
- [ ] Update type imports to use models and utils modules
- [ ] Implement repo_analysis_prompt:
  - [ ] Set up proper context handling
  - [ ] Create prompt structure with clear instructions
  - [ ] Define system message with detailed analysis instructions
  - [ ] Handle user input formatting and validation
  - [ ] Process and format assistant response
  - [ ] Add error handling for API failures
  - [ ] Add logging for debugging
- [ ] Implement generate_cursor_rule_prompt:
  - [ ] Set up proper context handling
  - [ ] Create prompt structure with rule generation instructions
  - [ ] Define system message with formatting guidelines
  - [ ] Incorporate template rule if provided
  - [ ] Process and validate user inputs
  - [ ] Format AI response into proper structure
  - [ ] Add error handling for API failures
  - [ ] Add logging for debugging
- [ ] Add proper docstrings and type hints
- [ ] Update __init__.py to re-export prompts
- [ ] Verify functionality through manual testing
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

if TYPE_CHECKING:
    from mcp.server.fastmcp.server import Context

    from .models import CursorRule

from codegen_lab.promptlib import mcp


@mcp.prompt(name="repo-analysis", description="Analyze a repository to gather information for cursor rule creation")
def repo_analysis_prompt(
    repo_description: str, main_languages: str, file_patterns: str, key_features: str, ctx: Context | None = None
) -> list[dict[str, Any]]:
    """Analyze a repository to gather information for cursor rule creation.

    Args:
        repo_description: Brief description of the repository
        main_languages: Main programming languages used in the repository
        file_patterns: Common file patterns in the repository
        key_features: Key features of the repository
        ctx: Context for the prompt

    Returns:
        List[Dict[str, Any]]: Analysis results

    """
    # This function will be implemented in a later phase
    # For now, it's a placeholder that references the original implementation
    from codegen_lab.promptlib import repo_analysis_prompt as original_repo_analysis_prompt

    return original_repo_analysis_prompt(
        repo_description=repo_description,
        main_languages=main_languages,
        file_patterns=file_patterns,
        key_features=key_features,
        ctx=ctx,
    )


@mcp.prompt(name="generate-cursor-rule", description="Generate a custom cursor rule based on repository information")
def generate_cursor_rule_prompt(
    rule_name: str,
    description: str,
    file_patterns: str,
    content_patterns: str,
    action_message: str,
    examples: str,
    tags: str,
    priority: str = "medium",
    template_rule: str | None = None,
    ctx: Context | None = None,
) -> list[dict[str, Any]]:
    """Generate a custom cursor rule based on repository information.

    Args:
        rule_name: Name of the rule to generate
        description: Description of the rule
        file_patterns: File patterns to match
        content_patterns: Content patterns to match
        action_message: Message to display when rule is triggered
        examples: Examples of rule application
        tags: Tags for the rule
        priority: Priority of the rule (default: "medium")
        template_rule: Optional template rule to use as a starting point
        ctx: Context for the prompt

    Returns:
        List[Dict[str, Any]]: Generated cursor rule

    """
    # This function will be implemented in a later phase
    # For now, it's a placeholder that references the original implementation
    from codegen_lab.promptlib import generate_cursor_rule_prompt as original_generate_cursor_rule_prompt

    return original_generate_cursor_rule_prompt(
        rule_name=rule_name,
        description=description,
        file_patterns=file_patterns,
        content_patterns=content_patterns,
        action_message=action_message,
        examples=examples,
        tags=tags,
        priority=priority,
        template_rule=template_rule,
        ctx=ctx,
    )
