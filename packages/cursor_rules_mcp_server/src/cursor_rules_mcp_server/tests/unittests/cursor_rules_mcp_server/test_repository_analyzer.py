"""Tests for the repository_analyzer module."""

import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Generator
if True:  # TYPE_CHECKING equivalent for runtime imports
    from _pytest.fixtures import FixtureRequest
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture

import pytest

from cursor_rules_mcp_server.repository_analyzer import (
    RepositoryAnalyzer,
    analyze_repository,
)


@pytest.fixture
def mock_repo_dir() -> Generator[Path, None, None]:
    """Create a mock repository directory with various file types.

    Returns:
        Generator[Path, None, None]: Path to the mock repository directory.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_dir = Path(temp_dir)

        # Create Python files
        py_dir = repo_dir / "src" / "mypackage"
        py_dir.mkdir(parents=True)

        with open(py_dir / "__init__.py", "w") as f:
            f.write("# Package init")

        with open(py_dir / "main.py", "w") as f:
            f.write("def main():\n    print('Hello world')")

        # Create JavaScript files
        js_dir = repo_dir / "static" / "js"
        js_dir.mkdir(parents=True)

        with open(js_dir / "app.js", "w") as f:
            f.write("console.log('Hello world');")

        # Create HTML files
        html_dir = repo_dir / "templates"
        html_dir.mkdir(parents=True)

        with open(html_dir / "index.html", "w") as f:
            f.write("<html><body><h1>Hello world</h1></body></html>")

        # Create requirements.txt
        with open(repo_dir / "requirements.txt", "w") as f:
            f.write("flask==2.0.1\npython-dotenv==0.19.0")

        # Create package.json
        with open(repo_dir / "package.json", "w") as f:
            f.write('{"name": "myapp", "dependencies": {"react": "^17.0.2"}}')

        # Create README.md
        with open(repo_dir / "README.md", "w") as f:
            f.write("# My App\n\nThis is a sample app.")

        yield repo_dir


def test_repository_analyzer_init() -> None:
    """Test RepositoryAnalyzer initialization."""
    analyzer = RepositoryAnalyzer("/path/to/repo")

    assert analyzer.repo_path == "/path/to/repo"
    assert analyzer.ignored_dirs == [".git", "node_modules", "venv", "__pycache__", ".venv"]


def test_collect_file_stats(mock_repo_dir: Path) -> None:
    """Test collecting file statistics.

    Args:
        mock_repo_dir (Path): Path to the mock repository directory.
    """
    analyzer = RepositoryAnalyzer(str(mock_repo_dir))
    stats = analyzer._collect_file_stats()

    assert stats["total_files"] > 0
    assert stats["has_requirements_txt"] is True
    assert stats["has_package_json"] is True
    assert stats["has_readme"] is True
    assert "src/mypackage" in stats["directories"]
    assert "static/js" in stats["directories"]
    assert "templates" in stats["directories"]
    assert ".py" in stats["extensions"]
    assert ".js" in stats["extensions"]
    assert ".html" in stats["extensions"]


def test_detect_languages(mock_repo_dir: Path) -> None:
    """Test detecting programming languages.

    Args:
        mock_repo_dir (Path): Path to the mock repository directory.
    """
    analyzer = RepositoryAnalyzer(str(mock_repo_dir))
    analyzer._collect_file_stats()  # Need to collect stats first
    languages = analyzer._detect_languages()

    assert "python" in languages
    assert "javascript" in languages
    assert "html" in languages


def test_detect_frameworks(mock_repo_dir: Path) -> None:
    """Test detecting frameworks.

    Args:
        mock_repo_dir (Path): Path to the mock repository directory.
    """
    analyzer = RepositoryAnalyzer(str(mock_repo_dir))
    analyzer._collect_file_stats()  # Need to collect stats first
    frameworks = analyzer._detect_frameworks()

    assert "flask" in frameworks
    assert "react" in frameworks


def test_determine_repo_type(mock_repo_dir: Path) -> None:
    """Test determining repository type.

    Args:
        mock_repo_dir (Path): Path to the mock repository directory.
    """
    analyzer = RepositoryAnalyzer(str(mock_repo_dir))
    analyzer._collect_file_stats()  # Need to collect stats first
    analyzer._detect_languages()  # Need to detect languages first
    analyzer._detect_frameworks()  # Need to detect frameworks first
    repo_type = analyzer._determine_repo_type()

    assert repo_type in ["web", "library", "cli", "unknown"]


def test_suggest_rules(mock_repo_dir: Path) -> None:
    """Test suggesting rules.

    Args:
        mock_repo_dir (Path): Path to the mock repository directory.
    """
    analyzer = RepositoryAnalyzer(str(mock_repo_dir))
    analyzer._collect_file_stats()  # Need to collect stats first
    analyzer._detect_languages()  # Need to detect languages first
    analyzer._detect_frameworks()  # Need to detect frameworks first
    analyzer._determine_repo_type()  # Need to determine repo type first
    rules = analyzer._suggest_rules()

    assert isinstance(rules, list)
    assert len(rules) > 0

    # Check that each rule has required fields
    for rule in rules:
        assert "name" in rule
        assert "description" in rule


def test_analyze(mock_repo_dir: Path) -> None:
    """Test the analyze method.

    Args:
        mock_repo_dir (Path): Path to the mock repository directory.
    """
    analyzer = RepositoryAnalyzer(str(mock_repo_dir))
    result = analyzer.analyze()

    assert isinstance(result, dict)
    assert "repo_type" in result
    assert "languages" in result
    assert "frameworks" in result
    assert "file_stats" in result
    assert "suggested_rules" in result


def test_analyze_repository_function(mock_repo_dir: Path) -> None:
    """Test the analyze_repository function.

    Args:
        mock_repo_dir (Path): Path to the mock repository directory.
    """
    result = analyze_repository(str(mock_repo_dir))

    assert isinstance(result, dict)
    assert "repo_type" in result
    assert "languages" in result
    assert "frameworks" in result
    assert "file_stats" in result
    assert "suggested_rules" in result
