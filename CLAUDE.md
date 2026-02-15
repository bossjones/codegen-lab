# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Key Development Commands

### Essential Commands for Daily Development

```bash
# Testing and Quality Assurance
uv run pytest                      # Run all tests
uv run pytest tests/unit/          # Run unit tests only
uv run pytest tests/integration/   # Run integration tests only
uv run pytest -k "test_name"       # Run specific test
uv run pytest --cov-report=html    # Generate HTML coverage report

# Code Quality and Formatting
uvx ruff format                    # Format Python code
uvx ruff check                     # Lint Python code
uvx ruff check --fix              # Auto-fix linting issues
uv run pre-commit run -a          # Run all pre-commit hooks

# Build System - Choose one task runner
just --list                       # Show available Just tasks
task --list                       # Show available Taskfile tasks
make help                        # Show available Makefile targets

# Package and Dependency Management
uv sync                          # Install dependencies
uv lock                          # Update lockfile
uv add package-name              # Add new dependency
uv remove package-name           # Remove dependency

# UV Workspace Commands (Multi-package management)
make uv-workspace-sync           # Install workspace dependencies
make uv-workspace-lock           # Update workspace lockfile
make uv-workspace-package-sync package=cursor-rules-mcp-server  # Sync specific package
make uv-workspace-run package=cursor-rules-mcp-server cmd="python -m cursor_rules_mcp_server"

# MCP Server Development
make run-prompt-library-mcp      # Run the prompt library MCP server
make run-mcp-dev script=src/codegen_lab/prompt_library.py  # Run MCP in dev mode
npx -y @modelcontextprotocol/inspector uv run python -m packages.cursor_rules_mcp_server.src.cursor_rules_mcp_server.fserver

# Documentation
make docs-serve                  # Serve documentation locally
uv run mkdocs serve             # Alternative docs serve command
make docs-build                 # Build documentation
```

### Task Runners Available

This project supports three equivalent task runners - choose based on your preference:

1. **Justfile** (recommended): `just <command>`
2. **Taskfile**: `task <command>`
3. **Makefile**: `make <command>`

## High-Level Architecture

### Core Application Structure

```
src/codegen_lab/
├── __init__.py                 # Main package
├── cli.py                     # MCP CLI client implementation
├── prompt_library.py          # Legacy monolithic prompt library
└── promptlib/                 # Modular refactored prompt library
    ├── models.py              # Data models for cursor rules
    ├── resources.py           # MCP resource endpoints
    ├── tools.py              # MCP tool implementations
    ├── utils.py              # Utility functions
    └── workflows.py           # Workflow orchestration
```

### Multi-Package Workspace

This repository uses UV workspace to manage multiple packages:

- **Root package**: `codegen-lab` - Main application and CLI
- **Workspace package**: `cursor-rules-mcp-server` - Specialized MCP server for cursor rules

### Key Components

1. **MCP Integration**: Implements Model Context Protocol for AI tooling
   - Prompt library MCP server at `src/codegen_lab/prompt_library.py`
   - Cursor rules MCP server at `packages/cursor_rules_mcp_server/`

2. **Cursor Rules System**: Manages AI cursor rule files
   - Staging area: `hack/drafts/cursor_rules/`
   - Production rules: `.cursor/rules/`
   - Migration command: `make update-cursor-rules`

3. **LLM Workflow Tools**: Task-based AI workflow automation
   - Bundle generation with repomix: `task llm:generate_bundle`
   - Code analysis and review generation
   - Test generation workflows

### Testing Framework

- **Framework**: pytest exclusively (unittest module prohibited)
- **Structure**:
  - `tests/unit/` - Unit tests
  - `tests/integration/` - Integration tests
  - `tests/conftest.py` - Shared fixtures
- **Coverage**: Configured for HTML, XML, and terminal output
- **Required imports for tests**:
  ```python
  from typing import TYPE_CHECKING
  if TYPE_CHECKING:
      from _pytest.capture import CaptureFixture
      from _pytest.fixtures import FixtureRequest
      from _pytest.logging import LogCaptureFixture
      from _pytest.monkeypatch import MonkeyPatch
      from pytest_mock.plugin import MockerFixture
  ```

### Documentation System

- **Framework**: MkDocs with Material theme
- **Source**: `docs/` directory
- **Auto-generation**: API docs generated from source code
- **Deployment**: GitHub Pages integration

### Release Management

- **Version Management**: Commitizen for semantic versioning
- **Changelog**: Automated via towncrier
- **Release Scripts**: `scripts/ci/` directory contains release automation
- **Commands**:
  - `make changelog-update` - Update changelog from git history
  - `make changelog-finalize VERSION=x.y.z` - Finalize release

### Development Workflow Integration

1. **AI-Assisted Development**:
   - Cursor rules in `.cursor/rules/` for IDE assistance
   - Prompt library for code generation workflows
   - LLM bundle generation for context feeding

2. **Quality Gates**:
   - Pre-commit hooks for code quality
   - Automated testing with pytest
   - Coverage reporting and requirements
   - Type checking with pyright/ruff

3. **Package Management**:
   - UV for fast dependency resolution
   - Workspace setup for multi-package development
   - Lock file management for reproducible builds

## Common Development Patterns

### Adding New Dependencies
```bash
# Add to main package
uv add package-name

# Add to workspace package
cd packages/cursor-rules-mcp-server
uv add package-name

# Update workspace lockfile
make uv-workspace-lock
```

### Running Tests During Development
```bash
# Quick test run
uv run pytest tests/unit/test_specific.py -v

# With coverage
uv run pytest --cov=src --cov-report=term-missing

# Debug mode
uv run pytest --pdb tests/unit/test_failing.py
```

### Working with MCP Servers
```bash
# Develop prompt library MCP server
make run-mcp-dev script=src/codegen_lab/prompt_library.py

# Test cursor rules MCP server
make uv-workspace-run package=cursor-rules-mcp-server cmd="python -m cursor_rules_mcp_server"

# Inspect MCP server with tools
make inspect-mcp
```

### Managing Cursor Rules
```bash
# Update rules from staging to production
make update-cursor-rules

# Dry run to see what would change
make update-cursor-rules-dry-run

# Audit rule files
make audit-cursor-rules-stage
make audit-cursor-rules-prod
```
