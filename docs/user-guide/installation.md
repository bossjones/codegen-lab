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
