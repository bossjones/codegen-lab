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
    CURSOR_RULES_DIR,
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
        str: A sample cursor rule content

    """
    return """---
description: Test Rule
globs: *.py
alwaysApply: false
---
# Test Rule

This is a test cursor rule.

<rule>
name: test_rule
description: A test rule for testing
filters:
  - type: file_extension
    pattern: "\\.py$"
actions:
  - type: suggest
    message: |
      This is a test suggestion.
</rule>
"""


@pytest.mark.anyio
async def test_get_static_cursor_rule_integration() -> None:
    """Test the get_static_cursor_rule function through the MCP server.

    This integration test verifies that the get_static_cursor_rule function
    can be called through the MCP server and returns the expected result
    using a real cursor rule file (tree.mdc.md).
    """
    # Create an in-memory client-server connection
    async with client_session(mcp._mcp_server) as client:
        # Use the real tree.mdc rule
        rule_name = "tree"

        # Call the get_static_cursor_rule tool
        result = await client.call_tool("get_static_cursor_rule", {"rule_name": rule_name})

        # Verify the result
        assert len(result.content) == 1
        content = result.content[0]
        assert isinstance(content, TextContent)

        # Parse the JSON response
        response_data = json.loads(content.text)

        # Verify the response structure
        assert "rule_name" in response_data
        assert "content" in response_data
        assert response_data["rule_name"] == "tree.md"

        # Verify the content contains the expected tree command
        assert "tree -L 7 -I" in response_data["content"]
        assert "Display repository structure" in response_data["content"]

        # Test with non-existent rule - this should return an error message in the response
        nonexistent_result = await client.call_tool("get_static_cursor_rule", {"rule_name": "nonexistent_rule"})

        # Verify the result
        assert len(nonexistent_result.content) == 1
        nonexistent_content = nonexistent_result.content[0]
        assert isinstance(nonexistent_content, TextContent)

        # Parse the JSON response
        nonexistent_response = json.loads(nonexistent_content.text)

        # Verify the error structure
        assert "isError" in nonexistent_response
        assert nonexistent_response["isError"] is True
        assert "content" in nonexistent_response
        assert isinstance(nonexistent_response["content"], list)
        assert len(nonexistent_response["content"]) == 1
        assert nonexistent_response["content"][0]["type"] == "text"
        assert "Error: Static cursor rule 'nonexistent_rule' not found" in nonexistent_response["content"][0]["text"]


@pytest.mark.anyio
async def test_get_static_cursor_rules_integration() -> None:
    """Test the get_static_cursor_rules function through the MCP server.

    This integration test verifies that the get_static_cursor_rules function
    can be called through the MCP server and returns the expected results,
    including handling of both existing and non-existent rules using real cursor rules.
    """
    # Create an in-memory client-server connection
    async with client_session(mcp._mcp_server) as client:
        # Use real cursor rules: "tree" and "notify"
        rule_names = ["tree", "notify"]

        # Call the get_static_cursor_rules tool
        result = await client.call_tool("get_static_cursor_rules", {"rule_names": rule_names})

        # Verify the result
        assert len(result.content) == 1
        content = result.content[0]
        assert isinstance(content, TextContent)

        # Parse the JSON response
        response_data = json.loads(content.text)

        # Verify the response structure
        assert "rules" in response_data
        assert isinstance(response_data["rules"], list)
        assert len(response_data["rules"]) == 2

        # Check the first rule (tree)
        assert response_data["rules"][0]["rule_name"] == "tree.md"
        assert "tree -L 7 -I" in response_data["rules"][0]["content"]
        assert "Display repository structure" in response_data["rules"][0]["content"]

        # Check the second rule (notify)
        assert response_data["rules"][1]["rule_name"] == "notify.md"
        assert "At the end of any task" in response_data["rules"][1]["content"]

        # Test with a mix of existing and non-existent rules
        mixed_rule_names = ["tree", "nonexistent_rule"]

        # Call the get_static_cursor_rules tool with mixed rules
        mixed_result = await client.call_tool("get_static_cursor_rules", {"rule_names": mixed_rule_names})

        # Verify the result
        assert len(mixed_result.content) == 1
        mixed_content = mixed_result.content[0]
        assert isinstance(mixed_content, TextContent)

        # Parse the JSON response
        mixed_response_data = json.loads(mixed_content.text)

        # Verify the response structure
        assert "rules" in mixed_response_data
        assert isinstance(mixed_response_data["rules"], list)
        assert len(mixed_response_data["rules"]) == 2

        # Check the first rule (tree)
        assert mixed_response_data["rules"][0]["rule_name"] == "tree.md"
        assert "tree -L 7 -I" in mixed_response_data["rules"][0]["content"]

        # Check the non-existent rule - should have isError and content fields
        assert mixed_response_data["rules"][1]["isError"] is True
        assert isinstance(mixed_response_data["rules"][1]["content"], list)
        assert len(mixed_response_data["rules"][1]["content"]) == 1
        assert mixed_response_data["rules"][1]["content"][0]["type"] == "text"
        assert (
            "Error: Static cursor rule 'nonexistent_rule' not found"
            in mixed_response_data["rules"][1]["content"][0]["text"]
        )
