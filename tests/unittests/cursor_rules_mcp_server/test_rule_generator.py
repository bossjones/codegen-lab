"""Tests for the rule_generator module."""

import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Generator
from unittest.mock import patch, MagicMock
if True:  # TYPE_CHECKING equivalent for runtime imports
    from _pytest.fixtures import FixtureRequest
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture

import pytest

from cursor_rules_mcp_server.rule_generator import (
    RuleGenerator,
    generate_rule,
    analyze_and_suggest_rules,
    validate_rule_content,
)


@pytest.fixture
def mock_repo_analysis() -> Dict[str, Any]:
    """Create a mock repository analysis result.

    Returns:
        Dict[str, Any]: Mock repository analysis.
    """
    return {
        "repo_type": "web",
        "languages": {
            "python": 10,
            "javascript": 5,
            "html": 3
        },
        "frameworks": ["flask", "react"],
        "file_stats": {
            "total_files": 20,
            "has_requirements_txt": True,
            "has_package_json": True,
            "has_readme": True,
            "directories": ["src/myapp", "static/js", "templates"],
            "extensions": [".py", ".js", ".html"]
        },
        "suggested_rules": [
            {
                "name": "python-code-standards",
                "description": "Python code standards for web applications"
            },
            {
                "name": "web-development-workflow",
                "description": "Web development workflow for Flask and React"
            }
        ]
    }


@pytest.fixture
def mock_rule_template() -> Dict[str, Any]:
    """Create a mock rule template.

    Returns:
        Dict[str, Any]: Mock rule template.
    """
    return {
        "name": "python-code-standards",
        "title": "Python Code Standards",
        "description": "Python code standards for web applications",
        "content": """# Python Code Standards

Follow these Python code standards for web applications.

## Message Patterns
- When the user asks about Python code style
- When the user asks about PEP 8

## Context Patterns
- When the file extension is .py

## Instructions
Follow these Python code style guidelines:
- Use 4 spaces for indentation
- Follow PEP 8 guidelines
- Use docstrings for all functions and classes

## Examples
```python
def example_function():
    \"\"\"This is a docstring.\"\"\"
    return True
```

## Metadata
- language: python
- framework: flask
"""
    }


@pytest.fixture
def temp_output_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for output files.

    Returns:
        Generator[Path, None, None]: Path to the temporary directory.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


def test_rule_generator_init() -> None:
    """Test RuleGenerator initialization."""
    generator = RuleGenerator("/path/to/repo")

    assert generator.repo_path == "/path/to/repo"
    assert generator.analysis is None


def test_analyze_repo(mocker: "MockerFixture") -> None:
    """Test analyzing a repository.

    Args:
        mocker (MockerFixture): Pytest mocker fixture.
    """
    # Mock the analyze_repository function
    mock_analyze = mocker.patch("cursor_rules_mcp_server.rule_generator.analyze_repository")
    mock_analyze.return_value = {"repo_type": "web"}

    generator = RuleGenerator("/path/to/repo")
    result = generator.analyze_repo()

    assert result == {"repo_type": "web"}
    assert generator.analysis == {"repo_type": "web"}
    mock_analyze.assert_called_once_with("/path/to/repo")


def test_analyze_repo_no_path() -> None:
    """Test analyzing a repository with no path."""
    generator = RuleGenerator()

    with pytest.raises(ValueError):
        generator.analyze_repo()


def test_get_suggested_rules(mock_repo_analysis: Dict[str, Any], mocker: "MockerFixture") -> None:
    """Test getting suggested rules.

    Args:
        mock_repo_analysis (Dict[str, Any]): Mock repository analysis.
        mocker (MockerFixture): Pytest mocker fixture.
    """
    generator = RuleGenerator("/path/to/repo")
    generator.analysis = mock_repo_analysis

    rules = generator.get_suggested_rules()

    assert rules == mock_repo_analysis["suggested_rules"]


def test_get_suggested_rules_no_analysis(mocker: "MockerFixture") -> None:
    """Test getting suggested rules with no analysis.

    Args:
        mocker (MockerFixture): Pytest mocker fixture.
    """
    # Mock the analyze_repo method
    mock_analyze = mocker.patch.object(RuleGenerator, "analyze_repo")
    mock_analyze.return_value = {"suggested_rules": [{"name": "test-rule"}]}

    generator = RuleGenerator("/path/to/repo")
    rules = generator.get_suggested_rules()

    assert rules == [{"name": "test-rule"}]
    mock_analyze.assert_called_once()


def test_generate_rule(mock_rule_template: Dict[str, Any], mocker: "MockerFixture") -> None:
    """Test generating a rule.

    Args:
        mock_rule_template (Dict[str, Any]): Mock rule template.
        mocker (MockerFixture): Pytest mocker fixture.
    """
    # Mock the get_rule_template function
    mock_get_template = mocker.patch("cursor_rules_mcp_server.rule_generator.get_rule_template")
    mock_get_template.return_value = mock_rule_template

    generator = RuleGenerator("/path/to/repo")
    rule = generator.generate_rule("python-code-standards")

    assert rule["name"] == "python-code-standards"
    assert rule["title"] == "Python Code Standards"
    assert "Python code standards" in rule["description"]
    assert "# Python Code Standards" in rule["content"]
    mock_get_template.assert_called_once_with("python-code-standards", None)


def test_generate_rule_with_customizations(mock_rule_template: Dict[str, Any], mocker: "MockerFixture") -> None:
    """Test generating a rule with customizations.

    Args:
        mock_rule_template (Dict[str, Any]): Mock rule template.
        mocker (MockerFixture): Pytest mocker fixture.
    """
    # Mock the get_rule_template function
    mock_get_template = mocker.patch("cursor_rules_mcp_server.rule_generator.get_rule_template")
    mock_get_template.return_value = mock_rule_template

    generator = RuleGenerator("/path/to/repo")
    rule = generator.generate_rule(
        "python-code-standards",
        customizations={
            "title": "Custom Python Standards",
            "description": "Custom description"
        }
    )

    assert rule["name"] == "python-code-standards"
    assert rule["title"] == "Custom Python Standards"
    assert rule["description"] == "Custom description"
    assert "# Python Code Standards" in rule["content"]
    mock_get_template.assert_called_once_with("python-code-standards", None)


def test_generate_rule_template_not_found(mocker: "MockerFixture") -> None:
    """Test generating a rule with a non-existent template.

    Args:
        mocker (MockerFixture): Pytest mocker fixture.
    """
    # Mock the get_rule_template function
    mock_get_template = mocker.patch("cursor_rules_mcp_server.rule_generator.get_rule_template")
    mock_get_template.return_value = None

    generator = RuleGenerator("/path/to/repo")

    with pytest.raises(ValueError):
        generator.generate_rule("non-existent-template")


def test_validate_rule(mock_rule_template: Dict[str, Any]) -> None:
    """Test validating a rule.

    Args:
        mock_rule_template (Dict[str, Any]): Mock rule template.
    """
    generator = RuleGenerator()

    # Valid rule
    assert generator.validate_rule(mock_rule_template) is True

    # Invalid rule (missing title)
    invalid_rule = mock_rule_template.copy()
    invalid_rule.pop("title")
    assert generator.validate_rule(invalid_rule) is False

    # Invalid rule (missing content)
    invalid_rule = mock_rule_template.copy()
    invalid_rule.pop("content")
    assert generator.validate_rule(invalid_rule) is False


def test_generate_multiple_rules(mock_rule_template: Dict[str, Any], mocker: "MockerFixture") -> None:
    """Test generating multiple rules.

    Args:
        mock_rule_template (Dict[str, Any]): Mock rule template.
        mocker (MockerFixture): Pytest mocker fixture.
    """
    # Mock the generate_rule method
    mock_generate = mocker.patch.object(RuleGenerator, "generate_rule")
    mock_generate.side_effect = [
        {"name": "rule1", "content": "content1"},
        {"name": "rule2", "content": "content2"}
    ]

    generator = RuleGenerator()
    rules = generator.generate_multiple_rules(["rule1", "rule2"])

    assert len(rules) == 2
    assert rules[0]["name"] == "rule1"
    assert rules[1]["name"] == "rule2"
    assert mock_generate.call_count == 2


def test_customize_rule_for_repo(mock_repo_analysis: Dict[str, Any], mock_rule_template: Dict[str, Any]) -> None:
    """Test customizing a rule for a repository.

    Args:
        mock_repo_analysis (Dict[str, Any]): Mock repository analysis.
        mock_rule_template (Dict[str, Any]): Mock rule template.
    """
    generator = RuleGenerator("/path/to/repo")
    generator.analysis = mock_repo_analysis

    customizations = generator.customize_rule_for_repo(mock_rule_template)

    assert "title" in customizations
    assert "description" in customizations
    assert "flask" in customizations["description"] or "web" in customizations["description"]


def test_export_rules_to_files(mock_rule_template: Dict[str, Any], temp_output_dir: Path) -> None:
    """Test exporting rules to files.

    Args:
        mock_rule_template (Dict[str, Any]): Mock rule template.
        temp_output_dir (Path): Temporary output directory.
    """
    generator = RuleGenerator()
    rules = [mock_rule_template]

    generator.export_rules_to_files(rules, str(temp_output_dir))

    # Check that the file was created
    output_file = temp_output_dir / "python-code-standards.md"
    assert output_file.exists()

    # Check file content
    with open(output_file, "r") as f:
        content = f.read()
        assert "# Python Code Standards" in content


def test_generate_rule_function(mock_rule_template: Dict[str, Any], mocker: "MockerFixture") -> None:
    """Test the generate_rule function.

    Args:
        mock_rule_template (Dict[str, Any]): Mock rule template.
        mocker (MockerFixture): Pytest mocker fixture.
    """
    # Mock the RuleGenerator class
    mock_generator = MagicMock()
    mock_generator.generate_rule.return_value = mock_rule_template

    mock_generator_class = mocker.patch("cursor_rules_mcp_server.rule_generator.RuleGenerator")
    mock_generator_class.return_value = mock_generator

    result = generate_rule("python-code-standards", "/path/to/repo")

    assert result == mock_rule_template
    mock_generator_class.assert_called_once_with("/path/to/repo")
    mock_generator.generate_rule.assert_called_once_with("python-code-standards", None)


def test_analyze_and_suggest_rules(mock_repo_analysis: Dict[str, Any], mocker: "MockerFixture") -> None:
    """Test the analyze_and_suggest_rules function.

    Args:
        mock_repo_analysis (Dict[str, Any]): Mock repository analysis.
        mocker (MockerFixture): Pytest mocker fixture.
    """
    # Mock the RuleGenerator class
    mock_generator = MagicMock()
    mock_generator.analyze_repo.return_value = mock_repo_analysis
    mock_generator.get_suggested_rules.return_value = mock_repo_analysis["suggested_rules"]

    mock_generator_class = mocker.patch("cursor_rules_mcp_server.rule_generator.RuleGenerator")
    mock_generator_class.return_value = mock_generator

    result = analyze_and_suggest_rules("/path/to/repo")

    assert result == mock_repo_analysis["suggested_rules"]
    mock_generator_class.assert_called_once_with("/path/to/repo")
    mock_generator.analyze_repo.assert_called_once()
    mock_generator.get_suggested_rules.assert_called_once()


def test_validate_rule_content() -> None:
    """Test the validate_rule_content function."""
    # Valid rule content
    valid_content = """# Test Rule

This is a test rule.

## Message Patterns
- When the user asks about testing

## Context Patterns
- When the file extension is .py

## Instructions
Follow these instructions.

## Examples
```python
def test():
    pass
```

## Metadata
- language: python
"""

    assert validate_rule_content(valid_content) is True

    # Invalid rule content (missing sections)
    invalid_content = """# Test Rule

This is a test rule.

## Instructions
Follow these instructions.
"""

    assert validate_rule_content(invalid_content) is False
