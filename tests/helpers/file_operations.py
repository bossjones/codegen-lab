"""Helpers for testing file operations in FastMCP server implementations.

This module provides utilities to simulate file operations in tests without
actually performing them on the filesystem, making it easier to test MCP
tools that return file operation instructions.
"""

import json
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, TypedDict, Union, cast


class FileOperation(TypedDict):
    """TypedDict representing a file operation instruction."""

    type: Literal["create_directory", "write_file", "read_file", "execute_command", "check_file_exists"]
    path: str
    content: str | None
    args: list[str] | None
    kwargs: dict[str, Any] | None


def apply_operations(operations: list[FileOperation], base_dir: str | Path) -> dict[str, Any]:
    """Apply a list of file operations in a given directory.

    This function simulates the execution of file operations that would normally be
    performed by an MCP client. It's useful for testing MCP tools that return
    operation instructions rather than performing operations directly.

    Args:
        operations: List of file operation instructions to apply
        base_dir: Base directory where operations should be applied

    Returns:
        Dict containing results of operations, such as file contents for read operations

    """
    results: dict[str, Any] = {}
    base_dir = Path(base_dir)

    for op in operations:
        op_type = op["type"]
        path = base_dir / op["path"]

        if op_type == "create_directory":
            os.makedirs(path, exist_ok=True)
            results[op["path"]] = {"success": True}

        elif op_type == "write_file":
            # Ensure parent directory exists
            os.makedirs(path.parent, exist_ok=True)
            content = op.get("content", "")
            with open(path, "w", encoding="utf-8") as f:
                f.write(content if content is not None else "")
            results[op["path"]] = {"success": True}

        elif op_type == "read_file":
            if path.exists():
                with open(path, encoding="utf-8") as f:
                    content = f.read()
                results[op["path"]] = {"success": True, "content": content}
            else:
                results[op["path"]] = {"success": False, "error": "File not found"}

        elif op_type == "check_file_exists":
            results[op["path"]] = {"exists": path.exists()}

        elif op_type == "execute_command":
            # For testing purposes, we just record the command rather than executing it
            args = op.get("args", [])
            kwargs = op.get("kwargs", {})
            results[f"command_{len(results)}"] = {
                "command": args[0] if args else "",
                "args": args[1:] if len(args) > 1 else [],
                "kwargs": kwargs,
                "cwd": str(path),
            }

    return results


def setup_test_directory(base_dir: str | Path, initial_files: dict[str, str]) -> None:
    """Set up a test directory with initial files.

    Args:
        base_dir: Directory to set up
        initial_files: Dictionary mapping file paths to their contents

    """
    base_dir = Path(base_dir)

    # Create base directory if it doesn't exist
    os.makedirs(base_dir, exist_ok=True)

    # Create initial files
    for file_path, content in initial_files.items():
        full_path = base_dir / file_path
        os.makedirs(full_path.parent, exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)


def cleanup_test_directory(base_dir: str | Path) -> None:
    """Clean up a test directory by removing it and all its contents.

    Args:
        base_dir: Directory to clean up

    """
    base_dir = Path(base_dir)
    if base_dir.exists():
        shutil.rmtree(base_dir)


def assert_file_operations(operations: list[FileOperation], expected_patterns: list[dict[str, Any]]) -> None:
    """Assert that file operations match expected patterns.

    Args:
        operations: List of file operations to check
        expected_patterns: List of patterns to match against operations

    """
    for pattern in expected_patterns:
        pattern_type = pattern.get("type")
        pattern_path = pattern.get("path")

        # Find matching operations
        matches = [
            op
            for op in operations
            if (pattern_type is None or op["type"] == pattern_type)
            and (pattern_path is None or op["path"] == pattern_path)
        ]

        assert matches, f"No operations match pattern: {pattern}"

        # Check content if specified in pattern
        if "content" in pattern:
            content_matches = [
                op for op in matches if "content" in op and pattern["content"] in cast(str, op.get("content", ""))
            ]
            assert content_matches, f"No operations with matching content for pattern: {pattern}"
