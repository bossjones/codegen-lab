"""Unit tests for promptlib workflows.

This test suite verifies the behavior of cursor rule workflow functions.
"""

from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional

import pytest
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.testing import client_session

from codegen_lab.promptlib.workflows import (
    execute_phase_1,
    execute_phase_2,
    execute_phase_3,
    execute_phase_4,
    execute_phase_5,
    plan_and_execute_prompt_library_workflow,
)

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture


@pytest.fixture
def temp_workspace(tmp_path: Path) -> Path:
    """Create a temporary workspace with sample repository structure.

    Args:
        tmp_path: Pytest fixture providing a temporary directory.

    Returns:
        Path: Path to the temporary workspace.

    """
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    # Create basic repository structure
    (workspace / "src").mkdir()
    (workspace / ".cursor" / "rules").mkdir(parents=True)
    (workspace / ".github" / "workflows").mkdir(parents=True)

    # Create sample files
    (workspace / "Makefile").write_text("""
.PHONY: help
help:
    @echo "Available targets:"
    """)

    (workspace / "src" / "main.py").write_text("""
def main():
    print("Hello, World!")
    """)

    return workspace


@pytest.fixture
def mcp_server(temp_workspace: Path) -> FastMCP:
    """Create a FastMCP server instance with cursor rule workflows.

    Args:
        temp_workspace: Fixture providing a temporary workspace.

    Returns:
        FastMCP: A configured FastMCP server instance.

    """
    server = FastMCP()

    @server.tool()
    def execute_workflow(
        repo_description: str,
        main_languages: list[str],
        file_patterns: list[str],
        key_features: list[str],
        phase: int = 1,
    ) -> dict:
        """Execute the prompt library workflow."""
        return plan_and_execute_prompt_library_workflow(
            repo_description=repo_description,
            main_languages=main_languages,
            file_patterns=file_patterns,
            key_features=key_features,
            phase=phase,
        )

    return server


@pytest.mark.anyio
async def test_workflow_phase_1(
    mcp_server: FastMCP,
    temp_workspace: Path,
) -> None:
    """Test phase 1 of the prompt library workflow.

    Args:
        mcp_server: Fixture providing a configured FastMCP server.
        temp_workspace: Fixture providing a temporary workspace.

    """
    async with client_session(mcp_server._mcp_server) as client:
        result = await client.call_tool(
            "execute_workflow",
            {
                "repo_description": "A Python project with basic structure",
                "main_languages": ["python"],
                "file_patterns": ["*.py"],
                "key_features": ["basic-python"],
                "phase": 1,
            },
        )
        assert not result.isError
        workflow_state = result.content[0].text

        # Verify phase 1 results
        assert workflow_state["phase"] == 1
        assert workflow_state["status"] == "completed"
        assert "directory_structure" in workflow_state
        assert ".cursor/rules" in str(workflow_state["directory_structure"])


@pytest.mark.anyio
async def test_workflow_phase_2(
    mcp_server: FastMCP,
    temp_workspace: Path,
) -> None:
    """Test phase 2 of the prompt library workflow.

    Args:
        mcp_server: Fixture providing a configured FastMCP server.
        temp_workspace: Fixture providing a temporary workspace.

    """
    # First run phase 1
    async with client_session(mcp_server._mcp_server) as client:
        phase1_result = await client.call_tool(
            "execute_workflow",
            {
                "repo_description": "A Python project with basic structure",
                "main_languages": ["python"],
                "file_patterns": ["*.py"],
                "key_features": ["basic-python"],
                "phase": 1,
            },
        )
        assert not phase1_result.isError

        # Then run phase 2
        result = await client.call_tool(
            "execute_workflow",
            {
                "repo_description": "A Python project with basic structure",
                "main_languages": ["python"],
                "file_patterns": ["*.py"],
                "key_features": ["basic-python"],
                "phase": 2,
                "workflow_state": phase1_result.content[0].text,
            },
        )
        assert not result.isError
        workflow_state = result.content[0].text

        # Verify phase 2 results
        assert workflow_state["phase"] == 2
        assert workflow_state["status"] == "completed"
        assert "models_migrated" in workflow_state
        assert workflow_state["models_migrated"] is True


@pytest.mark.anyio
async def test_workflow_phase_3(
    mcp_server: FastMCP,
    temp_workspace: Path,
) -> None:
    """Test phase 3 of the prompt library workflow.

    Args:
        mcp_server: Fixture providing a configured FastMCP server.
        temp_workspace: Fixture providing a temporary workspace.

    """
    # Run phases 1 and 2 first
    async with client_session(mcp_server._mcp_server) as client:
        phase1_result = await client.call_tool(
            "execute_workflow",
            {
                "repo_description": "A Python project with basic structure",
                "main_languages": ["python"],
                "file_patterns": ["*.py"],
                "key_features": ["basic-python"],
                "phase": 1,
            },
        )
        assert not phase1_result.isError

        phase2_result = await client.call_tool(
            "execute_workflow",
            {
                "repo_description": "A Python project with basic structure",
                "main_languages": ["python"],
                "file_patterns": ["*.py"],
                "key_features": ["basic-python"],
                "phase": 2,
                "workflow_state": phase1_result.content[0].text,
            },
        )
        assert not phase2_result.isError

        # Then run phase 3
        result = await client.call_tool(
            "execute_workflow",
            {
                "repo_description": "A Python project with basic structure",
                "main_languages": ["python"],
                "file_patterns": ["*.py"],
                "key_features": ["basic-python"],
                "phase": 3,
                "workflow_state": phase2_result.content[0].text,
            },
        )
        assert not result.isError
        workflow_state = result.content[0].text

        # Verify phase 3 results
        assert workflow_state["phase"] == 3
        assert workflow_state["status"] == "completed"
        assert "resources_migrated" in workflow_state
        assert workflow_state["resources_migrated"] is True
        assert "tools_migrated" in workflow_state
        assert workflow_state["tools_migrated"] is True
        assert "prompts_migrated" in workflow_state
        assert workflow_state["prompts_migrated"] is True


@pytest.mark.anyio
async def test_workflow_invalid_phase(
    mcp_server: FastMCP,
    temp_workspace: Path,
) -> None:
    """Test workflow execution with invalid phase number.

    Args:
        mcp_server: Fixture providing a configured FastMCP server.
        temp_workspace: Fixture providing a temporary workspace.

    """
    async with client_session(mcp_server._mcp_server) as client:
        result = await client.call_tool(
            "execute_workflow",
            {
                "repo_description": "A Python project with basic structure",
                "main_languages": ["python"],
                "file_patterns": ["*.py"],
                "key_features": ["basic-python"],
                "phase": 99,  # Invalid phase number
            },
        )
        assert result.isError
        assert "Invalid phase" in result.error.message


@pytest.mark.anyio
async def test_workflow_missing_state(
    mcp_server: FastMCP,
    temp_workspace: Path,
) -> None:
    """Test workflow execution with missing state for non-first phase.

    Args:
        mcp_server: Fixture providing a configured FastMCP server.
        temp_workspace: Fixture providing a temporary workspace.

    """
    async with client_session(mcp_server._mcp_server) as client:
        result = await client.call_tool(
            "execute_workflow",
            {
                "repo_description": "A Python project with basic structure",
                "main_languages": ["python"],
                "file_patterns": ["*.py"],
                "key_features": ["basic-python"],
                "phase": 2,  # Phase 2 without previous state
            },
        )
        assert result.isError
        assert "Missing workflow state" in result.error.message
