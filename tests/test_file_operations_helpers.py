"""Tests for the file operations helpers module."""
# pyright: reportMissingImports=false
# pyright: reportUnusedVariable=warning
# pyright: reportUntypedBaseClass=error
# pyright: reportGeneralTypeIssues=false
# pyright: reportAttributeAccessIssue=false

import os
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List

import pytest

from tests.helpers.file_operations import (
    FileOperation,
    apply_operations,
    assert_file_operations,
    cleanup_test_directory,
    setup_test_directory,
)

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture


@pytest.fixture
def test_dir() -> Path:
    """Create a temporary directory for testing.

    Returns:
        Path to the temporary directory

    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def test_apply_operations(test_dir: Path) -> None:
    """Test that apply_operations correctly simulates file operations.

    Args:
        test_dir: Temporary directory for testing

    """
    # Define operations
    operations: list[FileOperation] = [
        {
            "type": "create_directory",
            "path": "project/src",
            "content": None,
            "args": None,
            "kwargs": None,
        },
        {
            "type": "write_file",
            "path": "project/src/main.py",
            "content": "print('Hello, world!')",
            "args": None,
            "kwargs": None,
        },
        {
            "type": "check_file_exists",
            "path": "project/src/main.py",
            "content": None,
            "args": None,
            "kwargs": None,
        },
    ]

    # Apply operations
    results = apply_operations(operations, test_dir)

    # Verify results
    assert results["project/src"]["success"] is True
    assert results["project/src/main.py"]["success"] is True

    # Verify the check_file_exists result
    file_exists_result = results.get("project/src/main.py")
    assert file_exists_result is not None
    assert file_exists_result.get("type") == "file_exists"
    assert file_exists_result.get("exists") is True

    # Verify files were actually created
    assert (test_dir / "project" / "src").is_dir()
    assert (test_dir / "project" / "src" / "main.py").is_file()

    # Verify file content
    with open(test_dir / "project" / "src" / "main.py") as f:
        content = f.read()
    assert content == "print('Hello, world!')"


def test_setup_and_cleanup_test_directory(test_dir: Path) -> None:
    """Test setup_test_directory and cleanup_test_directory functions.

    Args:
        test_dir: Temporary directory for testing

    """
    # Initial files to create
    initial_files: dict[str, str] = {"config.json": '{"name": "test"}', "src/main.py": "print('Hello')"}

    # Set up directory
    setup_test_directory(test_dir, initial_files)

    # Verify files were created
    assert (test_dir / "config.json").is_file()
    assert (test_dir / "src" / "main.py").is_file()

    # Check content
    with open(test_dir / "config.json") as f:
        assert f.read() == '{"name": "test"}'

    with open(test_dir / "src" / "main.py") as f:
        assert f.read() == "print('Hello')"

    # Clean up
    cleanup_test_directory(test_dir)

    # Verify directory was removed
    assert not (test_dir / "config.json").exists()
    assert not (test_dir / "src").exists()


def test_assert_file_operations() -> None:
    """Test that assert_file_operations correctly checks operations against patterns."""
    operations: list[FileOperation] = [
        {
            "type": "write_file",
            "path": "project/src/main.py",
            "content": "print('Hello, world!')",
            "args": None,
            "kwargs": None,
        },
        {
            "type": "write_file",
            "path": "project/README.md",
            "content": "# Project\nThis is a test project.",
            "args": None,
            "kwargs": None,
        },
    ]

    # Valid patterns
    patterns: list[dict[str, Any]] = [
        {"type": "write_file", "path": "project/src/main.py"},
        {"type": "write_file", "content": "# Project"},
    ]

    # This should not raise an assertion error
    assert_file_operations(operations, patterns)

    # Invalid pattern
    with pytest.raises(AssertionError):
        assert_file_operations(operations, [{"type": "read_file"}])
