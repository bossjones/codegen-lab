import json
from typing import TYPE_CHECKING, Any, Dict

import pytest
from mcp.shared.memory import create_connected_server_and_client_session as client_session
from mcp.types import TextContent

from codegen_lab.prompt_library import mcp

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture


class TestInstructRepoAnalysis:
    """Tests for the instruct_repo_analysis tool."""

    @pytest.mark.anyio
    async def test_instruct_repo_analysis(self, mocker: "MockerFixture") -> None:
        """Test that the instruct_repo_analysis tool returns the expected structure.

        This test verifies that the tool returns a properly structured dictionary
        with instructions for repository analysis.

        Args:
            mocker: Pytest fixture for mocking

        """
        # Mock the Context object if needed
        mock_context = mocker.MagicMock()
        mocker.patch("codegen_lab.prompt_library.Context", return_value=mock_context)

        async with client_session(mcp._mcp_server) as client:
            # Call the tool
            result = await client.call_tool("instruct_repo_analysis", {})

            # Verify the result structure
            assert result is not None
            assert len(result.content) > 0
            content = result.content[0]
            assert isinstance(content, TextContent)

            # Parse the text content - it's a JSON string, not a dict
            text_data_str = content.text
            assert isinstance(text_data_str, str)

            # Parse the JSON string into a dictionary
            parsed_data = json.loads(text_data_str)
            assert isinstance(parsed_data, dict)

            # Extract the content from the parsed data
            assert "content" in parsed_data
            assert len(parsed_data["content"]) > 0
            assert parsed_data["content"][0]["type"] == "text"

            # Get the actual data from the content
            text_data = parsed_data["content"][0]["text"]
            assert isinstance(text_data, dict)

            # Verify the expected fields are present
            assert "status" in text_data
            assert text_data["status"] == "success"

            assert "message" in text_data
            assert "Repository Analysis Instructions" in text_data["message"]

            assert "repository_analysis" in text_data
            assert text_data["repository_analysis"] is True

            assert "analysis_rule" in text_data
            assert text_data["analysis_rule"] == "./.cursor/rules/repo_analyzer.mdc"

            assert "processing_method" in text_data
            assert text_data["processing_method"] == "sequentialthinking"

            assert "output_file" in text_data
            assert text_data["output_file"] == "ai_report.md"

            assert "required_parameters" in text_data
            assert isinstance(text_data["required_parameters"], list)
            assert "main_languages" in text_data["required_parameters"]
            assert "frameworks" in text_data["required_parameters"]
            assert "packages" in text_data["required_parameters"]
            assert "dev_packages" in text_data["required_parameters"]
            assert "testing" in text_data["required_parameters"]

            assert "analysis_status" in text_data
            assert isinstance(text_data["analysis_status"], dict)
            assert text_data["analysis_status"]["status"] == "pending"
            assert "message" in text_data["analysis_status"]
            assert text_data["analysis_status"]["rule_exists"] is True
            assert text_data["analysis_status"]["rule_path"] == "./.cursor/rules/repo_analyzer.mdc"
            assert text_data["analysis_status"]["output_destination"] == "ai_report.md"

            # Verify isError is False
            assert not result.isError

    @pytest.mark.anyio
    async def test_instruct_repo_analysis_rule_not_found(self, mocker: "MockerFixture") -> None:
        """Test that the instruct_repo_analysis tool handles missing rule file correctly.

        This test verifies that the tool returns a properly structured dictionary
        with appropriate status when the repo_analyzer.mdc rule doesn't exist.

        Args:
            mocker: Pytest fixture for mocking

        """
        # Mock the Context object if needed
        mock_context = mocker.MagicMock()
        mocker.patch("codegen_lab.prompt_library.Context", return_value=mock_context)

        # Mock the rule existence check to return False
        # We need to be more specific with our patching to ensure it affects the right call
        original_exists = mocker.patch("os.path.exists")

        # Make exists return False only for the repo_analyzer.mdc file
        def mock_exists(path: str) -> bool:
            if "repo_analyzer.mdc" in path:
                return False
            return True

        original_exists.side_effect = mock_exists

        async with client_session(mcp._mcp_server) as client:
            # Call the tool
            result = await client.call_tool("instruct_repo_analysis", {})

            # Verify the result structure
            assert result is not None
            assert len(result.content) > 0
            content = result.content[0]
            assert isinstance(content, TextContent)

            # Parse the text content - it's a JSON string, not a dict
            text_data_str = content.text
            assert isinstance(text_data_str, str)

            # Parse the JSON string into a dictionary
            parsed_data = json.loads(text_data_str)
            assert isinstance(parsed_data, dict)

            # Extract the content from the parsed data
            assert "content" in parsed_data
            assert len(parsed_data["content"]) > 0
            assert parsed_data["content"][0]["type"] == "text"

            # Get the actual data from the content
            text_data = parsed_data["content"][0]["text"]
            assert isinstance(text_data, dict)

            # Verify the expected fields are present
            assert "status" in text_data
            assert text_data["status"] == "success"  # Status should still be success

            assert "message" in text_data
            assert "Repository Analysis Instructions" in text_data["message"]

            assert "repository_analysis" in text_data
            assert text_data["repository_analysis"] is True

            assert "analysis_rule" in text_data
            assert text_data["analysis_rule"] == "./.cursor/rules/repo_analyzer.mdc"

            # Verify analysis_status shows rule doesn't exist
            assert "analysis_status" in text_data
            assert isinstance(text_data["analysis_status"], dict)
            assert text_data["analysis_status"]["status"] == "pending"
            assert "message" in text_data["analysis_status"]
            assert text_data["analysis_status"]["rule_exists"] is False
            assert text_data["analysis_status"]["rule_path"] == "./.cursor/rules/repo_analyzer.mdc"

            # Verify isError is False - this is not an error condition, just a status
            assert not result.isError
