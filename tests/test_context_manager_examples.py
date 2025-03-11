"""Examples of using the temporary MCP environment context manager.

This module demonstrates how to use the temporary MCP environment
context manager for more concise and readable tests.
"""

from typing import TYPE_CHECKING, Any, Dict, Optional

import pytest

from tests.helpers.test_fixtures import temp_mcp_environment

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture


# Sample MCP tool function
def update_config_file(config_path: str, settings: dict[str, Any]) -> dict[str, Any]:
    """Update settings in a configuration file.

    Args:
        config_path: Path to the configuration file
        settings: Settings to update

    Returns:
        Dictionary with operations to update the configuration file

    """
    return {
        "operations": [
            {
                "type": "check_file_exists",
                "path": config_path,
                "content": None,
                "args": None,
                "kwargs": None,
            },
            {
                "type": "read_file",
                "path": config_path,
                "content": None,
                "args": None,
                "kwargs": {"encoding": "utf-8"},
            },
            {
                "type": "write_file",
                "path": config_path,
                "content": "# Updated Configuration\n" + "\n".join([f"{k} = {v}" for k, v in settings.items()]),
                "args": None,
                "kwargs": {"encoding": "utf-8"},
            },
        ],
        "requires_result": True,
        "message": f"Instructions to update configuration file {config_path}",
    }


def test_update_config_with_context_manager() -> None:
    """Test updating a configuration file using the context manager."""
    # Initial file content
    initial_files = {"config.ini": "# Configuration\nport = 8080\nhost = localhost"}

    # Use the context manager for a cleaner test
    with temp_mcp_environment(initial_files=initial_files) as env:
        # Get the client from the environment
        client = env["client"]
        base_dir = env["base_dir"]

        # Call the tool via the client
        new_settings = {"port": 9000, "host": "127.0.0.1", "debug": True}

        result = client.call_tool(update_config_file, config_path="config.ini", settings=new_settings)

        # Verify the file was updated
        config_path = base_dir / "config.ini"
        assert config_path.exists()

        # Read the updated content
        content = config_path.read_text()
        assert "# Updated Configuration" in content
        assert "port = 9000" in content
        assert "host = 127.0.0.1" in content
        assert "debug = True" in content


def test_file_not_found_with_context_manager() -> None:
    """Test handling a file not found situation using the context manager."""
    # Use the context manager with no initial files
    with temp_mcp_environment() as env:
        # Get the client from the environment
        client = env["client"]

        # Call the tool via the client with a non-existent file
        new_settings = {"port": 9000}
        result = client.call_tool(update_config_file, config_path="non_existent.ini", settings=new_settings)

        # Verify the result indicates the file doesn't exist
        assert "non_existent.ini" in result
        file_exists_result = result.get("non_existent.ini")
        assert file_exists_result is not None
        assert file_exists_result.get("type") == "file_exists"
        assert file_exists_result.get("exists") is False
