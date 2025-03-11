# UV Workspace Management

This document provides documentation for working with UV workspaces in this project. UV workspaces allow you to manage multiple Python packages within a single repository, with proper dependency management and isolation.

## Quick Reference

| Command | Description |
|---------|-------------|
| `make uv-workspace-lock` | Update lockfile for entire workspace |
| `make uv-workspace-sync` | Install dependencies for workspace root |
| `make uv-workspace-package-sync package=name` | Install dependencies for specific package |
| `make uv-workspace-run package=name cmd="command"` | Run command in specific package |
| `make uv-workspace-init-package name=new-package` | Initialize a new package |
| `make uv-workspace-add-dep package=name` | Add package as workspace dependency |

## What is a UV Workspace?

UV Workspace is a feature of the [UV package manager](https://github.com/astral-sh/uv) that allows for managing multiple packages within a single repository. Benefits include:

- Single lockfile for the entire workspace
- Proper isolation between packages
- Ability to develop interdependent packages locally
- Simplified dependency management

## Workspace Structure

Our workspace is structured as follows:

```
codegen-lab/
├── pyproject.toml       # Workspace root config
├── packages/            # Directory containing workspace packages
│   ├── package-a/       # Individual package
│   │   ├── pyproject.toml
│   │   └── src/
│   │       └── package_a/
│   │           └── __init__.py
│   └── cursor-rules-mcp-server/  # Example package
│       ├── pyproject.toml
│       └── src/
│           └── cursor_rules_mcp_server/
│               └── __init__.py
└── src/
    └── codegen_lab/     # Workspace root package
        └── __init__.py
```

## Available Commands

These commands are available in the Makefile to help you work with UV workspaces:

### Core Workspace Management Commands

#### Update Lockfile for the Entire Workspace

```bash
make uv-workspace-lock
```

This command updates the lockfile for the entire workspace, resolving all dependencies across all packages and ensuring they work well together.

#### Install Dependencies for the Workspace Root

```bash
make uv-workspace-sync
```

This command installs all dependencies required by the workspace root package.

#### Install Dependencies for a Specific Package

```bash
make uv-workspace-package-sync package=cursor-rules-mcp-server
```

This command installs all dependencies required by a specific package. Replace `cursor-rules-mcp-server` with the name of your package.

#### Run a Command in a Specific Package

```bash
make uv-workspace-run package=cursor-rules-mcp-server cmd="python -m cursor_rules_mcp_server"
```

This command runs a specified command within the context of a specific package. Replace `cursor-rules-mcp-server` with the name of your package and `python -m cursor_rules_mcp_server` with the command you want to run.

### Package Management Utilities

#### Initialize a New Package in the Workspace

```bash
make uv-workspace-init-package name=new-package
```

This command initializes a new package in the workspace with the following:
- Creates the proper directory structure under `packages/new-package/`
- Generates a basic `pyproject.toml` file with required fields
- Creates an initial `__init__.py` file
- Adds a `README.md` file

After running this command, you'll need to add the package as a workspace dependency in the root `pyproject.toml` file, which can be done with the command below.

#### Add a Workspace Package as a Dependency to the Root

```bash
make uv-workspace-add-dep package=new-package
```

This command adds a workspace package as a dependency to the root `pyproject.toml` file. After running this command, you should run `make uv-workspace-lock` to update the lockfile.

## Working with Workspace Packages

### Creating a New Package

1. Initialize the package:
   ```bash
   make uv-workspace-init-package name=my-new-package
   ```

2. Add it as a workspace dependency:
   ```bash
   make uv-workspace-add-dep package=my-new-package
   ```

3. Update the lockfile:
   ```bash
   make uv-workspace-lock
   ```

### Developing Across Packages

If you need to use one workspace package in another:

1. Add the dependency in the package's `pyproject.toml`:
   ```toml
   [project]
   dependencies = [
       "other-workspace-package",
   ]
   ```

2. Run the workspace lock to update dependencies:
   ```bash
   make uv-workspace-lock
   ```

### Running Tests for a Specific Package

```bash
make uv-workspace-run package=my-package cmd="pytest"
```

## Troubleshooting

### Dependency Resolution Issues

If you encounter dependency resolution issues:

1. Make sure all workspace packages have compatible Python version requirements:
   ```bash
   grep "requires-python" packages/*/pyproject.toml
   ```

2. Try reinstalling all dependencies:
   ```bash
   make uv-workspace-sync
   ```

### Package Not Found

If a workspace package cannot be imported:

1. Verify it's properly added to the workspace sources in root `pyproject.toml`:
   ```toml
   [tool.uv.sources]
   my-package = { workspace = true }
   ```

2. Ensure the package directory structure follows the convention:
   ```
   packages/my-package/src/my_package/__init__.py
   ```

## Further Reading

- [UV Package Manager Documentation](https://github.com/astral-sh/uv)
- [UV Workspace Documentation](https://github.com/astral-sh/uv/blob/main/WORKSPACE.md)
