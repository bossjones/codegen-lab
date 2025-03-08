# Building a CLI MCP Client

This report provides a comprehensive guide to building a command-line interface (CLI) client for the Model Context Protocol (MCP). It covers the architecture, components, implementation details, and best practices based on the analysis of the MCP Python SDK.

## Table of Contents

- [Building a CLI MCP Client](#building-a-cli-mcp-client)
  - [Table of Contents](#table-of-contents)
  - [Introduction to MCP](#introduction-to-mcp)
  - [Architecture Overview](#architecture-overview)
  - [Core Components](#core-components)
    - [Client Session](#client-session)
    - [Transport Mechanisms](#transport-mechanisms)
    - [Protocol Types](#protocol-types)
    - [CLI Interface](#cli-interface)
  - [Implementation Guide](#implementation-guide)
    - [Setting Up the Project](#setting-up-the-project)
    - [Implementing the Client Session](#implementing-the-client-session)
    - [Implementing Transport Mechanisms](#implementing-transport-mechanisms)
    - [Building the CLI Interface](#building-the-cli-interface)
    - [Error Handling and Logging](#error-handling-and-logging)
  - [Advanced Features](#advanced-features)
    - [Server Discovery](#server-discovery)
    - [Tool Execution](#tool-execution)
    - [Resource Management](#resource-management)
    - [Prompt Handling](#prompt-handling)
  - [Testing and Debugging](#testing-and-debugging)
  - [Example Implementation](#example-implementation)
  - [Best Practices](#best-practices)
  - [References](#references)

## Introduction to MCP

The Model Context Protocol (MCP) is a standardized JSON-RPC 2.0 based communication protocol for interaction between LLM clients and servers. It enables structured communication for accessing resources, calling tools, and exchanging messages with LLMs.

MCP separates the concerns of providing context from the actual LLM interaction, allowing applications to provide context for LLMs in a standardized way. This separation enables:

1. Building MCP clients that can connect to any MCP server
2. Creating MCP servers that expose resources, prompts, and tools
3. Using standard transports like stdio and SSE
4. Handling all MCP protocol messages and lifecycle events

## Architecture Overview

A CLI MCP client consists of several key architectural components:

1. **Client Session**: Manages the connection to MCP servers and handles protocol messages
2. **Transport Layer**: Provides communication channels (stdio, SSE) between client and server
3. **Protocol Types**: Defines the structure of messages exchanged between client and server
4. **CLI Interface**: Provides user interaction through command-line arguments and options
5. **Tool and Resource Management**: Handles discovery and interaction with server capabilities

The architecture follows a layered approach:

```
┌─────────────────────────────────────┐
│             CLI Interface           │
├─────────────────────────────────────┤
│           Client Session            │
├─────────────────────────────────────┤
│ Transport Layer (stdio, SSE, etc.)  │
├─────────────────────────────────────┤
│          Protocol Types             │
└─────────────────────────────────────┘
```

## Core Components

### Client Session

The `ClientSession` class is the central component that manages the connection to MCP servers. It handles:

- Initialization and connection setup
- Sending requests and receiving responses
- Managing protocol lifecycle events
- Handling server capabilities

Key methods include:
- `initialize()`: Establishes the connection and negotiates protocol version
- `list_resources()`: Retrieves available resources from the server
- `list_tools()`: Retrieves available tools from the server
- `call_tool()`: Executes a tool on the server
- `read_resource()`: Reads a resource from the server

### Transport Mechanisms

MCP supports multiple transport mechanisms:

1. **stdio**: Communication through standard input/output streams
   - Implemented in `stdio_client()` function
   - Uses `StdioServerParameters` for configuration
   - Suitable for local server processes

2. **SSE (Server-Sent Events)**: Communication through HTTP with server-sent events
   - Implemented in `sse_client()` function
   - Supports long-lived connections with event streaming
   - Suitable for remote server connections

### Protocol Types

The protocol types define the structure of messages exchanged between client and server. Key types include:

- `JSONRPCMessage`: Base type for all JSON-RPC messages
- `ClientRequest`: Requests sent from client to server
- `ServerRequest`: Requests sent from server to client
- `ClientNotification`: Notifications sent from client to server
- `ServerNotification`: Notifications sent from server to client
- `Resource`: Definition of a resource on the server
- `Tool`: Definition of a tool on the server
- `Prompt`: Definition of a prompt on the server

### CLI Interface

The CLI interface provides user interaction through command-line arguments and options. It includes:

- Command parsing and execution
- Help text and documentation
- Error handling and reporting
- Configuration management

## Implementation Guide

### Setting Up the Project

1. **Project Structure**:
   ```
   cli_mcp_client/
   ├── pyproject.toml
   ├── src/
   │   └── cli_mcp_client/
   │       ├── __init__.py
   │       ├── cli.py
   │       ├── client.py
   │       ├── config.py
   │       └── utils.py
   └── tests/
       └── test_cli_mcp_client.py
   ```

2. **Dependencies**:
   - `mcp`: Core MCP protocol implementation
   - `typer`: CLI framework
   - `pydantic`: Data validation and settings management
   - `anyio`: Asynchronous I/O library
   - `httpx`: HTTP client for SSE transport

3. **Configuration**:
   ```python
   # config.py
   from pydantic import BaseModel, Field
   from typing import Dict, List, Optional, Any

   class ServerConfig(BaseModel):
       command: str
       args: List[str] = Field(default_factory=list)
       env: Optional[Dict[str, str]] = None

   class Config(BaseModel):
       servers: Dict[str, ServerConfig]
       default_server: Optional[str] = None
   ```

### Implementing the Client Session

The client session manages the connection to MCP servers:

```python
# client.py
import asyncio
from contextlib import AsyncExitStack
from typing import Any, Dict, List, Optional, Tuple

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import mcp.types as types

class MCPClient:
    def __init__(self, server_name: str, server_config: Dict[str, Any]):
        self.server_name = server_name
        self.server_config = server_config
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

    async def connect(self) -> None:
        """Connect to the MCP server."""
        server_params = StdioServerParameters(
            command=self.server_config["command"],
            args=self.server_config["args"],
            env=self.server_config.get("env")
        )

        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        read, write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(read, write)
        )

        # Initialize the connection
        await self.session.initialize()

    async def list_tools(self) -> List[types.Tool]:
        """List available tools from the server."""
        if not self.session:
            raise RuntimeError("Not connected to server")

        result = await self.session.list_tools()
        return result.tools

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> types.CallToolResult:
        """Call a tool on the server."""
        if not self.session:
            raise RuntimeError("Not connected to server")

        return await self.session.call_tool(name, arguments)

    async def disconnect(self) -> None:
        """Disconnect from the server."""
        await self.exit_stack.aclose()
        self.session = None
```

### Implementing Transport Mechanisms

The transport mechanisms provide communication channels between client and server:

1. **stdio Transport**:
   ```python
   # Already implemented in mcp.client.stdio
   from mcp.client.stdio import stdio_client
   from mcp import StdioServerParameters

   # Usage
   server_params = StdioServerParameters(
       command="python",
       args=["server.py"],
       env={"API_KEY": "your-api-key"}
   )

   async with stdio_client(server_params) as (read, write):
       # Use read and write streams
   ```

2. **SSE Transport**:
   ```python
   # Already implemented in mcp.client.sse
   from mcp.client.sse import sse_client

   # Usage
   async with sse_client("https://example.com/mcp") as (read, write):
       # Use read and write streams
   ```

### Building the CLI Interface

The CLI interface provides user interaction:

```python
# cli.py
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

import typer
from rich.console import Console
from rich.table import Table

from .client import MCPClient
from .config import Config, ServerConfig

app = typer.Typer(
    name="mcp-client",
    help="MCP CLI client",
    add_completion=False,
)

console = Console()

def load_config(config_path: Path) -> Config:
    """Load configuration from file."""
    if not config_path.exists():
        console.print(f"[red]Config file not found: {config_path}[/red]")
        sys.exit(1)

    try:
        with open(config_path, "r") as f:
            config_data = json.load(f)
        return Config(**config_data)
    except Exception as e:
        console.print(f"[red]Error loading config: {e}[/red]")
        sys.exit(1)

@app.command()
def list_servers(
    config_file: Path = typer.Option(
        Path.home() / ".mcp" / "config.json",
        help="Path to config file",
    )
):
    """List configured servers."""
    config = load_config(config_file)

    table = Table("Name", "Command", "Args")
    for name, server in config.servers.items():
        table.add_row(
            name,
            server.command,
            " ".join(server.args)
        )

    console.print(table)

@app.command()
def list_tools(
    server: str = typer.Argument(None, help="Server name"),
    config_file: Path = typer.Option(
        Path.home() / ".mcp" / "config.json",
        help="Path to config file",
    )
):
    """List tools available on the server."""
    config = load_config(config_file)

    if server is None:
        server = config.default_server
        if server is None:
            console.print("[red]No server specified and no default server configured[/red]")
            sys.exit(1)

    if server not in config.servers:
        console.print(f"[red]Server not found: {server}[/red]")
        sys.exit(1)

    async def run():
        client = MCPClient(server, config.servers[server].dict())
        try:
            await client.connect()
            tools = await client.list_tools()

            table = Table("Name", "Description")
            for tool in tools:
                table.add_row(
                    tool.name,
                    tool.description or ""
                )

            console.print(table)
        finally:
            await client.disconnect()

    asyncio.run(run())

@app.command()
def call_tool(
    server: str,
    tool: str,
    arguments: str = typer.Argument("{}", help="JSON arguments"),
    config_file: Path = typer.Option(
        Path.home() / ".mcp" / "config.json",
        help="Path to config file",
    )
):
    """Call a tool on the server."""
    config = load_config(config_file)

    if server not in config.servers:
        console.print(f"[red]Server not found: {server}[/red]")
        sys.exit(1)

    try:
        args = json.loads(arguments)
    except json.JSONDecodeError:
        console.print("[red]Invalid JSON arguments[/red]")
        sys.exit(1)

    async def run():
        client = MCPClient(server, config.servers[server].dict())
        try:
            await client.connect()
            result = await client.call_tool(tool, args)

            console.print(json.dumps(result.model_dump(), indent=2))
        finally:
            await client.disconnect()

    asyncio.run(run())

def main():
    app()

if __name__ == "__main__":
    main()
```

### Error Handling and Logging

Proper error handling and logging are essential for a robust CLI client:

```python
# utils.py
import logging
import sys
from typing import Any, Dict, Optional

from rich.console import Console

console = Console()

def setup_logging(level: int = logging.INFO) -> None:
    """Set up logging configuration."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )

def handle_error(error: Exception, message: Optional[str] = None) -> None:
    """Handle and display errors."""
    if message:
        console.print(f"[red]{message}: {error}[/red]")
    else:
        console.print(f"[red]Error: {error}[/red]")
    sys.exit(1)
```

## Advanced Features

### Server Discovery

Implement server discovery to automatically find and connect to available MCP servers:

```python
# discovery.py
import os
import json
from pathlib import Path
from typing import Dict, List, Optional

def discover_claude_servers() -> Dict[str, Dict]:
    """Discover servers configured in Claude Desktop."""
    claude_config_path = Path.home() / ".claude" / "servers.json"
    if not claude_config_path.exists():
        return {}

    try:
        with open(claude_config_path, "r") as f:
            config = json.load(f)
        return config.get("mcpServers", {})
    except Exception:
        return {}
```

### Tool Execution

Implement tool execution with proper error handling and result formatting:

```python
async def execute_tool(client, tool_name, arguments, retries=2):
    """Execute a tool with retry logic."""
    for attempt in range(retries + 1):
        try:
            result = await client.call_tool(tool_name, arguments)
            return result
        except Exception as e:
            if attempt < retries:
                await asyncio.sleep(1.0 * (attempt + 1))
            else:
                raise e
```

### Resource Management

Implement resource management for reading and subscribing to resources:

```python
async def read_resource(client, uri):
    """Read a resource from the server."""
    result = await client.read_resource(uri)
    return result.contents

async def subscribe_to_resource(client, uri):
    """Subscribe to resource updates."""
    await client.subscribe_resource(uri)
    # Handle updates in a separate task
```

### Prompt Handling

Implement prompt handling for retrieving and using prompts:

```python
async def get_prompt(client, name, arguments=None):
    """Get a prompt from the server."""
    result = await client.get_prompt(name, arguments)
    return result.messages
```

## Testing and Debugging

Implement testing and debugging utilities:

```python
# test_utils.py
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, List, Tuple

from mcp import ClientSession
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
import mcp.types as types

@asynccontextmanager
async def mock_mcp_server() -> AsyncGenerator[Tuple[ClientSession, Dict], None]:
    """Create a mock MCP server for testing."""
    # Create memory streams for communication
    client_read, server_write = anyio.create_memory_object_stream(0)
    server_read, client_write = anyio.create_memory_object_stream(0)

    # Create a client session
    session = ClientSession(client_read, client_write)

    # Store server state
    state = {
        "tools": [
            types.Tool(
                name="test-tool",
                description="A test tool",
                inputSchema={"type": "object", "properties": {}}
            )
        ],
        "resources": []
    }

    # Start server task
    async def server_task():
        async for message in server_read:
            # Handle messages based on method
            pass

    task = asyncio.create_task(server_task())

    try:
        yield session, state
    finally:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
```

## Example Implementation

Here's a complete example of a simple CLI MCP client:

```python
# main.py
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

import typer
from rich.console import Console
from rich.table import Table

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import mcp.types as types

app = typer.Typer(
    name="mcp-client",
    help="MCP CLI client",
    add_completion=False,
)

console = Console()

class MCPClient:
    def __init__(self, server_config: Dict):
        self.server_config = server_config
        self.session = None

    async def connect(self):
        server_params = StdioServerParameters(
            command=self.server_config["command"],
            args=self.server_config["args"],
            env=self.server_config.get("env")
        )

        self.stdio_transport = await stdio_client(server_params)
        read, write = self.stdio_transport
        self.session = ClientSession(read, write)

        # Initialize the connection
        await self.session.initialize()

    async def list_tools(self):
        if not self.session:
            raise RuntimeError("Not connected to server")

        result = await self.session.list_tools()
        return result.tools

    async def call_tool(self, name, arguments):
        if not self.session:
            raise RuntimeError("Not connected to server")

        return await self.session.call_tool(name, arguments)

    async def disconnect(self):
        if hasattr(self, 'stdio_transport'):
            read, write = self.stdio_transport
            await write.aclose()
        self.session = None

@app.command()
def list_tools(
    config_file: Path = typer.Option(
        Path.home() / ".mcp" / "config.json",
        help="Path to config file",
    ),
    server: str = typer.Option(None, help="Server name")
):
    """List tools available on the server."""
    try:
        with open(config_file, "r") as f:
            config = json.load(f)
    except Exception as e:
        console.print(f"[red]Error loading config: {e}[/red]")
        sys.exit(1)

    servers = config.get("servers", {})

    if server is None:
        server = config.get("default_server")
        if server is None:
            console.print("[red]No server specified and no default server configured[/red]")
            sys.exit(1)

    if server not in servers:
        console.print(f"[red]Server not found: {server}[/red]")
        sys.exit(1)

    async def run():
        client = MCPClient(servers[server])
        try:
            await client.connect()
            tools = await client.list_tools()

            table = Table("Name", "Description")
            for tool in tools:
                table.add_row(
                    tool.name,
                    tool.description or ""
                )

            console.print(table)
        finally:
            await client.disconnect()

    asyncio.run(run())

@app.command()
def call_tool(
    server: str,
    tool: str,
    arguments: str = typer.Argument("{}", help="JSON arguments"),
    config_file: Path = typer.Option(
        Path.home() / ".mcp" / "config.json",
        help="Path to config file",
    )
):
    """Call a tool on the server."""
    try:
        with open(config_file, "r") as f:
            config = json.load(f)
    except Exception as e:
        console.print(f"[red]Error loading config: {e}[/red]")
        sys.exit(1)

    servers = config.get("servers", {})

    if server not in servers:
        console.print(f"[red]Server not found: {server}[/red]")
        sys.exit(1)

    try:
        args = json.loads(arguments)
    except json.JSONDecodeError:
        console.print("[red]Invalid JSON arguments[/red]")
        sys.exit(1)

    async def run():
        client = MCPClient(servers[server])
        try:
            await client.connect()
            result = await client.call_tool(tool, args)

            # Format and display the result
            for content in result.content:
                if content.type == "text":
                    console.print(content.text)
                elif content.type == "image":
                    console.print("[Image content]")
                elif content.type == "resource":
                    console.print(f"[Resource: {content.resource.uri}]")
        finally:
            await client.disconnect()

    asyncio.run(run())

def main():
    app()

if __name__ == "__main__":
    main()
```

## Best Practices

1. **Error Handling**:
   - Implement proper error handling for all operations
   - Provide clear error messages to users
   - Handle connection failures gracefully

2. **Configuration Management**:
   - Use a configuration file for server settings
   - Support environment variables for sensitive information
   - Implement validation for configuration values

3. **User Experience**:
   - Provide clear help text and documentation
   - Implement progress indicators for long-running operations
   - Format output for readability

4. **Security**:
   - Handle sensitive information securely
   - Validate server responses
   - Implement proper authentication if needed

5. **Testing**:
   - Write unit tests for all components
   - Implement integration tests for end-to-end functionality
   - Use mock servers for testing

## References

1. MCP Python SDK: [https://github.com/modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk)
2. MCP Specification: [https://spec.modelcontextprotocol.io](https://spec.modelcontextprotocol.io)
3. JSON-RPC 2.0 Specification: [https://www.jsonrpc.org/specification](https://www.jsonrpc.org/specification)
4. Typer Documentation: [https://typer.tiangolo.com/](https://typer.tiangolo.com/)
5. Pydantic Documentation: [https://docs.pydantic.dev/](https://docs.pydantic.dev/)
