# """Unit tests for promptlib tools.

# This test suite verifies the behavior of MCP tools for cursor rule operations.
# It covers repository analysis, rule generation, rule management, and workspace setup.
# """

# import os
# from pathlib import Path
# from typing import TYPE_CHECKING, Dict, List, Optional

# import pytest
# from mcp.server.fastmcp import FastMCP

# # from mcp.server.fastmcp.testing import client_session
# from codegen_lab.promptlib.tools import (
#     create_cursor_rule_files,
#     cursor_rules_workflow,
#     ensure_ai_report,
#     ensure_makefile_task,
#     get_static_cursor_rule,
#     get_static_cursor_rules,
#     instruct_custom_repo_rules_generation,
#     instruct_repo_analysis,
#     prep_workspace,
#     recommend_cursor_rules,
#     run_update_cursor_rules,
#     save_cursor_rule,
#     update_dockerignore,
# )

# if TYPE_CHECKING:
#     from _pytest.capture import CaptureFixture
#     from _pytest.fixtures import FixtureRequest
#     from _pytest.logging import LogCaptureFixture
#     from _pytest.monkeypatch import MonkeyPatch
#     from pytest_mock.plugin import MockerFixture


# @pytest.fixture
# def temp_workspace(tmp_path: Path) -> Path:
#     """Create a temporary workspace with sample repository structure.

#     Args:
#         tmp_path: Pytest fixture providing a temporary directory.

#     Returns:
#         Path: Path to the temporary workspace.

#     """
#     workspace = tmp_path / "workspace"
#     workspace.mkdir()

#     # Create basic repository structure
#     (workspace / "src").mkdir()
#     (workspace / ".cursor" / "rules").mkdir(parents=True)
#     (workspace / ".github" / "workflows").mkdir(parents=True)

#     # Create sample files
#     (workspace / "Makefile").write_text("""
# .PHONY: help
# help:
#     @echo "Available targets:"
#     """)

#     (workspace / "src" / "main.py").write_text("""
# def main():
#     print("Hello, World!")
#     """)

#     return workspace


# @pytest.fixture
# def mcp_server(temp_workspace: Path) -> FastMCP:
#     """Create a FastMCP server instance with cursor rule tools.

#     Args:
#         temp_workspace: Fixture providing a temporary workspace.

#     Returns:
#         FastMCP: A configured FastMCP server instance.

#     """
#     server = FastMCP()

#     @server.tool()
#     def analyze_repo() -> dict:
#         """Run repository analysis."""
#         return instruct_repo_analysis(temp_workspace)

#     @server.tool()
#     def generate_rules(report_path: str) -> dict:
#         """Generate custom cursor rules."""
#         return instruct_custom_repo_rules_generation(temp_workspace, report_path)

#     @server.tool()
#     def get_rule(rule_name: str) -> str:
#         """Get a static cursor rule."""
#         return get_static_cursor_rule(rule_name)

#     @server.tool()
#     def get_rules(rule_names: list[str], ignore_missing: bool = False) -> list[str]:
#         """Get multiple static cursor rules."""
#         return get_static_cursor_rules(rule_names, ignore_missing)

#     @server.tool()
#     def save_rule(rule_name: str, rule_content: str, overwrite: bool = True) -> bool:
#         """Save a cursor rule."""
#         return save_cursor_rule(temp_workspace, rule_name, rule_content, overwrite)

#     return server


# @pytest.mark.anyio
# async def test_instruct_repo_analysis(
#     mcp_server: FastMCP,
#     temp_workspace: Path,
# ) -> None:
#     """Test the repository analysis tool.

#     This test verifies that the repository analysis tool:
#     1. Successfully analyzes a basic repository structure
#     2. Returns a valid analysis result with repository structure
#     3. Properly identifies Python files in the workspace

#     Args:
#         mcp_server: Fixture providing a configured FastMCP server.
#         temp_workspace: Fixture providing a temporary workspace.

#     """
#     async with client_session(mcp_server._mcp_server) as client:
#         result = await client.call_tool("analyze_repo")
#         assert not result.isError
#         analysis = result.content[0].text
#         assert "repository_structure" in analysis
#         assert "main.py" in str(analysis["repository_structure"])


# @pytest.mark.anyio
# async def test_generate_custom_rules(
#     mcp_server: FastMCP,
#     temp_workspace: Path,
# ) -> None:
#     """Test the custom rules generation tool.

#     This test verifies that the rule generation tool:
#     1. Successfully reads an AI analysis report
#     2. Generates appropriate cursor rules based on the report
#     3. Returns a valid list of generated rules

#     Edge cases covered:
#     - Basic repository structure with minimal files
#     - Simple AI report format

#     Args:
#         mcp_server: Fixture providing a configured FastMCP server.
#         temp_workspace: Fixture providing a temporary workspace.

#     """
#     report_path = "ai_report.md"
#     (temp_workspace / report_path).write_text("""# AI Analysis Report

# Repository contains Python code with basic structure.
#     """)

#     async with client_session(mcp_server._mcp_server) as client:
#         result = await client.call_tool("generate_rules", {"report_path": report_path})
#         assert not result.isError
#         rules = result.content[0].text
#         assert isinstance(rules, list)
#         assert len(rules) > 0


# @pytest.mark.anyio
# async def test_get_static_cursor_rule(
#     mcp_server: FastMCP,
#     temp_workspace: Path,
# ) -> None:
#     """Test getting a static cursor rule.

#     This test verifies that:
#     1. Static cursor rules can be retrieved by name
#     2. Retrieved rules contain valid rule syntax
#     3. Rule content matches expected format

#     Edge cases covered:
#     - Rule exists and is properly formatted
#     - Rule contains all required sections (name, description, filters, actions)

#     Args:
#         mcp_server: Fixture providing a configured FastMCP server.
#         temp_workspace: Fixture providing a temporary workspace.

#     """
#     async with client_session(mcp_server._mcp_server) as client:
#         result = await client.call_tool("get_rule", {"rule_name": "python-best-practices"})
#         assert not result.isError
#         rule_content = result.content[0].text
#         assert "<rule>" in rule_content
#         assert "name: python-best-practices" in rule_content


# @pytest.mark.anyio
# async def test_save_cursor_rule(
#     mcp_server: FastMCP,
#     temp_workspace: Path,
# ) -> None:
#     """Test saving a cursor rule.

#     This test verifies that:
#     1. Rules can be saved to the workspace
#     2. Saved rules are written with correct content
#     3. Rule files are created in the proper location
#     4. Overwrite parameter is respected

#     Edge cases covered:
#     - New rule creation
#     - Rule overwrite with overwrite=True
#     - Proper file permissions and structure

#     Args:
#         mcp_server: Fixture providing a configured FastMCP server.
#         temp_workspace: Fixture providing a temporary workspace.

#     """
#     rule_content = """# Test Rule

# <rule>
# name: test-rule
# description: Test rule description
# filters:
#   - type: file_extension
#     pattern: \\.py$
# actions:
#   - type: suggest
#     message: Test message
# </rule>
# """

#     async with client_session(mcp_server._mcp_server) as client:
#         result = await client.call_tool(
#             "save_rule", {"rule_name": "test-rule", "rule_content": rule_content, "overwrite": True}
#         )
#         assert not result.isError
#         assert result.content[0].text is True

#         # Verify file was created
#         rule_file = temp_workspace / ".cursor" / "rules" / "test-rule.mdc"
#         assert rule_file.exists()
#         assert rule_file.read_text() == rule_content


# # @pytest.mark.anyio
# # async def test_get_static_cursor_rule_nonexistent(
# #     mcp_server: FastMCP,
# #     temp_workspace: Path,
# # ) -> None:
# #     """Test getting a nonexistent static cursor rule.

# #     Args:
# #         mcp_server: Fixture providing a configured FastMCP server.
# #         temp_workspace: Fixture providing a temporary workspace.

# #     """
# #     async with client_session(mcp_server._mcp_server) as client:
# #         result = await client.call_tool("get_rule", {"rule_name": "nonexistent-rule"})
# #         assert result.isError
# #         assert "Rule not found" in result.error.message


# # @pytest.mark.anyio
# # async def test_save_cursor_rule_no_overwrite(
# #     mcp_server: FastMCP,
# #     temp_workspace: Path,
# # ) -> None:
# #     """Test saving a cursor rule without overwriting.

# #     Args:
# #         mcp_server: Fixture providing a configured FastMCP server.
# #         temp_workspace: Fixture providing a temporary workspace.

# #     """
# #     rule_content = """# Test Rule

# # <rule>
# # name: test-rule
# # description: Test rule description
# # filters:
# #   - type: file_extension
# #     pattern: \\.py$
# # actions:
# #   - type: suggest
# #     message: Original message
# # </rule>
# # """

# #     # Create initial rule
# #     rule_file = temp_workspace / ".cursor" / "rules" / "test-rule.mdc"
# #     rule_file.write_text(rule_content)

# #     # Try to save new content without overwrite
# #     new_content = rule_content.replace("Original message", "New message")

# #     async with client_session(mcp_server._mcp_server) as client:
# #         result = await client.call_tool(
# #             "save_rule", {"rule_name": "test-rule", "rule_content": new_content, "overwrite": False}
# #         )
# #         assert result.isError
# #         assert "Rule already exists" in result.error.message

# #         # Verify original content was preserved
# #         assert rule_file.read_text() == rule_content
