"""Unit tests for promptlib utilities.

This test suite verifies the behavior of utility functions for cursor rule operations.
"""

import os
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional

import pytest

from codegen_lab.promptlib.utils import (
    generate_cursor_rule,
    get_cursor_rule_files,
    get_cursor_rule_names,
    parse_cursor_rule,
    read_cursor_rule,
)

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture


@pytest.fixture
def temp_rules_dir(tmp_path: Path) -> Path:
    """Create a temporary directory with sample cursor rules.

    Args:
        tmp_path: Pytest fixture providing a temporary directory.

    Returns:
        Path: Path to the temporary rules directory.

    """
    rules_dir = tmp_path / ".cursor" / "rules"
    rules_dir.mkdir(parents=True)

    # Create sample rule files
    rule1 = rules_dir / "python-best-practices.mdc"
    rule2 = rules_dir / "typescript-patterns.mdc"

    rule1.write_text("""# Python Best Practices

<rule>
name: python-best-practices
description: Enforces Python best practices
filters:
  - type: file_extension
    pattern: \\.py$
actions:
  - type: suggest
    message: Follow Python best practices
</rule>
""")

    rule2.write_text("""# TypeScript Patterns

<rule>
name: typescript-patterns
description: TypeScript design patterns
filters:
  - type: file_extension
    pattern: \\.ts$
actions:
  - type: suggest
    message: Follow TypeScript patterns
</rule>
""")

    return rules_dir


def test_get_cursor_rule_files(temp_rules_dir: Path) -> None:
    """Test getting cursor rule files from a directory.

    Args:
        temp_rules_dir: Fixture providing a temporary rules directory.

    """
    rule_files = get_cursor_rule_files(temp_rules_dir)
    assert len(rule_files) == 2
    assert any(f.name == "python-best-practices.mdc" for f in rule_files)
    assert any(f.name == "typescript-patterns.mdc" for f in rule_files)


def test_get_cursor_rule_names(temp_rules_dir: Path) -> None:
    """Test getting cursor rule names from a directory.

    Args:
        temp_rules_dir: Fixture providing a temporary rules directory.

    """
    rule_names = get_cursor_rule_names(temp_rules_dir)
    assert len(rule_names) == 2
    assert "python-best-practices" in rule_names
    assert "typescript-patterns" in rule_names


def test_read_cursor_rule(temp_rules_dir: Path) -> None:
    """Test reading a cursor rule from a file.

    Args:
        temp_rules_dir: Fixture providing a temporary rules directory.

    """
    rule_content = read_cursor_rule(temp_rules_dir / "python-best-practices.mdc")
    assert "# Python Best Practices" in rule_content
    assert "<rule>" in rule_content
    assert "name: python-best-practices" in rule_content


def test_parse_cursor_rule(temp_rules_dir: Path) -> None:
    """Test parsing a cursor rule from content.

    Args:
        temp_rules_dir: Fixture providing a temporary rules directory.

    """
    rule_content = read_cursor_rule(temp_rules_dir / "python-best-practices.mdc")
    rule = parse_cursor_rule(rule_content)

    assert rule["name"] == "python-best-practices"
    assert rule["description"] == "Enforces Python best practices"
    assert len(rule["filters"]) == 1
    assert rule["filters"][0]["type"] == "file_extension"
    assert rule["filters"][0]["pattern"] == "\\.py$"
    assert len(rule["actions"]) == 1
    assert rule["actions"][0]["type"] == "suggest"
    assert rule["actions"][0]["message"] == "Follow Python best practices"


def test_generate_cursor_rule() -> None:
    """Test generating a cursor rule from components."""
    rule_data = {
        "name": "test-rule",
        "description": "Test rule description",
        "filters": [{"type": "file_extension", "pattern": "\\.py$"}],
        "actions": [{"type": "suggest", "message": "Test message"}],
    }

    rule_content = generate_cursor_rule(rule_data)
    assert "# Test rule description" in rule_content
    assert "<rule>" in rule_content
    assert "name: test-rule" in rule_content
    assert "type: file_extension" in rule_content
    assert "pattern: \\.py$" in rule_content
    assert "type: suggest" in rule_content
    assert "message: Test message" in rule_content


def test_parse_cursor_rule_invalid_content() -> None:
    """Test parsing invalid cursor rule content."""
    with pytest.raises(ValueError, match="Invalid cursor rule content"):
        parse_cursor_rule("Invalid content without <rule> tag")


def test_get_cursor_rule_files_empty_dir(tmp_path: Path) -> None:
    """Test getting cursor rule files from an empty directory.

    Args:
        tmp_path: Pytest fixture providing a temporary directory.

    """
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    rule_files = get_cursor_rule_files(empty_dir)
    assert len(rule_files) == 0


def test_read_cursor_rule_nonexistent_file(tmp_path: Path) -> None:
    """Test reading a nonexistent cursor rule file.

    Args:
        tmp_path: Pytest fixture providing a temporary directory.

    """
    nonexistent_file = tmp_path / "nonexistent.mdc"
    with pytest.raises(FileNotFoundError):
        read_cursor_rule(nonexistent_file)
