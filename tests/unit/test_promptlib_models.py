"""Unit tests for promptlib models.

This test suite verifies the behavior and validation of the promptlib data models.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

import pytest

from codegen_lab.promptlib.models import (
    CursorRule,
    CursorRuleAction,
    CursorRuleExample,
    CursorRuleFilter,
    CursorRuleMetadata,
)

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture


@pytest.fixture
def sample_metadata() -> dict[str, str]:
    """Create a sample metadata dictionary for testing.

    Returns:
        Dict[str, str]: A dictionary containing sample metadata.

    """
    return {"priority": "high", "version": "1.0", "tags": ["python", "testing", "best-practices"]}


@pytest.fixture
def sample_filter() -> dict[str, str]:
    """Create a sample filter dictionary for testing.

    Returns:
        Dict[str, str]: A dictionary containing sample filter data.

    """
    return {"type": "file_extension", "pattern": "\\.py$"}


@pytest.fixture
def sample_action() -> dict[str, str]:
    """Create a sample action dictionary for testing.

    Returns:
        Dict[str, str]: A dictionary containing sample action data.

    """
    return {"type": "suggest", "message": "Follow Python best practices"}


@pytest.fixture
def sample_example() -> dict[str, str]:
    """Create a sample example dictionary for testing.

    Returns:
        Dict[str, str]: A dictionary containing sample example data.

    """
    return {
        "input": "def function():\n    pass",
        "output": 'def function() -> None:\n    """Function docstring."""\n    pass',
    }


def test_cursor_rule_metadata_validation(sample_metadata: dict[str, str]) -> None:
    """Test CursorRuleMetadata validation.

    Args:
        sample_metadata: Fixture providing sample metadata.

    """
    metadata = CursorRuleMetadata(**sample_metadata)
    assert metadata["priority"] == "high"
    assert metadata["version"] == "1.0"
    assert metadata["tags"] == ["python", "testing", "best-practices"]


def test_cursor_rule_filter_validation(sample_filter: dict[str, str]) -> None:
    """Test CursorRuleFilter validation.

    Args:
        sample_filter: Fixture providing sample filter data.

    """
    filter_obj = CursorRuleFilter(**sample_filter)
    assert filter_obj["type"] == "file_extension"
    assert filter_obj["pattern"] == "\\.py$"


def test_cursor_rule_action_validation(sample_action: dict[str, str]) -> None:
    """Test CursorRuleAction validation.

    Args:
        sample_action: Fixture providing sample action data.

    """
    action = CursorRuleAction(**sample_action)
    assert action["type"] == "suggest"
    assert action["message"] == "Follow Python best practices"


def test_cursor_rule_example_validation(sample_example: dict[str, str]) -> None:
    """Test CursorRuleExample validation.

    Args:
        sample_example: Fixture providing sample example data.

    """
    example = CursorRuleExample(**sample_example)
    assert "def function():" in example["input"]
    assert "def function() -> None:" in example["output"]


def test_cursor_rule_validation(
    sample_metadata: dict[str, str],
    sample_filter: dict[str, str],
    sample_action: dict[str, str],
    sample_example: dict[str, str],
) -> None:
    """Test complete CursorRule validation.

    Args:
        sample_metadata: Fixture providing sample metadata.
        sample_filter: Fixture providing sample filter data.
        sample_action: Fixture providing sample action data.
        sample_example: Fixture providing sample example data.

    """
    rule_data = {
        "name": "python-best-practices",
        "description": "Enforces Python best practices",
        "filters": [sample_filter],
        "actions": [sample_action],
        "examples": [sample_example],
        "metadata": sample_metadata,
    }

    rule = CursorRule(**rule_data)
    assert rule["name"] == "python-best-practices"
    assert rule["description"] == "Enforces Python best practices"
    assert len(rule["filters"]) == 1
    assert len(rule["actions"]) == 1
    assert len(rule["examples"]) == 1
    assert rule["metadata"] == sample_metadata
