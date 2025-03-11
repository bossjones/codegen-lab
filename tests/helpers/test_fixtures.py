"""Advanced pytest fixtures for testing FastMCP server implementations.

This module provides fixtures and context managers that make it easier to test
MCP tools that return file operation instructions rather than performing
operations directly.
"""

import contextlib
import os
import tempfile
from collections.abc import Callable, Generator, Iterator
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type, TypeVar, Union, cast

import pytest

from tests.helpers.file_operations import (
    FileOperation,
    apply_operations,
    cleanup_test_directory,
    setup_test_directory,
)

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture

T = TypeVar("T")


@pytest.fixture
def mcp_test_dir() -> Iterator[Path]:
    """Create a temporary directory for testing MCP file operations.

    This fixture creates a temporary directory that is automatically
    cleaned up when the test completes.

    Yields:
        Path to the temporary directory

    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mcp_test_env(mcp_test_dir: Path) -> dict[str, Any]:
    """Create a test environment with state tracking for MCP operations.

    This fixture provides a dictionary that can be used to track state
    across multiple MCP operations in a test.

    Args:
        mcp_test_dir: Temporary directory for testing

    Returns:
        Dictionary with test environment state

    """
    return {
        "base_dir": mcp_test_dir,
        "operation_history": [],
        "results": {},
    }


class MockMCPClient:
    """Mock MCP client for testing tools that return operation instructions.

    This class simulates an MCP client that applies operations and tracks results.
    It's useful for testing the complete flow of MCP tools.

    Attributes:
        base_dir: Directory where operations will be applied
        operation_history: List of all operations applied
        last_result: Result of the last operation

    """

    def __init__(self, base_dir: str | Path) -> None:
        """Initialize the mock client.

        Args:
            base_dir: Directory where operations will be applied

        """
        self.base_dir = Path(base_dir)
        self.operation_history: list[FileOperation] = []
        self.last_result: dict[str, Any] | None = None

    def apply_tool_result(self, result: dict[str, Any]) -> dict[str, Any]:
        """Apply operations from a tool result and return the results.

        Args:
            result: Tool result dictionary with operations

        Returns:
            Results of applying the operations

        """
        if result.get("isError"):
            # Return error result without applying operations
            return result

        operations = result.get("operations", [])
        if not operations:
            return result

        # Track operations
        self.operation_history.extend(operations)

        # Apply operations
        operation_results = apply_operations(operations, self.base_dir)

        # Store results
        self.last_result = operation_results

        if result.get("requires_result", False):
            return operation_results
        else:
            return {"success": True, "message": result.get("message", "")}

    def call_tool(self, tool_func: Callable[..., dict[str, Any]], **kwargs: Any) -> dict[str, Any]:
        """Call an MCP tool and apply its operations.

        Args:
            tool_func: MCP tool function to call
            **kwargs: Arguments to pass to the tool

        Returns:
            Results of applying the operations

        """
        # Call the tool
        result = tool_func(**kwargs)

        # Apply operations
        return self.apply_tool_result(result)


@pytest.fixture
def mock_mcp_client(mcp_test_dir: Path) -> MockMCPClient:
    """Create a mock MCP client for testing.

    Args:
        mcp_test_dir: Temporary directory for testing

    Returns:
        MockMCPClient instance

    """
    return MockMCPClient(mcp_test_dir)


@contextlib.contextmanager
def temp_mcp_environment(initial_files: dict[str, str] | None = None) -> Generator[dict[str, Any], None, None]:
    """Context manager that creates a temporary environment for MCP testing.

    Args:
        initial_files: Dictionary mapping file paths to their contents

    Yields:
        Dictionary with test environment state

    """
    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)

        # Set up initial files if provided
        if initial_files:
            setup_test_directory(base_dir, initial_files)

        # Create environment state
        env = {
            "base_dir": base_dir,
            "client": MockMCPClient(base_dir),
            "operation_history": [],
            "results": {},
        }

        try:
            yield env
        finally:
            # Cleanup will happen automatically when the context exits
            pass


def assert_file_exists(base_dir: Path, file_path: str) -> None:
    """Assert that a file exists in the given directory.

    Args:
        base_dir: Base directory
        file_path: Path to file, relative to base_dir

    """
    full_path = base_dir / file_path
    assert full_path.exists(), f"File does not exist: {file_path}"
    assert full_path.is_file(), f"Path exists but is not a file: {file_path}"


def assert_dir_exists(base_dir: Path, dir_path: str) -> None:
    """Assert that a directory exists in the given directory.

    Args:
        base_dir: Base directory
        dir_path: Path to directory, relative to base_dir

    """
    full_path = base_dir / dir_path
    assert full_path.exists(), f"Directory does not exist: {dir_path}"
    assert full_path.is_dir(), f"Path exists but is not a directory: {dir_path}"


def assert_file_content(base_dir: Path, file_path: str, expected_content: str) -> None:
    """Assert that a file exists and has the expected content.

    Args:
        base_dir: Base directory
        file_path: Path to file, relative to base_dir
        expected_content: Expected file content

    """
    full_path = base_dir / file_path
    assert_file_exists(base_dir, file_path)

    with open(full_path, encoding="utf-8") as f:
        content = f.read()

    assert content == expected_content, f"File content does not match expected: {file_path}"
