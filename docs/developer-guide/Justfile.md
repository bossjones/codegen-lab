# Towncrier and Commitizen Commands

This document outlines the available commands for managing changelogs with Towncrier and commits with Commitizen in the project.

## Commitizen Commands

### Commit Management

| Command | Description |
|---------|-------------|
| `just commit-bump` | Bump the package version |
| `just commit-files` | Commit files using commitizen |
| `just commit-info` | Get commit information |

## Towncrier Commands

### Basic Usage

| Command | Description |
|---------|-------------|
| `just towncrier-build` | Build the combined news file from news fragments. If no fragments exist, adds "no significant changes". Processed fragments are removed after building. |
| `just towncrier-build-yes` | Build changelog without asking for confirmation |
| `just towncrier-build-version <version>` | Build changelog with a specific version override |
| `just towncrier-check` | Check if any news fragments exist that need to be added to changelog |
| `just towncrier-draft` | Show draft of what would be added to changelog without actually adding it |

### Creating News Fragments

| Command | Description |
|---------|-------------|
| `just towncrier-create <type> <issue> <content>` | Create a news fragment with specified type, issue number, and content |
| `just towncrier-new [entry_type] [message]` | Interactive creation of changelog entries. If type/message not provided, will prompt or use PR/commit info |

### Bulk Operations

| Command | Description |
|---------|-------------|
| `just towncrier-from-commits <tag> [branch]` | Create changelog entries from commit messages between a tag and branch (defaults to main) |

### Helper Commands

| Command | Description |
|---------|-------------|
| `just towncrier-types` | List all available news fragment types from config |
| `just init-changelog` | Initialize the changelog |
| `just changelog` | Show towncrier version and build draft changelog for main version |

## News Fragment Types

The following types are available for changelog entries:

| Type | Description |
|------|-------------|
| `breaking` | Breaking Changes |
| `feat` | Features |
| `fix` | Bug Fixes |
| `docs` | Documentation |
| `chore` | Chores |
| `refactor` | Code Refactoring |
| `perf` | Performance Improvements |
| `ci` | CI/CD Improvements |
| `deps` | Dependencies |
| `security` | Security |
| `test` | Testing |
| `style` | Code Style |
| `build` | Build System |

## Examples

### Creating a New Changelog Entry

```bash
# Interactive mode (will prompt for type and message)
just towncrier-new

# Specify type and message directly
just towncrier-new feat "Added new feature X"

# Create entry for specific issue/PR
just towncrier-create feat 123 "Added new feature X"
```

### Building the Changelog

```bash
# Build with confirmation prompt
just towncrier-build

# Build without confirmation
just towncrier-build-yes

# Build with specific version
just towncrier-build-version 1.2.3
```

### Bulk Creating Entries from Commits

```bash
# Create entries from commits between v1.0.0 and main branch
just towncrier-from-commits v1.0.0

# Create entries from commits between v1.0.0 and develop branch
just towncrier-from-commits v1.0.0 develop
```

### Committing Changes

```bash
# Commit files using commitizen
just commit-files

# Bump version
just commit-bump

# Get commit information
just commit-info
```
