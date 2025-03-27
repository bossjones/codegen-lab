---
description:
globs:
alwaysApply: false
---

# MCP Client Expert

 Expert guidance for building and working with MCP clients

This rule provides guidance for building and working with Model Context Protocol (MCP) clients.

<rule>
name: mcp-client-expert
description: Expert guidance for building and working with MCP clients
filters:
  - type: message
    pattern: "(?i)(mcp client|model context protocol|client implementation|mcp transport|mcp session|mcp tools|mcp resources)"
  - type: context
    pattern: "client session|transport mechanism|protocol types|cli interface|mcp client"

actions:
  - type: suggest
    message: |
      # MCP Client Development Guide

      I'll help you build a robust MCP client. The Model Context Protocol (MCP) is a standardized JSON-RPC 2.0 based protocol for LLM clients and servers.

      ## Core Architecture

      An MCP client consists of these key components:

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

      ## Implementation Approach

      1. **Client Session**: Implement `ClientSession` to manage server connections
      2. **Transport Layer**: Use `stdio_client` or `sse_client` for communication
      3. **Protocol Types**: Leverage the MCP types for structured messages
      4. **CLI Interface**: Build a user-friendly command interface

      ## Key Components to Implement

      ### 1. Client Session
      ```python
      class MCPClient:
          def __init__(self, server_config: Dict):
              self.server_config = server_config
              self.session = None

          async def connect(self):
              # Initialize connection to server

          async def list_tools(self):
              # List available tools

          async def call_tool(self, name, arguments):
              # Call a tool on the server

          async def disconnect(self):
              # Clean up connection
      ```

      ### 2. Transport Mechanisms
      ```python
      # stdio transport
      server_params = StdioServerParameters(
          command="python",
          args=["server.py"],
          env={"API_KEY": "your-api-key"}
      )

      async with stdio_client(server_params) as (read, write):
          # Use read and write streams

      # SSE transport
      async with sse_client("https://example.com/mcp") as (read, write):
          # Use read and write streams
      ```

      ### 3. CLI Interface
      ```python
      app = typer.Typer(
          name="mcp-client",
          help="MCP CLI client",
          add_completion=False,
      )

      @app.command()
      def list_tools(server: str, config_file: Path):
          """List tools available on the server."""
          # Implementation

      @app.command()
      def call_tool(server: str, tool: str, arguments: str):
          """Call a tool on the server."""
          # Implementation
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

      ## Advanced Features

      - **Server Discovery**: Auto-detect available MCP servers
      - **Tool Execution**: Handle tool calls with proper error handling
      - **Resource Management**: Read and subscribe to server resources
      - **Prompt Handling**: Retrieve and use server-defined prompts

examples:
  - input: |
      I need to build an MCP client that can connect to a server and list available tools.
    output: |
      To build an MCP client that connects to a server and lists available tools, you'll need to implement these key components:

      1. First, set up the client session and transport layer:

      ```python
      import asyncio
      import json
      from pathlib import Path
      from typing import Dict, List, Optional

      from mcp import ClientSession, StdioServerParameters
      from mcp.client.stdio import stdio_client
      import mcp.types as types

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

          async def disconnect(self):
              if hasattr(self, 'stdio_transport'):
                  read, write = self.stdio_transport
                  await write.aclose()
              self.session = None
      ```

      2. Then, create a simple function to run the client:

      ```python
      async def list_server_tools(server_config):
          client = MCPClient(server_config)
          try:
              await client.connect()
              tools = await client.list_tools()

              print("Available tools:")
              for tool in tools:
                  print(f"- {tool.name}: {tool.description or ''}")

          finally:
              await client.disconnect()

      # Example usage
      server_config = {
          "command": "python",
          "args": ["path/to/server.py"],
          "env": {"API_KEY": "your-api-key"}
      }

      asyncio.run(list_server_tools(server_config))
      ```

      This implementation:
      - Creates a client session that connects to the MCP server
      - Initializes the connection using the stdio transport
      - Lists available tools from the server
      - Properly handles connection cleanup

      For a more robust implementation, you should add:
      - Error handling for connection failures
      - Configuration loading from a file
      - A proper CLI interface using a library like Typer
      - Formatted output using Rich or a similar library

  - input: |
      How do I implement tool execution in my MCP client?
    output: |
      To implement tool execution in your MCP client, you'll need to:

      1. Add a method to call tools with proper error handling:

      ```python
      async def call_tool(self, name: str, arguments: Dict[str, Any]) -> types.CallToolResult:
          """Call a tool on the server with retry logic."""
          if not self.session:
              raise RuntimeError("Not connected to server")

          # Implement retry logic for resilience
          retries = 2
          for attempt in range(retries + 1):
              try:
                  result = await self.session.call_tool(name, arguments)
                  return result
              except Exception as e:
                  if attempt < retries:
                      # Exponential backoff
                      await asyncio.sleep(1.0 * (attempt + 1))
                  else:
                      raise RuntimeError(f"Failed to call tool {name}: {str(e)}")
      ```

      2. Add a helper method to process tool results:

      ```python
      def process_tool_result(self, result: types.CallToolResult) -> Any:
          """Process and format tool execution results."""
          # Check for errors
          if result.isError:
              raise RuntimeError(f"Tool execution failed: {result.content}")

          # Process different content types
          processed_content = []
          for content in result.content:
              if content.type == "text":
                  processed_content.append(content.text)
              elif content.type == "image":
                  # Handle image content
                  processed_content.append("[Image content]")
              elif content.type == "resource":
                  # Handle resource content
                  processed_content.append(f"Resource: {content.resource.uri}")

          return processed_content
      ```

      3. Create a CLI command to execute tools:

      ```python
      @app.command()
      def execute_tool(
          server: str,
          tool_name: str,
          arguments: str = typer.Argument("{}", help="JSON arguments"),
          config_file: Path = typer.Option(
              Path.home() / ".mcp" / "config.json",
              help="Path to config file",
          )
      ):
          """Execute a tool on the MCP server."""
          # Load configuration
          config = load_config(config_file)

          if server not in config.servers:
              console.print(f"[red]Server not found: {server}[/red]")
              sys.exit(1)

          # Parse arguments
          try:
              args = json.loads(arguments)
          except json.JSONDecodeError:
              console.print("[red]Invalid JSON arguments[/red]")
              sys.exit(1)

          async def run():
              client = MCPClient(config.servers[server])
              try:
                  # Connect to server
                  await client.connect()

                  # Call the tool
                  with console.status(f"Executing tool '{tool_name}'..."):
                      result = await client.call_tool(tool_name, args)

                  # Process and display results
                  processed_results = client.process_tool_result(result)

                  console.print("\n[bold green]Results:[/bold green]")
                  for item in processed_results:
                      console.print(item)

              except Exception as e:
                  console.print(f"[red]Error: {str(e)}[/red]")
                  sys.exit(1)
              finally:
                  await client.disconnect()

          asyncio.run(run())
      ```

      This implementation provides:
      - Robust error handling with retries
      - Support for different content types in results
      - A user-friendly CLI interface
      - Progress indication during execution
      - Formatted output of results

      For production use, consider adding:
      - Timeout handling for long-running tools
      - Streaming results for tools that produce partial outputs
      - Validation of tool arguments against the tool's input schema
      - Caching of frequently used tool results

metadata:
  priority: high
  version: 1.0
  tags:
    - mcp
    - client
    - development
    - protocol
</rule>

## MCP Client Development Guide

The Model Context Protocol (MCP) is a standardized JSON-RPC 2.0 based communication protocol for interaction between LLM clients and servers. This guide provides comprehensive information on building robust MCP clients.

### Core Components

1. **Client Session**: The central component that manages connections to MCP servers
2. **Transport Layer**: Provides communication channels between client and server
3. **Protocol Types**: Defines the structure of messages exchanged
4. **CLI Interface**: Provides user interaction through command-line arguments

### Implementation Steps

1. **Set up the project structure**:
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

2. **Implement the client session**:
   - Create a class to manage server connections
   - Implement methods for initialization, tool listing, tool execution, etc.
   - Handle connection lifecycle properly

3. **Use appropriate transport mechanisms**:
   - stdio: For local server processes
   - SSE: For remote server connections

4. **Build a user-friendly CLI interface**:
   - Use a framework like Typer for command parsing
   - Implement commands for common operations
   - Provide clear help text and error messages

### Best Practices

1. **Error handling**: Implement proper error handling with clear messages
2. **Configuration management**: Use configuration files and environment variables
3. **User experience**: Provide progress indicators and formatted output
4. **Security**: Handle sensitive information securely
5. **Testing**: Write comprehensive tests for all components

### Advanced Features

- **Server discovery**: Auto-detect available MCP servers
- **Tool execution**: Handle tool calls with proper error handling
- **Resource management**: Read and subscribe to server resources
- **Prompt handling**: Retrieve and use server-defined prompts

### References

1. MCP Python SDK: [https://github.com/modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk)
2. MCP Specification: [https://spec.modelcontextprotocol.io](https://spec.modelcontextprotocol.io)
3. JSON-RPC 2.0 Specification: [https://www.jsonrpc.org/specification](https://www.jsonrpc.org/specification)
