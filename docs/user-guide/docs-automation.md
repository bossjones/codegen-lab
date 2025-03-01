# Documentation Automation

This guide explains how Codegen Lab's documentation server is automated to prevent port conflicts and simplify the development workflow.

## Automatic Port Management

The `make docs-serve` command now includes automatic port management, featuring:

1. **Automatic Process Detection**: The system automatically detects if a MkDocs server is already running on port 8000
2. **Process Termination**: If requested (with the `--kill-existing` flag), it automatically terminates existing MkDocs processes
3. **Alternative Port Selection**: If killing is not possible or not requested, it finds an available port automatically
4. **Clear Status Messages**: The system provides clear messages about what it's doing and which port it's using

## Usage

### Basic Usage

To start the documentation server with automatic port management:

```bash
make docs-serve
```

This will:
- Use port 8000 if available
- Kill any existing MkDocs processes on port 8000 if found
- Fall back to an alternative port if needed

### Custom Options

You can customize the behavior by running the script directly:

```bash
uv run python scripts/serve_docs.py --no-kill-existing --port 8080
```

Available options:
- `--port PORT`: Specify a custom port (default: 8000)
- `--kill-existing`: Kill existing MkDocs processes on the port (default)
- `--no-kill-existing`: Don't kill existing processes, use an alternative port instead
- `--no-gh-deploy-url`: Don't use GitHub Pages URL in configuration (useful for local development)
- `--clean`: Clean the build directory before building
- `--build-only`: Only build the documentation, don't serve it

## How It Works

The automation script (`scripts/serve_docs.py`) performs the following steps:

1. Checks if the requested port is already in use
2. Identifies any MkDocs processes running on that port
3. If `--kill-existing` is set, attempts to terminate those processes
4. If the port is still unavailable, scans for an available port
5. Starts the MkDocs server with the appropriate configuration
6. Provides clear terminal output about what's happening

## Graceful Termination

The script also handles interruption gracefully. When you press Ctrl+C:

1. The script catches the keyboard interrupt
2. It sends a graceful termination signal to the MkDocs process
3. It ensures clean exit of all processes

This prevents orphaned processes that might cause port conflicts in the future.
