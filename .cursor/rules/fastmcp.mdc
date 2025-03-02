---
description: Fast Python MCP Server Development
globs: "**/*.py,**/mcp/**"
---
# Fast Python MCP Server Development

This rule provides comprehensive guidance for developing Model Context Protocol (MCP) servers in Python, enabling seamless communication between AI clients and servers.

<rule>
name: fastmcp
description: Expert guidelines for developing Python MCP servers efficiently

filters:
  - type: file_extension
    pattern: "\\.py$"
  - type: path
    pattern: ".*/mcp/.*"

actions:
  - type: suggest
    message: |
      # Python MCP Server Development Guidelines

      ## Overview

      The Model Context Protocol (MCP) is a standardized communication protocol that enables AI clients and servers to exchange
      messages, capabilities, and resources. This guide provides best practices for implementing MCP servers in Python.

      ## Core MCP Concepts

      1. **Protocol Structure**: MCP follows the JSON-RPC 2.0 specification with specific message types:
         - **Requests**: Messages requiring a response (with ID)
         - **Responses**: Replies to requests (matching request ID)
         - **Notifications**: Messages not requiring a response (no ID)

      2. **Lifecycle Phases**:
         - **Initialization**: Capability negotiation and protocol version agreement
         - **Operation**: Normal message exchange
         - **Shutdown**: Graceful connection termination

      3. **Transport Mechanisms**:
         - **stdio**: Communication over standard input/output
         - **HTTP with SSE**: Server-Sent Events for server-to-client communication

      ## Python MCP Server Implementation

      ### Project Structure

      ```
      mcp_server/
      ├── server.py             # Main server implementation
      ├── capabilities/         # Capability implementations
      │   ├── __init__.py
      │   ├── tools.py          # Tool implementations
      │   ├── resources.py      # Resource implementations
      │   └── prompts.py        # Prompt template implementations
      ├── transport/            # Transport implementations
      │   ├── __init__.py
      │   ├── stdio.py          # stdio transport
      │   └── http.py           # HTTP+SSE transport
      ├── handlers/             # Request handlers
      │   ├── __init__.py
      │   └── request_router.py # Routes requests to appropriate handlers
      └── utils/                # Utility functions
          ├── __init__.py
          └── json_rpc.py       # JSON-RPC helpers
      ```

      ### Core Components

      1. **Message Handling**:
         - Implement JSON-RPC message parsing and validation
         - Create a router to dispatch requests to appropriate handlers
         - Manage request IDs and matching responses

      2. **Capability Implementation**:
         - Tools: Callable functions exposed to clients
         - Resources: Data or files accessible to clients
         - Prompts: Template strings for AI interactions

      3. **Transport Layer**:
         - stdio: Read from stdin, write to stdout
         - HTTP+SSE: Implement HTTP server with SSE endpoint

      ## Best Practices

      1. **Clean Architecture**:
         - Separate message handling from business logic
         - Use dependency injection for flexibility
         - Implement proper error handling

      2. **Asynchronous Design**:
         - Use `asyncio` for non-blocking I/O
         - Handle multiple concurrent requests efficiently
         - Implement proper cancellation support

      3. **Testing**:
         - Unit test each component in isolation
         - Integration test the server with mock clients
         - Test error handling and edge cases

      4. **Security Considerations**:
         - Validate all incoming messages
         - Implement proper authentication if needed
         - Sanitize all outputs to prevent injection attacks

      ## Sample Code

      ### Basic MCP Server

      ```python
      import asyncio
      import json
      import sys
      from typing import Dict, Any, Optional, Union

      class MCPServer:
          """Simple MCP server implementation using stdio transport."""

          def __init__(self):
              """Initialize the server with default capabilities."""
              self.capabilities = {
                  "tools": {"listChanged": True},
                  "resources": {"listChanged": True, "subscribe": True},
                  "prompts": {"listChanged": True}
              }
              self.protocol_version = "2024-11-05"

          async def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
              """Handle initialization request from client."""
              client_version = params.get("protocolVersion", "")
              # Check if we support the requested version
              if client_version != self.protocol_version:
                  # Respond with our supported version
                  return {
                      "protocolVersion": self.protocol_version,
                      "serverInfo": {
                          "name": "Python MCP Server",
                          "version": "1.0.0"
                      },
                      "capabilities": self.capabilities
                  }

              # We support the requested version
              return {
                  "protocolVersion": self.protocol_version,
                  "serverInfo": {
                      "name": "Python MCP Server",
                      "version": "1.0.0"
                  },
                  "capabilities": self.capabilities
              }

          async def handle_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
              """Handle an incoming JSON-RPC request."""
              method = request.get("method")
              params = request.get("params", {})
              request_id = request.get("id")

              # Handle initialization request
              if method == "initialize":
                  result = await self.handle_initialize(params)
                  return {
                      "jsonrpc": "2.0",
                      "id": request_id,
                      "result": result
                  }

              # Handle other requests based on method
              # ...

              # Return error for unknown methods
              return {
                  "jsonrpc": "2.0",
                  "id": request_id,
                  "error": {
                      "code": -32601,
                      "message": f"Method not found: {method}"
                  }
              }

          async def handle_notification(self, notification: Dict[str, Any]) -> None:
              """Handle an incoming JSON-RPC notification."""
              method = notification.get("method")
              params = notification.get("params", {})

              # Handle initialized notification
              if method == "initialized":
                  # Server is now ready for operation phase
                  pass

              # Handle other notifications
              # ...

          async def process_message(self, message: str) -> Optional[str]:
              """Process an incoming message and return a response if needed."""
              try:
                  data = json.loads(message)

                  # Check if it's a request (has ID) or notification (no ID)
                  if "id" in data:
                      response = await self.handle_request(data)
                      if response:
                          return json.dumps(response)
                  else:
                      await self.handle_notification(data)
                      return None
              except json.JSONDecodeError:
                  # Invalid JSON
                  return json.dumps({
                      "jsonrpc": "2.0",
                      "id": None,
                      "error": {
                          "code": -32700,
                          "message": "Parse error"
                      }
                  })
              except Exception as e:
                  # Internal error
                  return json.dumps({
                      "jsonrpc": "2.0",
                      "id": None,
                      "error": {
                          "code": -32603,
                          "message": f"Internal error: {str(e)}"
                      }
                  })

          async def run_stdio(self):
              """Run the server using stdio transport."""
              # Set up non-blocking stdin/stdout
              loop = asyncio.get_event_loop()
              reader = asyncio.StreamReader()
              protocol = asyncio.StreamReaderProtocol(reader)
              await loop.connect_read_pipe(lambda: protocol, sys.stdin)

              w_transport, w_protocol = await loop.connect_write_pipe(
                  asyncio.streams.FlowControlMixin, sys.stdout
              )
              writer = asyncio.StreamWriter(w_transport, w_protocol, None, loop)

              while True:
                  # Read a line from stdin
                  try:
                      line = await reader.readline()
                      if not line:
                          break  # EOF

                      # Process the message
                      response = await self.process_message(line.decode('utf-8').strip())
                      if response:
                          # Write response to stdout
                          writer.write((response + '\n').encode('utf-8'))
                          await writer.drain()
                  except Exception as e:
                      # Log error to stderr
                      print(f"Error: {str(e)}", file=sys.stderr)

          def run(self):
              """Start the MCP server."""
              asyncio.run(self.run_stdio())

      if __name__ == "__main__":
          server = MCPServer()
          server.run()
      ```

      ### HTTP+SSE Transport Implementation

      ```python
      import asyncio
      import json
      import uuid
      from typing import Dict, Any, Set
      from aiohttp import web

      class MCPHttpServer:
          """MCP server implementation using HTTP+SSE transport."""

          def __init__(self, host: str = "localhost", port: int = 8000):
              """Initialize the HTTP+SSE server."""
              self.host = host
              self.port = port
              self.app = web.Application()
              self.clients: Dict[str, web.StreamResponse] = {}
              self.setup_routes()

          def setup_routes(self):
              """Set up the HTTP routes."""
              self.app.router.add_get('/sse', self.sse_handler)
              self.app.router.add_post('/rpc', self.rpc_handler)

          async def sse_handler(self, request: web.Request) -> web.StreamResponse:
              """Handle SSE connections from clients."""
              client_id = str(uuid.uuid4())
              response = web.StreamResponse()
              response.headers['Content-Type'] = 'text/event-stream'
              response.headers['Cache-Control'] = 'no-cache'
              response.headers['Connection'] = 'keep-alive'
              await response.prepare(request)

              # Store the client connection
              self.clients[client_id] = response

              # Send the endpoint event
              endpoint_data = {
                  "endpoint": f"/rpc?client={client_id}"
              }
              await response.write(
                  f"event: endpoint\ndata: {json.dumps(endpoint_data)}\n\n".encode('utf-8')
              )

              try:
                  # Keep the connection open
                  while True:
                      await asyncio.sleep(60)  # Heartbeat
                      await response.write(b": heartbeat\n\n")
              except ConnectionResetError:
                  # Client disconnected
                  pass
              finally:
                  # Clean up on disconnect
                  if client_id in self.clients:
                      del self.clients[client_id]

              return response

          async def send_message(self, client_id: str, message: Dict[str, Any]) -> bool:
              """Send a message to a specific client."""
              if client_id not in self.clients:
                  return False

              response = self.clients[client_id]
              try:
                  message_data = json.dumps(message)
                  await response.write(f"event: message\ndata: {message_data}\n\n".encode('utf-8'))
                  return True
              except Exception:
                  # Failed to send, remove client
                  del self.clients[client_id]
                  return False

          async def rpc_handler(self, request: web.Request) -> web.Response:
              """Handle RPC requests from clients."""
              client_id = request.query.get('client')
              if not client_id or client_id not in self.clients:
                  return web.json_response(
                      {
                          "jsonrpc": "2.0",
                          "id": None,
                          "error": {
                              "code": -32000,
                              "message": "Invalid client ID"
                          }
                      },
                      status=400
                  )

              try:
                  # Parse the request
                  data = await request.json()

                  # Process the message (implement your handler here)
                  # This is where you'd integrate with the core MCP server logic

                  # For example, a simple echo response:
                  if "id" in data:
                      return web.json_response({
                          "jsonrpc": "2.0",
                          "id": data["id"],
                          "result": {
                              "echo": data.get("params", {})
                          }
                      })
                  else:
                      # It's a notification, no response needed
                      return web.Response(status=204)  # No content
              except json.JSONDecodeError:
                  return web.json_response({
                      "jsonrpc": "2.0",
                      "id": None,
                      "error": {
                          "code": -32700,
                          "message": "Parse error"
                      }
                  }, status=400)

          def run(self):
              """Start the HTTP+SSE server."""
              web.run_app(self.app, host=self.host, port=self.port)
      ```

      ## FastMCP: Higher-level API

      FastMCP provides a more convenient, decorator-based API for creating MCP servers:

      ### Simple Echo Server

      ```python
      from mcp.server.fastmcp import FastMCP

      # Create server
      mcp = FastMCP("Echo Server")

      @mcp.tool()
      def echo(text: str) -> str:
          """Echo the input text"""
          return text
      ```

      ### Complex Input Validation with Pydantic

      ```python
      from typing import Annotated, List
      from pydantic import BaseModel, Field
      from mcp.server.fastmcp import FastMCP

      mcp = FastMCP("Validation Example")

      # Define complex models with validation
      class User(BaseModel):
          name: str
          email: Annotated[str, Field(pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")]
          age: Annotated[int, Field(ge=0, lt=150)]

      class TeamRequest(BaseModel):
          team_name: Annotated[str, Field(min_length=3, max_length=50)]
          members: Annotated[List[User], Field(min_length=1)]

      @mcp.tool()
      def create_team(request: TeamRequest) -> dict:
          """Create a team with the given members"""
          return {
              "team_id": "team_123",
              "team_name": request.team_name,
              "member_count": len(request.members),
              "members": [user.name for user in request.members]
          }
      ```

      ### Parameter Descriptions with Field

      ```python
      from pydantic import Field
      from mcp.server.fastmcp import FastMCP

      mcp = FastMCP("Parameter Descriptions Server")

      @mcp.tool()
      def greet_user(
          name: str = Field(description="The name of the person to greet"),
          title: str = Field(description="Optional title like Mr/Ms/Dr", default=""),
          times: int = Field(description="Number of times to repeat the greeting", default=1),
      ) -> str:
          """Greet a user with optional title and repetition"""
          greeting = f"Hello {title + ' ' if title else ''}{name}!"
          return "\n".join([greeting] * times)
      ```

      ### Dynamic Resources with Path Templates

      ```python
      from mcp.server.fastmcp import FastMCP

      mcp = FastMCP("Demo")

      # Dynamic resource with path variable
      @mcp.resource("greeting://{name}")
      def get_greeting(name: str) -> str:
          """Get a personalized greeting"""
          return f"Hello, {name}!"
      ```

      ### Unicode Support

      ```python
      from mcp.server.fastmcp import FastMCP

      mcp = FastMCP()

      @mcp.tool(
          description="🌟 A tool that uses various Unicode characters in its description: "
          "á é í ó ú ñ 漢字 🎉"
      )
      def hello_unicode(name: str = "世界", greeting: str = "¡Hola") -> str:
          """
          A simple tool that demonstrates Unicode handling in:
          - Tool description (emojis, accents, CJK characters)
          - Parameter defaults (CJK characters)
          - Return values (Spanish punctuation, emojis)
          """
          return f"{greeting}, {name}! 👋"
      ```

      ### Return Types Beyond Primitives

      ```python
      import io
      from mcp.server.fastmcp import FastMCP
      from mcp.server.fastmcp.utilities.types import Image

      mcp = FastMCP("Screenshot Demo", dependencies=["pyautogui", "Pillow"])

      @mcp.tool()
      def take_screenshot() -> Image:
          """
          Take a screenshot of the user's screen and return it as an image.
          """
          import pyautogui

          buffer = io.BytesIO()
          screenshot = pyautogui.screenshot()
          screenshot.convert("RGB").save(buffer, format="JPEG", quality=60, optimize=True)
          return Image(data=buffer.getvalue(), format="jpeg")
      ```

      ### Desktop Files Listing

      This example demonstrates how to expose the user's desktop directory as a resource, providing a practical file system integration with FastMCP:

      ```python
      """
      FastMCP Desktop Example

      A simple example that exposes the desktop directory as a resource.
      """

      from pathlib import Path

      from mcp.server.fastmcp import FastMCP

      # Create server
      mcp = FastMCP("Demo")


      @mcp.resource("dir://desktop")
      def desktop() -> list[str]:
          """List the files in the user's desktop"""
          desktop = Path.home() / "Desktop"
          return [str(f) for f in desktop.iterdir()]


      @mcp.tool()
      def add(a: int, b: int) -> int:
          """Add two numbers"""
          return a + b
      ```

      Key aspects of this example:

      1. **Directory Resource**: Demonstrates exposing a filesystem directory as a resource with a custom protocol `dir://`.
      2. **Path Handling**: Uses `pathlib.Path` for cross-platform path management.
      3. **Resource Protocol**: Shows how to define custom resource protocols (like `dir://`).
      4. **Simple Tool**: Includes a basic tool for demonstration purposes alongside the resource.

      This pattern can be extended to expose other directories or file system structures as resources, making it useful for file browsers, document managers, or any application that needs access to the local file system.

      ## Advanced Examples

      ### Complex Input Validation with Pydantic

      ```python
      from typing import Annotated, List
      from pydantic import BaseModel, Field
      from mcp.server.fastmcp import FastMCP

      # Create the server
      mcp = FastMCP("Validation Example")

      # Define complex models with validation
      class User(BaseModel):
          name: str
          email: Annotated[str, Field(pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")]
          age: Annotated[int, Field(ge=0, lt=150)]

      class TeamRequest(BaseModel):
          team_name: Annotated[str, Field(min_length=3, max_length=50)]
          members: Annotated[List[User], Field(min_length=1)]

      @mcp.tool()
      def create_team(request: TeamRequest) -> dict:
          """Create a team with the given members"""
          return {
              "team_id": "team_123",
              "team_name": request.team_name,
              "member_count": len(request.members),
              "members": [user.name for user in request.members]
          }
      ```

      ### Unicode Support for International Characters

      ```python
      from mcp.server.fastmcp import FastMCP

      mcp = FastMCP("Unicode Support Demo")

      @mcp.tool(
          description="🌍 International greeting tool supporting multiple languages"
      )
      def multilingual_greeting(
          name: str,
          language: str = "english"
      ) -> str:
          """
          Generate a greeting in different languages.

          Supported languages:
          - english: "Hello"
          - spanish: "¡Hola!"
          - french: "Bonjour"
          - japanese: "こんにちは"
          - arabic: "مرحبا"
          """
          greetings = {
              "english": f"Hello, {name}!",
              "spanish": f"¡Hola, {name}!",
              "french": f"Bonjour, {name}!",
              "japanese": f"こんにちは, {name}さん!",
              "arabic": f"مرحبا {name}!"
          }

          return greetings.get(language.lower(), f"Hello, {name}!")
      ```

      ### Recursive Memory System with Vector Database

      This advanced example demonstrates how to create a FastMCP server that implements a recursive memory system with vector embeddings, database integration, and asynchronous operations.

      ```python
      """
      Recursive memory system inspired by the human brain's clustering of memories.
      Uses OpenAI's embeddings and pgvector for efficient similarity search.
      """

      import asyncio
      import math
      import os
      from dataclasses import dataclass
      from datetime import datetime, timezone
      from pathlib import Path
      from typing import Annotated, Self, list

      import asyncpg
      import numpy as np
      from openai import AsyncOpenAI
      from pgvector.asyncpg import register_vector
      from pydantic import BaseModel, Field
      from pydantic_ai import Agent

      from mcp.server.fastmcp import FastMCP

      # Configuration constants
      MAX_DEPTH = 5
      SIMILARITY_THRESHOLD = 0.7
      DECAY_FACTOR = 0.99
      REINFORCEMENT_FACTOR = 1.1

      DEFAULT_LLM_MODEL = "openai:gpt-4o"
      DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"

      # Initialize the MCP server with required dependencies
      mcp = FastMCP(
          "Memory System",
          dependencies=[
              "pydantic-ai-slim[openai]",
              "asyncpg",
              "numpy",
              "pgvector",
          ],
      )

      # Database connection string
      DB_DSN = "postgresql://postgres:postgres@localhost:54320/memory_db"

      # User profile directory for persistent storage
      PROFILE_DIR = (
          Path.home() / ".fastmcp" / os.environ.get("USER", "anon") / "memory"
      ).resolve()
      PROFILE_DIR.mkdir(parents=True, exist_ok=True)


      def cosine_similarity(a: list[float], b: list[float]) -> float:
          """Calculate cosine similarity between two vectors."""
          a_array = np.array(a, dtype=np.float64)
          b_array = np.array(b, dtype=np.float64)
          return np.dot(a_array, b_array) / (
              np.linalg.norm(a_array) * np.linalg.norm(b_array)
          )


      @dataclass
      class Deps:
          """Dependencies container for easier passing of shared resources."""
          openai: AsyncOpenAI
          pool: asyncpg.Pool


      class MemoryNode(BaseModel):
          """Model representing a memory node in the system."""
          id: int | None = None
          content: str
          summary: str = ""
          importance: float = 1.0
          access_count: int = 0
          timestamp: float = Field(
              default_factory=lambda: datetime.now(timezone.utc).timestamp()
          )
          embedding: list[float]

          @classmethod
          async def from_content(cls, content: str, deps: Deps):
              """Create a memory node from text content by generating its embedding."""
              embedding = await get_embedding(content, deps)
              return cls(content=content, embedding=embedding)

          async def save(self, deps: Deps):
              """Save the memory node to the database."""
              async with deps.pool.acquire() as conn:
                  if self.id is None:
                      result = await conn.fetchrow(
                          """
                          INSERT INTO memories (content, summary, importance, access_count,
                              timestamp, embedding)
                          VALUES ($1, $2, $3, $4, $5, $6)
                          RETURNING id
                          """,
                          self.content,
                          self.summary,
                          self.importance,
                          self.access_count,
                          self.timestamp,
                          self.embedding,
                      )
                      self.id = result["id"]
                  else:
                      await conn.execute(
                          """
                          UPDATE memories
                          SET content = $1, summary = $2, importance = $3,
                              access_count = $4, timestamp = $5, embedding = $6
                          WHERE id = $7
                          """,
                          self.content,
                          self.summary,
                          self.importance,
                          self.access_count,
                          self.timestamp,
                          self.embedding,
                          self.id,
                      )


      async def get_embedding(text: str, deps: Deps) -> list[float]:
          """Get vector embedding for text using OpenAI's embedding model."""
          embedding_response = await deps.openai.embeddings.create(
              input=text,
              model=DEFAULT_EMBEDDING_MODEL,
          )
          return embedding_response.data[0].embedding


      async def get_db_pool() -> asyncpg.Pool:
          """Create and initialize a database connection pool."""
          async def init(conn):
              await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
              await register_vector(conn)

          pool = await asyncpg.create_pool(DB_DSN, init=init)
          return pool


      async def find_similar_memories(embedding: list[float], deps: Deps) -> list[MemoryNode]:
          """Find memories similar to the given embedding vector."""
          async with deps.pool.acquire() as conn:
              rows = await conn.fetch(
                  """
                  SELECT id, content, summary, importance, access_count, timestamp, embedding
                  FROM memories
                  ORDER BY embedding <-> $1
                  LIMIT 5
                  """,
                  embedding,
              )
          memories = [
              MemoryNode(
                  id=row["id"],
                  content=row["content"],
                  summary=row["summary"],
                  importance=row["importance"],
                  access_count=row["access_count"],
                  timestamp=row["timestamp"],
                  embedding=row["embedding"],
              )
              for row in rows
          ]
          return memories


      # Expose memory functions as MCP tools
      @mcp.tool()
      async def remember(
          contents: list[str] = Field(description="List of observations or memories to store")
      ) -> str:
          """
          Store multiple memory items in the database.

          This function processes each memory, computes its embedding, finds similar
          existing memories to merge with, and performs importance updates.
          """
          deps = Deps(openai=AsyncOpenAI(), pool=await get_db_pool())
          try:
              async def add_memory(content: str) -> str:
                  """Add a single memory item to the database."""
                  new_memory = await MemoryNode.from_content(content, deps)
                  await new_memory.save(deps)
                  return f"Remembered: {content}"

              return "\n".join(
                  await asyncio.gather(*[add_memory(content) for content in contents])
              )
          finally:
              await deps.pool.close()


      @mcp.tool()
      async def read_memories() -> str:
          """
          Read all memories sorted by importance.

          Returns a formatted string with all memories and their importance scores.
          """
          deps = Deps(openai=AsyncOpenAI(), pool=await get_db_pool())
          try:
              async with deps.pool.acquire() as conn:
                  rows = await conn.fetch(
                      """
                      SELECT content, summary, importance, access_count
                      FROM memories
                      ORDER BY importance DESC
                      LIMIT $1
                      """,
                      MAX_DEPTH,
                  )

              result = []
              for row in rows:
                  effective_importance = row["importance"] * (
                      1 + math.log(row["access_count"] + 1)
                  )
                  summary = row["summary"] or row["content"]
                  result.append(
                      f"- {summary} (Importance: {effective_importance:.2f})"
                  )

              return "\n".join(result) if result else "No memories found."
          finally:
              await deps.pool.close()


      async def initialize_database():
          """Initialize the database schema for the memory system."""
          # Create database if it doesn't exist
          pool = await asyncpg.create_pool(
              "postgresql://postgres:postgres@localhost:54320/postgres"
          )
          try:
              async with pool.acquire() as conn:
                  await conn.execute("CREATE DATABASE IF NOT EXISTS memory_db;")
          finally:
              await pool.close()

          # Initialize database schema
          pool = await get_db_pool()
          try:
              async with pool.acquire() as conn:
                  await conn.execute("""
                      CREATE TABLE IF NOT EXISTS memories (
                          id SERIAL PRIMARY KEY,
                          content TEXT NOT NULL,
                          summary TEXT,
                          importance REAL NOT NULL,
                          access_count INT NOT NULL,
                          timestamp DOUBLE PRECISION NOT NULL,
                          embedding vector(1536) NOT NULL
                      );
                      CREATE INDEX IF NOT EXISTS idx_memories_embedding ON memories
                          USING hnsw (embedding vector_l2_ops);
                  """)
          finally:
              await pool.close()


      if __name__ == "__main__":
          # Initialize the database when the script is run directly
          asyncio.run(initialize_database())
          # Start the MCP server
          mcp.run()
      ```

      Key aspects of this example:

      1. **Database Integration**: Uses PostgreSQL with pgvector extension for vector similarity search
      2. **Embeddings**: Leverages OpenAI's text embedding model to convert memories to vector representations
      3. **Asynchronous Operations**: Implements async/await pattern for efficient database and API operations
      4. **Complex Pydantic Models**: Uses advanced Pydantic features for data validation and representation
      5. **Resource Management**: Demonstrates proper connection pooling and resource cleanup
      6. **Tool Annotations**: Provides detailed Field descriptions for better client experiences

      ## Implementation Checklist

      - [ ] Basic server structure with request/notification handling
      - [ ] Protocol version negotiation
      - [ ] Capability declaration and negotiation
      - [ ] Transport layer implementation (stdio and/or HTTP+SSE)
      - [ ] Tool implementation
      - [ ] Resource implementation
      - [ ] Prompt template implementation
      - [ ] Proper error handling and logging
      - [ ] Unit and integration tests
      - [ ] Documentation

      ## References

      - [MCP Specification](https://github.com/microsoft/mcp)
      - [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)

examples:
  - input: |
      # Example of implementing an MCP server in Python
      import asyncio
      import json
      import sys

      # Need to implement a basic MCP server
    output: |
      Here's how to implement a basic MCP server in Python following best practices:

      ```python
      import asyncio
      import json
      import sys
      from typing import Dict, Any, Optional

      class MCPServer:
          """Simple MCP server implementation using stdio transport."""

          def __init__(self):
              """Initialize the server with default capabilities."""
              self.capabilities = {
                  "tools": {"listChanged": True}
              }
              self.protocol_version = "2024-11-05"

          async def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
              """Handle initialization request from client."""
              client_version = params.get("protocolVersion", "")
              return {
                  "protocolVersion": self.protocol_version,
                  "serverInfo": {
                      "name": "Python MCP Server",
                      "version": "1.0.0"
                  },
                  "capabilities": self.capabilities
              }

          async def process_message(self, message: str) -> Optional[str]:
              """Process an incoming message and return a response if needed."""
              try:
                  data = json.loads(message)
                  # Handle request based on method
                  # ...
              except Exception as e:
                  # Handle errors
                  # ...

          async def run_stdio(self):
              """Run the server using stdio transport."""
              # Implement stdio communication
              # ...

          def run(self):
              """Start the MCP server."""
              asyncio.run(self.run_stdio())

      if __name__ == "__main__":
          server = MCPServer()
          server.run()
      ```

  - input: |
      # Need to add tool support to my MCP server
      class MCPServer:
          def __init__(self):
              self.capabilities = {}

          # How do I implement tools?
    output: |
      Here's how to implement tool support in your MCP server:

      ```python
      from typing import Dict, Any, Callable, List

      class Tool:
          """Represents a callable tool in MCP."""

          def __init__(self, name: str, description: str, handler: Callable):
              self.name = name
              self.description = description
              self.handler = handler
              self.schema = {
                  "type": "object",
                  "properties": {},
                  "required": []
              }

          def add_parameter(self, name: str, param_type: str, description: str, required: bool = False):
              """Add a parameter to the tool schema."""
              self.schema["properties"][name] = {
                  "type": param_type,
                  "description": description
              }
              if required:
                  self.schema["required"].append(name)

          async def call(self, params: Dict[str, Any]) -> Any:
              """Call the tool with the given parameters."""
              return await self.handler(params)

      class MCPServer:
          def __init__(self):
              """Initialize the server with tools capability."""
              self.tools: Dict[str, Tool] = {}
              self.capabilities = {
                  "tools": {"listChanged": True}
              }

          def register_tool(self, tool: Tool):
              """Register a tool with the server."""
              self.tools[tool.name] = tool

          async def handle_list_tools(self) -> Dict[str, Any]:
              """Handle listTools request."""
              return {
                  "tools": [
                      {
                          "name": name,
                          "description": tool.description,
                          "schema": tool.schema
                      }
                      for name, tool in self.tools.items()
                  ]
              }

          async def handle_call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
              """Handle callTool request."""
              tool_name = params.get("name")
              tool_params = params.get("params", {})

              if tool_name not in self.tools:
                  raise Exception(f"Tool not found: {tool_name}")

              result = await self.tools[tool_name].call(tool_params)
              return {"result": result}
      ```

  - input: |
      # Need to implement a FastMCP server with complex input validation
      from mcp.server.fastmcp import FastMCP

      # How do I use Pydantic models for parameter validation?
    output: |
      Here's how to implement complex input validation using Pydantic models with FastMCP:

      ```python
      from typing import Annotated, List
      from pydantic import BaseModel, Field
      from mcp.server.fastmcp import FastMCP

      # Create the server
      mcp = FastMCP("Validation Example")

      # Define complex models with validation
      class User(BaseModel):
          name: str
          email: Annotated[str, Field(pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")]
          age: Annotated[int, Field(ge=0, lt=150)]

      class TeamRequest(BaseModel):
          team_name: Annotated[str, Field(min_length=3, max_length=50)]
          members: Annotated[List[User], Field(min_length=1)]

      @mcp.tool()
      def create_team(request: TeamRequest) -> dict:
          """Create a team with the given members"""
          return {
              "team_id": "team_123",
              "team_name": request.team_name,
              "member_count": len(request.members),
              "members": [user.name for user in request.members]
          }
      ```

  - input: |
      # How do I handle Unicode in MCP tools?
      from mcp.server.fastmcp import FastMCP

      # Need to support international characters
    output: |
      Here's how to handle Unicode properly in your MCP tools:

      ```python
      from mcp.server.fastmcp import FastMCP

      mcp = FastMCP("Unicode Support Demo")

      @mcp.tool(
          description="🌟 A tool that uses various Unicode characters in its description: "
          "á é í ó ú ñ 漢字 🎉"
      )
      def hello_unicode(name: str = "世界", greeting: str = "¡Hola") -> str:
          """
          A simple tool that demonstrates Unicode handling in:
          - Tool description (emojis, accents, CJK characters)
          - Parameter defaults (CJK characters)
          - Return values (Spanish punctuation, emojis)
          """
          return f"{greeting}, {name}! 👋"
      ```

metadata:
  priority: high
  version: 1.0
  author: "AI Assistant"
  created: "2024-07-16"
</rule>

## References and Resources

- [MCP GitHub Repository](https://github.com/microsoft/mcp) - Official specification
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification) - Base protocol
- [Python asyncio Documentation](https://docs.python.org/3/library/asyncio.html) - Asynchronous I/O for Python
