# """Unit tests for promptlib prompts.

# This test suite verifies the behavior of MCP prompts for cursor rule generation.
# """

# from pathlib import Path
# from typing import TYPE_CHECKING, Dict, List, Optional

# import pytest
# from mcp.server.fastmcp import FastMCP
# from mcp.server.fastmcp.testing import client_session

# from codegen_lab.promptlib.prompts import (
#     generate_cursor_rule_prompt,
#     repo_analysis_prompt,
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
#     (workspace / "src" / "main.py").write_text("""
# def main():
#     print("Hello, World!")
#     """)

#     (workspace / "src" / "utils.py").write_text("""
# def helper_function():
#     pass
#     """)

#     return workspace


# @pytest.fixture
# def mcp_server(temp_workspace: Path) -> FastMCP:
#     """Create a FastMCP server instance with cursor rule prompts.

#     Args:
#         temp_workspace: Fixture providing a temporary workspace.

#     Returns:
#         FastMCP: A configured FastMCP server instance.

#     """
#     server = FastMCP()

#     @server.prompt()
#     def analyze_repo(repo_path: str) -> str:
#         """Generate repository analysis prompt."""
#         return repo_analysis_prompt(repo_path)

#     @server.prompt()
#     def generate_rule(
#         rule_name: str,
#         description: str,
#         file_patterns: list[str],
#     ) -> str:
#         """Generate cursor rule creation prompt."""
#         return generate_cursor_rule_prompt(rule_name, description, file_patterns)

#     return server


# @pytest.mark.anyio
# async def test_repo_analysis_prompt(
#     mcp_server: FastMCP,
#     temp_workspace: Path,
# ) -> None:
#     """Test the repository analysis prompt generation.

#     Args:
#         mcp_server: Fixture providing a configured FastMCP server.
#         temp_workspace: Fixture providing a temporary workspace.

#     """
#     async with client_session(mcp_server._mcp_server) as client:
#         result = await client.call_prompt("analyze_repo", {"repo_path": str(temp_workspace)})
#         assert not result.isError
#         prompt = result.content[0].text

#         # Verify prompt contains key elements
#         assert "repository structure" in prompt.lower()
#         assert "main.py" in prompt
#         assert "utils.py" in prompt
#         assert "analyze" in prompt.lower()


# @pytest.mark.anyio
# async def test_generate_cursor_rule_prompt(
#     mcp_server: FastMCP,
#     temp_workspace: Path,
# ) -> None:
#     """Test the cursor rule generation prompt.

#     Args:
#         mcp_server: Fixture providing a configured FastMCP server.
#         temp_workspace: Fixture providing a temporary workspace.

#     """
#     async with client_session(mcp_server._mcp_server) as client:
#         result = await client.call_prompt(
#             "generate_rule",
#             {"rule_name": "python-style", "description": "Python code style guidelines", "file_patterns": ["\\.py$"]},
#         )
#         assert not result.isError
#         prompt = result.content[0].text

#         # Verify prompt contains key elements
#         assert "python-style" in prompt
#         assert "Python code style guidelines" in prompt
#         assert "\\.py$" in prompt
#         assert "<rule>" in prompt


# @pytest.mark.anyio
# async def test_repo_analysis_prompt_empty_repo(
#     mcp_server: FastMCP,
#     tmp_path: Path,
# ) -> None:
#     """Test repository analysis prompt with an empty repository.

#     Args:
#         mcp_server: Fixture providing a configured FastMCP server.
#         tmp_path: Pytest fixture providing a temporary directory.

#     """
#     empty_repo = tmp_path / "empty_repo"
#     empty_repo.mkdir()

#     async with client_session(mcp_server._mcp_server) as client:
#         result = await client.call_prompt("analyze_repo", {"repo_path": str(empty_repo)})
#         assert not result.isError
#         prompt = result.content[0].text

#         # Verify prompt handles empty repository
#         assert "empty" in prompt.lower()
#         assert "repository" in prompt.lower()


# @pytest.mark.anyio
# async def test_generate_cursor_rule_prompt_multiple_patterns(
#     mcp_server: FastMCP,
#     temp_workspace: Path,
# ) -> None:
#     """Test cursor rule generation prompt with multiple file patterns.

#     Args:
#         mcp_server: Fixture providing a configured FastMCP server.
#         temp_workspace: Fixture providing a temporary workspace.

#     """
#     async with client_session(mcp_server._mcp_server) as client:
#         result = await client.call_prompt(
#             "generate_rule",
#             {
#                 "rule_name": "web-frontend",
#                 "description": "Web frontend best practices",
#                 "file_patterns": ["\\.js$", "\\.ts$", "\\.jsx$", "\\.tsx$"],
#             },
#         )
#         assert not result.isError
#         prompt = result.content[0].text

#         # Verify prompt contains all patterns
#         assert "web-frontend" in prompt
#         assert "Web frontend best practices" in prompt
#         assert all(pattern in prompt for pattern in ["\\.js$", "\\.ts$", "\\.jsx$", "\\.tsx$"])
#         assert "<rule>" in prompt


# @pytest.mark.anyio
# async def test_generate_cursor_rule_prompt_invalid_name(
#     mcp_server: FastMCP,
#     temp_workspace: Path,
# ) -> None:
#     """Test cursor rule generation prompt with invalid rule name.

#     Args:
#         mcp_server: Fixture providing a configured FastMCP server.
#         temp_workspace: Fixture providing a temporary workspace.

#     """
#     async with client_session(mcp_server._mcp_server) as client:
#         result = await client.call_prompt(
#             "generate_rule",
#             {
#                 "rule_name": "Invalid Rule Name!",  # Contains spaces and special characters
#                 "description": "Test description",
#                 "file_patterns": ["\\.py$"],
#             },
#         )
#         assert result.isError
#         assert "Invalid rule name" in result.error.message
