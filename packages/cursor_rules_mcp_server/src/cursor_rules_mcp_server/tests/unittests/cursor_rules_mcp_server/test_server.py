"""Tests for the server module."""

import os
import json
import tempfile
import sqlite3
from pathlib import Path
from typing import Dict, Any, Generator, List, Tuple
from unittest.mock import patch, MagicMock, AsyncMock
if True:  # TYPE_CHECKING equivalent for runtime imports
    from _pytest.fixtures import FixtureRequest
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture

import pytest

from cursor_rules_mcp_server.server import (
    CursorRulesDatabase,
    list_resources_handler,
    read_resource_handler,
    list_prompts_handler,
    execute_tool_handler,
    main,
)
from cursor_rules_mcp_server.models import RuleTemplate, Rule, Repository


@pytest.fixture
def temp_db_path() -> Generator[str, None, None]:
    """Create a temporary database file.

    Returns:
        Generator[str, None, None]: Path to the temporary database file.
    """
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_file:
        temp_path = temp_file.name

    yield temp_path

    # Clean up
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def db(temp_db_path: str) -> CursorRulesDatabase:
    """Create a database instance.

    Args:
        temp_db_path (str): Path to the temporary database file.

    Returns:
        CursorRulesDatabase: Database instance.
    """
    return CursorRulesDatabase(temp_db_path)


@pytest.fixture
def sample_rule_template() -> RuleTemplate:
    """Create a sample rule template.

    Returns:
        RuleTemplate: Sample rule template.
    """
    return RuleTemplate(
        id=0,
        name="python-code-standards",
        title="Python Code Standards",
        description="Python code standards for web applications",
        content="# Python Code Standards\n\nFollow these Python code standards.",
        category="Python",
        created_at="2023-01-01T00:00:00"
    )


@pytest.fixture
def sample_rule() -> Rule:
    """Create a sample rule.

    Returns:
        Rule: Sample rule.
    """
    return Rule(
        id=0,
        name="my-python-standards",
        description="My Python standards",
        content="# My Python Standards\n\nFollow these Python standards.",
        template_id=1,
        repository_id=1,
        created_at="2023-01-01T00:00:00",
        updated_at="2023-01-01T00:00:00"
    )


@pytest.fixture
def sample_repository() -> Repository:
    """Create a sample repository.

    Returns:
        Repository: Sample repository.
    """
    return Repository(
        id=0,
        name="my-repo",
        path="/path/to/repo",
        repo_type="web",
        languages=json.dumps({"python": 10}),
        frameworks=json.dumps(["flask"]),
        file_stats=json.dumps({"total_files": 20}),
        analysis_date="2023-01-01T00:00:00"
    )


def test_database_init(temp_db_path: str) -> None:
    """Test database initialization.

    Args:
        temp_db_path (str): Path to the temporary database file.
    """
    db = CursorRulesDatabase(temp_db_path)

    # Check that the database file was created
    assert os.path.exists(temp_db_path)

    # Check that the tables were created
    conn = sqlite3.connect(temp_db_path)
    cursor = conn.cursor()

    # Get list of tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    assert "rules" in tables
    assert "rule_templates" in tables
    assert "repositories" in tables

    conn.close()


def test_add_rule_template(db: CursorRulesDatabase, sample_rule_template: RuleTemplate) -> None:
    """Test adding a rule template.

    Args:
        db (CursorRulesDatabase): Database instance.
        sample_rule_template (RuleTemplate): Sample rule template.
    """
    template_id = db.add_rule_template(sample_rule_template)

    assert template_id > 0

    # Check that the template was added
    templates = db.get_rule_templates()
    assert len(templates) == 1
    assert templates[0].name == "python-code-standards"
    assert templates[0].title == "Python Code Standards"


def test_get_rule_template(db: CursorRulesDatabase, sample_rule_template: RuleTemplate) -> None:
    """Test getting a rule template.

    Args:
        db (CursorRulesDatabase): Database instance.
        sample_rule_template (RuleTemplate): Sample rule template.
    """
    template_id = db.add_rule_template(sample_rule_template)

    template = db.get_rule_template(template_id)

    assert template is not None
    assert template.id == template_id
    assert template.name == "python-code-standards"
    assert template.title == "Python Code Standards"


def test_get_rule_template_by_name(db: CursorRulesDatabase, sample_rule_template: RuleTemplate) -> None:
    """Test getting a rule template by name.

    Args:
        db (CursorRulesDatabase): Database instance.
        sample_rule_template (RuleTemplate): Sample rule template.
    """
    db.add_rule_template(sample_rule_template)

    template = db.get_rule_template_by_name("python-code-standards")

    assert template is not None
    assert template.name == "python-code-standards"
    assert template.title == "Python Code Standards"


def test_add_rule(db: CursorRulesDatabase, sample_rule: Rule) -> None:
    """Test adding a rule.

    Args:
        db (CursorRulesDatabase): Database instance.
        sample_rule (Rule): Sample rule.
    """
    rule_id = db.add_rule(sample_rule)

    assert rule_id > 0

    # Check that the rule was added
    rules = db.get_rules()
    assert len(rules) == 1
    assert rules[0].name == "my-python-standards"
    assert rules[0].description == "My Python standards"


def test_get_rule(db: CursorRulesDatabase, sample_rule: Rule) -> None:
    """Test getting a rule.

    Args:
        db (CursorRulesDatabase): Database instance.
        sample_rule (Rule): Sample rule.
    """
    rule_id = db.add_rule(sample_rule)

    rule = db.get_rule(rule_id)

    assert rule is not None
    assert rule.id == rule_id
    assert rule.name == "my-python-standards"
    assert rule.description == "My Python standards"


def test_update_rule(db: CursorRulesDatabase, sample_rule: Rule) -> None:
    """Test updating a rule.

    Args:
        db (CursorRulesDatabase): Database instance.
        sample_rule (Rule): Sample rule.
    """
    rule_id = db.add_rule(sample_rule)

    # Update the rule
    updated_rule = Rule(
        id=rule_id,
        name="updated-python-standards",
        description="Updated Python standards",
        content="# Updated Python Standards\n\nFollow these updated Python standards.",
        template_id=1,
        repository_id=1,
        created_at="2023-01-01T00:00:00",
        updated_at="2023-01-02T00:00:00"
    )

    db.update_rule(updated_rule)

    # Check that the rule was updated
    rule = db.get_rule(rule_id)
    assert rule is not None
    assert rule.name == "updated-python-standards"
    assert rule.description == "Updated Python standards"


def test_delete_rule(db: CursorRulesDatabase, sample_rule: Rule) -> None:
    """Test deleting a rule.

    Args:
        db (CursorRulesDatabase): Database instance.
        sample_rule (Rule): Sample rule.
    """
    rule_id = db.add_rule(sample_rule)

    db.delete_rule(rule_id)

    # Check that the rule was deleted
    rule = db.get_rule(rule_id)
    assert rule is None


def test_add_repository(db: CursorRulesDatabase, sample_repository: Repository) -> None:
    """Test adding a repository.

    Args:
        db (CursorRulesDatabase): Database instance.
        sample_repository (Repository): Sample repository.
    """
    repo_id = db.add_repository(sample_repository)

    assert repo_id > 0

    # Check that the repository was added
    repo = db.get_repository(repo_id)
    assert repo is not None
    assert repo.name == "my-repo"
    assert repo.path == "/path/to/repo"


def test_get_repository_by_path(db: CursorRulesDatabase, sample_repository: Repository) -> None:
    """Test getting a repository by path.

    Args:
        db (CursorRulesDatabase): Database instance.
        sample_repository (Repository): Sample repository.
    """
    db.add_repository(sample_repository)

    repo = db.get_repository_by_path("/path/to/repo")

    assert repo is not None
    assert repo.name == "my-repo"
    assert repo.path == "/path/to/repo"


def test_add_repo_analysis(db: CursorRulesDatabase) -> None:
    """Test adding repository analysis.

    Args:
        db (CursorRulesDatabase): Database instance.
    """
    analysis = {
        "repo_type": "web",
        "languages": {"python": 10},
        "frameworks": ["flask"],
        "file_stats": {"total_files": 20},
        "suggested_rules": [{"name": "python-code-standards"}]
    }

    repo_id = db.add_repo_analysis("my-repo", "/path/to/repo", analysis)

    assert repo_id > 0

    # Check that the repository was added
    repo = db.get_repository(repo_id)
    assert repo is not None
    assert repo.name == "my-repo"
    assert repo.path == "/path/to/repo"
    assert json.loads(repo.languages) == {"python": 10}
    assert json.loads(repo.frameworks) == ["flask"]


@pytest.mark.asyncio
async def test_list_resources_handler() -> None:
    """Test the list_resources_handler function."""
    result = await list_resources_handler({})

    assert isinstance(result, dict)
    assert "resources" in result
    assert isinstance(result["resources"], list)


@pytest.mark.asyncio
async def test_read_resource_handler() -> None:
    """Test the read_resource_handler function."""
    # Test with invalid resource
    with pytest.raises(ValueError):
        await read_resource_handler({"resource_id": "invalid"})

    # Test with valid resource
    result = await read_resource_handler({"resource_id": "prompt_template"})

    assert isinstance(result, dict)
    assert "content" in result


@pytest.mark.asyncio
async def test_list_prompts_handler() -> None:
    """Test the list_prompts_handler function."""
    result = await list_prompts_handler({})

    assert isinstance(result, dict)
    assert "prompts" in result
    assert isinstance(result["prompts"], list)
    assert len(result["prompts"]) > 0

    # Check that each prompt has required fields
    for prompt in result["prompts"]:
        assert "id" in prompt
        assert "name" in prompt
        assert "description" in prompt


@pytest.mark.asyncio
async def test_execute_tool_handler_analyze_repository(mocker: "MockerFixture") -> None:
    """Test the execute_tool_handler function with analyze_repository tool.

    Args:
        mocker (MockerFixture): Pytest mocker fixture.
    """
    # Mock the analyze_repository function
    mock_analyze = mocker.patch("cursor_rules_mcp_server.server.analyze_repository")
    mock_analyze.return_value = {"repo_type": "web"}

    # Mock the add_repo_analysis method
    mock_db = mocker.patch("cursor_rules_mcp_server.server.CursorRulesDatabase")
    mock_db_instance = MagicMock()
    mock_db.return_value = mock_db_instance
    mock_db_instance.add_repo_analysis.return_value = 1

    result = await execute_tool_handler({
        "tool_name": "analyze_repository",
        "tool_args": {
            "repo_path": "/path/to/repo",
            "repo_name": "my-repo"
        }
    })

    assert isinstance(result, dict)
    assert "result" in result
    assert result["result"]["repo_type"] == "web"
    mock_analyze.assert_called_once_with("/path/to/repo")
    mock_db_instance.add_repo_analysis.assert_called_once()


@pytest.mark.asyncio
async def test_execute_tool_handler_generate_rule(mocker: "MockerFixture") -> None:
    """Test the execute_tool_handler function with generate_rule tool.

    Args:
        mocker (MockerFixture): Pytest mocker fixture.
    """
    # Mock the generate_rule function
    mock_generate = mocker.patch("cursor_rules_mcp_server.server.generate_rule")
    mock_generate.return_value = {
        "name": "python-code-standards",
        "title": "Python Code Standards",
        "content": "# Python Code Standards"
    }

    result = await execute_tool_handler({
        "tool_name": "generate_rule",
        "tool_args": {
            "rule_name": "python-code-standards",
            "repo_path": "/path/to/repo"
        }
    })

    assert isinstance(result, dict)
    assert "result" in result
    assert result["result"]["name"] == "python-code-standards"
    mock_generate.assert_called_once_with("python-code-standards", "/path/to/repo", None)


@pytest.mark.asyncio
async def test_execute_tool_handler_export_rules(mocker: "MockerFixture") -> None:
    """Test the execute_tool_handler function with export_rules tool.

    Args:
        mocker (MockerFixture): Pytest mocker fixture.
    """
    # Mock the RuleGenerator class
    mock_generator = MagicMock()
    mock_generator.generate_multiple_rules.return_value = [
        {"name": "rule1", "content": "content1"},
        {"name": "rule2", "content": "content2"}
    ]
    mock_generator.export_rules_to_files.return_value = None

    mock_generator_class = mocker.patch("cursor_rules_mcp_server.server.RuleGenerator")
    mock_generator_class.return_value = mock_generator

    result = await execute_tool_handler({
        "tool_name": "export_rules",
        "tool_args": {
            "rule_names": ["rule1", "rule2"],
            "output_dir": "/path/to/output",
            "repo_path": "/path/to/repo"
        }
    })

    assert isinstance(result, dict)
    assert "result" in result
    assert "Exported 2 rules" in result["result"]
    mock_generator_class.assert_called_once_with("/path/to/repo")
    mock_generator.generate_multiple_rules.assert_called_once_with(["rule1", "rule2"])
    mock_generator.export_rules_to_files.assert_called_once_with(
        [{"name": "rule1", "content": "content1"}, {"name": "rule2", "content": "content2"}],
        "/path/to/output"
    )


@pytest.mark.asyncio
async def test_execute_tool_handler_invalid_tool() -> None:
    """Test the execute_tool_handler function with an invalid tool."""
    with pytest.raises(ValueError):
        await execute_tool_handler({
            "tool_name": "invalid_tool",
            "tool_args": {}
        })


@pytest.mark.asyncio
async def test_main(mocker: "MockerFixture") -> None:
    """Test the main function.

    Args:
        mocker (MockerFixture): Pytest mocker fixture.
    """
    # Mock the MCPServer class
    mock_server = AsyncMock()
    mock_server_class = mocker.patch("cursor_rules_mcp_server.server.MCPServer")
    mock_server_class.return_value = mock_server

    # Mock the handlers
    mock_list_resources = mocker.patch("cursor_rules_mcp_server.server.list_resources_handler")
    mock_read_resource = mocker.patch("cursor_rules_mcp_server.server.read_resource_handler")
    mock_list_prompts = mocker.patch("cursor_rules_mcp_server.server.list_prompts_handler")
    mock_execute_tool = mocker.patch("cursor_rules_mcp_server.server.execute_tool_handler")

    # Run the main function
    await main()

    # Check that the server was created and started
    mock_server_class.assert_called_once()
    mock_server.register_handler.assert_called()
    mock_server.start.assert_called_once()
