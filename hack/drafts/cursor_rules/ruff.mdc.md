---
description: Ruff linting configuration and usage guidelines
globs: "*.py"
---
# Ruff Configuration Guide

When you have questions about Ruff linting configuration, need help with linting rules, or want to run Ruff commands in this project, I can provide guidance based on the project's configuration.

## Running Ruff Commands

```bash
# Check linting issues in a file or directory
uv run ruff check path/to/file_or_dir

# Fix auto-fixable issues
uv run ruff check --fix path/to/file_or_dir

# Format code using Ruff formatter
uv run ruff format path/to/file_or_dir
```

## Project Configuration Overview

This project uses Ruff with the following configuration:

### Selected Rule Categories
- `D`: pydocstyle (Google convention)
- `E`: pycodestyle
- `F`: Pyflakes
- `UP`: pyupgrade
- `B`: flake8-bugbear
- `I`: isort

### Major Ignore Rules
- `B008`: Function calls in default arguments
- `D417`: Not requiring documentation for every function parameter
- `E501`: Line length limitations
- `UP006/UP007`: Type annotation format rules

### Special Configurations
- Special rules for tests, allowing relaxed documentation
- Special handling for notebook files
- Different rules for documentation and example files

## Troubleshooting Common Issues

If you encounter linting errors, I can help you understand and fix them by:
1. Identifying which rule is triggering
2. Explaining the purpose of the rule
3. Suggesting ways to fix the issue or properly ignore it
4. Explaining when to use per-file ignores vs. inline ignores

## Ignore Strategies

For one-off ignores:
```python
# Example of inline ignore
my_long_line = "..." # noqa: E501
```

For file-level ignores, add to pyproject.toml:
```toml
[tool.ruff.lint.per-file-ignores]
"your/file/path.py" = ["E501", "F401"]
```
