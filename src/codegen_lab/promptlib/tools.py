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

        # Get the current working directory
        cwd = os.getcwd()
        logger.debug(f"Running analysis in directory: {cwd}")

        # Determine the directory for saving results
        ai_dir = os.path.join(cwd, "ai_docs")
        os.makedirs(ai_dir, exist_ok=True)
        report_path = os.path.join(ai_dir, "ai_report.md")

        # Execute the analysis script
        logger.debug("Executing repository analysis script")
        result = subprocess.run(
            ["python", "-m", "codegen_lab.repo_analyzer"], capture_output=True, text=True, check=True
        )

        if result.returncode != 0:
            logger.error(f"Repository analysis failed with error: {result.stderr}")
            return {
                "success": False,
                "error": "Repository analysis failed",
                "message": result.stderr,
            }

        # Check if the report was generated
        if not os.path.exists(report_path):
            logger.warning(f"Repository analysis did not generate a report at {report_path}")
            return {
                "success": False,
                "error": "Report not generated",
                "message": f"Repository analysis did not generate a report at {report_path}",
            }

        logger.debug(f"Repository analysis completed successfully, report saved to {report_path}")
        return {
            "success": True,
            "message": "Repository analysis completed successfully",
            "report_path": report_path,
            "output": result.stdout,
        }
    except subprocess.CalledProcessError as e:
        logger.error(f"Repository analysis failed with error: {e.stderr}")
        return {
            "success": False,
            "error": "Repository analysis failed",
            "message": e.stderr,
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

    This tool analyzes a repository summary and recommends cursor rules that
    would be useful for that repository, based on the technologies, frameworks,
    and key features mentioned in the summary.

    Args:
        repo_summary: A summary description of the repository, including technologies,
            frameworks, and key features

    Returns:
        Union[List[Dict[str, Union[str, List[str]]]], Dict[str, Union[bool, List[Dict[str, str]]]]]:
            Recommendations for cursor rules, or an error message if the analysis fails.

    """
    try:
        logger.debug(f"Analyzing repository summary: {repo_summary[:100]}...")

        # Get the available cursor rule templates
        templates_dir = Path(
            os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../hack/static/cursor_rules"))
        )
        template_files = list(templates_dir.glob("*.mdc.md"))

        if not template_files:
            logger.warning("No template cursor rules found")
            return {
                "success": False,
                "error": "No template cursor rules found",
                "message": f"No template cursor rules found in {templates_dir}",
            }

        # Extract rule names from template files
        template_names = [file.stem.replace(".mdc", "") for file in template_files]
        logger.debug(f"Found {len(template_names)} template cursor rules")

        # Simplified matching logic: match repository summary against rule names and descriptions
        repo_summary_lower = repo_summary.lower()
        matched_rules = []

        # Common technology categories
        technology_categories = {
            "python": ["python", "django", "flask", "fastapi", "sqlalchemy", "pytest", "pip", "conda"],
            "javascript": ["javascript", "js", "react", "vue", "angular", "node", "npm", "yarn", "webpack", "babel"],
            "typescript": ["typescript", "ts", "tsc", "tsconfig"],
            "testing": ["test", "pytest", "jest", "mocha", "chai", "unittest", "integration test"],
            "database": ["sql", "database", "orm", "mongodb", "postgresql", "mysql", "sqlite"],
            "documentation": ["documentation", "docs", "sphinx", "docstring", "jsdoc", "readme"],
            "git": ["git", "github", "gitlab", "bitbucket", "version control"],
            "ci_cd": [
                "ci",
                "cd",
                "continuous integration",
                "continuous delivery",
                "github actions",
                "jenkins",
                "travis",
            ],
            "docker": ["docker", "container", "containerization", "dockerfile", "docker-compose"],
            "code_quality": ["linting", "linter", "ruff", "eslint", "prettier", "black", "isort"],
        }

        # Match categories mentioned in the repo summary
        matched_categories = []
        for category, keywords in technology_categories.items():
            if any(keyword in repo_summary_lower for keyword in keywords):
                matched_categories.append(category)

        logger.debug(f"Matched technology categories: {matched_categories}")

        # Define cursor rule recommendations based on matched categories
        recommendations = []

        if "python" in matched_categories:
            if "testing" in matched_categories:
                recommendations.append(
                    {
                        "name": "python-tdd-basics",
                        "description": "Test-Driven Development basics for Python",
                        "relevance": "Python testing best practices",
                        "tags": ["python", "testing", "tdd"],
                    }
                )
                recommendations.append(
                    {
                        "name": "pytest-loop",
                        "description": "Quality assurance with pytest for every code edit",
                        "relevance": "Ensures good test coverage for Python code",
                        "tags": ["python", "testing", "pytest"],
                    }
                )

            if "code_quality" in matched_categories:
                recommendations.append(
                    {
                        "name": "ruff",
                        "description": "Ruff linting configuration and usage guidelines",
                        "relevance": "Ensures code quality with the Ruff linter",
                        "tags": ["python", "linting", "code quality"],
                    }
                )

            recommendations.append(
                {
                    "name": "python-refactor",
                    "description": "Python refactoring and modularization guidelines with TDD",
                    "relevance": "Helps maintain clean code architecture",
                    "tags": ["python", "refactoring", "architecture"],
                }
            )

        if "javascript" in matched_categories or "typescript" in matched_categories:
            recommendations.append(
                {
                    "name": "js-best-practices",
                    "description": "JavaScript/TypeScript best practices",
                    "relevance": "Provides guidance for JavaScript/TypeScript development",
                    "tags": ["javascript", "typescript", "best practices"],
                }
            )

        if "documentation" in matched_categories:
            recommendations.append(
                {
                    "name": "documentation-standards",
                    "description": "Documentation standards for code and project documentation",
                    "relevance": "Helps maintain consistent documentation",
                    "tags": ["documentation", "docs", "standards"],
                }
            )

        if "git" in matched_categories:
            recommendations.append(
                {
                    "name": "git-workflow",
                    "description": "Git workflow and branch management guidelines",
                    "relevance": "Establishes good practices for version control",
                    "tags": ["git", "workflow", "branching"],
                }
            )

        if "ci_cd" in matched_categories:
            recommendations.append(
                {
                    "name": "gh-action-security",
                    "description": "Security guidelines for GitHub Actions workflows",
                    "relevance": "Helps secure CI/CD pipelines in GitHub Actions",
                    "tags": ["github", "actions", "security", "ci/cd"],
                }
            )

        if "docker" in matched_categories:
            recommendations.append(
                {
                    "name": "docker-best-practices",
                    "description": "Docker best practices for containerization",
                    "relevance": "Provides guidance for Docker container setup",
                    "tags": ["docker", "containers", "best practices"],
                }
            )

        # If no specific categories matched, provide general recommendations
        if not recommendations:
            logger.debug("No specific categories matched, providing general recommendations")
            recommendations = [
                {
                    "name": "code-organization",
                    "description": "General code organization and architecture principles",
                    "relevance": "Provides guidance for any codebase",
                    "tags": ["architecture", "organization", "best practices"],
                },
                {
                    "name": "documentation-standards",
                    "description": "Documentation standards for code and project documentation",
                    "relevance": "Helps maintain consistent documentation",
                    "tags": ["documentation", "docs", "standards"],
                },
                {
                    "name": "explain-code-modification",
                    "description": "Guidelines for explaining code modifications and changes",
                    "relevance": "Helps ensure clear communication about code changes",
                    "tags": ["code changes", "documentation", "communication"],
                },
            ]

        # Limit to a reasonable number of recommendations
        recommendations = recommendations[:5]

        logger.debug(f"Generated {len(recommendations)} cursor rule recommendations")
        return recommendations
    except Exception as e:
        logger.error(f"Error generating cursor rule recommendations: {e!s}", exc_info=True)
        return {
            "success": False,
            "error": "Error generating recommendations",
            "message": str(e),
        }


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
