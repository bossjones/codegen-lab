"""Prompt Library Module for Cursor Rules

This module provides functionality for managing cursor rules, including:
- Data models for cursor rule components
- Utility functions for working with cursor rules
- MCP resources for exposing cursor rules
- MCP tools for cursor rule operations
- MCP prompts for cursor rule generation
- Workflow functions for executing cursor rule tasks

This is a re-export module that maintains backward compatibility with the original
prompt_library.py module while providing a more modular structure.
"""

from __future__ import annotations

# Re-export everything from the original module for backward compatibility
# These imports will be gradually replaced with imports from the new modules
# as the refactoring progresses.
from codegen_lab.promptlib import (
    # Constants
    CURSOR_RULES_DIR,
    CursorRule,
    CursorRuleAction,
    CursorRuleExample,
    CursorRuleFilter,
    # Data models
    CursorRuleMetadata,
    create_cursor_rule_files,
    cursor_rules_workflow,
    ensure_ai_report,
    ensure_makefile_task,
    execute_phase_1,
    execute_phase_2,
    execute_phase_3,
    execute_phase_4,
    execute_phase_5,
    generate_cursor_rule,
    generate_cursor_rule_prompt,
    get_cursor_rule,
    # Utility functions
    get_cursor_rule_files,
    get_cursor_rule_names,
    get_cursor_rule_raw,
    get_static_cursor_rule,
    get_static_cursor_rules,
    instruct_custom_repo_rules_generation,
    # Tool functions
    instruct_repo_analysis,
    # Resource endpoints
    list_cursor_rules,
    mcp,
    parse_cursor_rule,
    # Workflow functions
    plan_and_execute_prompt_library_workflow,
    prep_workspace,
    read_cursor_rule,
    recommend_cursor_rules,
    # Prompt functions
    repo_analysis_prompt,
    run_update_cursor_rules,
    save_cursor_rule,
    update_dockerignore,
)

# Define what should be exported when using 'from prompt_library import *'
__all__ = [
    # Constants
    "CURSOR_RULES_DIR",
    "mcp",
    # Data models
    "CursorRuleMetadata",
    "CursorRuleExample",
    "CursorRuleFilter",
    "CursorRuleAction",
    "CursorRule",
    # Utility functions
    "get_cursor_rule_files",
    "get_cursor_rule_names",
    "read_cursor_rule",
    "parse_cursor_rule",
    "generate_cursor_rule",
    # Resource endpoints
    "list_cursor_rules",
    "get_cursor_rule",
    "get_cursor_rule_raw",
    # Tool functions
    "instruct_repo_analysis",
    "instruct_custom_repo_rules_generation",
    "get_static_cursor_rule",
    "get_static_cursor_rules",
    "save_cursor_rule",
    "recommend_cursor_rules",
    "prep_workspace",
    "create_cursor_rule_files",
    "ensure_makefile_task",
    "ensure_ai_report",
    "run_update_cursor_rules",
    "update_dockerignore",
    "cursor_rules_workflow",
    # Prompt functions
    "repo_analysis_prompt",
    "generate_cursor_rule_prompt",
    # Workflow functions
    "plan_and_execute_prompt_library_workflow",
    "execute_phase_1",
    "execute_phase_2",
    "execute_phase_3",
    "execute_phase_4",
    "execute_phase_5",
]
