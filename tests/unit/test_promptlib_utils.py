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


@pytest.mark.parametrize(
    "rule_data,expected_content",
    [
        (
            {
                "name": "test-rule",
                "description": "Test description",
                "filters": [{"type": "file_extension", "pattern": "\\.py$"}],
                "actions": [{"type": "suggest", "message": "Test message"}],
            },
            ["name: test-rule", "description: Test description", "type: file_extension", "pattern: \\.py$"],
        ),
        (
            {
                "name": "complex-rule",
                "description": "Complex test rule",
                "filters": [
                    {"type": "file_extension", "pattern": "\\.py$"},
                    {"type": "content", "pattern": "def|class"},
                ],
                "actions": [
                    {"type": "suggest", "message": "First message"},
                    {"type": "suggest", "message": "Second message"},
                ],
            },
            [
                "name: complex-rule",
                "description: Complex test rule",
                "type: file_extension",
                "pattern: \\.py$",
                "type: content",
                "pattern: def|class",
                "First message",
                "Second message",
            ],
        ),
    ],
    ids=["simple_rule", "complex_rule"],
)
def test_generate_cursor_rule_variations(
    rule_data: dict,
    expected_content: list[str],
) -> None:
    """Test generating cursor rules with various configurations.

    This test verifies that generate_cursor_rule properly handles:
    1. Simple rules with single filter and action
    2. Complex rules with multiple filters and actions
    3. Proper YAML formatting of nested structures

    Args:
        rule_data: The rule data to generate
        expected_content: List of strings that should appear in the generated content

    """
    rule_content = generate_cursor_rule(rule_data)
    for expected in expected_content:
        assert expected in rule_content


@pytest.mark.parametrize(
    "rule_content,expected_error",
    [
        (
            "Invalid content without rule tag",
            "Invalid cursor rule content",
        ),
        (
            "<rule>\nname: test\n</rule>",
            "Missing required fields in cursor rule",
        ),
        (
            "<rule>\ndescription: test\n</rule>",
            "Missing required fields in cursor rule",
        ),
        (
            "<rule>\nname: test\ndescription: test\n</rule>",
            "Missing required fields in cursor rule",
        ),
    ],
    ids=[
        "no_rule_tag",
        "missing_description_and_filters",
        "missing_name_and_filters",
        "missing_filters",
    ],
)
def test_parse_cursor_rule_invalid_content(rule_content: str, expected_error: str) -> None:
    """Test parsing invalid cursor rule content.

    This test verifies that parse_cursor_rule properly handles various invalid inputs:
    1. Content without <rule> tag
    2. Rule missing required fields
    3. Rule with partial required fields

    Args:
        rule_content: The invalid rule content to test
        expected_error: The expected error message

    """
    with pytest.raises(ValueError, match=expected_error):
        parse_cursor_rule(rule_content)


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
