"""Tests for different types of file operations in FastMCP.

This module demonstrates how to use parameterized tests to verify
that different types of file operations work correctly.
"""

from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, cast

import pytest

from tests.helpers.file_operations import FileOperation, apply_operations
from tests.helpers.test_fixtures import (
    MockMCPClient,
    assert_dir_exists,
    assert_file_content,
    assert_file_exists,
    mcp_test_dir,
    mock_mcp_client,
)

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture


# Sample MCP tool functions that return file operations
def create_project_structure(project_name: str) -> dict[str, Any]:
    """Create a standard project structure.

    Args:
        project_name: Name of the project

    Returns:
        Dictionary with operations to create the project structure

    """
    return {
        "operations": [
            {
                "type": "create_directory",
                "path": f"{project_name}",
                "content": None,
                "args": None,
                "kwargs": {"parents": True, "exist_ok": True},
            },
            {
                "type": "create_directory",
                "path": f"{project_name}/src",
                "content": None,
                "args": None,
                "kwargs": {"parents": True, "exist_ok": True},
            },
            {
                "type": "create_directory",
                "path": f"{project_name}/tests",
                "content": None,
                "args": None,
                "kwargs": {"parents": True, "exist_ok": True},
            },
            {
                "type": "write_file",
                "path": f"{project_name}/README.md",
                "content": f"# {project_name}\n\nA sample project.",
                "args": None,
                "kwargs": None,
            },
            {
                "type": "write_file",
                "path": f"{project_name}/src/__init__.py",
                "content": "",
                "args": None,
                "kwargs": None,
            },
            {
                "type": "write_file",
                "path": f"{project_name}/tests/__init__.py",
                "content": "",
                "args": None,
                "kwargs": None,
            },
        ],
        "message": f"Created project structure for {project_name}",
    }


def read_file_contents(file_path: str) -> dict[str, Any]:
    """Read the contents of a file.

    Args:
        file_path: Path to the file

    Returns:
        Dictionary with operations to read the file

    """
    return {
        "operations": [
            {
                "type": "check_file_exists",
                "path": file_path,
                "content": None,
                "args": None,
                "kwargs": None,
            },
            {
                "type": "read_file",
                "path": file_path,
                "content": None,
                "args": None,
                "kwargs": {"encoding": "utf-8"},
            },
        ],
        "requires_result": True,
        "message": f"Instructions to read file {file_path}",
    }


@pytest.mark.parametrize(
    "operation_type,params,expected",
    [
        ("create_directory", {"path": "test_dir"}, {"exists": True, "is_dir": True}),
        (
            "write_file",
            {"path": "test.txt", "content": "Hello, world!"},
            {"exists": True, "is_file": True, "content": "Hello, world!"},
        ),
        ("check_file_exists", {"path": "non_existent.txt"}, {"exists": False}),
    ],
)
def test_apply_operations_by_type(operation_type: str, params: dict[str, Any], expected: dict[str, Any]) -> None:
    """Test applying different types of operations.

    Args:
        operation_type: Type of operation to test
        params: Parameters for the operation
        expected: Expected results from the operation

    """
    # Create the operation
    operation: FileOperation = {
        "type": cast(Any, operation_type),
        "path": params["path"],
        "content": params.get("content"),
        "args": None,
        "kwargs": None,
    }

    # For write_file operations, create parent directories if needed
    if operation_type == "write_file":
        file_path = Path(params["path"])
        if len(file_path.parts) > 1:
            dir_path = str(file_path.parent)
            dir_op: FileOperation = {
                "type": "create_directory",
                "path": dir_path,
                "content": None,
                "args": None,
                "kwargs": None,
            }
            apply_operations([dir_op], mcp_test_dir)

    # Apply the operation
    results = apply_operations([operation], mcp_test_dir)

    # Verify results based on expected outcomes
    if expected.get("exists", True):
        if expected.get("is_dir", False):
            assert_dir_exists(mcp_test_dir, params["path"])
        elif expected.get("is_file", False):
            assert_file_exists(mcp_test_dir, params["path"])

            if "content" in expected:
                assert_file_content(mcp_test_dir, params["path"], expected["content"])
    else:
        # If not expected to exist, verify it doesn't
        assert not (mcp_test_dir / params["path"]).exists()


def test_project_structure_creation() -> None:
    """Test creating a project structure using the mock client."""
    # Call the tool via the mock client
    project_name = "sample_project"
    result = mock_mcp_client.call_tool(create_project_structure, project_name=project_name)

    # Verify the result
    assert result["success"] is True

    # Verify the project structure was created
    base_dir = mock_mcp_client.base_dir
    assert_dir_exists(base_dir, project_name)
    assert_dir_exists(base_dir, f"{project_name}/src")
    assert_dir_exists(base_dir, f"{project_name}/tests")
    assert_file_exists(base_dir, f"{project_name}/README.md")
    assert_file_exists(base_dir, f"{project_name}/src/__init__.py")
    assert_file_exists(base_dir, f"{project_name}/tests/__init__.py")

    # Verify README content
    assert_file_content(base_dir, f"{project_name}/README.md", f"# {project_name}\n\nA sample project.")


def test_file_reading() -> None:
    """Test reading a file using the mock client."""
    # Create a file to read
    file_path = "test_file.txt"
    file_content = "This is a test file."

    # Write the file directly
    with open(mock_mcp_client.base_dir / file_path, "w", encoding="utf-8") as f:
        f.write(file_content)

    # Call the tool via the mock client
    result = mock_mcp_client.call_tool(read_file_contents, file_path=file_path)

    # Verify the result
    assert file_path in result
    assert result[file_path]["type"] == "file_read"
    assert result[file_path]["content"] == file_content

    # Test reading a non-existent file
    non_existent = "non_existent.txt"
    result = mock_mcp_client.call_tool(read_file_contents, file_path=non_existent)

    # Verify the result
    assert non_existent in result
    assert result[non_existent]["type"] == "file_exists"
    assert result[non_existent]["exists"] is False
