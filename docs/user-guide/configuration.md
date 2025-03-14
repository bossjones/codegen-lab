# Configuration

This page explains how to configure Codegen Lab for your specific needs.

## Configuration File

Codegen Lab uses a YAML-based configuration file located at `config.yaml` in the project root directory. You can also specify a custom configuration file path when running Codegen Lab.

### Example Configuration

```yaml
# Basic configuration
name: "My Codegen Project"
version: "1.0.0"

# Environment settings
environment:
  python_version: "3.12.0"
  cuda_support: true
  debug_mode: false

# Model settings
model:
  name: "gpt-4"
  temperature: 0.7
  max_tokens: 2048
  top_p: 0.95

# Paths
paths:
  output_dir: "./generated"
  templates_dir: "./templates"
  cache_dir: "./.cache"

# Logging
logging:
  level: "INFO"
  file: "./logs/codegen.log"
  rotation: "daily"
```

## Configuration Options

### Basic Configuration

| Option | Description | Default |
|--------|-------------|---------|
| `name` | Project name | "Codegen Project" |
| `version` | Project version | "0.1.0" |

### Environment Settings

| Option | Description | Default |
|--------|-------------|---------|
| `environment.python_version` | Python version to use | "3.10.0" |
| `environment.cuda_support` | Enable CUDA support | false |
| `environment.debug_mode` | Enable debug mode | false |

### Model Settings

| Option | Description | Default |
|--------|-------------|---------|
| `model.name` | Model to use | "gpt-3.5-turbo" |
| `model.temperature` | Temperature parameter | 0.7 |
| `model.max_tokens` | Maximum tokens to generate | 1024 |
| `model.top_p` | Top-p sampling parameter | 0.9 |

### Paths

| Option | Description | Default |
|--------|-------------|---------|
| `paths.output_dir` | Output directory | "./generated" |
| `paths.templates_dir` | Templates directory | "./templates" |
| `paths.cache_dir` | Cache directory | "./.cache" |

### Logging

| Option | Description | Default |
|--------|-------------|---------|
| `logging.level` | Logging level | "INFO" |
| `logging.file` | Log file path | "./logs/codegen.log" |
| `logging.rotation` | Log rotation | "daily" |

## Environment Variables

Configuration can also be specified using environment variables. Environment variables take precedence over config file settings.

| Environment Variable | Config Equivalent | Description |
|----------------------|-------------------|-------------|
| `CODEGEN_MODEL_NAME` | `model.name` | Model to use |
| `CODEGEN_MODEL_TEMP` | `model.temperature` | Temperature parameter |
| `CODEGEN_DEBUG` | `environment.debug_mode` | Enable debug mode |
| `CODEGEN_OUTPUT_DIR` | `paths.output_dir` | Output directory |
| `CODEGEN_LOG_LEVEL` | `logging.level` | Logging level |

## Command Line Arguments

Most configuration options can also be set via command line arguments. Command line arguments take precedence over both environment variables and config file settings.

```bash
python -m codegen_lab --model gpt-4 --temperature 0.8 --debug --output-dir ./custom_output
```

## UV Workspace Configuration

Codegen Lab uses UV workspaces to manage multiple packages within a single repository. The workspace configuration is defined in the root `pyproject.toml` file.

### Root pyproject.toml Configuration

The root `pyproject.toml` file contains the configuration for the entire workspace:

```toml
[build-system]
requires = ["setuptools>=61"]
build-backend = "setuptools.build_meta"

[project]
name = "codegen-lab"
version = "0.1.0"
description = "A toolkit for AI-assisted code generation and development"
requires-python = ">=3.12"
dependencies = [
    "better-exceptions>=0.3.3",
]

# UV Workspace Configuration
[tool.uv.sources]
# Workspace packages
cursor-rules-mcp-server = { workspace = true }
# Add other packages here
```

### Workspace Package Configuration

Each package in the `packages` directory has its own `pyproject.toml` file:

```toml
[project]
name = "cursor-rules-mcp-server"
version = "0.1.0"
description = "Cursor rules MCP server package"
requires-python = ">=3.12"
dependencies = [
    "better-exceptions>=0.3.3",
]

[build-system]
requires = ["setuptools>=61"]
build-backend = "setuptools.build_meta"

[tool.setuptools]
package-dir = {"" = "src"}
packages = ["cursor_rules_mcp_server"]
```

### Workspace Dependencies

To use one workspace package as a dependency in another, add it to the dependencies list:

```toml
[project]
dependencies = [
    "another-workspace-package",
]
```

Then update the workspace lockfile:

```bash
make uv-workspace-lock
```

For more detailed information about working with UV workspaces, refer to the [UV Workspace documentation](../tools/uv-workspace.md).
