"""Shared fixtures for tests."""

import os
import tempfile
import sqlite3
from pathlib import Path
from typing import Dict, Any, Generator, List, Optional
if True:  # TYPE_CHECKING equivalent for runtime imports
    from _pytest.fixtures import FixtureRequest
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture

import pytest
from unittest.mock import patch, MagicMock

from cursor_rules_mcp_server.models import DB_SCHEMA


@pytest.fixture
def temp_db_path() -> Generator[str, None, None]:
    """Create a temporary database file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_file:
        temp_db_path = temp_file.name

    try:
        # Initialize the database with schema
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()

        # Create tables
        for table_name, schema in DB_SCHEMA.items():
            columns = []
            for col_name, col_def in schema.items():
                columns.append(f"{col_name} {col_def}")

            create_table_sql = f"CREATE TABLE {table_name} ({', '.join(columns)})"
            cursor.execute(create_table_sql)

        conn.commit()
        conn.close()

        yield temp_db_path
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_db_path):
            os.unlink(temp_db_path)


@pytest.fixture
def sample_rule_template() -> Dict[str, Any]:
    """Generate a sample rule template for testing."""
    return {
        "name": "python-standards",
        "title": "Python Standards",
        "description": "Python coding standards for web applications",
        "content": "# Python Standards\n\nFollow these Python code standards.",
        "category": "Python",
        "created_at": "2023-01-01T00:00:00"
    }


@pytest.fixture
def sample_rule() -> Dict[str, Any]:
    """Generate a sample rule for testing."""
    return {
        "name": "my-python-standards",
        "description": "My Python standards",
        "content": "# My Python Standards\n\nFollow these Python standards.",
        "template_id": 1,
        "repository_id": 1,
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:00"
    }


@pytest.fixture
def sample_repository() -> Dict[str, Any]:
    """Generate a sample repository for testing."""
    return {
        "name": "test-repo",
        "path": "/path/to/test-repo",
        "repo_type": "web",
        "languages": '{"python": 80, "javascript": 20}',
        "frameworks": '["flask", "react"]',
        "file_stats": '{"total_files": 100, "python_files": 50, "javascript_files": 30}',
        "analysis_date": "2023-01-01T00:00:00"
    }


@pytest.fixture
def mock_repo_dir() -> Generator[str, None, None]:
    """Create a temporary mock repository directory with various file types."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create Python files
        (Path(temp_dir) / "main.py").write_text("print('Hello, world!')")
        (Path(temp_dir) / "app.py").write_text("from flask import Flask\napp = Flask(__name__)")

        # Create JavaScript files
        (Path(temp_dir) / "script.js").write_text("console.log('Hello, world!');")
        (Path(temp_dir) / "app.js").write_text("import React from 'react';")

        # Create HTML files
        (Path(temp_dir) / "index.html").write_text("<html><body>Hello</body></html>")

        # Create configuration files
        (Path(temp_dir) / "requirements.txt").write_text("flask==2.0.1\npython-dotenv==0.19.0")
        (Path(temp_dir) / "package.json").write_text('{"dependencies": {"react": "^17.0.2"}}')

        # Create a subdirectory with files
        subdir = Path(temp_dir) / "src"
        subdir.mkdir()
        (subdir / "utils.py").write_text("def helper(): pass")

        yield temp_dir
