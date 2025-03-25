"""Tools for cursor rules.

This module contains MCP tool functions for cursor rule operations, including:
- instruct_repo_analysis: Run a repository analysis
- instruct_custom_repo_rules_generation: Run a cursor rules generation process
- get_static_cursor_rule: Get a static cursor rule file by name
- get_static_cursor_rules: Get multiple static cursor rule files
- save_cursor_rule: Save a cursor rule to the cursor rules directory
- recommend_cursor_rules: Analyze a repository summary and recommend cursor rules
- prep_workspace: Prepare the workspace for cursor rules
- create_cursor_rule_files: Create empty cursor rule files
- ensure_makefile_task: Ensure the Makefile has the update-cursor-rules task
- ensure_ai_report: Check for the existence of an AI report file
- run_update_cursor_rules: Run the update-cursor-rules Makefile task
- update_dockerignore: Update the .dockerignore file
- cursor_rules_workflow: Execute the complete cursor rules workflow
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from pydantic import Field

if TYPE_CHECKING:
    from codegen_lab.promptlib.models import CursorRule
    from codegen_lab.promptlib.utils import generate_cursor_rule, parse_cursor_rule, read_cursor_rule

from codegen_lab.promptlib import mcp


@mcp.tool(
    name="instruct_repo_analysis",
    description="Run a repository analysis to gather information for cursor rule creation",
)
def instruct_repo_analysis() -> dict[str, Any]:
    """Run a repository analysis to gather information for cursor rule creation.

    Returns:
        Dict[str, Any]: Repository analysis results

    """
    # This function will be implemented in a later phase
    # For now, it's a placeholder that references the original implementation
    from codegen_lab.promptlib import instruct_repo_analysis as original_instruct_repo_analysis

    return original_instruct_repo_analysis()


@mcp.tool(
    name="instruct_custom_repo_rules_generation",
    description="Run a cursor rules generation process based on repository analysis",
)
def instruct_custom_repo_rules_generation(
    report_path: str = Field(
        description="Path to the AI report file, relative to the project root",
        examples=["ai_report.md", "docs/ai_report.md"],
        default="ai_report.md",
    ),
) -> dict[str, Any]:
    """Run a cursor rules generation process based on repository analysis.

    Args:
        report_path: Path to the AI report file, relative to the project root

    Returns:
        Dict[str, Any]: Generation results

    """
    # This function will be implemented in a later phase
    # For now, it's a placeholder that references the original implementation
    from codegen_lab.promptlib import (
        instruct_custom_repo_rules_generation as original_instruct_custom_repo_rules_generation,
    )

    return original_instruct_custom_repo_rules_generation(report_path=report_path)


@mcp.tool(
    name="get_static_cursor_rule",
    description="Get a static cursor rule file by name to be written to the caller's .cursor/rules directory",
)
def get_static_cursor_rule(
    rule_name: str = Field(
        description="Name of the cursor rule to retrieve (with or without .md extension)",
        examples=["python-best-practices", "react-patterns", "error-handling"],
        min_length=1,
    ),
) -> dict[str, str | bool | list[dict[str, str]]]:
    """Get a static cursor rule file by name to be written to the caller's .cursor/rules directory.

    Args:
        rule_name: Name of the cursor rule to retrieve (with or without .md extension)

    Returns:
        Dict[str, Union[str, bool, List[Dict[str, str]]]]: Static cursor rule information

    """
    # This function will be implemented in a later phase
    # For now, it's a placeholder that references the original implementation
    from codegen_lab.promptlib import get_static_cursor_rule as original_get_static_cursor_rule

    return original_get_static_cursor_rule(rule_name=rule_name)


@mcp.tool(
    name="get_static_cursor_rules",
    description="Get multiple static cursor rule files to be written to the caller's .cursor/rules directory",
)
def get_static_cursor_rules(
    rule_names: list[str] = Field(
        description="List of cursor rule names to retrieve (with or without .md extension)",
        examples=[["python-best-practices", "react-patterns"], ["error-handling"]],
        min_length=1,
    ),
    ignore_missing: bool = Field(
        description="If True, missing rules will be skipped instead of returning errors",
        default=False,
    ),
) -> dict[str, list[dict[str, str | bool | list[dict[str, str]]]]]:
    """Get multiple static cursor rule files to be written to the caller's .cursor/rules directory.

    Args:
        rule_names: List of cursor rule names to retrieve (with or without .md extension)
        ignore_missing: If True, missing rules will be skipped instead of returning errors

    Returns:
        Dict[str, List[Dict[str, Union[str, bool, List[Dict[str, str]]]]]]: Static cursor rules information

    """
    # This function will be implemented in a later phase
    # For now, it's a placeholder that references the original implementation
    from codegen_lab.promptlib import get_static_cursor_rules as original_get_static_cursor_rules

    return original_get_static_cursor_rules(rule_names=rule_names, ignore_missing=ignore_missing)


@mcp.tool(name="save_cursor_rule", description="Save a cursor rule to the cursor rules directory in the project")
def save_cursor_rule(
    rule_name: str = Field(
        description="The name of the cursor rule file (without extension)",
        examples=["python-best-practices", "react-component-patterns", "error-handling"],
        min_length=3,
        pattern="^[a-z0-9-]+$",
    ),
    rule_content: str = Field(
        description="The complete content of the cursor rule in mdc.md format",
        examples=[
            '---\ndescription: Rule description\nglobs: *.py\nalwaysApply: false\n---\n# Python Best Practices\n\nWhen writing Python code, follow these guidelines:\n\n<rule>\nname: python-best-practices\ndescription: Best practices for Python development\nfilters:\n  - type: file_extension\n    pattern: "\\.py$"\nactions:\n  - type: suggest\n    message: |\n      Follow these guidelines:\n      1. Use type hints\n      2. Write docstrings\n      3. Follow PEP 8\n</rule>'
        ],
        min_length=10,
    ),
    overwrite: bool = Field(
        description="Whether to overwrite the file if it already exists",
        default=True,
    ),
) -> dict[str, list[dict[str, str | dict[str, bool | str]]] | str]:
    """Save a cursor rule to the cursor rules directory in the project.

    Args:
        rule_name: The name of the cursor rule file (without extension)
        rule_content: The complete content of the cursor rule in mdc.md format
        overwrite: Whether to overwrite the file if it already exists

    Returns:
        Dict[str, Union[List[Dict[str, Union[str, Dict[str, Union[bool, str]]]]], str]]: Save result

    """
    # This function will be implemented in a later phase
    # For now, it's a placeholder that references the original implementation
    from codegen_lab.promptlib import save_cursor_rule as original_save_cursor_rule

    return original_save_cursor_rule(rule_name=rule_name, rule_content=rule_content, overwrite=overwrite)


@mcp.tool(
    name="recommend_cursor_rules",
    description="Analyze a repository summary and recommend cursor rules to generate based on identified technologies and patterns",
)
def recommend_cursor_rules(
    repo_summary: str = Field(
        description="A summary description of the repository, including technologies, frameworks, and key features",
        examples=[
            "A Python web application using FastAPI, SQLAlchemy, and React for the frontend. Includes authentication, API endpoints, and database models.",
            "A TypeScript library for data visualization with React components. Uses webpack for bundling and Jest for testing.",
        ],
        min_length=20,
    ),
) -> list[dict[str, str | list[str]]] | dict[str, bool | list[dict[str, str]]]:
    """Analyze a repository summary and recommend cursor rules to generate.

    Args:
        repo_summary: A summary description of the repository

    Returns:
        Union[List[Dict[str, Union[str, List[str]]]], Dict[str, Union[bool, List[Dict[str, str]]]]]: Recommendations

    """
    # This function will be implemented in a later phase
    # For now, it's a placeholder that references the original implementation
    from codegen_lab.promptlib import recommend_cursor_rules as original_recommend_cursor_rules

    return original_recommend_cursor_rules(repo_summary=repo_summary)


@mcp.tool(
    name="prep_workspace",
    description="Prepare the workspace for cursor rules by returning natural language instructions",
)
def prep_workspace() -> dict[str, str]:
    """Prepare the workspace for cursor rules by returning natural language instructions.

    Returns:
        Dict[str, str]: Instructions for preparing the workspace

    """
    # This function will be implemented in a later phase
    # For now, it's a placeholder that references the original implementation
    from codegen_lab.promptlib import prep_workspace as original_prep_workspace

    return original_prep_workspace()


@mcp.tool(
    name="create_cursor_rule_files",
    description="Create empty cursor rule files and provide instructions for sequential content creation",
)
def create_cursor_rule_files(
    rule_names: list[str] = Field(
        description="A list of cursor rule names to create (without file extensions)",
        examples=["python-best-practices", "react-component-structure", "typescript-patterns"],
        min_length=1,
    ),
) -> dict[str, Any]:
    """Create empty cursor rule files and provide instructions for sequential content creation.

    Args:
        rule_names: A list of cursor rule names to create (without file extensions)

    Returns:
        Dict[str, Any]: Creation results

    """
    # This function will be implemented in a later phase
    # For now, it's a placeholder that references the original implementation
    from codegen_lab.promptlib import create_cursor_rule_files as original_create_cursor_rule_files

    return original_create_cursor_rule_files(rule_names=rule_names)


@mcp.tool(
    name="ensure_makefile_task",
    description="Ensure the Makefile has the update-cursor-rules task",
)
def ensure_makefile_task(
    makefile_path: str = Field(
        description="Path to the Makefile file, relative to the project root",
        examples=["Makefile", "build/Makefile"],
        default="Makefile",
    ),
) -> dict[str, Any]:
    """Ensure the Makefile has the update-cursor-rules task.

    Args:
        makefile_path: Path to the Makefile file, relative to the project root

    Returns:
        Dict[str, Any]: Task verification results

    """
    # This function will be implemented in a later phase
    # For now, it's a placeholder that references the original implementation
    from codegen_lab.promptlib import ensure_makefile_task as original_ensure_makefile_task

    return original_ensure_makefile_task(makefile_path=makefile_path)


@mcp.tool(
    name="ensure_ai_report",
    description="Check for the existence of an AI report file and ensure its content aligns with requirements",
)
def ensure_ai_report(
    report_path: str = Field(
        description="Path to the AI report file, relative to the project root",
        examples=[
            "./ai_report.md",
            "./docs/ai_report.md",
            "./reports/ai_report.md",
        ],
        default="./ai_report.md",
    ),
) -> dict[str, Any]:
    """Check for the existence of an AI report file and ensure its content aligns with requirements.

    Args:
        report_path: Path to the AI report file, relative to the project root

    Returns:
        Dict[str, Any]: Report verification results

    """
    # This function will be implemented in a later phase
    # For now, it's a placeholder that references the original implementation
    from codegen_lab.promptlib import ensure_ai_report as original_ensure_ai_report

    return original_ensure_ai_report(report_path=report_path)


@mcp.tool(
    name="run_update_cursor_rules",
    description="Run the update-cursor-rules Makefile task to deploy cursor rules",
)
def run_update_cursor_rules() -> dict[str, Any]:
    """Run the update-cursor-rules Makefile task to deploy cursor rules.

    Returns:
        Dict[str, Any]: Task execution results

    """
    # This function will be implemented in a later phase
    # For now, it's a placeholder that references the original implementation
    from codegen_lab.promptlib import run_update_cursor_rules as original_run_update_cursor_rules

    return original_run_update_cursor_rules()


@mcp.tool(
    name="update_dockerignore",
    description="Update the .dockerignore file to exclude the cursor rules drafts directory",
)
def update_dockerignore() -> dict[str, Any]:
    """Update the .dockerignore file to exclude the cursor rules drafts directory.

    Returns:
        Dict[str, Any]: Update results

    """
    # This function will be implemented in a later phase
    # For now, it's a placeholder that references the original implementation
    from codegen_lab.promptlib import update_dockerignore as original_update_dockerignore

    return original_update_dockerignore()


@mcp.tool(
    name="cursor_rules_workflow",
    description="Execute the complete cursor rules workflow",
)
def cursor_rules_workflow(
    rule_names: list[str] = Field(
        description="A list of cursor rule names to create (without file extensions)",
        examples=["python-best-practices", "react-component-structure", "typescript-patterns"],
    ),
) -> dict[str, Any]:
    """Execute the complete cursor rules workflow.

    Args:
        rule_names: A list of cursor rule names to create (without file extensions)

    Returns:
        Dict[str, Any]: Workflow execution results

    """
    # This function will be implemented in a later phase
    # For now, it's a placeholder that references the original implementation
    from codegen_lab.promptlib import cursor_rules_workflow as original_cursor_rules_workflow

    return original_cursor_rules_workflow(rule_names=rule_names)
