"""Tests for the utils module."""

import os
import tempfile
import json
from pathlib import Path
from typing import Dict, Any, Generator, List, Optional
if True:  # TYPE_CHECKING equivalent for runtime imports
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture

import pytest
from unittest.mock import patch, MagicMock

from cursor_rules_mcp_server.utils import (
    get_file_extension,
    count_files_by_extension,
    detect_language_from_extension,
    detect_framework_from_files,
    read_file_content,
    write_file_content,
    format_timestamp,
    slugify,
    validate_rule_content,
    extract_metadata_from_markdown,
)


def test_get_file_extension() -> None:
    """Test get_file_extension function."""
    assert get_file_extension("file.py") == "py"
    assert get_file_extension("file.txt") == "txt"
    assert get_file_extension("file") == ""
    assert get_file_extension("path/to/file.js") == "js"
    assert get_file_extension(".gitignore") == "gitignore"


@pytest.fixture
def temp_dir_with_files() -> Generator[str, None, None]:
    """Create a temporary directory with various file types."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create some files with different extensions
        (Path(temp_dir) / "file1.py").write_text("print('Hello')")
        (Path(temp_dir) / "file2.py").write_text("print('World')")
        (Path(temp_dir) / "file.js").write_text("console.log('Hello');")
        (Path(temp_dir) / "file.txt").write_text("Hello, world!")
        (Path(temp_dir) / "file.md").write_text("# Hello")

        # Create a subdirectory with files
        subdir = Path(temp_dir) / "subdir"
        subdir.mkdir()
        (subdir / "subfile.py").write_text("print('Subdir')")

        yield temp_dir


def test_count_files_by_extension(temp_dir_with_files: str) -> None:
    """Test count_files_by_extension function."""
    result = count_files_by_extension(temp_dir_with_files)

    assert result["py"] == 3  # 2 in root dir, 1 in subdir
    assert result["js"] == 1
    assert result["txt"] == 1
    assert result["md"] == 1


def test_detect_language_from_extension() -> None:
    """Test detect_language_from_extension function."""
    assert detect_language_from_extension("py") == "python"
    assert detect_language_from_extension("js") == "javascript"
    assert detect_language_from_extension("ts") == "typescript"
    assert detect_language_from_extension("html") == "html"
    assert detect_language_from_extension("css") == "css"
    assert detect_language_from_extension("unknown") is None


@pytest.fixture
def temp_dir_with_frameworks() -> Generator[str, None, None]:
    """Create a temporary directory with framework-specific files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create React-specific files
        (Path(temp_dir) / "package.json").write_text(json.dumps({
            "dependencies": {
                "react": "^17.0.2",
                "react-dom": "^17.0.2"
            }
        }))

        # Create Flask-specific files
        (Path(temp_dir) / "requirements.txt").write_text("flask==2.0.1\npython-dotenv==0.19.0")

        # Create Django-specific files
        (Path(temp_dir) / "manage.py").write_text("#!/usr/bin/env python\nimport django")

        yield temp_dir


def test_detect_framework_from_files(temp_dir_with_frameworks: str) -> None:
    """Test detect_framework_from_files function."""
    frameworks = detect_framework_from_files(temp_dir_with_frameworks)

    assert "react" in frameworks
    assert "flask" in frameworks
    assert "django" in frameworks


def test_read_file_content() -> None:
    """Test read_file_content function."""
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
        temp_file.write("Hello, world!")
        temp_file_path = temp_file.name

    try:
        content = read_file_content(temp_file_path)
        assert content == "Hello, world!"

        # Test with non-existent file
        with pytest.raises(FileNotFoundError):
            read_file_content("non_existent_file.txt")
    finally:
        os.unlink(temp_file_path)


def test_write_file_content() -> None:
    """Test write_file_content function."""
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, "test_file.txt")

        # Test writing to a new file
        write_file_content(file_path, "Hello, world!")
        assert os.path.exists(file_path)
        with open(file_path, "r") as f:
            assert f.read() == "Hello, world!"

        # Test overwriting an existing file
        write_file_content(file_path, "New content")
        with open(file_path, "r") as f:
            assert f.read() == "New content"

        # Test creating directories if they don't exist
        nested_file_path = os.path.join(temp_dir, "nested", "dir", "test_file.txt")
        write_file_content(nested_file_path, "Nested content")
        assert os.path.exists(nested_file_path)
        with open(nested_file_path, "r") as f:
            assert f.read() == "Nested content"


def test_format_timestamp() -> None:
    """Test format_timestamp function."""
    # Test with a specific timestamp
    timestamp = 1609459200.0  # 2021-01-01 00:00:00 UTC
    formatted = format_timestamp(timestamp)

    # The exact format might depend on the local timezone, so we'll check for key parts
    assert "2021" in formatted
    assert "01" in formatted  # Month or day

    # Test with current time
    current_formatted = format_timestamp()
    assert isinstance(current_formatted, str)
    assert len(current_formatted) > 0


def test_slugify() -> None:
    """Test slugify function."""
    assert slugify("Hello World") == "hello-world"
    assert slugify("Hello  World") == "hello-world"  # Multiple spaces
    assert slugify("Hello, World!") == "hello-world"  # Punctuation
    assert slugify("Hello_World") == "hello-world"  # Underscores
    assert slugify("HELLO WORLD") == "hello-world"  # Uppercase
    assert slugify("  hello  ") == "hello"  # Leading/trailing spaces
    assert slugify("hello-world") == "hello-world"  # Already slugified


def test_validate_rule_content() -> None:
    """Test validate_rule_content function."""
    # Valid rule content with all required sections
    valid_content = """# Title

## Description
This is a description.

## When to Use
Use this when needed.

## Examples
Example code here.
"""
    assert validate_rule_content(valid_content) is True

    # Missing Description section
    invalid_content1 = """# Title

## When to Use
Use this when needed.

## Examples
Example code here.
"""
    assert validate_rule_content(invalid_content1) is False

    # Missing When to Use section
    invalid_content2 = """# Title

## Description
This is a description.

## Examples
Example code here.
"""
    assert validate_rule_content(invalid_content2) is False

    # Missing Examples section
    invalid_content3 = """# Title

## Description
This is a description.

## When to Use
Use this when needed.
"""
    assert validate_rule_content(invalid_content3) is False


def test_extract_metadata_from_markdown() -> None:
    """Test extract_metadata_from_markdown function."""
    markdown_content = """---
name: python-standards
title: Python Standards
description: Python coding standards
category: Python
---

# Python Standards

Follow these Python standards.
"""

    metadata, content = extract_metadata_from_markdown(markdown_content)

    assert metadata["name"] == "python-standards"
    assert metadata["title"] == "Python Standards"
    assert metadata["description"] == "Python coding standards"
    assert metadata["category"] == "Python"

    assert content.strip() == "# Python Standards\n\nFollow these Python standards."

    # Test with no metadata
    markdown_without_metadata = """# Python Standards

Follow these Python standards.
"""

    metadata, content = extract_metadata_from_markdown(markdown_without_metadata)

    assert metadata == {}
    assert content.strip() == "# Python Standards\n\nFollow these Python standards."

    # Test with empty metadata
    markdown_with_empty_metadata = """---
---

# Python Standards

Follow these Python standards.
"""

    metadata, content = extract_metadata_from_markdown(markdown_with_empty_metadata)

    assert metadata == {}
    assert content.strip() == "# Python Standards\n\nFollow these Python standards."
