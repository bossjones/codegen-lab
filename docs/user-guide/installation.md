# Installation

This page provides detailed installation instructions for Codegen Lab.

## System Requirements

- **Operating System**: macOS, Linux, or Windows
- **Python**: Version 3.10 or higher
- **Disk Space**: At least 500MB of free disk space
- **Memory**: Minimum 4GB RAM recommended

## Installation Methods

### Method 1: Using UV (Recommended)

UV is the preferred package manager for Codegen Lab.

```bash
# Clone the repository
git clone https://github.com/bossjones/codegen-lab.git
cd codegen-lab

# Create and activate virtual environment
uv venv --python 3.12.0
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv sync --frozen
```

### Working with UV Workspace

Codegen Lab is structured as a UV workspace, allowing management of multiple packages within a single repository.

```bash
# Install dependencies for the workspace root
make uv-workspace-sync

# Install dependencies for a specific package
make uv-workspace-package-sync package=cursor-rules-mcp-server

# Run a command in context of a specific package
make uv-workspace-run package=cursor-rules-mcp-server cmd="python -m cursor_rules_mcp_server"
```

For detailed information about UV workspace management, refer to the [UV Workspace documentation](../tools/uv-workspace.md).

### Method 2: Using pip

While UV is recommended, you can also use pip for installation.

```bash
# Clone the repository
git clone https://github.com/bossjones/codegen-lab.git
cd codegen-lab

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
```

### Method 3: Docker

For containerized deployment, you can use Docker.

```bash
# Build the Docker image
docker build -t codegen-lab .

# Run the container
docker run -it codegen-lab
```

## Troubleshooting

### Common Issues

#### Issue 1: Dependency Conflict

If you encounter dependency conflicts during installation, try:

```bash
uv sync --frozen --reinstall
```

#### Issue 2: Python Version

If your Python version is too old, update your Python installation or use a tool like pyenv to manage multiple Python versions.

### Getting Help

If you encounter any issues during installation, please:

1. Check the [Troubleshooting Guide](../troubleshooting.md)
2. Open an issue on the [GitHub repository](https://github.com/bossjones/codegen-lab/issues)
