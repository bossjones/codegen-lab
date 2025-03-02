"""Tests for the CLI module."""

import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Generator, List
if True:  # TYPE_CHECKING equivalent for runtime imports
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture

import pytest
from unittest.mock import patch, MagicMock

from cursor_rules_mcp_server.cli import (
    parse_args,
    setup_logging,
    analyze_repository_command,
    generate_rule_command,
    export_rules_command,
    main,
)


def test_parse_args() -> None:
    """Test argument parsing."""
    with patch('sys.argv', ['cursor-rules', 'analyze', '--repo-path', '/path/to/repo']):
        args = parse_args()
        assert args.command == 'analyze'
        assert args.repo_path == '/path/to/repo'

    with patch('sys.argv', ['cursor-rules', 'generate', '--rule-name', 'python-standards']):
        args = parse_args()
        assert args.command == 'generate'
        assert args.rule_name == 'python-standards'

    with patch('sys.argv', ['cursor-rules', 'export', '--output-dir', '/path/to/output']):
        args = parse_args()
        assert args.command == 'export'
        assert args.output_dir == '/path/to/output'


def test_setup_logging(caplog: "LogCaptureFixture") -> None:
    """Test logging setup."""
    # Test with default log level
    setup_logging()
    assert caplog.get_records('call')[0].levelname == 'INFO'

    # Test with debug log level
    caplog.clear()
    setup_logging(log_level='DEBUG')
    assert caplog.get_records('call')[0].levelname == 'DEBUG'

    # Test with warning log level
    caplog.clear()
    setup_logging(log_level='WARNING')
    assert len(caplog.get_records('call')) == 0  # No INFO logs should be present


@pytest.fixture
def temp_repo_dir() -> Generator[str, None, None]:
    """Create a temporary directory for testing repository analysis."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create some mock files
        python_file = Path(temp_dir) / "main.py"
        python_file.write_text("print('Hello, world!')")

        requirements_file = Path(temp_dir) / "requirements.txt"
        requirements_file.write_text("flask==2.0.1\npython-dotenv==0.19.0")

        yield temp_dir


def test_analyze_repository_command(temp_repo_dir: str, capsys: "CaptureFixture") -> None:
    """Test analyze_repository_command function."""
    with patch('cursor_rules_mcp_server.cli.analyze_repository') as mock_analyze:
        mock_analyze.return_value = {
            'repo_type': 'web',
            'languages': {'python': 100},
            'frameworks': ['flask'],
            'file_stats': {'total_files': 2},
            'suggested_rules': ['python-standards', 'flask-best-practices']
        }

        # Create mock args
        args = MagicMock()
        args.repo_path = temp_repo_dir
        args.output_format = 'json'

        analyze_repository_command(args)

        # Check that analyze_repository was called with the correct path
        mock_analyze.assert_called_once_with(temp_repo_dir)

        # Check output
        captured = capsys.readouterr()
        assert 'web' in captured.out
        assert 'python' in captured.out
        assert 'flask' in captured.out
        assert 'python-standards' in captured.out


def test_generate_rule_command(capsys: "CaptureFixture") -> None:
    """Test generate_rule_command function."""
    with patch('cursor_rules_mcp_server.cli.generate_rule') as mock_generate:
        mock_generate.return_value = {
            'name': 'python-standards',
            'title': 'Python Standards',
            'description': 'Python coding standards',
            'content': '# Python Standards\n\nFollow these Python standards.'
        }

        # Create mock args
        args = MagicMock()
        args.rule_name = 'python-standards'
        args.repo_path = '/path/to/repo'
        args.output_format = 'json'
        args.title = None
        args.description = None

        generate_rule_command(args)

        # Check that generate_rule was called with the correct arguments
        mock_generate.assert_called_once_with(
            'python-standards',
            repo_path='/path/to/repo',
            title=None,
            description=None
        )

        # Check output
        captured = capsys.readouterr()
        assert 'Python Standards' in captured.out
        assert 'Python coding standards' in captured.out


@pytest.fixture
def temp_output_dir() -> Generator[str, None, None]:
    """Create a temporary directory for testing rule export."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


def test_export_rules_command(temp_output_dir: str, capsys: "CaptureFixture") -> None:
    """Test export_rules_command function."""
    with patch('cursor_rules_mcp_server.cli.RuleGenerator') as MockRuleGenerator:
        # Setup mock rule generator
        mock_generator = MagicMock()
        MockRuleGenerator.return_value = mock_generator

        mock_generator.analyze_repo.return_value = {
            'repo_type': 'web',
            'languages': {'python': 100},
            'frameworks': ['flask'],
            'suggested_rules': ['python-standards', 'flask-best-practices']
        }

        mock_generator.generate_multiple_rules.return_value = [
            {
                'name': 'python-standards',
                'title': 'Python Standards',
                'description': 'Python coding standards',
                'content': '# Python Standards\n\nFollow these Python standards.'
            },
            {
                'name': 'flask-best-practices',
                'title': 'Flask Best Practices',
                'description': 'Best practices for Flask applications',
                'content': '# Flask Best Practices\n\nFollow these Flask best practices.'
            }
        ]

        # Create mock args
        args = MagicMock()
        args.repo_path = '/path/to/repo'
        args.output_dir = temp_output_dir
        args.rule_names = ['python-standards', 'flask-best-practices']

        export_rules_command(args)

        # Check that methods were called with correct arguments
        mock_generator.analyze_repo.assert_called_once_with('/path/to/repo')
        mock_generator.generate_multiple_rules.assert_called_once_with(
            ['python-standards', 'flask-best-practices']
        )
        mock_generator.export_rules_to_files.assert_called_once()

        # Check output
        captured = capsys.readouterr()
        assert 'Exported 2 rules to' in captured.out


def test_main() -> None:
    """Test main function."""
    with patch('cursor_rules_mcp_server.cli.parse_args') as mock_parse_args, \
         patch('cursor_rules_mcp_server.cli.setup_logging') as mock_setup_logging, \
         patch('cursor_rules_mcp_server.cli.analyze_repository_command') as mock_analyze, \
         patch('cursor_rules_mcp_server.cli.generate_rule_command') as mock_generate, \
         patch('cursor_rules_mcp_server.cli.export_rules_command') as mock_export:

        # Test analyze command
        mock_args = MagicMock()
        mock_args.command = 'analyze'
        mock_args.log_level = 'INFO'
        mock_parse_args.return_value = mock_args

        main()

        mock_setup_logging.assert_called_once_with('INFO')
        mock_analyze.assert_called_once_with(mock_args)
        mock_generate.assert_not_called()
        mock_export.assert_not_called()

        # Reset mocks
        mock_setup_logging.reset_mock()
        mock_analyze.reset_mock()

        # Test generate command
        mock_args.command = 'generate'
        main()

        mock_setup_logging.assert_called_once_with('INFO')
        mock_analyze.assert_not_called()
        mock_generate.assert_called_once_with(mock_args)
        mock_export.assert_not_called()

        # Reset mocks
        mock_setup_logging.reset_mock()
        mock_generate.reset_mock()

        # Test export command
        mock_args.command = 'export'
        main()

        mock_setup_logging.assert_called_once_with('INFO')
        mock_analyze.assert_not_called()
        mock_generate.assert_not_called()
        mock_export.assert_called_once_with(mock_args)

        # Reset mocks
        mock_setup_logging.reset_mock()
        mock_export.reset_mock()

        # Test invalid command
        mock_args.command = 'invalid'
        with pytest.raises(ValueError):
            main()
