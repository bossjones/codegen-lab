# Release Process Guide

This document outlines the release process for the Codegen Lab project. We use a combination of tools to ensure consistent, high-quality releases.

## Core Tools

- **UV**: Primary package manager for dependency management
- **Commitizen**: For conventional commits and version management
- **Towncrier**: For changelog management
- **Just**: For automation of common tasks
- **Pre-commit**: For code quality checks

## Versioning Scheme

This project follows [PEP 440](https://www.python.org/dev/peps/pep-0440/) for versioning and uses Commitizen for version management. Version numbers are automatically handled by Commitizen based on conventional commits.

Version components:
- **Major**: Breaking changes to the public API
- **Minor**: New features or non-breaking changes
- **Patch**: Bug fixes and minor improvements

## Release Process

### 1. Pre-release Checks

Run the full test suite and quality checks:
```bash
just check
```

This runs:
- Code quality checks (ruff)
- Type checking (mypy)
- Unit tests (pytest)
- Security checks
- Coverage verification

### 2. Changelog Management

We use Towncrier to manage our changelog. For each PR, create a news fragment:

```bash
# Create a new changelog entry
just towncrier-new

# Or manually with type and message
just towncrier-create type issue "Your change description"
```

Available fragment types:
- `breaking`: Breaking changes
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `chore`: Maintenance tasks
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `ci`: CI/CD changes
- `deps`: Dependency updates
- `security`: Security fixes
- `test`: Test improvements
- `style`: Code style changes
- `build`: Build system changes

### 3. Version Bumping

When ready to release:

```bash
# Bump version based on conventional commits
just commit-bump

# This will:
# 1. Analyze commits since last release
# 2. Determine appropriate version bump
# 3. Update version in pyproject.toml
# 4. Create a git tag
```

### 4. Building the Release

```bash
# Build the package
just package-build

# This creates:
# - A wheel file in dist/
# - A source distribution in dist/
```

### 5. Creating the Release

```bash
# Create GitHub release
just release-create

# This will:
# 1. Create a GitHub release
# 2. Generate release notes
# 3. Tag the release
```

If something goes wrong:
```bash
# Delete the release
just release-delete

# Or reset (delete and recreate)
just release-reset
```

### 6. Post-release Tasks

After a successful release:

1. Verify the GitHub release was created correctly
2. Check the generated release notes
3. Verify the version tag was created
4. Ensure the changelog was updated

## Development Workflow

### 1. Making Changes

Follow the conventional commits specification when making commits:

```bash
just commit-files
```

This will guide you through creating a properly formatted commit message.

### 2. Adding Changelog Entries

Create changelog entries as you work:

```bash
just towncrier-new
```

### 3. Checking Status

View commit information:
```bash
just commit-info
```

View pending changelog entries:
```bash
just towncrier-draft
```

## UV Package Management

We use UV for all package management tasks. Common commands:

```bash
# Install all dependencies
just uv-sync

# Install development dependencies
just uv-sync-dev

# Add a new dependency
just uv-add package_name

# Add a development dependency
just uv-add-dev package_name

# Update lockfile
just uv-lock

# Check for outdated packages
just uv-outdated
```

## Troubleshooting

If you encounter issues during the release process:

1. **Version conflicts**: Use `just release-delete` to remove the problematic release and try again
2. **Changelog issues**: Use `just towncrier-check` to verify fragments
3. **Build problems**: Clean the build artifacts with `just clean-build` and retry
4. **Dependency issues**: Update the lockfile with `just uv-lock-upgrade`

For more detailed information about available commands, run:
```bash
just --list
```
