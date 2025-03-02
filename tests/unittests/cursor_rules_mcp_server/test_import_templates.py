"""Tests for the import_templates script."""

import os
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Generator
from unittest.mock import patch, MagicMock
if True:  # TYPE_CHECKING equivalent for runtime imports
    from _pytest.fixtures import FixtureRequest
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture

import pytest

from cursor_rules_mcp_server.scripts.import_templates import (
    parse_template_file,
    import_templates,
)
from cursor_rules_mcp_server.models import RuleTemplate


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files.

    Returns:
        Generator[Path, None, None]: Path to the temporary directory.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_template(temp_dir: Path) -> Path:
    """Create a sample template file.

    Args:
        temp_dir (Path): Path to the temporary directory.

    Returns:
        Path: Path to the sample template file.
    """
    template_content = """# Sample Template

This is a sample template for testing purposes.

## Message Patterns
- When the user asks about Python code style

## Context Patterns
- When the file extension is .py

## Instructions
Follow these Python code style guidelines:
- Use 4 spaces for indentation
- Follow PEP 8 guidelines
- Use docstrings for all functions and classes
"""

    file_path = temp_dir / "sample-template.md"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(template_content)

    return file_path


def test_parse_template_file(sample_template: Path) -> None:
    """Test parsing a template file.

    Args:
        sample_template (Path): Path to the sample template file.
    """
    result = parse_template_file(sample_template)

    assert result is not None
    assert result["name"] == "sample-template"
    assert result["title"] == "Sample Template"
    assert result["description"] == "This is a sample template for testing purposes."
    assert "Python code style" in result["content"]
    assert result["category"] == "Python"


def test_parse_template_file_empty(temp_dir: Path) -> None:
    """Test parsing an empty template file.

    Args:
        temp_dir (Path): Path to the temporary directory.
    """
    empty_file = temp_dir / "empty.md"
    with open(empty_file, "w") as f:
        f.write("")

    result = parse_template_file(empty_file)

    assert result is None


def test_import_templates(temp_dir: Path, mocker: "MockerFixture") -> None:
    """Test importing templates.

    Args:
        temp_dir (Path): Path to the temporary directory.
        mocker (MockerFixture): Pytest mocker fixture.
    """
    # Create multiple template files
    templates = [
        {
            "filename": "python-style.md",
            "content": "# Python Style\nPython style guidelines.\n## Instructions\nUse PEP 8."
        },
        {
            "filename": "js-style.md",
            "content": "# JavaScript Style\nJS style guidelines.\n## Instructions\nUse ESLint."
        }
    ]

    for template in templates:
        file_path = temp_dir / template["filename"]
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(template["content"])

    # Mock the database
    mock_db = MagicMock()
    mock_db.add_rule_template.side_effect = lambda t: len(templates)  # Return incrementing IDs

    # Mock the database class
    mock_db_class = mocker.patch("cursor_rules_mcp_server.scripts.import_templates.CursorRulesDatabase")
    mock_db_class.return_value = mock_db

    # Import templates
    result = import_templates(temp_dir)

    # Verify results
    assert len(result) == 2
    assert mock_db.add_rule_template.call_count == 2

    # Check template names
    template_names = [t.name for t in result]
    assert "python-style" in template_names
    assert "js-style" in template_names


def test_import_templates_nonexistent_dir() -> None:
    """Test importing templates from a nonexistent directory."""
    result = import_templates(Path("/nonexistent/directory"))

    assert result == []


def test_import_templates_database_error(temp_dir: Path, mocker: "MockerFixture") -> None:
    """Test handling database errors during import.

    Args:
        temp_dir (Path): Path to the temporary directory.
        mocker (MockerFixture): Pytest mocker fixture.
    """
    # Create a template file
    file_path = temp_dir / "template.md"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("# Template\nTest template.")

    # Mock the database to raise an exception
    mock_db_class = mocker.patch("cursor_rules_mcp_server.scripts.import_templates.CursorRulesDatabase")
    mock_db_class.side_effect = Exception("Database error")

    # Import templates
    result = import_templates(temp_dir)

    # Verify results
    assert result == []
