"""Tests for the API module."""

import json
import tempfile
from pathlib import Path
from typing import Dict, Any, Generator, List, Optional, Callable
if True:  # TYPE_CHECKING equivalent for runtime imports
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from cursor_rules_mcp_server.api import (
    list_resources_handler,
    read_resource_handler,
    create_resource_handler,
    update_resource_handler,
    delete_resource_handler,
    list_prompts_handler,
    execute_tool_handler,
    analyze_repository_tool,
    generate_rule_tool,
    export_rules_tool,
    import_templates_tool,
)


@pytest.fixture
def mock_db() -> MagicMock:
    """Create a mock database for testing."""
    mock_db = MagicMock()

    # Mock rule templates
    mock_db.get_rule_templates.return_value = [
        {"id": 1, "name": "python-standards", "title": "Python Standards"},
        {"id": 2, "name": "react-best-practices", "title": "React Best Practices"}
    ]

    # Mock rules
    mock_db.get_rules.return_value = [
        {"id": 1, "name": "my-python-standards", "description": "My Python standards"},
        {"id": 2, "name": "my-react-practices", "description": "My React practices"}
    ]

    # Mock repositories
    mock_db.get_repositories.return_value = [
        {"id": 1, "name": "repo1", "path": "/path/to/repo1"},
        {"id": 2, "name": "repo2", "path": "/path/to/repo2"}
    ]

    # Mock get_rule_template
    mock_db.get_rule_template.return_value = {
        "id": 1,
        "name": "python-standards",
        "title": "Python Standards",
        "description": "Python coding standards",
        "content": "# Python Standards\n\nFollow these Python standards.",
        "category": "Python",
        "created_at": "2023-01-01T00:00:00"
    }

    # Mock get_rule
    mock_db.get_rule.return_value = {
        "id": 1,
        "name": "my-python-standards",
        "description": "My Python standards",
        "content": "# My Python Standards\n\nFollow these Python standards.",
        "template_id": 1,
        "repository_id": 1,
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:00"
    }

    # Mock get_repository
    mock_db.get_repository.return_value = {
        "id": 1,
        "name": "repo1",
        "path": "/path/to/repo1",
        "repo_type": "web",
        "languages": json.dumps({"python": 10}),
        "frameworks": json.dumps(["flask"]),
        "file_stats": json.dumps({"total_files": 20}),
        "analysis_date": "2023-01-01T00:00:00"
    }

    return mock_db


@pytest.mark.asyncio
async def test_list_resources_handler(mock_db: MagicMock) -> None:
    """Test list_resources_handler function."""
    # Test listing rule templates
    result = await list_resources_handler({"resource_type": "rule_templates"}, mock_db)
    assert result["status"] == "success"
    assert len(result["data"]) == 2
    assert result["data"][0]["name"] == "python-standards"

    # Test listing rules
    result = await list_resources_handler({"resource_type": "rules"}, mock_db)
    assert result["status"] == "success"
    assert len(result["data"]) == 2
    assert result["data"][0]["name"] == "my-python-standards"

    # Test listing repositories
    result = await list_resources_handler({"resource_type": "repositories"}, mock_db)
    assert result["status"] == "success"
    assert len(result["data"]) == 2
    assert result["data"][0]["name"] == "repo1"

    # Test with invalid resource type
    result = await list_resources_handler({"resource_type": "invalid"}, mock_db)
    assert result["status"] == "error"
    assert "Invalid resource type" in result["message"]


@pytest.mark.asyncio
async def test_read_resource_handler(mock_db: MagicMock) -> None:
    """Test read_resource_handler function."""
    # Test reading a rule template
    result = await read_resource_handler({
        "resource_type": "rule_templates",
        "resource_id": 1
    }, mock_db)
    assert result["status"] == "success"
    assert result["data"]["name"] == "python-standards"

    # Test reading a rule
    result = await read_resource_handler({
        "resource_type": "rules",
        "resource_id": 1
    }, mock_db)
    assert result["status"] == "success"
    assert result["data"]["name"] == "my-python-standards"

    # Test reading a repository
    result = await read_resource_handler({
        "resource_type": "repositories",
        "resource_id": 1
    }, mock_db)
    assert result["status"] == "success"
    assert result["data"]["name"] == "repo1"

    # Test with invalid resource type
    result = await read_resource_handler({
        "resource_type": "invalid",
        "resource_id": 1
    }, mock_db)
    assert result["status"] == "error"
    assert "Invalid resource type" in result["message"]

    # Test with non-existent resource
    mock_db.get_rule_template.side_effect = ValueError("Resource not found")
    result = await read_resource_handler({
        "resource_type": "rule_templates",
        "resource_id": 999
    }, mock_db)
    assert result["status"] == "error"
    assert "Resource not found" in result["message"]


@pytest.mark.asyncio
async def test_create_resource_handler(mock_db: MagicMock) -> None:
    """Test create_resource_handler function."""
    # Test creating a rule
    mock_db.add_rule.return_value = 1

    result = await create_resource_handler({
        "resource_type": "rules",
        "data": {
            "name": "new-rule",
            "description": "New rule description",
            "content": "# New Rule\n\nThis is a new rule.",
            "template_id": 1,
            "repository_id": 1
        }
    }, mock_db)

    assert result["status"] == "success"
    assert result["data"]["id"] == 1
    mock_db.add_rule.assert_called_once()

    # Test creating a repository
    mock_db.add_repository.return_value = 3

    result = await create_resource_handler({
        "resource_type": "repositories",
        "data": {
            "name": "new-repo",
            "path": "/path/to/new-repo",
            "repo_type": "web"
        }
    }, mock_db)

    assert result["status"] == "success"
    assert result["data"]["id"] == 3
    mock_db.add_repository.assert_called_once()

    # Test with invalid resource type
    result = await create_resource_handler({
        "resource_type": "invalid",
        "data": {}
    }, mock_db)

    assert result["status"] == "error"
    assert "Invalid resource type" in result["message"]

    # Test with missing data
    result = await create_resource_handler({
        "resource_type": "rules"
    }, mock_db)

    assert result["status"] == "error"
    assert "Missing data" in result["message"]


@pytest.mark.asyncio
async def test_update_resource_handler(mock_db: MagicMock) -> None:
    """Test update_resource_handler function."""
    # Test updating a rule
    result = await update_resource_handler({
        "resource_type": "rules",
        "resource_id": 1,
        "data": {
            "description": "Updated description",
            "content": "# Updated Rule\n\nThis is an updated rule."
        }
    }, mock_db)

    assert result["status"] == "success"
    mock_db.update_rule.assert_called_once()

    # Test with invalid resource type
    result = await update_resource_handler({
        "resource_type": "invalid",
        "resource_id": 1,
        "data": {}
    }, mock_db)

    assert result["status"] == "error"
    assert "Invalid resource type" in result["message"]

    # Test with missing data
    result = await update_resource_handler({
        "resource_type": "rules",
        "resource_id": 1
    }, mock_db)

    assert result["status"] == "error"
    assert "Missing data" in result["message"]

    # Test with non-existent resource
    mock_db.update_rule.side_effect = ValueError("Resource not found")
    result = await update_resource_handler({
        "resource_type": "rules",
        "resource_id": 999,
        "data": {
            "description": "Updated description"
        }
    }, mock_db)

    assert result["status"] == "error"
    assert "Resource not found" in result["message"]


@pytest.mark.asyncio
async def test_delete_resource_handler(mock_db: MagicMock) -> None:
    """Test delete_resource_handler function."""
    # Test deleting a rule
    result = await delete_resource_handler({
        "resource_type": "rules",
        "resource_id": 1
    }, mock_db)

    assert result["status"] == "success"
    mock_db.delete_rule.assert_called_once_with(1)

    # Test with invalid resource type
    result = await delete_resource_handler({
        "resource_type": "invalid",
        "resource_id": 1
    }, mock_db)

    assert result["status"] == "error"
    assert "Invalid resource type" in result["message"]

    # Test with non-existent resource
    mock_db.delete_rule.side_effect = ValueError("Resource not found")
    result = await delete_resource_handler({
        "resource_type": "rules",
        "resource_id": 999
    }, mock_db)

    assert result["status"] == "error"
    assert "Resource not found" in result["message"]


@pytest.mark.asyncio
async def test_list_prompts_handler() -> None:
    """Test list_prompts_handler function."""
    result = await list_prompts_handler({}, None)

    assert result["status"] == "success"
    assert isinstance(result["data"], list)
    assert len(result["data"]) > 0

    # Check that each prompt has the required fields
    for prompt in result["data"]:
        assert "name" in prompt
        assert "description" in prompt


@pytest.mark.asyncio
async def test_execute_tool_handler_analyze_repository(mock_db: MagicMock) -> None:
    """Test execute_tool_handler function with analyze_repository tool."""
    with patch('cursor_rules_mcp_server.api.analyze_repository_tool') as mock_tool:
        mock_tool.return_value = {
            "repo_type": "web",
            "languages": {"python": 100},
            "frameworks": ["flask"],
            "suggested_rules": ["python-standards", "flask-best-practices"]
        }

        result = await execute_tool_handler({
            "tool": "analyze_repository",
            "params": {
                "repo_path": "/path/to/repo"
            }
        }, mock_db)

        assert result["status"] == "success"
        assert result["data"]["repo_type"] == "web"
        mock_tool.assert_called_once_with({"repo_path": "/path/to/repo"}, mock_db)


@pytest.mark.asyncio
async def test_execute_tool_handler_generate_rule(mock_db: MagicMock) -> None:
    """Test execute_tool_handler function with generate_rule tool."""
    with patch('cursor_rules_mcp_server.api.generate_rule_tool') as mock_tool:
        mock_tool.return_value = {
            "name": "python-standards",
            "title": "Python Standards",
            "description": "Python coding standards",
            "content": "# Python Standards\n\nFollow these Python standards."
        }

        result = await execute_tool_handler({
            "tool": "generate_rule",
            "params": {
                "rule_name": "python-standards",
                "repo_path": "/path/to/repo"
            }
        }, mock_db)

        assert result["status"] == "success"
        assert result["data"]["name"] == "python-standards"
        mock_tool.assert_called_once_with({
            "rule_name": "python-standards",
            "repo_path": "/path/to/repo"
        }, mock_db)


@pytest.mark.asyncio
async def test_execute_tool_handler_export_rules(mock_db: MagicMock) -> None:
    """Test execute_tool_handler function with export_rules tool."""
    with patch('cursor_rules_mcp_server.api.export_rules_tool') as mock_tool:
        mock_tool.return_value = {
            "exported_rules": 2,
            "output_dir": "/path/to/output"
        }

        result = await execute_tool_handler({
            "tool": "export_rules",
            "params": {
                "repo_path": "/path/to/repo",
                "output_dir": "/path/to/output",
                "rule_names": ["python-standards", "flask-best-practices"]
            }
        }, mock_db)

        assert result["status"] == "success"
        assert result["data"]["exported_rules"] == 2
        mock_tool.assert_called_once_with({
            "repo_path": "/path/to/repo",
            "output_dir": "/path/to/output",
            "rule_names": ["python-standards", "flask-best-practices"]
        }, mock_db)


@pytest.mark.asyncio
async def test_execute_tool_handler_import_templates(mock_db: MagicMock) -> None:
    """Test execute_tool_handler function with import_templates tool."""
    with patch('cursor_rules_mcp_server.api.import_templates_tool') as mock_tool:
        mock_tool.return_value = {
            "imported_templates": 2,
            "templates_dir": "/path/to/templates"
        }

        result = await execute_tool_handler({
            "tool": "import_templates",
            "params": {
                "templates_dir": "/path/to/templates"
            }
        }, mock_db)

        assert result["status"] == "success"
        assert result["data"]["imported_templates"] == 2
        mock_tool.assert_called_once_with({
            "templates_dir": "/path/to/templates"
        }, mock_db)


@pytest.mark.asyncio
async def test_execute_tool_handler_invalid_tool() -> None:
    """Test execute_tool_handler function with an invalid tool."""
    result = await execute_tool_handler({
        "tool": "invalid_tool",
        "params": {}
    }, MagicMock())

    assert result["status"] == "error"
    assert "Invalid tool" in result["message"]


@pytest.mark.asyncio
async def test_analyze_repository_tool() -> None:
    """Test analyze_repository_tool function."""
    with patch('cursor_rules_mcp_server.api.analyze_repository') as mock_analyze:
        mock_analyze.return_value = {
            "repo_type": "web",
            "languages": {"python": 100},
            "frameworks": ["flask"],
            "suggested_rules": ["python-standards", "flask-best-practices"]
        }

        result = await analyze_repository_tool({
            "repo_path": "/path/to/repo"
        }, MagicMock())

        assert result["repo_type"] == "web"
        assert result["languages"]["python"] == 100
        assert "flask" in result["frameworks"]
        assert "python-standards" in result["suggested_rules"]
        mock_analyze.assert_called_once_with("/path/to/repo")


@pytest.mark.asyncio
async def test_generate_rule_tool() -> None:
    """Test generate_rule_tool function."""
    with patch('cursor_rules_mcp_server.api.generate_rule') as mock_generate:
        mock_generate.return_value = {
            "name": "python-standards",
            "title": "Python Standards",
            "description": "Python coding standards",
            "content": "# Python Standards\n\nFollow these Python standards."
        }

        result = await generate_rule_tool({
            "rule_name": "python-standards",
            "repo_path": "/path/to/repo"
        }, MagicMock())

        assert result["name"] == "python-standards"
        assert result["title"] == "Python Standards"
        mock_generate.assert_called_once_with(
            "python-standards",
            repo_path="/path/to/repo",
            title=None,
            description=None
        )


@pytest.mark.asyncio
async def test_export_rules_tool() -> None:
    """Test export_rules_tool function."""
    with patch('cursor_rules_mcp_server.api.RuleGenerator') as MockRuleGenerator:
        # Setup mock rule generator
        mock_generator = MagicMock()
        MockRuleGenerator.return_value = mock_generator

        mock_generator.analyze_repo.return_value = {
            "repo_type": "web",
            "languages": {"python": 100},
            "frameworks": ["flask"],
            "suggested_rules": ["python-standards", "flask-best-practices"]
        }

        mock_generator.generate_multiple_rules.return_value = [
            {
                "name": "python-standards",
                "title": "Python Standards",
                "description": "Python coding standards",
                "content": "# Python Standards\n\nFollow these Python standards."
            },
            {
                "name": "flask-best-practices",
                "title": "Flask Best Practices",
                "description": "Best practices for Flask applications",
                "content": "# Flask Best Practices\n\nFollow these Flask best practices."
            }
        ]

        mock_generator.export_rules_to_files.return_value = [
            "/path/to/output/python-standards.md",
            "/path/to/output/flask-best-practices.md"
        ]

        result = await export_rules_tool({
            "repo_path": "/path/to/repo",
            "output_dir": "/path/to/output",
            "rule_names": ["python-standards", "flask-best-practices"]
        }, MagicMock())

        assert result["exported_rules"] == 2
        assert result["output_dir"] == "/path/to/output"
        mock_generator.analyze_repo.assert_called_once_with("/path/to/repo")
        mock_generator.generate_multiple_rules.assert_called_once_with(
            ["python-standards", "flask-best-practices"]
        )
        mock_generator.export_rules_to_files.assert_called_once_with("/path/to/output")


@pytest.mark.asyncio
async def test_import_templates_tool() -> None:
    """Test import_templates_tool function."""
    with patch('cursor_rules_mcp_server.api.import_templates') as mock_import:
        mock_import.return_value = [
            {"name": "python-standards", "title": "Python Standards"},
            {"name": "flask-best-practices", "title": "Flask Best Practices"}
        ]

        result = await import_templates_tool({
            "templates_dir": "/path/to/templates"
        }, MagicMock())

        assert result["imported_templates"] == 2
        assert result["templates_dir"] == "/path/to/templates"
        mock_import.assert_called_once()
