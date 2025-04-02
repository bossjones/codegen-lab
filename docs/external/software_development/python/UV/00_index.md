---
tags:
  - UV
  - Python
  - Open source
---

# Overview

## Official docs

The definitive source of info about UV is [here][UV docs].

## Install

=== "Homebrew"

    ```shell
    brew install uv
    ```

=== "pipx"

    ```shell
    pipx install uv
    ```

=== "pip"

    ```shell
    pip install --user uv
    ```

=== "Installer script (Linux/Mac)"

    ```shell
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

More info on [Installation](https://github.com/astral/uv#installation)

## TL;DR &mdash; It's like npm for Python, but faster

[UV][] is a modern Python package manager and environment management tool that's significantly faster than pip and other alternatives. If you are familiar with `npm` in Node.js, UV provides similar functionality but with blazing fast performance.

| npm                                 | UV                                           |
| ----------------------------------- | -------------------------------------------- |
| `npm install`                       | :material-check: `uv sync --frozen`          |
| `npm install <package>`             | :material-check: `uv add <package>`          |
| `npm install --save-dev <package>`  | :material-check: `uv add --dev <package>`    |
| `npm run <script>`                  | :material-check: `uv run <script>`           |
| `package.json`                      | :material-check: `pyproject.toml`            |
| `package-lock.json`                 | :material-check: `uv.lock`                   |

## Why should I use UV?

### Blazing Fast Package Management

- UV is written in Rust and is significantly faster than traditional Python package managers
- Parallel downloads and optimized dependency resolution
- Smart caching for improved performance
- Native support for modern Python packaging standards

### Nicer management of dependencies (including an auto-generated lock file)

- When you `git clone` a Python project that uses UV, your next step is to run `uv sync --frozen` to install dependencies from the lockfile.

- Adding dependencies is simple:
  - For production: `uv add <package>`
  - For development: `uv add --dev <package>`
  These commands install the package and update your `pyproject.toml` file.

- Dependencies are managed in two files:
  - `pyproject.toml`: Your direct dependencies
  - `uv.lock`: Complete locked dependency tree with hashes
  This replaces traditional `requirements.txt` files with a more robust solution.

### Python Environment Management

UV can manage Python environments and installations directly:

```shell
# Install specific Python versions
uv python install 3.12.0  # Install specific version
uv python install 3.11    # Install latest 3.11.x
uv python install 3.12 --default  # Install and set as default

# Installation options
uv python install 3.12 --install-dir /custom/path  # Custom installation directory
uv python install 3.12 --reinstall  # Reinstall existing version
uv python install 3.12 --force  # Replace existing executables

# Create virtual environments
uv venv --python 3.12.0  # Create venv with specific version
uv venv  # Create venv with default Python version

# Install dependencies using lockfile
uv sync --frozen
```

UV's Python installer supports:
- Multiple Python versions side by side
- Custom installation directories via `--install-dir`
- Mirror configuration for downloads
- Offline mode and caching options
- PyPy installations with custom mirrors
- Setting default Python versions

For secure installations, UV provides options like:
- `--native-tls` for platform certificate stores
- `--offline` for air-gapped environments
- `--allow-insecure-host` for specific trusted hosts
- Cache control via `--no-cache` or `--cache-dir`

### Running Python Code

UV provides a clean way to run Python code in your environment:

```shell
# Run Python scripts
uv run python script.py

# Run modules
uv run python -m pytest

# Run specific commands
uv run pytest tests/
```

### Just Integration

The project includes helpful just targets for common UV operations:

```shell
# Install all dependencies (including dev)
just install-project

# Run Python commands through UV
just run-python script.py

# Run tests with UV
just check-test

# Format code
just format

# Check code quality, types, and tests
just check

# Clean all caches and build artifacts
just clean

# Package management
just package-constraints  # Generate constraints.txt with hashes
just package-build       # Build package with constraints
```

### Package Management Operations

UV manages dependencies through locking and syncing. Here are common operations:

```shell
# Lock dependencies (creates/updates uv.lock)
just uv-lock  # Basic lock
just uv-lock-upgrade  # Upgrade all packages
just uv-lock-upgrade-package requests  # Upgrade specific package

# Sync environment from lockfile
just uv-sync  # Sync all dependencies
just uv-sync-dev  # Sync only dev dependencies
just uv-sync-extras extra_name  # Sync with specific extras

# Check lockfile status
just uv-check-lock  # Check if lockfile is up to date

# Add new packages
just uv-add requests  # Add production dependency
just uv-add-dev pytest  # Add development dependency

# View dependency information
just uv-outdated  # List outdated packages
just uv-tree  # Show dependency tree
```

Advanced sync options are available:

```shell
# Sync with specific options
just uv-sync-inexact  # Keep existing packages
just uv-sync-no-deps  # Skip dependencies
just uv-sync-no-project  # Skip project installation

# Group management
just uv-sync-group group_name  # Sync specific group
just uv-sync-all-groups  # Sync all groups
```

[UV]: https://github.com/astral/uv
[UV docs]: https://github.com/astral/uv#readme

## Common Issues and Solutions

### Environment Activation

Always ensure you're in the right environment:

```shell
# Activate the virtual environment
source .venv/bin/activate

# Verify activation
echo $VIRTUAL_ENV
```

### No Module Found Error

If you encounter a "module not found" error after adding new dependencies:

1. Ensure the package is in your `pyproject.toml`
2. Run `uv sync --frozen` to reinstall all dependencies
3. If the issue persists, try `uv sync --reinstall --frozen`
