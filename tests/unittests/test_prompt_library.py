"""Tests for the prompt_library FastMCP server.

This module contains tests for the prompt_library FastMCP server, which exposes
cursor rules as resources and provides a prompt endpoint for creating custom cursor rules.
"""

import json
import os
import pathlib
import subprocess
from collections.abc import Generator
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import pytest
from _pytest.monkeypatch import MonkeyPatch
from pytest_mock import MockerFixture

from codegen_lab.prompt_library import (
    create_cursor_rule_files,
    cursor_rules_workflow,
    ensure_makefile_task,
    generate_cursor_rule,
    get_cursor_rule_names,
    get_static_cursor_rule,
    get_static_cursor_rules,
    mcp,
    parse_cursor_rule,
    plan_and_execute_prompt_library_workflow,
    prep_workspace,
    read_cursor_rule,
    run_update_cursor_rules,
    save_cursor_rule,
    update_dockerignore,
)

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
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

    def test_prep_workspace(self, mocker: "MockerFixture", tmp_path: Path) -> None:
        """Test that prep_workspace creates the necessary directories.

        Args:
            mocker: Pytest fixture for mocking
            tmp_path: Pytest fixture providing a temporary directory path

        """
        # Mock the current working directory
        mocker.patch("pathlib.Path.cwd", return_value=tmp_path)

        # Call the function
        result = prep_workspace()

        # Check that the directories were created
        cursor_rules_dir = tmp_path / "hack" / "drafts" / "cursor_rules"

        # Check the results instead of checking if directories were created
        # The function only returns instructions, it doesn't create directories
        assert result["directory_path"] == str(cursor_rules_dir)
        assert result["directory_exists"] is False
        assert "mkdir -p" in result["mkdir_command"]
        assert str(cursor_rules_dir) in result["mkdir_command"]
        assert "Create the cursor rules directory structure" in result["message"]

    def test_create_cursor_rule_files(self, mocker: "MockerFixture", tmp_path: Path) -> None:
        """Test that create_cursor_rule_files creates the specified files.

        Args:
            mocker: Pytest fixture for mocking
            tmp_path: Pytest fixture providing a temporary directory path

        """
        # Mock Path.mkdir and Path.touch to avoid actual file creation
        mkdir_mock = mocker.patch("pathlib.Path.mkdir")
        touch_mock = mocker.patch("pathlib.Path.touch")
        exists_mock = mocker.patch("pathlib.Path.exists", return_value=False)
        read_text_mock = mocker.patch("pathlib.Path.read_text", return_value="")

        # Mock Path constructor to return a path relative to tmp_path
        orig_path_init = Path.__new__

        def mock_path_init(cls, *args, **kwargs):
            path_str = str(args[0]) if args else ""
            if path_str == "hack/drafts/cursor_rules":
                return orig_path_init(cls, tmp_path / "hack" / "drafts" / "cursor_rules")
            return orig_path_init(cls, *args, **kwargs)

        mocker.patch.object(Path, "__new__", mock_path_init)

        try:
            # Define some test rules (just names)
            rule_names = ["test-rule-1", "test-rule-2"]

            # Call the function
            result = create_cursor_rule_files(rule_names)

            # Verify mkdir was called
            mkdir_mock.assert_called_once_with(parents=True, exist_ok=True)

            # Verify touch was called for each rule
            assert touch_mock.call_count == len(rule_names)

            # Check the results dictionary
            assert result["success"] is True
            assert len(result["created_files"]) == len(rule_names)
            for rule_name in rule_names:
                assert f"{rule_name}.mdc.md" in result["created_files"]
        finally:
            # Cleanup step: Remove any test files and directories created during the test
            cursor_rules_dir = tmp_path / "hack" / "drafts" / "cursor_rules"
            if cursor_rules_dir.exists():
                # Remove test files
                for rule_name in ["test-rule-1", "test-rule-2"]:
                    file_path = cursor_rules_dir / f"{rule_name}.mdc.md"
                    if file_path.exists():
                        file_path.unlink()

                # Clean up directories
                if cursor_rules_dir.exists():
                    try:
                        cursor_rules_dir.rmdir()
                        (tmp_path / "hack" / "drafts").rmdir()
                        (tmp_path / "hack").rmdir()
                    except OSError:
                        # Directory might not be empty or might not exist, which is fine
                        pass

    def test_ensure_makefile_task(self, mocker: "MockerFixture", tmp_path: Path) -> None:
        """Test that ensure_makefile_task adds or verifies the update-cursor-rules task.

        Args:
            mocker: Pytest fixture for mocking
            tmp_path: Pytest fixture providing a temporary directory path

        """
        # Mock Path.cwd to return our temporary directory
        mocker.patch("pathlib.Path.cwd", return_value=tmp_path)

        # Case 1: Makefile doesn't exist
        # Setup: ensure the makefile doesn't exist
        makefile_path = tmp_path / "Makefile"
        if makefile_path.exists():
            makefile_path.unlink()

        # Test
        result = ensure_makefile_task()

        # Verify
        assert result["success"] is True
        assert result["has_makefile"] is True
        assert result["has_update_task"] is True
        assert result["action_taken"] == "created"
        assert "Created a new Makefile" in result["message"]
        assert makefile_path.exists()
        assert "update-cursor-rules" in makefile_path.read_text()

        # Case 2: Makefile exists but lacks the task
        # Setup: create a makefile without the task
        makefile_path.write_text("""
.PHONY: test
test:
	pytest
""")

        # Mock open to check what's written
        mock_open = mocker.patch("builtins.open", mocker.mock_open())

        # Test
        result = ensure_makefile_task()

        # Verify
        assert result["success"] is True
        assert result["has_makefile"] is True
        assert result["has_update_task"] is False
        assert result["action_taken"] == "updated"
        assert "Added the update-cursor-rules task" in result["message"]

        # Case 3: Makefile exists and has the task
        # Setup: create a makefile with the task
        makefile_content_with_task = """
.PHONY: test update-cursor-rules
test:
	pytest

update-cursor-rules:
	cp hack/drafts/cursor_rules/*.mdc.md .cursor/rules/
"""
        makefile_path.write_text(makefile_content_with_task)

        # Test
        result = ensure_makefile_task()

        # Verify
        assert result["success"] is True
        assert result["has_makefile"] is True
        assert result["has_update_task"] is True
        assert result["action_taken"] == "none"
        assert "already contains" in result["message"]

    def test_run_update_cursor_rules(self, mocker: "MockerFixture") -> None:
        """Test that run_update_cursor_rules executes the make command.

        Args:
            mocker: Pytest fixture for mocking

        """
        # Mock Path.cwd to return a predictable path
        cwd_mock = mocker.patch("pathlib.Path.cwd")
        test_path = Path("/test/path")
        cwd_mock.return_value = test_path

        # Mock exists and read_text to simulate Makefile existing with update-cursor-rules
        mocker.patch("pathlib.Path.exists", return_value=True)
        mocker.patch("pathlib.Path.read_text", return_value="update-cursor-rules: cp files")
        mocker.patch("pathlib.Path.glob", return_value=[])

        # Mock the subprocess.run function
        mock_run = mocker.patch(
            "subprocess.run", return_value=mocker.MagicMock(returncode=0, stdout="Deployment successful", stderr="")
        )

        # Call the function
        result = run_update_cursor_rules()

        # Check that subprocess.run was called with the correct command and cwd parameter
        mock_run.assert_called_once_with(
            ["make", "update-cursor-rules"], cwd=test_path, check=True, capture_output=True, text=True
        )

        # Check that the result indicates success
        assert result["success"] is True
        assert "Successfully deployed cursor rules" in result["message"]

        # Test error handling
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd=["make", "update-cursor-rules"], output="", stderr="Command failed"
        )

        # Call the function again
        result = run_update_cursor_rules()

        # Check that the result indicates failure
        assert result["success"] is False
        assert "Failed to run the update-cursor-rules task" in result["message"]

    def test_update_dockerignore(self, mocker: "MockerFixture", tmp_path: Path) -> None:
        """Test update_dockerignore function.

        This test verifies that the update_dockerignore function correctly updates
        the .dockerignore file by adding the cursor rules drafts directory.

        Args:
            mocker: MockerFixture for patching
            tmp_path: Pytest fixture providing a temporary directory path

        """
        # Create a mock .dockerignore file in the tmp_path
        dockerignore_path = tmp_path / ".dockerignore"
        dockerignore_path.write_text("node_modules\n.env\n")

        # Patch Path.cwd() to return our tmp_path instead of the real cwd
        mocker.patch("pathlib.Path.cwd", return_value=tmp_path)

        # Execute the function
        result = update_dockerignore()

        # Assert
        assert result["success"] is True
        assert result["action_taken"] == "updated"

        # Verify the file was updated correctly
        updated_content = dockerignore_path.read_text()
        assert updated_content == "node_modules\n.env\nhack/drafts/cursor_rules\n"

    def test_get_static_cursor_rule(self, mocker: "MockerFixture", sample_cursor_rule: str) -> None:
        """Test get_static_cursor_rule function."""
        # Setup
        rule_name = "test_rule"
        mocker.patch("codegen_lab.prompt_library.read_cursor_rule", return_value=sample_cursor_rule)

        # Execute
        result = get_static_cursor_rule(rule_name)

        # Assert
        assert result["rule_name"] == "test_rule.md"
        assert result["content"] == sample_cursor_rule

        # Test with .md extension already in the name
        result = get_static_cursor_rule("test_rule.md")
        assert result["rule_name"] == "test_rule.md"

        # Test not found case
        mocker.patch("codegen_lab.prompt_library.read_cursor_rule", return_value=None)
        with pytest.raises(FileNotFoundError):
            get_static_cursor_rule("nonexistent_rule")

    def test_get_static_cursor_rules(self, mocker: "MockerFixture", sample_cursor_rule: str) -> None:
        """Test get_static_cursor_rules function."""
        # Setup
        rule_names = ["rule1", "rule2", "nonexistent_rule"]

        # Mock to return content for rule1 and rule2, but None for nonexistent_rule
        def mock_read_cursor_rule(name: str) -> str | None:
            if name in ["rule1", "rule2"]:
                return sample_cursor_rule
            return None

        mocker.patch("codegen_lab.prompt_library.read_cursor_rule", side_effect=mock_read_cursor_rule)

        # Execute
        results = get_static_cursor_rules(rule_names)

        # Assert
        assert len(results) == 3

        # Check first two rules have content
        assert results[0]["rule_name"] == "rule1.md"
        assert results[0]["content"] == sample_cursor_rule
        assert results[1]["rule_name"] == "rule2.md"
        assert results[1]["content"] == sample_cursor_rule

        # Check nonexistent rule has error information
        assert results[2]["rule_name"] == "nonexistent_rule.md"
        assert results[2]["content"] is None
        assert "not found" in results[2]["error"]


class TestWorkflowFunctions:
    """Tests for workflow orchestration functions."""

    def test_cursor_rules_workflow(self, mocker: "MockerFixture", tmp_path: Path) -> None:
        """Test the complete cursor_rules_workflow function.

        Args:
            mocker: Pytest fixture for mocking
            tmp_path: Pytest fixture providing a temporary directory path

        """
        # Mock the current working directory
        mocker.patch("pathlib.Path.cwd", return_value=tmp_path)

        # Mock all the component functions to return dictionaries
        mock_prep = mocker.patch(
            "codegen_lab.prompt_library.prep_workspace",
            return_value={
                "message": "Workspace prepared",
                "directory_exists": False,
                "directory_path": str(tmp_path / "hack" / "drafts" / "cursor_rules"),
                "mkdir_command": "mkdir -p",
            },
        )

        # Define test rules
        rule_names = ["test-rule"]

        mock_create = mocker.patch(
            "codegen_lab.prompt_library.create_cursor_rule_files",
            return_value={
                "success": True,
                "created_files": [f"{name}.mdc.md" for name in rule_names],
                "message": "Files created",
            },
        )

        mock_ensure = mocker.patch(
            "codegen_lab.prompt_library.ensure_makefile_task",
            return_value={
                "success": True,
                "has_makefile": True,
                "has_update_task": True,
                "action_taken": "none",
                "message": "Makefile task ensured",
            },
        )

        mock_run = mocker.patch(
            "codegen_lab.prompt_library.run_update_cursor_rules",
            return_value={"success": True, "message": "Rules updated"},
        )

        mock_docker = mocker.patch(
            "codegen_lab.prompt_library.update_dockerignore",
            return_value={"success": True, "message": "Dockerignore updated"},
        )

        # Call the function
        result = cursor_rules_workflow(rule_names)

        # Check that all component functions were called
        mock_prep.assert_called_once()
        mock_create.assert_called_once_with(rule_names)
        mock_ensure.assert_called_once()
        mock_docker.assert_called_once()

        # Check that the result combines the results of all functions
        assert result["success"] is True
        assert len(result["created_files"]) == len(rule_names)
        assert "message" in result
        assert "next_steps" in result


class TestPlanAndExecuteWorkflow:
    """Tests for the plan_and_execute_prompt_library_workflow function.

    This test class verifies that the plan_and_execute_prompt_library_workflow function
    correctly orchestrates the cursor rule workflow, including planning, creating,
    and deploying cursor rules.
    """

    def test_plan_and_execute_workflow_success(self, mocker: "MockerFixture") -> None:
        """Test that plan_and_execute_prompt_library_workflow successfully executes the workflow.

        This test verifies that the workflow correctly:
        1. Processes the repository information
        2. Calls the necessary component functions
        3. Returns a successful result with the expected data

        Args:
            mocker: Pytest fixture for mocking

        """
        # Mock the component functions
        mock_repo_analysis = mocker.patch(
            "codegen_lab.prompt_library.repo_analysis_prompt",
            return_value=[
                {"content": [{"text": "Python API"}]},
                {"content": [{"text": "Common patterns"}]},
                {"content": [{"text": "rule-1\nrule-2"}]},
                {"content": [{"text": "Analysis summary"}]},
            ],
        )

        mock_recommend = mocker.patch(
            "codegen_lab.prompt_library.recommend_cursor_rules",
            return_value=[
                {"name": "test-rule-1", "category": "Testing", "priority": "high"},
                {"name": "test-rule-2", "category": "Style", "priority": "medium"},
            ],
        )

        mock_prep_workspace = mocker.patch(
            "codegen_lab.prompt_library.prep_workspace",
            return_value={"status": "success", "directory_structure": "structure"},
        )

        mock_ensure_makefile = mocker.patch(
            "codegen_lab.prompt_library.ensure_makefile_task", return_value={"status": "success"}
        )

        mock_update_dockerignore = mocker.patch(
            "codegen_lab.prompt_library.update_dockerignore", return_value={"status": "success"}
        )

        mock_create_files = mocker.patch(
            "codegen_lab.prompt_library.create_cursor_rule_files",
            return_value={"status": "success", "created_files": ["test_rule_1.mdc.md", "test_rule_2.mdc.md"]},
        )

        # First call with phase 1 to set up the workflow state
        phase1_result = plan_and_execute_prompt_library_workflow(
            repo_description="Test repository",
            main_languages="Python",
            file_patterns="*.py",
            key_features="API, Database",
            phase=1,
        )

        # Verify that repo_analysis_prompt was called
        mock_repo_analysis.assert_called_once()

        # Now call with phase 2 to test recommend_cursor_rules
        result = plan_and_execute_prompt_library_workflow(
            repo_description="Test repository",
            main_languages="Python",
            file_patterns="*.py",
            key_features="API, Database",
            phase=2,
            workflow_state=phase1_result["workflow_state"],
        )

        # Verify that recommend_cursor_rules was called
        mock_recommend.assert_called_once()

        # Verify the result
        assert result["status"] == "complete"
        assert "recommended_rules" in result
        assert "next_phase" in result
        assert result["next_phase"] == 3

    def test_plan_and_execute_workflow_empty_rules(self, mocker: "MockerFixture") -> None:
        """Test workflow execution when no cursor rules are recommended.

        This test verifies that the workflow handles the case where the repository
        analysis doesn't recommend any cursor rules to create.

        Args:
            mocker: Pytest fixture for mocking

        """
        # Mock the component functions
        mock_repo_analysis = mocker.patch(
            "codegen_lab.prompt_library.repo_analysis_prompt",
            return_value=[
                {"content": [{"text": "Python API"}]},
                {"content": [{"text": "Common patterns"}]},
                {"content": [{"text": ""}]},  # Empty rules list
                {"content": [{"text": "Analysis summary"}]},
            ],
        )

        mock_recommend = mocker.patch(
            "codegen_lab.prompt_library.recommend_cursor_rules",
            return_value=[],  # No recommended rules
        )

        # First call with phase 1 to set up the workflow state
        phase1_result = plan_and_execute_prompt_library_workflow(
            repo_description="Test repository",
            main_languages="Python",
            file_patterns="*.py",
            key_features="API, Database",
            phase=1,
        )

        # Verify that repo_analysis_prompt was called
        mock_repo_analysis.assert_called_once()

        # Now call with phase 2 to test recommend_cursor_rules
        result = plan_and_execute_prompt_library_workflow(
            repo_description="Test repository",
            main_languages="Python",
            file_patterns="*.py",
            key_features="API, Database",
            phase=2,
            workflow_state=phase1_result["workflow_state"],
        )

        # Verify that recommend_cursor_rules was called
        mock_recommend.assert_called_once()

        # Verify the result
        assert result["status"] == "complete"
        assert "recommended_rules" in result
        assert len(result["recommended_rules"]) == 0

    def test_plan_and_execute_workflow_failure(self, mocker: "MockerFixture") -> None:
        """Test workflow execution when a component function fails.

        This test verifies that the workflow correctly handles and reports errors
        when a component function fails.

        Args:
            mocker: Pytest fixture for mocking

        """
        # Mock repo_analysis_prompt to raise an exception
        mock_repo_analysis = mocker.patch(
            "codegen_lab.prompt_library.repo_analysis_prompt", side_effect=Exception("Failed to analyze repository")
        )

        # Call the function with required arguments
        result = plan_and_execute_prompt_library_workflow(
            repo_description="Test repository",
            main_languages="Python",
            file_patterns="*.py",
            key_features="API, Database",
        )

        # Verify that the component function was called
        mock_repo_analysis.assert_called_once()

        # Verify the result
        assert result["status"] == "error"
        assert "Error during repository analysis" in result["message"]

    def test_get_cursor_rule_names(self, tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
        """Test retrieving cursor rule names by copying existing rules from the project.

        Args:
            tmp_path: Pytest fixture providing a temporary directory path
            monkeypatch: Pytest fixture for patching objects during testing

        """
        import shutil
        from pathlib import Path

        from codegen_lab.prompt_library import CURSOR_RULES_DIR

        # Create a temporary directory for cursor rules
        cursor_rules_dir = tmp_path / "cursor_rules"
        cursor_rules_dir.mkdir()

        # Path to the project's cursor rules
        source_dir = Path("./hack/drafts/cursor_rules")

        # Copy rules if the source directory exists
        if source_dir.exists():
            # Copy only .mdc files
            for rule_file in source_dir.glob("*.mdc.md"):
                shutil.copy(rule_file, cursor_rules_dir)
        else:
            # If source doesn't exist, create some sample files
            (cursor_rules_dir / "sample1.mdc.md").write_text("# Sample rule 1")
            (cursor_rules_dir / "sample2.mdc.md").write_text("# Sample rule 2")

        # Temporarily patch the CURSOR_RULES_DIR to point to our test directory
        monkeypatch.setattr("codegen_lab.prompt_library.CURSOR_RULES_DIR", cursor_rules_dir)

        # Call the function under test
        rule_names = get_cursor_rule_names()

        # Verify results
        assert len(rule_names) > 0
        # Verify all names correspond to .mdc files
        for name in rule_names:
            assert (cursor_rules_dir / f"{name}.mdc.md").exists()

    def test_read_cursor_rule_existing(self, mocker: "MockerFixture", tmp_path: Path) -> None:
        """Test that read_cursor_rule correctly reads an existing cursor rule.

        Args:
            mocker: Pytest fixture for mocking
            tmp_path: Pytest fixture providing a temporary directory path

        """
        # Mock the current working directory
        mocker.patch("pathlib.Path.cwd", return_value=tmp_path)

        # Create a mock cursor rules directory with a test file
        cursor_rules_dir = tmp_path / "hack" / "drafts" / "cursor_rules"
        cursor_rules_dir.mkdir(parents=True, exist_ok=True)

        # Create a test rule file
        rule_content = "# Test Rule\n\nThis is a test rule."
        rule_file = cursor_rules_dir / "test-rule.mdc.md"
        rule_file.write_text(rule_content)

        # Call the function
        result = read_cursor_rule("test-rule")

        # Verify the result
        assert result == rule_content

    def test_read_cursor_rule_nonexistent(self, mocker: "MockerFixture", tmp_path: Path) -> None:
        """Test that read_cursor_rule handles nonexistent rules correctly.

        Args:
            mocker: Pytest fixture for mocking
            tmp_path: Pytest fixture providing a temporary directory path

        """
        # Mock the current working directory
        mocker.patch("pathlib.Path.cwd", return_value=tmp_path)

        # Create a mock cursor rules directory without the test file
        cursor_rules_dir = tmp_path / "hack" / "drafts" / "cursor_rules"
        cursor_rules_dir.mkdir(parents=True, exist_ok=True)

        # Call the function
        result = read_cursor_rule("nonexistent-rule")

        # Verify the result
        assert result is None

    @pytest.mark.anyio
    async def test_recommend_cursor_rules(self, mocker: "MockerFixture") -> None:
        """Test that the recommend_cursor_rules tool generates recommendations.

        Args:
            mocker: Pytest fixture for mocking

        """
        # Mock the Context object
        mock_context = mocker.MagicMock()
        mocker.patch("codegen_lab.prompt_library.Context", return_value=mock_context)

        async with client_session(mcp._mcp_server) as client:
            result = await client.call_tool(
                "recommend_cursor_rules",
                {"repo_summary": "A Python project with FastAPI, SQLAlchemy, and React frontend."},
            )

            # Verify the result
            assert len(result.content) > 0
            content = result.content[0]
            assert isinstance(content, TextContent)
            assert "recommendations" in content.text.lower()
            assert "fastapi" in content.text.lower()
            assert "sqlalchemy" in content.text.lower()
            assert "react" in content.text.lower()

    @pytest.mark.anyio
    async def test_recommend_cursor_rules_empty_summary(self, mocker: "MockerFixture") -> None:
        """Test that the recommend_cursor_rules tool handles empty summaries.

        Args:
            mocker: Pytest fixture for mocking

        """
        # Mock the Context object
        mock_context = mocker.MagicMock()
        mocker.patch("codegen_lab.prompt_library.Context", return_value=mock_context)

        async with client_session(mcp._mcp_server) as client:
            result = await client.call_tool("recommend_cursor_rules", {"repo_summary": ""})

            # Verify the result
            assert len(result.content) > 0
            content = result.content[0]
            assert isinstance(content, TextContent)
            assert "empty" in content.text.lower() or "insufficient" in content.text.lower()
