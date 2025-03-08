"""MCP CLI Client

This module implements a command-line interface for interacting with MCP servers.

Implementation Checklist:
1. ✅ Set up basic Typer application structure
2. ✅ Implement configuration management
   - Load configuration from file
   - Support environment variables
   - Handle server profiles
3. ✅ Implement server connection handling
   - Support different transport mechanisms (stdio, SSE)
   - Handle connection lifecycle
4. ✅ Implement core commands
   - list-servers: List configured servers
   - list-tools: List available tools on a server
   - call-tool: Call a tool on a server
   - list-resources: List available resources on a server
   - read-resource: Read a resource from a server
5. Implement utility commands
   - config: Manage configuration
   - version: Show version information
6. Add proper error handling
   - Connection errors
   - Protocol errors
   - User input validation
7. Implement output formatting
   - JSON output
   - Pretty-printed output
   - Support for different output formats
8. Add documentation
   - Help text for commands
   - Examples
   - Man page generation
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, cast

import typer
from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client
from mcp.types import (
    AnyUrl,
    BlobResourceContents,
    CallToolResult,
    ImageContent,
    ListResourcesResult,
    ListToolsResult,
    ReadResourceResult,
    Resource,
    ResourceTemplate,
    TextContent,
    TextResourceContents,
)
from pydantic import BaseModel, Field
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.traceback import install as install_rich_traceback

# Install rich traceback handler
install_rich_traceback(show_locals=True)

# Create Typer app
app = typer.Typer(
    name="mcp-client",
    help="Command-line client for MCP servers",
    add_completion=False,
)

# Create console for rich output
console = Console()

# Define version
__version__ = "0.1.0"


# Custom exceptions
class MCPClientError(Exception):
    """Base exception for MCP client errors."""

    pass


class ConfigurationError(MCPClientError):
    """Exception raised for configuration errors."""

    pass


class MCPConnectionError(MCPClientError):
    """Exception raised for connection errors."""

    pass


class ProtocolError(MCPClientError):
    """Exception raised for protocol errors."""

    pass


class InputValidationError(MCPClientError):
    """Exception raised for input validation errors."""

    pass


# Configuration models
class StdioServerConfig(BaseModel):
    """Configuration for a stdio server."""

    type: str = Field("stdio", const=True)
    command: str
    args: list[str] = Field(default_factory=list)
    env: dict[str, str] = Field(default_factory=dict)


class SSEServerConfig(BaseModel):
    """Configuration for an SSE server."""

    type: str = Field("sse", const=True)
    url: str
    headers: dict[str, str] = Field(default_factory=dict)


class Config(BaseModel):
    """MCP client configuration."""

    servers: dict[str, StdioServerConfig | SSEServerConfig] = Field(default_factory=dict)
    default_server: str | None = None


def get_config_path() -> Path:
    """Get the path to the configuration file.

    Returns:
        Path: The path to the configuration file.

    """
    # Check for environment variable
    if config_path_env := os.environ.get("MCP_CONFIG_PATH"):
        return Path(config_path_env)

    # Default to ~/.mcp/config.json
    return Path.home() / ".mcp" / "config.json"


def load_config() -> Config:
    """Load the configuration from the configuration file.

    Returns:
        Config: The loaded configuration.

    Raises:
        ConfigurationError: If the configuration file cannot be loaded.

    """
    config_path = get_config_path()

    # Create default config if it doesn't exist
    if not config_path.exists():
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config = Config()
        save_config(config)
        return config

    try:
        with open(config_path) as f:
            config_data = json.load(f)
        return Config.model_validate(config_data)
    except json.JSONDecodeError as e:
        raise ConfigurationError(f"Invalid JSON in configuration file: {e!s}")
    except Exception as e:
        raise ConfigurationError(f"Error loading configuration: {e!s}")


def save_config(config: Config) -> None:
    """Save the configuration to the configuration file.

    Args:
        config: The configuration to save.

    Raises:
        ConfigurationError: If the configuration file cannot be saved.

    """
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(config_path, "w") as f:
            json.dump(config.model_dump(), f, indent=2)
    except Exception as e:
        raise ConfigurationError(f"Error saving configuration: {e!s}")


# Server connection handling
async def connect_to_server(server_name: str | None = None) -> tuple[ClientSession, Any]:
    """Connect to an MCP server.

    Args:
        server_name: Name of the server to connect to. If None, the default server is used.

    Returns:
        Tuple containing the client session and the transport context manager.

    Raises:
        ConfigurationError: If the server is not found or if no servers are configured.
        MCPConnectionError: If the connection to the server fails.

    """
    config = load_config()

    # Check if there are any servers configured
    if not config.servers:
        raise ConfigurationError(
            "No servers configured. Use 'mcp-client config add-stdio-server' or "
            "'mcp-client config add-sse-server' to add a server."
        )

    # Determine which server to use
    if server_name is None:
        server_name = config.default_server
        if server_name is None:
            # Use the first server if no default is set
            server_name = next(iter(config.servers.keys()))

    # Check if the server exists
    if server_name not in config.servers:
        raise ConfigurationError(f"Server '{server_name}' not found in configuration")

    server_config = config.servers[server_name]

    try:
        # Connect to the server based on its type
        if server_config.type == "stdio":
            stdio_config = cast(StdioServerConfig, server_config)
            server_params = StdioServerParameters(
                command=stdio_config.command,
                args=stdio_config.args,
                env=stdio_config.env,
            )
            transport = await stdio_client(server_params)
            read, write = transport
            session = ClientSession(read, write)
            await session.initialize()
            return session, transport
        else:  # sse
            sse_config = cast(SSEServerConfig, server_config)
            transport = await sse_client(
                sse_config.url,
                headers=sse_config.headers,
            )
            read, write = transport
            session = ClientSession(read, write)
            await session.initialize()
            return session, transport
    except Exception as e:
        raise MCPConnectionError(f"Failed to connect to server '{server_name}': {e!s}")


async def with_server_connection(server_name: str | None, callback: Any) -> Any:
    """Execute a callback with a server connection.

    Args:
        server_name: Name of the server to connect to. If None, the default server is used.
        callback: Async function to call with the client session.

    Returns:
        The result of the callback.

    """
    try:
        session, transport = await connect_to_server(server_name)
        try:
            return await callback(session)
        except Exception as e:
            if isinstance(e, MCPClientError):
                raise e
            raise ProtocolError(f"Error during server communication: {e!s}")
        finally:
            # Clean up the connection
            read, write = transport
            await write.aclose()
    except MCPClientError as e:
        # Re-raise client errors
        raise e
    except Exception as e:
        # Wrap other exceptions
        raise MCPConnectionError(f"Unexpected error: {e!s}")


# Output formatting functions
def format_tool_result(result: CallToolResult, output_format: str = "pretty") -> None:
    """Format and print a tool result.

    Args:
        result: The tool result to format.
        output_format: The output format to use.

    """
    if output_format == "json":
        console.print(json.dumps(result.model_dump(), indent=2))
        return

    # Pretty print
    if result.isError:
        console.print("[red]Tool execution failed[/red]")

    for content in result.content:
        if isinstance(content, TextContent):
            console.print(Panel(content.text, title="Text Content"))
        elif isinstance(content, ImageContent):
            console.print(
                Panel(f"[Image data: {len(content.data)} bytes]", title=f"Image Content ({content.mimeType})")
            )
        else:
            console.print(Panel(str(content), title="Unknown Content"))


def format_resource_result(result: ReadResourceResult, output_format: str = "pretty") -> None:
    """Format and print a resource result.

    Args:
        result: The resource result to format.
        output_format: The output format to use.

    """
    if output_format == "json":
        console.print(json.dumps(result.model_dump(), indent=2))
        return

    # Pretty print
    for content in result.contents:
        if isinstance(content, TextResourceContents):
            console.print(Panel(content.text, title=f"Text Resource: {content.uri}"))
        elif isinstance(content, BlobResourceContents):
            console.print(
                Panel(
                    f"[Blob data: {len(content.blob)} bytes]",
                    title=f"Blob Resource: {content.uri} ({content.mimeType})",
                )
            )
        else:
            console.print(Panel(str(content), title="Unknown Resource Content"))


# Core commands
@app.command("list-tools")
def list_tools(
    server: str | None = typer.Option(None, "--server", "-s", help="Server to connect to"),
    output_format: str = typer.Option("pretty", "--format", "-f", help="Output format (pretty, json)"),
) -> None:
    """List available tools on a server."""

    async def _list_tools(session: ClientSession) -> None:
        result: ListToolsResult = await session.list_tools()

        if output_format == "json":
            console.print(json.dumps(result.model_dump(), indent=2))
            return

        # Pretty print
        if not result.tools:
            console.print("[yellow]No tools available on this server.[/yellow]")
            return

        table = Table(title="Available Tools")
        table.add_column("Name")
        table.add_column("Description")

        for tool in result.tools:
            table.add_row(tool.name, tool.description or "")

        console.print(table)

    try:
        run_async(with_server_connection(server, _list_tools))
    except MCPClientError as e:
        handle_client_error(e)


@app.command("call-tool")
def call_tool(
    tool_name: str = typer.Argument(..., help="Name of the tool to call"),
    arguments: str = typer.Argument("{}", help="JSON arguments for the tool"),
    server: str | None = typer.Option(None, "--server", "-s", help="Server to connect to"),
    output_format: str = typer.Option("pretty", "--format", "-f", help="Output format (pretty, json)"),
) -> None:
    """Call a tool on a server."""
    # Parse arguments
    try:
        args = json.loads(arguments)
    except json.JSONDecodeError:
        handle_client_error(InputValidationError("Invalid JSON arguments"))
        return

    async def _call_tool(session: ClientSession) -> None:
        result: CallToolResult = await session.call_tool(tool_name, args)
        format_tool_result(result, output_format)

    try:
        run_async(with_server_connection(server, _call_tool))
    except MCPClientError as e:
        handle_client_error(e)


@app.command("list-resources")
def list_resources(
    server: str | None = typer.Option(None, "--server", "-s", help="Server to connect to"),
    output_format: str = typer.Option("pretty", "--format", "-f", help="Output format (pretty, json)"),
) -> None:
    """List available resources on a server."""

    async def _list_resources(session: ClientSession) -> None:
        result: ListResourcesResult = await session.list_resources()

        if output_format == "json":
            console.print(json.dumps(result.model_dump(), indent=2))
            return

        # Pretty print
        if not result.resources and not result.templates:
            console.print("[yellow]No resources available on this server.[/yellow]")
            return

        # Print resources
        if result.resources:
            table = Table(title="Available Resources")
            table.add_column("Name")
            table.add_column("URI")
            table.add_column("Description")
            table.add_column("MIME Type")

            for resource in result.resources:
                table.add_row(
                    resource.name,
                    str(resource.uri),
                    resource.description or "",
                    resource.mimeType or "",
                )

            console.print(table)

        # Print templates
        if result.templates:
            table = Table(title="Available Resource Templates")
            table.add_column("Name")
            table.add_column("URI Template")
            table.add_column("Description")

            for template in result.templates:
                table.add_row(
                    template.name,
                    template.uriTemplate,
                    template.description or "",
                )

            console.print(table)

    try:
        run_async(with_server_connection(server, _list_resources))
    except MCPClientError as e:
        handle_client_error(e)


@app.command("read-resource")
def read_resource(
    uri: str = typer.Argument(..., help="URI of the resource to read"),
    server: str | None = typer.Option(None, "--server", "-s", help="Server to connect to"),
    output_format: str = typer.Option("pretty", "--format", "-f", help="Output format (pretty, json)"),
    output_file: str | None = typer.Option(None, "--output", "-o", help="Output file for binary resources"),
) -> None:
    """Read a resource from a server."""

    async def _read_resource(session: ClientSession) -> None:
        try:
            resource_uri = AnyUrl(uri)
        except Exception:
            raise InputValidationError(f"Invalid resource URI: {uri}")

        result: ReadResourceResult = await session.read_resource(resource_uri)

        # Save to file if requested
        if output_file and result.contents:
            content = result.contents[0]
            try:
                if isinstance(content, BlobResourceContents):
                    with open(output_file, "wb") as f:
                        f.write(content.blob)
                    console.print(f"[green]Saved blob resource to {output_file}[/green]")
                    return
                elif isinstance(content, TextResourceContents):
                    with open(output_file, "w") as f:
                        f.write(content.text)
                    console.print(f"[green]Saved text resource to {output_file}[/green]")
                    return
            except Exception as e:
                raise MCPClientError(f"Failed to save resource to file: {e!s}")

        # Otherwise format and print
        format_resource_result(result, output_format)

    try:
        run_async(with_server_connection(server, _read_resource))
    except MCPClientError as e:
        handle_client_error(e)


# Config command group
config_app = typer.Typer(help="Manage MCP client configuration")
app.add_typer(config_app, name="config")


@config_app.command("list-servers")
def config_list_servers() -> None:
    """List all configured servers."""
    try:
        config = load_config()

        if not config.servers:
            console.print("[yellow]No servers configured.[/yellow]")
            return

        table = Table(title="Configured Servers")
        table.add_column("Name")
        table.add_column("Type")
        table.add_column("Details")
        table.add_column("Default")

        for name, server in config.servers.items():
            is_default = name == config.default_server
            default_mark = "✓" if is_default else ""

            if server.type == "stdio":
                details = f"Command: {server.command} {' '.join(server.args)}"
            else:  # sse
                details = f"URL: {server.url}"

            table.add_row(name, server.type, details, default_mark)

        console.print(table)
    except MCPClientError as e:
        handle_client_error(e)


@config_app.command("add-stdio-server")
def config_add_stdio_server(
    name: str = typer.Argument(..., help="Name of the server"),
    command: str = typer.Argument(..., help="Command to run the server"),
    args: list[str] = typer.Option([], "--arg", help="Arguments to pass to the command"),
    env: list[str] = typer.Option([], "--env", help="Environment variables in the format KEY=VALUE"),
    default: bool = typer.Option(False, "--default", help="Set as the default server"),
) -> None:
    """Add a stdio server to the configuration."""
    try:
        config = load_config()

        # Parse environment variables
        env_dict = {}
        for env_var in env:
            try:
                key, value = env_var.split("=", 1)
                env_dict[key] = value
            except ValueError:
                raise InputValidationError(f"Invalid environment variable format: {env_var}")

        # Create server config
        server_config = StdioServerConfig(
            command=command,
            args=args,
            env=env_dict,
        )

        # Add to config
        config.servers[name] = server_config

        # Set as default if requested or if it's the only server
        if default or len(config.servers) == 1:
            config.default_server = name

        # Save config
        save_config(config)
        console.print(f"[green]Added stdio server '{name}'[/green]")
    except MCPClientError as e:
        handle_client_error(e)


@config_app.command("add-sse-server")
def config_add_sse_server(
    name: str = typer.Argument(..., help="Name of the server"),
    url: str = typer.Argument(..., help="URL of the server"),
    headers: list[str] = typer.Option([], "--header", help="Headers in the format KEY=VALUE"),
    default: bool = typer.Option(False, "--default", help="Set as the default server"),
) -> None:
    """Add an SSE server to the configuration."""
    try:
        config = load_config()

        # Parse headers
        headers_dict = {}
        for header in headers:
            try:
                key, value = header.split("=", 1)
                headers_dict[key] = value
            except ValueError:
                raise InputValidationError(f"Invalid header format: {header}")

        # Create server config
        server_config = SSEServerConfig(
            url=url,
            headers=headers_dict,
        )

        # Add to config
        config.servers[name] = server_config

        # Set as default if requested or if it's the only server
        if default or len(config.servers) == 1:
            config.default_server = name

        # Save config
        save_config(config)
        console.print(f"[green]Added SSE server '{name}'[/green]")
    except MCPClientError as e:
        handle_client_error(e)


@config_app.command("remove-server")
def config_remove_server(
    name: str = typer.Argument(..., help="Name of the server to remove"),
) -> None:
    """Remove a server from the configuration."""
    try:
        config = load_config()

        if name not in config.servers:
            raise ConfigurationError(f"Server '{name}' not found in configuration")

        # Remove server
        del config.servers[name]

        # Update default server if needed
        if config.default_server == name:
            config.default_server = next(iter(config.servers.keys())) if config.servers else None

        # Save config
        save_config(config)
        console.print(f"[green]Removed server '{name}'[/green]")
    except MCPClientError as e:
        handle_client_error(e)


@config_app.command("set-default-server")
def config_set_default_server(
    name: str = typer.Argument(..., help="Name of the server to set as default"),
) -> None:
    """Set the default server."""
    try:
        config = load_config()

        if name not in config.servers:
            raise ConfigurationError(f"Server '{name}' not found in configuration")

        # Set default server
        config.default_server = name

        # Save config
        save_config(config)
        console.print(f"[green]Set '{name}' as the default server[/green]")
    except MCPClientError as e:
        handle_client_error(e)


@config_app.command("show")
def config_show() -> None:
    """Show the current configuration."""
    try:
        config = load_config()
        console.print(Syntax(json.dumps(config.model_dump(), indent=2), "json"))
    except MCPClientError as e:
        handle_client_error(e)


@config_app.command("path")
def config_path() -> None:
    """Show the path to the configuration file."""
    console.print(str(get_config_path()))


# Utility commands
@app.command()
def version() -> None:
    """Show the version of the MCP CLI client."""
    console.print(f"MCP CLI Client v{__version__}")


@app.command("list-servers")
def list_servers() -> None:
    """List all configured servers."""
    config_list_servers()


@app.command("info")
def info() -> None:
    """Show information about the MCP CLI client."""
    console.print(Panel(f"MCP CLI Client v{__version__}", title="Version"))

    # Show configuration path
    config_path = get_config_path()
    console.print(Panel(str(config_path), title="Configuration Path"))

    # Show server information
    try:
        config = load_config()

        if not config.servers:
            console.print(Panel("[yellow]No servers configured.[/yellow]", title="Servers"))
        else:
            server_info = []
            for name, server in config.servers.items():
                is_default = name == config.default_server
                default_mark = " (default)" if is_default else ""

                if server.type == "stdio":
                    server_info.append(f"{name}{default_mark}: stdio - {server.command}")
                else:  # sse
                    server_info.append(f"{name}{default_mark}: sse - {server.url}")

            console.print(Panel("\n".join(server_info), title="Servers"))
    except MCPClientError as e:
        console.print(Panel(f"[red]Error loading configuration: {e!s}[/red]", title="Servers"))


# Error handling
def handle_client_error(error: MCPClientError) -> None:
    """Handle client errors.

    Args:
        error: The error to handle.

    """
    if isinstance(error, ConfigurationError):
        console.print(f"[red]Configuration error: {error!s}[/red]")
    elif isinstance(error, MCPConnectionError):
        console.print(f"[red]Connection error: {error!s}[/red]")
    elif isinstance(error, ProtocolError):
        console.print(f"[red]Protocol error: {error!s}[/red]")
    elif isinstance(error, InputValidationError):
        console.print(f"[red]Input validation error: {error!s}[/red]")
    else:
        console.print(f"[red]Error: {error!s}[/red]")

    # Exit with error code
    sys.exit(1)


@app.callback()
def callback(
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
) -> None:
    """MCP CLI Client - Interact with MCP servers from the command line."""
    # Set debug mode
    if debug:
        # Show full traceback for errors
        def exception_handler(exc_type, exc_value, exc_traceback):
            console.print_exception(show_locals=True)

        sys.excepthook = exception_handler


def run_async(func: Any) -> Any:
    """Run an async function in the event loop.

    Args:
        func: Async function to run.

    Returns:
        The result of the async function.

    """
    return asyncio.run(func)


def main() -> None:
    """Run the MCP CLI client."""
    app()


if __name__ == "__main__":
    main()
