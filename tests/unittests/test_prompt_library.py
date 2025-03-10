"""Tests for the prompt_library FastMCP server.

This module contains tests for the prompt_library FastMCP server, which exposes
cursor rules as resources and provides a prompt endpoint for creating custom cursor rules.
"""

import json
from collections.abc import Generator
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import pytest

from codegen_lab.prompt_library import (
    generate_cursor_rule,
    get_cursor_rule_names,
    mcp,
    parse_cursor_rule,
    read_cursor_rule,
    save_cursor_rule,
)

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture

from mcp.shared.memory import create_connected_server_and_client_session as client_session
from mcp.types import TextContent, TextResourceContents
from pydantic import AnyUrl


@pytest.fixture
def sample_cursor_rule() -> str:
    """Provide a sample cursor rule for testing.

    Returns:
        str: A sample cursor rule in markdown format

    """
    return """---
description: Sample Rule
globs: *.py
alwaysApply: false
---
# Sample Rule

This is a sample rule.

<rule>
name: sample-rule
description: This is a sample rule
filters:
  - type: file_extension
    pattern: "\\.py$"

actions:
  - type: suggest
    message: |
      This is a sample message.

examples:
  - input: |
      # Sample input
    output: "Sample output"

metadata:
  priority: high
  version: 1.0
  tags:
    - sample
    - test
</rule>
"""


@pytest.fixture
def mock_cursor_rule(mocker: "MockerFixture", sample_cursor_rule: str) -> Generator[None, None, None]:
    """Mock the read_cursor_rule function to return a sample rule.

    Args:
        mocker: Pytest fixture for mocking
        sample_cursor_rule: Sample cursor rule fixture

    Yields:
        None

    """
    mocker.patch("codegen_lab.prompt_library.read_cursor_rule", return_value=sample_cursor_rule)
    yield


class TestCursorRuleResources:
    """Tests for cursor rule resources."""

    @pytest.mark.anyio
    async def test_list_cursor_rules(self) -> None:
        """Test that the list_cursor_rules resource returns a list of cursor rules."""
        async with client_session(mcp._mcp_server) as client:
            result = await client.read_resource(AnyUrl("cursor-rules://list"))

            assert len(result.contents) == 1
            content = result.contents[0]
            assert isinstance(content, TextResourceContents)

            rules = json.loads(content.text)
            assert isinstance(rules, list)
            assert len(rules) > 0

            # Check that each rule has the expected fields
            for rule in rules:
                assert "name" in rule
                assert "description" in rule

    @pytest.mark.anyio
    async def test_get_cursor_rule(self, mock_cursor_rule: None) -> None:
        """Test that the get_cursor_rule resource returns a cursor rule.

        Args:
            mock_cursor_rule: Fixture that mocks the read_cursor_rule function

        """
        async with client_session(mcp._mcp_server) as client:
            result = await client.read_resource(AnyUrl("cursor-rule://sample-rule"))

            assert len(result.contents) == 1
            content = result.contents[0]
            assert isinstance(content, TextResourceContents)

            rule = json.loads(content.text)
            assert isinstance(rule, dict)
            assert "title" in rule
            assert "description" in rule
            assert "rule" in rule

            # Check that the rule has the expected fields
            assert rule["title"] == "Sample Rule"
            assert rule["description"] == "This is a sample rule."
            assert rule["rule"]["name"] == "sample-rule"  # type: ignore
            assert rule["rule"]["description"] == "This is a sample rule"  # type: ignore
            assert "filters" in rule["rule"]  # type: ignore
            assert "actions" in rule["rule"]  # type: ignore
            assert "examples" in rule["rule"]  # type: ignore
            assert "metadata" in rule["rule"]  # type: ignore

    @pytest.mark.anyio
    async def test_get_cursor_rule_not_found(self, mocker: "MockerFixture") -> None:
        """Test that the get_cursor_rule resource handles missing rules gracefully.

        Args:
            mocker: Pytest fixture for mocking

        """
        # Mock the read_cursor_rule function to return None (rule not found)
        mocker.patch("codegen_lab.prompt_library.read_cursor_rule", return_value=None)

        async with client_session(mcp._mcp_server) as client:
            # The resource should return an error when the rule is not found
            with pytest.raises(Exception) as excinfo:
                await client.read_resource(AnyUrl("cursor-rule://nonexistent-rule"))

            assert "not found" in str(excinfo.value).lower()

    @pytest.mark.anyio
    async def test_get_cursor_rule_raw(self, mock_cursor_rule: None) -> None:
        """Test that the get_cursor_rule_raw resource returns the raw cursor rule content.

        Args:
            mock_cursor_rule: Fixture that mocks the read_cursor_rule function

        """
        async with client_session(mcp._mcp_server) as client:
            result = await client.read_resource(AnyUrl("cursor-rule-raw://sample-rule"))

            assert len(result.contents) == 1
            content = result.contents[0]
            assert isinstance(content, TextResourceContents)

            # The raw content should be returned as-is
            assert "---" in content.text
            assert "# Sample Rule" in content.text
            assert "<rule>" in content.text
            assert "</rule>" in content.text


class TestPrompts:
    """Tests for prompt endpoints."""

    @pytest.mark.anyio
    async def test_repo_analysis_prompt(self, mocker: "MockerFixture") -> None:
        """Test that the repo_analysis_prompt returns the expected messages.

        Args:
            mocker: Pytest fixture for mocking

        """
        # Mock the Context object
        mock_context = mocker.MagicMock()
        mocker.patch("codegen_lab.prompt_library.Context", return_value=mock_context)

        async with client_session(mcp._mcp_server) as client:
            result = await client.get_prompt(
                "repo-analysis",
                {
                    "repo_description": "A sample repository",
                    "main_languages": "Python, JavaScript",
                    "file_patterns": "*.py, *.js",
                    "key_features": "API, Database, UI",
                },
            )

            assert len(result.messages) == 1
            message = result.messages[0]
            assert message.role == "user"
            assert isinstance(message.content, TextContent)
            assert "Repository Description" in message.content.text
            assert "Main Languages" in message.content.text
            assert "File Patterns" in message.content.text
            assert "Key Features" in message.content.text

    @pytest.mark.anyio
    async def test_generate_cursor_rule_prompt(self, mocker: "MockerFixture") -> None:
        """Test that the generate_cursor_rule_prompt returns the expected messages.

        Args:
            mocker: Pytest fixture for mocking

        """
        # Mock the Context object
        mock_context = mocker.MagicMock()
        mocker.patch("codegen_lab.prompt_library.Context", return_value=mock_context)

        async with client_session(mcp._mcp_server) as client:
            result = await client.get_prompt(
                "generate-cursor-rule",
                {
                    "rule_name": "test-rule",
                    "description": "A test rule",
                    "file_patterns": "*.py, *.js",
                    "content_patterns": "test, example",
                    "action_message": "This is a test message.",
                    "examples": json.dumps([{"input": "# Test input", "output": "Test output"}]),
                    "tags": "test, example",
                    "priority": "high",
                },
            )

            assert len(result.messages) == 1
            message = result.messages[0]
            assert message.role == "user"
            assert isinstance(message.content, TextContent)
            assert "I've generated a cursor rule" in message.content.text
            assert "```markdown" in message.content.text
            assert "test-rule" in message.content.text
            assert "A test rule" in message.content.text
            assert "*.py" in message.content.text
            assert "*.js" in message.content.text
            assert "test" in message.content.text
            assert "example" in message.content.text
            assert "This is a test message." in message.content.text
            assert "Test input" in message.content.text
            assert "Test output" in message.content.text

    @pytest.mark.anyio
    async def test_generate_cursor_rule_prompt_with_template(self) -> None:
        """Test that the generate_cursor_rule_prompt returns expected messages with a template."""
        async with client_session(mcp._mcp_server) as client:
            result = await client.get_prompt(
                "generate-cursor-rule",
                {
                    "rule_name": "sample-rule",
                    "description": "This is a sample rule",
                    "file_patterns": "*.py",
                    "content_patterns": "def|class",
                    "action_message": "This is a sample message.",
                    "examples": '[{"input": "# Sample input", "output": "Sample output"}]',
                    "tags": "sample, test",
                    "template_rule": "sample-template",
                },
            )

            assert len(result.messages) > 0
            message_text = result.messages[0].content.text
            assert "sample-rule" in message_text
            assert "This is a sample rule" in message_text


class TestUtilityFunctions:
    """Tests for utility functions."""

    def test_parse_cursor_rule(self, sample_cursor_rule: str) -> None:
        """Test that the parse_cursor_rule function correctly parses a cursor rule.

        Args:
            sample_cursor_rule: Sample cursor rule fixture

        """
        result = parse_cursor_rule(sample_cursor_rule)

        assert isinstance(result, dict)
        assert "frontmatter" in result
        assert "title" in result
        assert "description" in result
        assert "rule" in result

        assert result["title"] == "Sample Rule"
        assert result["description"] == "This is a sample rule."
        assert result["rule"]["name"] == "sample-rule"
        assert result["rule"]["description"] == "This is a sample rule"
        assert "filters" in result["rule"]
        assert "actions" in result["rule"]
        assert "examples" in result["rule"]
        assert "metadata" in result["rule"]

        assert len(result["rule"]["filters"]) == 1
        assert result["rule"]["filters"][0]["type"] == "file_extension"
        assert result["rule"]["filters"][0]["pattern"] == "\\.py$"

        assert len(result["rule"]["actions"]) == 1
        assert result["rule"]["actions"][0]["type"] == "suggest"
        assert "This is a sample message." in result["rule"]["actions"][0]["message"]

        assert len(result["rule"]["examples"]) == 1
        assert "# Sample input" in result["rule"]["examples"][0]["input"]
        assert result["rule"]["examples"][0]["output"] == "Sample output"

        assert result["rule"]["metadata"]["priority"] == "high"
        assert result["rule"]["metadata"]["version"] == "1.0"
        assert "sample" in result["rule"]["metadata"]["tags"]
        assert "test" in result["rule"]["metadata"]["tags"]

    def test_generate_cursor_rule(self) -> None:
        """Test that the generate_cursor_rule function correctly generates a cursor rule."""
        result = generate_cursor_rule(
            rule_name="test-rule",
            description="A test rule",
            file_patterns=["*.py", "*.js"],
            content_patterns=["test", "example"],
            action_message="This is a test message.",
            examples=[{"input": "# Test input", "output": "Test output"}],
            tags=["test", "example"],
            priority="high",
        )

        assert isinstance(result, str)
        assert "---" in result
        assert "description: A test rule" in result
        assert "globs: *.py, *.js" in result
        assert "# Test Rule" in result
        assert "A test rule" in result
        assert "<rule>" in result
        assert "name: test-rule" in result
        assert "description: A test rule" in result
        assert "filters:" in result
        assert "file_extension" in result
        assert "*.py|*.js" in result
        assert "content" in result
        assert "(?s)(test|example)" in result
        assert "actions:" in result
        assert "type: suggest" in result
        assert "message: |" in result
        assert "This is a test message." in result
        assert "examples:" in result
        assert "input: |" in result
        assert "# Test input" in result
        assert 'output: "Test output"' in result
        assert "metadata:" in result
        assert "priority: high" in result
        assert "version: 1.0" in result
        assert "tags:" in result
        assert "- test" in result
        assert "- example" in result
        assert "</rule>" in result

    def test_save_cursor_rule(self, mocker: "MockerFixture", tmp_path: Path) -> None:
        """Test that the save_cursor_rule function saves files relative to the current working directory.

        Args:
            mocker: Pytest fixture for mocking
            tmp_path: Pytest fixture providing a temporary directory path

        """
        # Mock the current working directory to be the temporary directory
        mocker.patch("pathlib.Path.cwd", return_value=tmp_path)

        # Call the function
        rule_name = "test-rule"
        rule_content = "# Test Rule\n\nThis is a test rule."
        result = save_cursor_rule(rule_name, rule_content)

        # Check that the file was saved in the correct location
        expected_path = tmp_path / "hack" / "drafts" / "cursor_rules" / f"{rule_name}.mdc.md"
        assert expected_path.exists()
        assert expected_path.read_text() == rule_content
        assert f"Cursor rule saved to {expected_path}" in result

        # Check that the directory structure was created
        assert (tmp_path / "hack").exists()
        assert (tmp_path / "hack" / "drafts").exists()
        assert (tmp_path / "hack" / "drafts" / "cursor_rules").exists()


class TestToolFunctions:
    """Tests for tool functions."""

    @pytest.mark.anyio
    async def test_save_cursor_rule_tool(self, mocker: "MockerFixture", tmp_path: Path) -> None:
        """Test that the save_cursor_rule tool correctly saves a cursor rule.

        Args:
            mocker: Pytest fixture for mocking
            tmp_path: Pytest fixture providing a temporary directory path

        """
        # Mock the current working directory to be the temporary directory
        mocker.patch("pathlib.Path.cwd", return_value=tmp_path)

        async with client_session(mcp._mcp_server) as client:
            result = await client.call_tool(
                "save_cursor_rule",
                {
                    "rule_name": "test-rule",
                    "rule_content": "# Test Rule\n\nThis is a test rule.",
                },
            )

            assert len(result.content) == 1
            content = result.content[0]
            assert isinstance(content, TextContent)

            # Check that the response indicates success
            expected_path = tmp_path / "hack" / "drafts" / "cursor_rules" / "test-rule.mdc.md"
            assert f"Cursor rule saved to {expected_path}" in content.text

            # Check that the file was actually saved
            assert expected_path.exists()
            assert expected_path.read_text() == "# Test Rule\n\nThis is a test rule."

    @pytest.mark.anyio
    async def test_recommend_cursor_rules(self) -> None:
        """Test that the recommend_cursor_rules tool returns recommendations."""
        async with client_session(mcp._mcp_server) as client:
            result = await client.call_tool(
                "recommend_cursor_rules",
                {
                    "repo_summary": "This is a Python project with FastAPI endpoints and database models.",
                },
            )

            # The tool returns multiple recommendations
            assert len(result.content) > 0

            # Verify the structure of at least one recommendation
            first_recommendation = json.loads(result.content[0].text)
            assert "name" in first_recommendation
            assert "description" in first_recommendation
            assert "reason" in first_recommendation
