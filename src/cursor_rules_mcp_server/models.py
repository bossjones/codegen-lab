"""Database models for cursor rules MCP server.

This module defines the models and schema used by the cursor rules MCP server
for storing rule templates, repository analysis results, and user-generated rules.
"""

import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union


@dataclass
class RuleTemplate:
    """Represents a cursor rule template.

    Attributes:
        id (int): Unique identifier for the template.
        name (str): Name of the template (e.g., "python-code-standards").
        title (str): Display title of the template (e.g., "Python Code Standards").
        description (str): Description of what the rule template does.
        content (str): Full markdown content of the rule template.
        category (str): Category for organization (e.g., "workflow", "standards").
        created_at (str): Timestamp when the template was created.
    """
    id: int
    name: str
    title: str
    description: str
    content: str
    category: str
    created_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())


@dataclass
class Rule:
    """Represents a cursor rule created by a user.

    Attributes:
        id (int): Unique identifier for the rule.
        name (str): Name of the rule.
        description (str): Description of what the rule does.
        content (str): Full markdown content of the rule.
        template_id (Optional[int]): ID of the template it was based on, if any.
        repository_id (Optional[int]): ID of the repository it was created for, if any.
        created_at (str): Timestamp when the rule was created.
        updated_at (str): Timestamp when the rule was last updated.
    """
    id: int
    name: str
    description: str
    content: str
    template_id: Optional[int] = None
    repository_id: Optional[int] = None
    created_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())


@dataclass
class Repository:
    """Represents a repository that has been analyzed.

    Attributes:
        id (int): Unique identifier for the repository.
        name (str): Name of the repository.
        path (str): Path to the repository on disk.
        repo_type (str): Type of repository (e.g., "web", "library").
        languages (Dict[str, int]): Languages used in the repository with file counts.
        frameworks (Dict[str, List[str]]): Frameworks detected for each language.
        file_stats (Dict[str, Any]): Statistics about files in the repository.
        analysis_date (str): Timestamp when the repository was last analyzed.
    """
    id: int
    name: str
    path: str
    repo_type: str
    languages: Dict[str, int]
    frameworks: Dict[str, List[str]]
    file_stats: Dict[str, Any]
    analysis_date: str = field(default_factory=lambda: datetime.datetime.now().isoformat())


@dataclass
class RepositoryRuleAssociation:
    """Represents the association between a repository and a rule.

    Attributes:
        repository_id (int): ID of the repository.
        rule_id (int): ID of the rule.
        status (str): Status of the rule (e.g., "active", "disabled").
        priority (str): Priority of the rule (e.g., "high", "medium", "low").
    """
    repository_id: int
    rule_id: int
    status: str = "active"  # active, disabled
    priority: str = "medium"  # high, medium, low


# Schema definitions for the database tables
DB_SCHEMA = {
    "rule_templates": """
        CREATE TABLE IF NOT EXISTS rule_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """,

    "rules": """
        CREATE TABLE IF NOT EXISTS rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            content TEXT NOT NULL,
            template_id INTEGER,
            repository_id INTEGER,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (template_id) REFERENCES rule_templates (id),
            FOREIGN KEY (repository_id) REFERENCES repositories (id)
        )
    """,

    "repositories": """
        CREATE TABLE IF NOT EXISTS repositories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            path TEXT NOT NULL UNIQUE,
            repo_type TEXT NOT NULL,
            languages TEXT NOT NULL,
            frameworks TEXT NOT NULL,
            file_stats TEXT NOT NULL,
            analysis_date TEXT NOT NULL
        )
    """,

    "repository_rule_associations": """
        CREATE TABLE IF NOT EXISTS repository_rule_associations (
            repository_id INTEGER,
            rule_id INTEGER,
            status TEXT NOT NULL,
            priority TEXT NOT NULL,
            PRIMARY KEY (repository_id, rule_id),
            FOREIGN KEY (repository_id) REFERENCES repositories (id),
            FOREIGN KEY (rule_id) REFERENCES rules (id)
        )
    """
}


def rule_to_dict(rule: Rule) -> Dict[str, Any]:
    """Convert a Rule dataclass to a dictionary.

    Args:
        rule (Rule): The rule to convert.

    Returns:
        Dict[str, Any]: Dictionary representation of the rule.
    """
    return {
        "id": rule.id,
        "name": rule.name,
        "description": rule.description,
        "content": rule.content,
        "template_id": rule.template_id,
        "repository_id": rule.repository_id,
        "created_at": rule.created_at,
        "updated_at": rule.updated_at
    }


def dict_to_rule(rule_dict: Dict[str, Any]) -> Rule:
    """Convert a dictionary to a Rule dataclass.

    Args:
        rule_dict (Dict[str, Any]): Dictionary representation of a rule.

    Returns:
        Rule: The Rule dataclass.
    """
    return Rule(
        id=rule_dict["id"],
        name=rule_dict["name"],
        description=rule_dict["description"],
        content=rule_dict["content"],
        template_id=rule_dict.get("template_id"),
        repository_id=rule_dict.get("repository_id"),
        created_at=rule_dict.get("created_at", datetime.datetime.now().isoformat()),
        updated_at=rule_dict.get("updated_at", datetime.datetime.now().isoformat())
    )


def template_to_dict(template: RuleTemplate) -> Dict[str, Any]:
    """Convert a RuleTemplate dataclass to a dictionary.

    Args:
        template (RuleTemplate): The template to convert.

    Returns:
        Dict[str, Any]: Dictionary representation of the template.
    """
    return {
        "id": template.id,
        "name": template.name,
        "title": template.title,
        "description": template.description,
        "content": template.content,
        "category": template.category,
        "created_at": template.created_at
    }


def dict_to_template(template_dict: Dict[str, Any]) -> RuleTemplate:
    """Convert a dictionary to a RuleTemplate dataclass.

    Args:
        template_dict (Dict[str, Any]): Dictionary representation of a template.

    Returns:
        RuleTemplate: The RuleTemplate dataclass.
    """
    return RuleTemplate(
        id=template_dict["id"],
        name=template_dict["name"],
        title=template_dict["title"],
        description=template_dict["description"],
        content=template_dict["content"],
        category=template_dict["category"],
        created_at=template_dict.get("created_at", datetime.datetime.now().isoformat())
    )


def repository_to_dict(repo: Repository) -> Dict[str, Any]:
    """Convert a Repository dataclass to a dictionary.

    Args:
        repo (Repository): The repository to convert.

    Returns:
        Dict[str, Any]: Dictionary representation of the repository.
    """
    return {
        "id": repo.id,
        "name": repo.name,
        "path": repo.path,
        "repo_type": repo.repo_type,
        "languages": repo.languages,
        "frameworks": repo.frameworks,
        "file_stats": repo.file_stats,
        "analysis_date": repo.analysis_date
    }


def dict_to_repository(repo_dict: Dict[str, Any]) -> Repository:
    """Convert a dictionary to a Repository dataclass.

    Args:
        repo_dict (Dict[str, Any]): Dictionary representation of a repository.

    Returns:
        Repository: The Repository dataclass.
    """
    return Repository(
        id=repo_dict["id"],
        name=repo_dict["name"],
        path=repo_dict["path"],
        repo_type=repo_dict["repo_type"],
        languages=repo_dict["languages"],
        frameworks=repo_dict["frameworks"],
        file_stats=repo_dict["file_stats"],
        analysis_date=repo_dict.get("analysis_date", datetime.datetime.now().isoformat())
    )
