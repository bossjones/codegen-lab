"""Tests for the __main__ module."""

import sys
import logging
from typing import Dict, Any, List
if True:  # TYPE_CHECKING equivalent for runtime imports
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from cursor_rules_mcp_server.__main__ import (
    parse_args,
    setup_logging,
    main_cli,
)


def test_parse_args() -> None:
    """Test argument parsing."""
    # Test with default arguments
    with patch('sys.argv', ['cursor-rules-mcp-server']):
        args = parse_args()
        assert args.db_path == 'cursor_rules.db'
        assert args.port == 8000
        assert args.host == '127.0.0.1'
        assert args.log_level == 'INFO'

    # Test with custom arguments
    with patch('sys.argv', [
        'cursor-rules-mcp-server',
        '--db-path', 'custom.db',
        '--port', '9000',
        '--host', '0.0.0.0',
        '--log-level', 'DEBUG'
    ]):
        args = parse_args()
        assert args.db_path == 'custom.db'
        assert args.port == 9000
        assert args.host == '0.0.0.0'
        assert args.log_level == 'DEBUG'


def test_setup_logging(caplog: "LogCaptureFixture") -> None:
    """Test logging setup."""
    # Test with INFO level
    setup_logging('INFO')
    logger = logging.getLogger('cursor_rules_mcp_server')
    assert logger.level == logging.INFO

    # Test with DEBUG level
    setup_logging('DEBUG')
    logger = logging.getLogger('cursor_rules_mcp_server')
    assert logger.level == logging.DEBUG

    # Test with WARNING level
    setup_logging('WARNING')
    logger = logging.getLogger('cursor_rules_mcp_server')
    assert logger.level == logging.WARNING


def test_main_cli() -> None:
    """Test main_cli function."""
    with patch('cursor_rules_mcp_server.__main__.parse_args') as mock_parse_args, \
         patch('cursor_rules_mcp_server.__main__.setup_logging') as mock_setup_logging, \
         patch('cursor_rules_mcp_server.__main__.asyncio.set_event_loop_policy') as mock_set_policy, \
         patch('cursor_rules_mcp_server.__main__.asyncio.run') as mock_run, \
         patch('cursor_rules_mcp_server.__main__.run_server') as mock_run_server, \
         patch('sys.platform', 'win32'):

        # Mock arguments
        mock_args = MagicMock()
        mock_args.db_path = 'test.db'
        mock_args.port = 8000
        mock_args.host = '127.0.0.1'
        mock_args.log_level = 'INFO'
        mock_parse_args.return_value = mock_args

        # Call main_cli
        main_cli()

        # Verify function calls
        mock_parse_args.assert_called_once()
        mock_setup_logging.assert_called_once_with('INFO')
        mock_set_policy.assert_called_once()  # Windows-specific policy
        mock_run.assert_called_once()

        # Check that run_server was called with correct arguments
        run_server_call = mock_run.call_args[0][0]
        assert run_server_call == mock_run_server('test.db', 8000, '127.0.0.1')


def test_main_cli_keyboard_interrupt(capsys: "CaptureFixture") -> None:
    """Test main_cli function with KeyboardInterrupt."""
    with patch('cursor_rules_mcp_server.__main__.parse_args') as mock_parse_args, \
         patch('cursor_rules_mcp_server.__main__.setup_logging') as mock_setup_logging, \
         patch('cursor_rules_mcp_server.__main__.asyncio.run') as mock_run:

        # Mock arguments
        mock_args = MagicMock()
        mock_args.db_path = 'test.db'
        mock_args.port = 8000
        mock_args.host = '127.0.0.1'
        mock_args.log_level = 'INFO'
        mock_parse_args.return_value = mock_args

        # Simulate KeyboardInterrupt
        mock_run.side_effect = KeyboardInterrupt()

        # Call main_cli
        main_cli()

        # Check output
        captured = capsys.readouterr()
        assert "Shutting down" in captured.out


def test_main_cli_exception(capsys: "CaptureFixture") -> None:
    """Test main_cli function with general exception."""
    with patch('cursor_rules_mcp_server.__main__.parse_args') as mock_parse_args, \
         patch('cursor_rules_mcp_server.__main__.setup_logging') as mock_setup_logging, \
         patch('cursor_rules_mcp_server.__main__.asyncio.run') as mock_run:

        # Mock arguments
        mock_args = MagicMock()
        mock_args.db_path = 'test.db'
        mock_args.port = 8000
        mock_args.host = '127.0.0.1'
        mock_args.log_level = 'INFO'
        mock_parse_args.return_value = mock_args

        # Simulate exception
        mock_run.side_effect = Exception("Test error")

        # Call main_cli
        with pytest.raises(SystemExit) as excinfo:
            main_cli()

        # Check exit code
        assert excinfo.value.code == 1

        # Check output
        captured = capsys.readouterr()
        assert "Error:" in captured.out
        assert "Test error" in captured.out


def test_main_execution() -> None:
    """Test execution as main script."""
    with patch('cursor_rules_mcp_server.__main__.main_cli') as mock_main_cli, \
         patch.object(sys, 'argv', ['cursor-rules-mcp-server']):

        # Import __main__ module to trigger execution
        with patch.dict('sys.modules', {'__main__': None}):
            import cursor_rules_mcp_server.__main__

            # Check that main_cli was called
            mock_main_cli.assert_called_once()
