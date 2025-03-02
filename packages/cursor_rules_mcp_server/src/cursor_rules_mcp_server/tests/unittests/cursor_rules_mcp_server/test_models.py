"""Tests for the models module."""

import json
from typing import Dict, Any
if True:  # TYPE_CHECKING equivalent for runtime imports
    from _pytest.fixtures import FixtureRequest
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture

import pytest

from cursor_rules_mcp_server.models import (
    RuleTemplate,
    Rule,
    Repository,
    RepositoryRuleAssociation,
    rule_to_dict,
    dict_to_rule,
    template_to_dict,
    dict_to_template,
    repository_to_dict,
    dict_to_repository,
    DB_SCHEMA,
)


def test_rule_template_init() -> None:
    """Test RuleTemplate initialization."""
    template = RuleTemplate(
        id=1,
        name="python-code-standards",
        title="Python Code Standards",
        description="Python code standards for web applications",
        content="# Python Code Standards\n\nFollow these Python code standards.",
        category="Python",
        created_at="2023-01-01T00:00:00"
    )

    assert template.id == 1
    assert template.name == "python-code-standards"
    assert template.title == "Python Code Standards"
    assert template.description == "Python code standards for web applications"
    assert template.content == "# Python Code Standards\n\nFollow these Python code standards."
    assert template.category == "Python"
    assert template.created_at == "2023-01-01T00:00:00"


def test_rule_init() -> None:
    """Test Rule initialization."""
    rule = Rule(
        id=1,
        name="my-python-standards",
        description="My Python standards",
        content="# My Python Standards\n\nFollow these Python standards.",
        template_id=1,
        repository_id=1,
        created_at="2023-01-01T00:00:00",
        updated_at="2023-01-01T00:00:00"
    )

    assert rule.id == 1
    assert rule.name == "my-python-standards"
    assert rule.description == "My Python standards"
    assert rule.content == "# My Python Standards\n\nFollow these Python standards."
    assert rule.template_id == 1
    assert rule.repository_id == 1
    assert rule.created_at == "2023-01-01T00:00:00"
    assert rule.updated_at == "2023-01-01T00:00:00"


def test_repository_init() -> None:
    """Test Repository initialization."""
    repo = Repository(
        id=1,
        name="my-repo",
        path="/path/to/repo",
        repo_type="web",
        languages=json.dumps({"python": 10}),
        frameworks=json.dumps(["flask"]),
        file_stats=json.dumps({"total_files": 20}),
        analysis_date="2023-01-01T00:00:00"
    )

    assert repo.id == 1
    assert repo.name == "my-repo"
    assert repo.path == "/path/to/repo"
    assert repo.repo_type == "web"
    assert json.loads(repo.languages) == {"python": 10}
    assert json.loads(repo.frameworks) == ["flask"]
    assert json.loads(repo.file_stats) == {"total_files": 20}
    assert repo.analysis_date == "2023-01-01T00:00:00"


def test_repository_rule_association_init() -> None:
    """Test RepositoryRuleAssociation initialization."""
    association = RepositoryRuleAssociation(
        repository_id=1,
        rule_id=1,
        status="active",
        priority=1
    )

    assert association.repository_id == 1
    assert association.rule_id == 1
    assert association.status == "active"
    assert association.priority == 1


def test_rule_to_dict() -> None:
    """Test rule_to_dict function."""
    rule = Rule(
        id=1,
        name="my-python-standards",
        description="My Python standards",
        content="# My Python Standards\n\nFollow these Python standards.",
        template_id=1,
        repository_id=1,
        created_at="2023-01-01T00:00:00",
        updated_at="2023-01-01T00:00:00"
    )

    rule_dict = rule_to_dict(rule)

    assert rule_dict["id"] == 1
    assert rule_dict["name"] == "my-python-standards"
    assert rule_dict["description"] == "My Python standards"
    assert rule_dict["content"] == "# My Python Standards\n\nFollow these Python standards."
    assert rule_dict["template_id"] == 1
    assert rule_dict["repository_id"] == 1
    assert rule_dict["created_at"] == "2023-01-01T00:00:00"
    assert rule_dict["updated_at"] == "2023-01-01T00:00:00"


def test_dict_to_rule() -> None:
    """Test dict_to_rule function."""
    rule_dict = {
        "id": 1,
        "name": "my-python-standards",
        "description": "My Python standards",
        "content": "# My Python Standards\n\nFollow these Python standards.",
        "template_id": 1,
        "repository_id": 1,
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:00"
    }

    rule = dict_to_rule(rule_dict)

    assert rule.id == 1
    assert rule.name == "my-python-standards"
    assert rule.description == "My Python standards"
    assert rule.content == "# My Python Standards\n\nFollow these Python standards."
    assert rule.template_id == 1
    assert rule.repository_id == 1
    assert rule.created_at == "2023-01-01T00:00:00"
    assert rule.updated_at == "2023-01-01T00:00:00"


def test_template_to_dict() -> None:
    """Test template_to_dict function."""
    template = RuleTemplate(
        id=1,
        name="python-code-standards",
        title="Python Code Standards",
        description="Python code standards for web applications",
        content="# Python Code Standards\n\nFollow these Python code standards.",
        category="Python",
        created_at="2023-01-01T00:00:00"
    )

    template_dict = template_to_dict(template)

    assert template_dict["id"] == 1
    assert template_dict["name"] == "python-code-standards"
    assert template_dict["title"] == "Python Code Standards"
    assert template_dict["description"] == "Python code standards for web applications"
    assert template_dict["content"] == "# Python Code Standards\n\nFollow these Python code standards."
    assert template_dict["category"] == "Python"
    assert template_dict["created_at"] == "2023-01-01T00:00:00"


def test_dict_to_template() -> None:
    """Test dict_to_template function."""
    template_dict = {
        "id": 1,
        "name": "python-code-standards",
        "title": "Python Code Standards",
        "description": "Python code standards for web applications",
        "content": "# Python Code Standards\n\nFollow these Python code standards.",
        "category": "Python",
        "created_at": "2023-01-01T00:00:00"
    }

    template = dict_to_template(template_dict)

    assert template.id == 1
    assert template.name == "python-code-standards"
    assert template.title == "Python Code Standards"
    assert template.description == "Python code standards for web applications"
    assert template.content == "# Python Code Standards\n\nFollow these Python code standards."
    assert template.category == "Python"
    assert template.created_at == "2023-01-01T00:00:00"


def test_repository_to_dict() -> None:
    """Test repository_to_dict function."""
    repo = Repository(
        id=1,
        name="my-repo",
        path="/path/to/repo",
        repo_type="web",
        languages=json.dumps({"python": 10}),
        frameworks=json.dumps(["flask"]),
        file_stats=json.dumps({"total_files": 20}),
        analysis_date="2023-01-01T00:00:00"
    )

    repo_dict = repository_to_dict(repo)

    assert repo_dict["id"] == 1
    assert repo_dict["name"] == "my-repo"
    assert repo_dict["path"] == "/path/to/repo"
    assert repo_dict["repo_type"] == "web"
    assert repo_dict["languages"] == json.dumps({"python": 10})
    assert repo_dict["frameworks"] == json.dumps(["flask"])
    assert repo_dict["file_stats"] == json.dumps({"total_files": 20})
    assert repo_dict["analysis_date"] == "2023-01-01T00:00:00"


def test_dict_to_repository() -> None:
    """Test dict_to_repository function."""
    repo_dict = {
        "id": 1,
        "name": "my-repo",
        "path": "/path/to/repo",
        "repo_type": "web",
        "languages": json.dumps({"python": 10}),
        "frameworks": json.dumps(["flask"]),
        "file_stats": json.dumps({"total_files": 20}),
        "analysis_date": "2023-01-01T00:00:00"
    }

    repo = dict_to_repository(repo_dict)

    assert repo.id == 1
    assert repo.name == "my-repo"
    assert repo.path == "/path/to/repo"
    assert repo.repo_type == "web"
    assert repo.languages == json.dumps({"python": 10})
    assert repo.frameworks == json.dumps(["flask"])
    assert repo.file_stats == json.dumps({"total_files": 20})
    assert repo.analysis_date == "2023-01-01T00:00:00"


def test_db_schema() -> None:
    """Test DB_SCHEMA dictionary."""
    assert "rules" in DB_SCHEMA
    assert "rule_templates" in DB_SCHEMA
    assert "repositories" in DB_SCHEMA
    assert "repository_rule_associations" in DB_SCHEMA

    # Check that each schema has the required fields
    assert "id" in DB_SCHEMA["rules"]
    assert "name" in DB_SCHEMA["rules"]
    assert "content" in DB_SCHEMA["rules"]

    assert "id" in DB_SCHEMA["rule_templates"]
    assert "name" in DB_SCHEMA["rule_templates"]
    assert "content" in DB_SCHEMA["rule_templates"]

    assert "id" in DB_SCHEMA["repositories"]
    assert "name" in DB_SCHEMA["repositories"]
    assert "path" in DB_SCHEMA["repositories"]

    assert "repository_id" in DB_SCHEMA["repository_rule_associations"]
    assert "rule_id" in DB_SCHEMA["repository_rule_associations"]
