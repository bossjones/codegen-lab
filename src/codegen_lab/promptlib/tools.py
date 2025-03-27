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

Migration Plan for tools.py:
- [x] Import all necessary dependencies
- [x] Update type imports to use models and utils modules
- [ ] Group tools by functionality:
  - [x] Analysis tools:
    - [x] Implement instruct_repo_analysis
    - [x] Implement recommend_cursor_rules
  - [ ] Generation tools:
    - [ ] Implement instruct_custom_repo_rules_generation
    - [ ] Implement get_static_cursor_rule
    - [ ] Implement get_static_cursor_rules
    - [ ] Implement save_cursor_rule
  - [ ] Workspace preparation tools:
    - [ ] Implement prep_workspace
    - [ ] Implement create_cursor_rule_files
    - [ ] Implement ensure_makefile_task
    - [ ] Implement ensure_ai_report
    - [ ] Implement run_update_cursor_rules
    - [ ] Implement update_dockerignore
  - [ ] Workflow tools:
    - [ ] Implement cursor_rules_workflow
- [ ] Add proper error handling for each tool
- [ ] Add comprehensive logging for debugging
- [ ] Update type hints and docstrings
- [ ] Update __init__.py to re-export tools
- [ ] Verify functionality through manual testing
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union, cast

from pydantic import Field

if TYPE_CHECKING:
    from codegen_lab.promptlib.models import CursorRule
    from codegen_lab.promptlib.utils import generate_cursor_rule, parse_cursor_rule, read_cursor_rule

from codegen_lab.promptlib import mcp

# Set up logging
logger = logging.getLogger(__name__)

#
# Analysis Tools
#


@mcp.tool(
    name="instruct_repo_analysis",
    description="Run a repository analysis to gather information for cursor rule creation",
)
def instruct_repo_analysis() -> dict[str, Any]:
    """Run a repository analysis to gather information for cursor rule creation.

    This tool executes a script that analyzes the repository structure and
    generates a report with information that can be used to create cursor rules.

    Returns:
        Dict[str, Any]: Repository analysis results, or an error message if the analysis fails.

    """
    try:
        logger.debug("Starting repository analysis")

        # Get current working directory
        repo_root = Path.cwd()
        logger.debug(f"Repository root: {repo_root}")

        # Analyze repository structure
        repo_structure = {}

        # Get Python files
        python_files = list(repo_root.glob("**/*.py"))
        repo_structure["python_files"] = [str(f.relative_to(repo_root)) for f in python_files]

        # Get test files
        test_files = list(repo_root.glob("**/test_*.py"))
        repo_structure["test_files"] = [str(f.relative_to(repo_root)) for f in test_files]

        # Get configuration files
        config_files = []
        config_patterns = ["*.json", "*.yaml", "*.yml", "*.toml", "*.ini", "*.cfg"]
        for pattern in config_patterns:
            config_files.extend(repo_root.glob(f"**/{pattern}"))
        repo_structure["config_files"] = [str(f.relative_to(repo_root)) for f in config_files]

        # Get documentation files
        doc_files = []
        doc_patterns = ["*.md", "*.rst", "*.txt"]
        for pattern in doc_patterns:
            doc_files.extend(repo_root.glob(f"**/{pattern}"))
        repo_structure["doc_files"] = [str(f.relative_to(repo_root)) for f in doc_files]

        # Get directory structure
        def get_dir_structure(path: Path, max_depth: int = 3) -> dict[str, Any]:
            if max_depth <= 0:
                return {"type": "dir", "truncated": True}

            result = {"type": "dir", "contents": {}}
            try:
                for item in path.iterdir():
                    if item.name.startswith(".") or item.name == "__pycache__":
                        continue
                    if item.is_dir():
                        result["contents"][item.name] = get_dir_structure(item, max_depth - 1)
                    else:
                        result["contents"][item.name] = {"type": "file"}
            except PermissionError:
                result["error"] = "Permission denied"
            return result

        repo_structure["directory_structure"] = get_dir_structure(repo_root)

        # Get git information if available
        try:
            # Get current branch
            branch = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True, stderr=subprocess.PIPE
            ).strip()
            repo_structure["git_branch"] = branch

            # Get recent commits
            commits = subprocess.check_output(
                ["git", "log", "--oneline", "-n", "5"], text=True, stderr=subprocess.PIPE
            ).strip()
            repo_structure["recent_commits"] = commits.split("\n")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.debug("Git information not available")
            repo_structure["git_info"] = "Not available"

        # Get package dependencies
        dependencies = {}

        # Check for requirements.txt
        req_file = repo_root / "requirements.txt"
        if req_file.exists():
            dependencies["requirements.txt"] = req_file.read_text().strip().split("\n")

        # Check for pyproject.toml
        pyproject_file = repo_root / "pyproject.toml"
        if pyproject_file.exists():
            dependencies["pyproject.toml"] = "Present"

        # Check for setup.py
        setup_file = repo_root / "setup.py"
        if setup_file.exists():
            dependencies["setup.py"] = "Present"

        repo_structure["dependencies"] = dependencies

        logger.debug("Repository analysis completed successfully")
        return {
            "success": True,
            "repository_structure": repo_structure,
            "message": "Repository analysis completed successfully",
        }

    except Exception as e:
        logger.error(f"Error during repository analysis: {e!s}", exc_info=True)
        return {
            "success": False,
            "error": "Error during repository analysis",
            "message": str(e),
        }


@mcp.tool(
    name="recommend_cursor_rules",
    description="Recommend cursor rules based on repository analysis",
)
def recommend_cursor_rules(
    repo_summary: str = Field(
        description="Summary of the repository's purpose and structure",
        examples=["A Python web application using FastAPI and SQLAlchemy"],
    ),
    main_languages: list[str] = Field(
        description="List of main programming languages used in the repository",
        examples=[["python", "typescript"], ["python"]],
        default=["python"],
    ),
    file_patterns: list[str] = Field(
        description="List of common file patterns in the repository",
        examples=[["*.py", "*.ts"], ["*.py"]],
        default=["*.py"],
    ),
    key_features: list[str] = Field(
        description="List of key features or functionality in the repository",
        examples=[["web-api", "database"], ["cli-tool"]],
        default=[],
    ),
) -> dict[str, Any]:
    """Recommend cursor rules based on repository analysis.

    Args:
        repo_summary: Summary of the repository's purpose and structure
        main_languages: List of main programming languages used
        file_patterns: List of common file patterns
        key_features: List of key features or functionality

    Returns:
        Dict[str, Any]: Recommended cursor rules and their priorities

    """
    try:
        logger.debug("Starting cursor rule recommendations")
        logger.debug(f"Repository summary: {repo_summary}")
        logger.debug(f"Main languages: {main_languages}")
        logger.debug(f"File patterns: {file_patterns}")
        logger.debug(f"Key features: {key_features}")

        # Initialize recommendations
        recommendations = []

        # Helper function to add a recommendation
        def add_recommendation(name: str, category: str, priority: str, description: str) -> None:
            recommendations.append(
                {"name": name, "category": category, "priority": priority, "description": description}
            )

        # Recommend language-specific rules
        for lang in main_languages:
            if lang.lower() == "python":
                add_recommendation(
                    "python-best-practices",
                    "Language",
                    "high",
                    "Best practices for Python development including type hints, docstrings, and PEP 8",
                )
                add_recommendation(
                    "python-imports", "Style", "medium", "Guidelines for organizing and formatting Python imports"
                )
                add_recommendation(
                    "python-testing", "Testing", "high", "Best practices for Python testing using pytest"
                )
            elif lang.lower() == "typescript":
                add_recommendation(
                    "typescript-patterns", "Language", "high", "TypeScript best practices and common patterns"
                )

        # Recommend feature-specific rules
        for feature in key_features:
            if "api" in feature.lower():
                add_recommendation(
                    "api-design", "Architecture", "high", "Guidelines for designing consistent and maintainable APIs"
                )
            if "database" in feature.lower():
                add_recommendation(
                    "database-patterns",
                    "Architecture",
                    "high",
                    "Best practices for database interactions and ORM usage",
                )
            if "cli" in feature.lower():
                add_recommendation(
                    "cli-design",
                    "Architecture",
                    "medium",
                    "Guidelines for designing user-friendly command-line interfaces",
                )

        # Recommend general development rules
        add_recommendation(
            "code-documentation", "Documentation", "high", "Standards for code documentation and inline comments"
        )
        add_recommendation(
            "error-handling", "Best Practices", "high", "Guidelines for consistent error handling and logging"
        )
        add_recommendation(
            "security-practices", "Security", "high", "Security best practices and common vulnerability prevention"
        )

        # Check file patterns for specific recommendations
        for pattern in file_patterns:
            if "test" in pattern.lower():
                add_recommendation(
                    "test-organization", "Testing", "medium", "Guidelines for organizing and structuring tests"
                )
            if "docker" in pattern.lower():
                add_recommendation(
                    "docker-best-practices",
                    "DevOps",
                    "high",
                    "Best practices for Dockerfile creation and container configuration",
                )

        logger.debug(f"Generated {len(recommendations)} recommendations")
        return {
            "success": True,
            "recommendations": recommendations,
            "message": f"Generated {len(recommendations)} cursor rule recommendations",
        }

    except Exception as e:
        logger.error(f"Error generating recommendations: {e!s}", exc_info=True)
        return {"success": False, "error": "Failed to generate recommendations", "message": str(e)}


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
