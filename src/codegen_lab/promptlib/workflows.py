"""Workflows for cursor rules.

This module contains workflow functions for executing cursor rule tasks, including:
- plan_and_execute_prompt_library_workflow: Execute a structured workflow for cursor rule generation
- execute_phase_1: Execute the first phase of the workflow
- execute_phase_2: Execute the second phase of the workflow
- execute_phase_3: Execute the third phase of the workflow
- execute_phase_4: Execute the fourth phase of the workflow
- execute_phase_5: Execute the fifth phase of the workflow
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from pydantic import Field

if TYPE_CHECKING:
    from codegen_lab.promptlib.models import CursorRule
    from codegen_lab.promptlib.prompts import generate_cursor_rule_prompt, repo_analysis_prompt
    from codegen_lab.promptlib.tools import (
        create_cursor_rule_files,
        cursor_rules_workflow,
        ensure_ai_report,
        ensure_makefile_task,
        get_static_cursor_rule,
        get_static_cursor_rules,
        instruct_custom_repo_rules_generation,
        instruct_repo_analysis,
        prep_workspace,
        recommend_cursor_rules,
        run_update_cursor_rules,
        save_cursor_rule,
        update_dockerignore,
    )
    from codegen_lab.promptlib.utils import generate_cursor_rule, parse_cursor_rule, read_cursor_rule

from codegen_lab.promptlib import mcp

# Set up logging
logger = logging.getLogger(__name__)


@mcp.tool(
    name="plan_and_execute_prompt_library_workflow",
    description="Execute a structured workflow for generating custom cursor rules based on repository analysis",
)
def plan_and_execute_prompt_library_workflow(
    repo_description: str = Field(description="Brief description of the repository's purpose and functionality"),
    main_languages: str = Field(description="Main programming languages used in the repository (comma-separated)"),
    file_patterns: str = Field(description="Common file patterns/extensions in the repository (comma-separated)"),
    key_features: str = Field(description="Key features or functionality of the repository (comma-separated)"),
    client_repo_root: str = Field(description="Absolute path to the client's repository root directory", default=""),
    phase: int = Field(description="Current phase of the workflow (1-5)", default=1),
    workflow_state: dict[str, Any] = Field(
        description="Current state of the workflow for continuing execution", default=None
    ),
) -> dict[str, Any]:
    """Execute a structured workflow for generating custom cursor rules based on repository analysis.

    Args:
        repo_description: Brief description of the repository's purpose and functionality
        main_languages: Main programming languages used in the repository (comma-separated)
        file_patterns: Common file patterns/extensions in the repository (comma-separated)
        key_features: Key features or functionality of the repository (comma-separated)
        client_repo_root: Absolute path to the client's repository root directory
        phase: Current phase of the workflow (1-5)
        workflow_state: Current state of the workflow for continuing execution

    Returns:
        Dict[str, Any]: Workflow execution results

    """
    try:
        logger.debug(f"Starting workflow phase {phase}")
        logger.debug(f"Repository description: {repo_description}")
        logger.debug(f"Main languages: {main_languages}")
        logger.debug(f"File patterns: {file_patterns}")
        logger.debug(f"Key features: {key_features}")

        # Initialize workflow state if not provided
        if workflow_state is None:
            workflow_state = {
                "repository_info": {
                    "description": repo_description,
                    "main_languages": main_languages.split(","),
                    "file_patterns": file_patterns.split(","),
                    "key_features": key_features.split(","),
                },
                "recommended_rules": [],
                "created_rules": [],
                "deployed_rules": [],
                "workspace_prepared": False,
                "workspace_result": None,
            }

        # Execute the appropriate phase
        if phase == 1:
            return execute_phase_1(workflow_state)
        elif phase == 2:
            return execute_phase_2(workflow_state)
        elif phase == 3:
            return execute_phase_3(workflow_state)
        elif phase == 4:
            return execute_phase_4(workflow_state)
        elif phase == 5:
            return execute_phase_5(workflow_state)
        else:
            logger.error(f"Invalid workflow phase: {phase}")
            return {
                "status": "error",
                "message": f"Invalid workflow phase: {phase}",
                "workflow_state": workflow_state,
            }

    except Exception as e:
        logger.error(f"Error executing workflow phase {phase}: {e!s}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "workflow_state": workflow_state,
        }


def execute_phase_1(workflow_state: dict[str, Any]) -> dict[str, Any]:
    """Execute phase 1 of the workflow: Repository Analysis.

    Args:
        workflow_state: Current state of the workflow

    Returns:
        Dict[str, Any]: Phase 1 execution results

    """
    try:
        logger.debug("Executing workflow phase 1: Repository Analysis")

        # Run repository analysis
        analysis_result = instruct_repo_analysis()
        if not analysis_result["success"]:
            logger.error("Repository analysis failed")
            return {
                "status": "error",
                "message": "Repository analysis failed",
                "workflow_state": workflow_state,
            }

        # Update workflow state
        workflow_state["repository_analysis"] = analysis_result["repository_structure"]
        workflow_state["phase_1_complete"] = True

        logger.debug("Phase 1 completed successfully")
        return {
            "status": "complete",
            "message": "Repository analysis completed successfully",
            "workflow_state": workflow_state,
            "next_phase": 2,
        }

    except Exception as e:
        logger.error(f"Error in phase 1: {e!s}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "workflow_state": workflow_state,
        }


def execute_phase_2(workflow_state: dict[str, Any]) -> dict[str, Any]:
    """Execute phase 2 of the workflow: Rule Recommendations.

    Args:
        workflow_state: Current state of the workflow

    Returns:
        Dict[str, Any]: Phase 2 execution results

    """
    try:
        logger.debug("Executing workflow phase 2: Rule Recommendations")

        # Check if phase 1 is complete
        if not workflow_state.get("phase_1_complete"):
            logger.error("Phase 1 must be completed before executing phase 2")
            return {
                "status": "error",
                "message": "Phase 1 must be completed before executing phase 2",
                "workflow_state": workflow_state,
            }

        # Get rule recommendations
        repo_info = workflow_state["repository_info"]
        recommendations = recommend_cursor_rules(
            repo_summary=repo_info["description"],
            main_languages=repo_info["main_languages"],
            file_patterns=repo_info["file_patterns"],
            key_features=repo_info["key_features"],
        )

        if not recommendations["success"]:
            logger.error("Failed to generate rule recommendations")
            return {
                "status": "error",
                "message": "Failed to generate rule recommendations",
                "workflow_state": workflow_state,
            }

        # Update workflow state
        workflow_state["recommended_rules"] = recommendations["recommendations"]
        workflow_state["phase_2_complete"] = True

        logger.debug("Phase 2 completed successfully")
        return {
            "status": "complete",
            "message": "Rule recommendations generated successfully",
            "workflow_state": workflow_state,
            "next_phase": 3,
            "recommended_rules": recommendations["recommendations"],
        }

    except Exception as e:
        logger.error(f"Error in phase 2: {e!s}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "workflow_state": workflow_state,
        }


def execute_phase_3(workflow_state: dict[str, Any]) -> dict[str, Any]:
    """Execute phase 3 of the workflow: Workspace Preparation.

    Args:
        workflow_state: Current state of the workflow

    Returns:
        Dict[str, Any]: Phase 3 execution results

    """
    try:
        logger.debug("Executing workflow phase 3: Workspace Preparation")

        # Check if phase 2 is complete
        if not workflow_state.get("phase_2_complete"):
            logger.error("Phase 2 must be completed before executing phase 3")
            return {
                "status": "error",
                "message": "Phase 2 must be completed before executing phase 3",
                "workflow_state": workflow_state,
            }

        # Prepare workspace
        workspace_result = prep_workspace()
        if not workspace_result.get("success", False):
            logger.error("Failed to prepare workspace")
            return {
                "status": "error",
                "message": "Failed to prepare workspace",
                "workflow_state": workflow_state,
            }

        # Ensure Makefile task exists
        makefile_result = ensure_makefile_task()
        if not makefile_result.get("success", False):
            logger.error("Failed to ensure Makefile task")
            return {
                "status": "error",
                "message": "Failed to ensure Makefile task",
                "workflow_state": workflow_state,
            }

        # Update .dockerignore
        dockerignore_result = update_dockerignore()
        if not dockerignore_result.get("success", False):
            logger.error("Failed to update .dockerignore")
            return {
                "status": "error",
                "message": "Failed to update .dockerignore",
                "workflow_state": workflow_state,
            }

        # Update workflow state
        workflow_state["workspace_prepared"] = True
        workflow_state["workspace_result"] = workspace_result
        workflow_state["phase_3_complete"] = True

        logger.debug("Phase 3 completed successfully")
        return {
            "status": "complete",
            "message": "Workspace prepared successfully",
            "workflow_state": workflow_state,
            "next_phase": 4,
        }

    except Exception as e:
        logger.error(f"Error in phase 3: {e!s}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "workflow_state": workflow_state,
        }


def execute_phase_4(workflow_state: dict[str, Any]) -> dict[str, Any]:
    """Execute phase 4 of the workflow: Rule Creation.

    Args:
        workflow_state: Current state of the workflow

    Returns:
        Dict[str, Any]: Phase 4 execution results

    """
    try:
        logger.debug("Executing workflow phase 4: Rule Creation")

        # Check if phase 3 is complete
        if not workflow_state.get("phase_3_complete"):
            logger.error("Phase 3 must be completed before executing phase 4")
            return {
                "status": "error",
                "message": "Phase 3 must be completed before executing phase 4",
                "workflow_state": workflow_state,
            }

        # Get recommended rules
        recommended_rules = workflow_state.get("recommended_rules", [])
        if not recommended_rules:
            logger.error("No recommended rules found in workflow state")
            return {
                "status": "error",
                "message": "No recommended rules found in workflow state",
                "workflow_state": workflow_state,
            }

        # Create rule files
        rule_names = [rule["name"] for rule in recommended_rules]
        creation_result = create_cursor_rule_files(rule_names)
        if not creation_result.get("success", False):
            logger.error("Failed to create cursor rule files")
            return {
                "status": "error",
                "message": "Failed to create cursor rule files",
                "workflow_state": workflow_state,
            }

        # Update workflow state
        workflow_state["created_rules"] = creation_result.get("created_files", [])
        workflow_state["phase_4_complete"] = True

        logger.debug("Phase 4 completed successfully")
        return {
            "status": "complete",
            "message": "Cursor rules created successfully",
            "workflow_state": workflow_state,
            "next_phase": 5,
            "created_rules": creation_result.get("created_files", []),
        }

    except Exception as e:
        logger.error(f"Error in phase 4: {e!s}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "workflow_state": workflow_state,
        }


def execute_phase_5(workflow_state: dict[str, Any]) -> dict[str, Any]:
    """Execute phase 5 of the workflow: Rule Deployment.

    Args:
        workflow_state: Current state of the workflow

    Returns:
        Dict[str, Any]: Phase 5 execution results

    """
    try:
        logger.debug("Executing workflow phase 5: Rule Deployment")

        # Check if phase 4 is complete
        if not workflow_state.get("phase_4_complete"):
            logger.error("Phase 4 must be completed before executing phase 5")
            return {
                "status": "error",
                "message": "Phase 4 must be completed before executing phase 5",
                "workflow_state": workflow_state,
            }

        # Run update-cursor-rules task
        update_result = run_update_cursor_rules()
        if not update_result.get("success", False):
            logger.error("Failed to deploy cursor rules")
            return {
                "status": "error",
                "message": "Failed to deploy cursor rules",
                "workflow_state": workflow_state,
            }

        # Update workflow state
        workflow_state["deployed_rules"] = workflow_state.get("created_rules", [])
        workflow_state["phase_5_complete"] = True

        logger.debug("Phase 5 completed successfully")
        return {
            "status": "complete",
            "message": "Cursor rules deployed successfully",
            "workflow_state": workflow_state,
            "next_phase": None,
            "deployed_rules": workflow_state.get("created_rules", []),
        }

    except Exception as e:
        logger.error(f"Error in phase 5: {e!s}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "workflow_state": workflow_state,
        }
