# """Unit tests for promptlib resources.

# This test suite verifies the behavior of MCP resources for cursor rule operations.
# """

# from pathlib import Path
# from typing import TYPE_CHECKING, Dict, List, Optional

# import pytest
# from mcp.server.fastmcp import FastMCP
# from mcp.server.fastmcp.testing import client_session

# from codegen_lab.promptlib.resources import (
#     get_cursor_rule,
#     get_cursor_rule_raw,
#     list_cursor_rules,
# )

# if TYPE_CHECKING:
#     from _pytest.capture import CaptureFixture
#     from _pytest.fixtures import FixtureRequest
#     from _pytest.logging import LogCaptureFixture
#     from _pytest.monkeypatch import MonkeyPatch
#     from pytest_mock.plugin import MockerFixture


# @pytest.fixture
# def temp_rules_dir(tmp_path: Path) -> Path:
#     """Create a temporary directory with sample cursor rules.

#     Args:
#         tmp_path: Pytest fixture providing a temporary directory.

#     Returns:
#         Path: Path to the temporary rules directory.

#     """
#     rules_dir = tmp_path / ".cursor" / "rules"
#     rules_dir.mkdir(parents=True)

#     # Create sample rule files
#     rule1 = rules_dir / "python-best-practices.mdc"
#     rule2 = rules_dir / "typescript-patterns.mdc"

#     rule1.write_text("""# Python Best Practices

# <rule>
# name: python-best-practices
# description: Enforces Python best practices
# filters:
#   - type: file_extension
#     pattern: \\.py$
# actions:
#   - type: suggest
#     message: Follow Python best practices
# </rule>
# """)

#     rule2.write_text("""# TypeScript Patterns

# <rule>
# name: typescript-patterns
# description: TypeScript design patterns
# filters:
#   - type: file_extension
#     pattern: \\.ts$
# actions:
#   - type: suggest
#     message: Follow TypeScript patterns
# </rule>
# """)

#     return rules_dir


# @pytest.fixture
# def mcp_server(temp_rules_dir: Path) -> FastMCP:
#     """Create a FastMCP server instance with cursor rule resources.

#     Args:
#         temp_rules_dir: Fixture providing a temporary rules directory.

#     Returns:
#         FastMCP: A configured FastMCP server instance.

#     """
#     server = FastMCP()

#     @server.resource()
#     def list_rules() -> list[str]:
#         """List available cursor rules."""
#         return list_cursor_rules(temp_rules_dir)

#     @server.resource()
#     def get_rule(name: str) -> dict:
#         """Get a parsed cursor rule by name."""
#         return get_cursor_rule(temp_rules_dir, name)

#     @server.resource()
#     def get_rule_raw(name: str) -> str:
#         """Get raw cursor rule content by name."""
#         return get_cursor_rule_raw(temp_rules_dir, name)

#     return server


# @pytest.mark.anyio
# async def test_list_cursor_rules_resource(
#     mcp_server: FastMCP,
#     temp_rules_dir: Path,
# ) -> None:
#     """Test the list_cursor_rules resource.

#     Args:
#         mcp_server: Fixture providing a configured FastMCP server.
#         temp_rules_dir: Fixture providing a temporary rules directory.

#     """
#     async with client_session(mcp_server._mcp_server) as client:
#         result = await client.call_resource("list_rules")
#         assert not result.isError
#         rules = result.content[0].text
#         assert "python-best-practices" in rules
#         assert "typescript-patterns" in rules


# @pytest.mark.anyio
# async def test_get_cursor_rule_resource(
#     mcp_server: FastMCP,
#     temp_rules_dir: Path,
# ) -> None:
#     """Test the get_cursor_rule resource.

#     Args:
#         mcp_server: Fixture providing a configured FastMCP server.
#         temp_rules_dir: Fixture providing a temporary rules directory.

#     """
#     async with client_session(mcp_server._mcp_server) as client:
#         result = await client.call_resource("get_rule", {"name": "python-best-practices"})
#         assert not result.isError
#         rule = result.content[0].text
#         assert rule["name"] == "python-best-practices"
#         assert rule["description"] == "Enforces Python best practices"
#         assert rule["filters"][0]["pattern"] == "\\.py$"


# @pytest.mark.anyio
# async def test_get_cursor_rule_raw_resource(
#     mcp_server: FastMCP,
#     temp_rules_dir: Path,
# ) -> None:
#     """Test the get_cursor_rule_raw resource.

#     Args:
#         mcp_server: Fixture providing a configured FastMCP server.
#         temp_rules_dir: Fixture providing a temporary rules directory.

#     """
#     async with client_session(mcp_server._mcp_server) as client:
#         result = await client.call_resource("get_rule_raw", {"name": "python-best-practices"})
#         assert not result.isError
#         content = result.content[0].text
#         assert "# Python Best Practices" in content
#         assert "<rule>" in content
#         assert "name: python-best-practices" in content


# @pytest.mark.anyio
# async def test_get_cursor_rule_nonexistent(
#     mcp_server: FastMCP,
#     temp_rules_dir: Path,
# ) -> None:
#     """Test getting a nonexistent cursor rule.

#     Args:
#         mcp_server: Fixture providing a configured FastMCP server.
#         temp_rules_dir: Fixture providing a temporary rules directory.

#     """
#     async with client_session(mcp_server._mcp_server) as client:
#         result = await client.call_resource("get_rule", {"name": "nonexistent-rule"})
#         assert result.isError
#         assert "Rule not found" in result.error.message


# @pytest.mark.anyio
# async def test_get_cursor_rule_raw_nonexistent(
#     mcp_server: FastMCP,
#     temp_rules_dir: Path,
# ) -> None:
#     """Test getting raw content of a nonexistent cursor rule.

#     Args:
#         mcp_server: Fixture providing a configured FastMCP server.
#         temp_rules_dir: Fixture providing a temporary rules directory.

#     """
#     async with client_session(mcp_server._mcp_server) as client:
#         result = await client.call_resource("get_rule_raw", {"name": "nonexistent-rule"})
#         assert result.isError
#         assert "Rule not found" in result.error.message
