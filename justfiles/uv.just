# UV-specific commands

# Add a new package to the project's dependencies
[group('uv')]
uv-add package:
    {{UV_RUN}} uv add {{package}}

# Add a new development package to the project's dependencies
[group('uv')]
uv-add-dev package:
    {{UV_RUN}} uv add --dev {{package}}

# Generate a new lock file based on requirements.txt
[group('uv')]
uv-lock:
    {{UV_RUN}} uv lock

# Update all dependencies to their latest versions and regenerate the lock file
[group('uv')]
uv-lock-upgrade:
    {{UV_RUN}} uv lock --upgrade

# Update a specific package to its latest version in the lock file
[group('uv')]
uv-lock-upgrade-package package:
    {{UV_RUN}} uv lock --upgrade-package {{package}}

# Verify that the lock file is up-to-date with requirements
[group('uv')]
uv-check-lock:
    {{UV_RUN}} uv lock --check

# Install dependencies from the lock file in frozen mode
[group('uv')]
uv-sync:
    {{UV_RUN}} uv sync --frozen

# Install development dependencies from the lock file in frozen mode
[group('uv')]
uv-sync-dev:
    {{UV_RUN}} uv sync --frozen --dev

# Install dependencies with specific extras from the lock file
[group('uv')]
uv-sync-extras extra:
    {{UV_RUN}} uv sync --frozen --extra {{extra}}

# Install dependencies with all extras from the lock file
[group('uv')]
uv-sync-all-extras:
    {{UV_RUN}} uv sync --frozen --all-extras

# Install dependencies with inexact version matching
[group('uv')]
uv-sync-inexact:
    {{UV_RUN}} uv sync --frozen --inexact

# Install only direct dependencies without sub-dependencies
[group('uv')]
uv-sync-no-deps:
    {{UV_RUN}} uv sync --frozen --no-deps

# Install dependencies without installing the project itself
[group('uv')]
uv-sync-no-project:
    {{UV_RUN}} uv sync --frozen --no-install-project

# Install dependencies for a specific dependency group
[group('uv')]
uv-sync-group group:
    {{UV_RUN}} uv sync --frozen --group {{group}}

# Install dependencies for all dependency groups
[group('uv')]
uv-sync-all-groups:
    {{UV_RUN}} uv sync --frozen --all-groups

# List all outdated packages in the environment
[group('uv')]
uv-outdated:
    {{UV_RUN}} uv pip list --outdated

# Display dependency tree for the project
[group('uv')]
uv-tree:
    {{UV_RUN}} uv tree

# Run a Python script with UV
run-python +args:
    {{UV_RUN}} python {{args}}
