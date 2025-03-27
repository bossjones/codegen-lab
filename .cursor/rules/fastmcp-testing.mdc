---
description: This rule provides expert guidance for writing and debugging FastMCP tool tests using pytest.
globs: *_test.py
alwaysApply: false
---

# FastMCP Tool Testing Guide

This rule provides expert guidance for writing and debugging FastMCP tool tests using pytest.

<rule>
name: fastmcp-tool-testing
description: Expert guidance for writing FastMCP tool tests using pytest
filters:
  - type: file_extension
    pattern: "\\_test\\.py$"
  - type: content
    pattern: "(from mcp\\.server\\.fastmcp\\.testing import|import mcp\\.server\\.fastmcp\\.testing)"

actions:
  - type: suggest
    message: |
      # FastMCP Tool Testing Guide

      ## Core Concepts

      Testing FastMCP tools involves using `pytest` and the `mcp.server.fastmcp.testing` utilities. Key principles include:

      1.  **Mocking the MCP Server**: Use `client_session` to create a test client that interacts with your tool without a real MCP server.
      2.  **Testing Tool Logic**: Focus on testing the core logic of your tools, including input validation, functionality, and output.
      3.  **Testing Context Interactions**: Verify how your tools use the `Context` object for logging, progress reporting, etc.
      4.  **Testing Error Handling**: Ensure your tests cover both successful tool executions and expected error conditions.
      5.  **Async Testing**: Use `pytest.mark.anyio` for testing asynchronous tools.
      6.  **Debugging in a Feedback Loop**: Leverage pytest's features for efficient debugging, such as `-x` (stop on first failure), `--pdb` (drop into debugger on failure), and `--capture=no` (show stdout/stderr).

      ## Testing Tools

      Use the `client_session` helper to test tools:

      ```python
      import pytest
      from mcp.server.fastmcp import FastMCP
      from mcp.server.fastmcp.testing import client_session

      @pytest.mark.anyio
      async def test_my_tool():
          server = FastMCP()

          @server.tool()
          def my_tool(param: str) -> str:
              return f"Processed {param}"

          async with client_session(server._mcp_server) as client:
              result = await client.call_tool("my_tool", {"param": "test"})
              assert len(result.content) == 1
              assert result.content[0].text == "Processed test"
      ```

      ### Comprehensive Testing Guide

      Testing is crucial for ensuring your FastMCP tools work correctly. Here's a comprehensive guide to testing different types of tools:

      #### Testing Synchronous Tools

      ```python
      import pytest
      from mcp.server.fastmcp import FastMCP
      from mcp.server.fastmcp.testing import client_session
      from typing import Dict, Any

      @pytest.mark.anyio
      async def test_sync_tool_with_validation():
          """Test a synchronous tool with input validation."""
          server = FastMCP()

          @server.tool()
          def validate_user(name: str, age: int) -> Dict[str, Any]:
              """Validate user data."""
              if len(name) < 2:
                  raise ValueError("Name must be at least 2 characters")
              if age < 0 or age > 120:
                  raise ValueError("Age must be between 0 and 120")
              return {"status": "valid", "name": name, "age": age}

          async with client_session(server._mcp_server) as client:
              # Test valid input
              result = await client.call_tool("validate_user", {"name": "Alice", "age": 30})
              assert not result.isError
              assert "valid" in result.content[0].text

              # Test invalid input - name too short
              result = await client.call_tool("validate_user", {"name": "A", "age": 30})
              assert result.isError
              assert "Name must be at least 2 characters" in result.content[0].text

              # Test invalid input - age out of range
              result = await client.call_tool("validate_user", {"name": "Bob", "age": 150})
              assert result.isError
              assert "Age must be between 0 and 120" in result.content[0].text
      ```

      #### Testing Asynchronous Tools

      ```python
      import pytest
      import asyncio
      from mcp.server.fastmcp import FastMCP
      from mcp.server.fastmcp.testing import client_session

      @pytest.mark.anyio
      async def test_async_tool():
          """Test an asynchronous tool with delay."""
          server = FastMCP()

          @server.tool()
          async def delayed_response(delay_seconds: float, message: str) -> str:
              """Return a message after a delay."""
              await asyncio.sleep(delay_seconds)
              return f"Delayed {delay_seconds}s: {message}"

          async with client_session(server._mcp_server) as client:
              # Test with short delay
              result = await client.call_tool(
                  "delayed_response",
                  {"delay_seconds": 0.1, "message": "Hello"}
              )
              assert not result.isError
              assert "Delayed 0.1s: Hello" in result.content[0].text

              # Test with timeout
              with pytest.raises(asyncio.TimeoutError):
                  # Set a short timeout to test timeout handling
                  await asyncio.wait_for(
                      client.call_tool(
                          "delayed_response",
                          {"delay_seconds": 1.0, "message": "Timeout"}
                      ),
                      timeout=0.5
                  )
      ```

      #### Testing Tools with Context

      ```python
      import pytest
      from mcp.server.fastmcp import FastMCP, Context
      from mcp.server.fastmcp.testing import client_session
      from typing import List, Tuple, Any

      @pytest.mark.anyio
      async def test_tool_with_context():
          """Test a tool that uses the Context object."""
          server = FastMCP()

          @server.tool()
          async def logging_tool(message: str, level: str, ctx: Context) -> str:
              """Log a message with the specified level."""
              if level == "debug":
                  await ctx.debug(message)
              elif level == "info":
                  await ctx.info(message)
              elif level == "warning":
                  await ctx.warning(message)
              elif level == "error":
                  await ctx.error(message)
              else:
                  raise ValueError(f"Unknown log level: {level}")
              return f"Logged: {message} at {level} level"

          # Capture log messages
          log_messages: List[Tuple[str, str, Any]] =

          async with client_session(server._mcp_server) as client:
              # Set up logging callback
              async def log_callback(level: str, message: str, logger: str = None) -> None:
                  log_messages.append((level, message, logger))

              # Register callback
              client.session.on_log_message = log_callback

              # Test different log levels
              levels = ["debug", "info", "warning", "error"]
              for level in levels:
                  message = f"Test {level} message"
                  result = await client.call_tool(
                      "logging_tool",
                      {"message": message, "level": level}
                  )
                  assert not result.isError
                  assert f"Logged: {message} at {level} level" in result.content[0].text

              # Verify log messages were captured
              assert len(log_messages) == len(levels)
              for i, level in enumerate(levels):
                  assert log_messages[i][0] == level
                  assert f"Test {level} message" in log_messages[i][1]
      ```

      #### Testing Progress Reporting

      ```python
      import pytest
      import asyncio
      from mcp.server.fastmcp import FastMCP, Context
      from mcp.server.fastmcp.testing import client_session
      from typing import List, Tuple, Optional

      @pytest.mark.anyio
      async def test_progress_reporting():
          """Test a tool that reports progress."""
          server = FastMCP()

          @server.tool()
          async def process_with_progress(steps: int, ctx: Context) -> str:
              """Process a task with progress reporting."""
              for i in range(steps):
                  # Report progress
                  await ctx.report_progress(i, steps)
                  # Do some work
                  await asyncio.sleep(0.01)
              # Final progress
              await ctx.report_progress(steps, steps)
              return f"Completed {steps} steps"

          # Capture progress updates
          progress_updates: List[Tuple[int, Optional[int]]] =

          async with client_session(server._mcp_server) as client:
              # Set up progress callback
              async def progress_callback(progress: int, total: Optional[int] = None) -> None:
                  progress_updates.append((progress, total))

              # Register callback
              client.session.on_progress = progress_callback

              # Test with 5 steps
              result = await client.call_tool("process_with_progress", {"steps": 5})
              assert not result.isError
              assert "Completed 5 steps" in result.content[0].text

              # Verify progress updates
              assert len(progress_updates) == 6  # 0 through 4, plus final update
              assert progress_updates[0] == (0, 5)
              assert progress_updates[-1] == (5, 5)
      ```

      #### Testing Error Handling

      ```python
      import pytest
      from mcp.server.fastmcp import FastMCP
      from mcp.server.fastmcp.testing import client_session

      @pytest.mark.anyio
      async def test_error_handling():
          """Test a tool with error handling."""
          server = FastMCP()

          @server.tool()
          def division_tool(numerator: float, denominator: float) -> float:
              """Divide two numbers with error handling."""
              try:
                  if denominator == 0:
                      raise ZeroDivisionError("Cannot divide by zero")
                  return numerator / denominator
              except Exception as e:
                  # Re-raise with clear message
                  raise ValueError(f"Division error: {str(e)}")

          async with client_session(server._mcp_server) as client:
              # Test valid division
              result = await client.call_tool(
                  "division_tool",
                  {"numerator": 10.0, "denominator": 2.0}
              )
              assert not result.isError
              assert "5.0" in result.content[0].text

              # Test division by zero
              result = await client.call_tool(
                  "division_tool",
                  {"numerator": 10.0, "denominator": 0.0}
              )
              assert result.isError
              assert "Division error: Cannot divide by zero" in result.content[0].text
      ```

      #### Testing Complex Return Types

      ```python
      import pytest
      from mcp.server.fastmcp import FastMCP, Image
      from mcp.server.fastmcp.testing import client_session
      from typing import List, Dict, Any, Union
      import tempfile
      import os

      @pytest.mark.anyio
      async def test_complex_return_types():
          """Test a tool that returns complex data types."""
          server = FastMCP()

          @server.tool()
          def mixed_return_types() -> List[Union[str, Dict[str, Any], Image]]:
              """Return multiple content types."""
              # Create a temporary image file
              with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                  tmp_path = tmp.name
                  # In a real test, you might create an actual image here
                  with open(tmp_path, "wb") as f:
                      f.write(b"MOCK_IMAGE_DATA")

              # Return mixed content types
              return [
                  "Text content",
                  {"key1": "value1", "key2": 42},
                  Image(path=tmp_path)
              ]

          async with client_session(server._mcp_server) as client:
              result = await client.call_tool("mixed_return_types", {})
              assert not result.isError

              # Check number of content items
              assert len(result.content) == 3

              # Check text content
              assert result.content[0].text == "Text content"

              # Check JSON content
              assert "key1" in result.content[1].text
              assert "value1" in result.content[1].text

              # Check image content
              assert result.content[2].type == "image"
              assert result.content[2].mimeType == "image/png"

              # Clean up temporary file
              os.unlink(tmp_path)
      ```

      #### Integration Testing with Multiple Tools

      ```python
      import pytest
      from mcp.server.fastmcp import FastMCP, Context
      from mcp.server.fastmcp.testing import client_session
      from typing import Dict, Any

      @pytest.mark.anyio
      async def test_tool_integration():
          """Test integration between multiple tools."""
          server = FastMCP()

          @server.tool()
          def generate_data(count: int) -> Dict[str, Any]:
              """Generate test data."""
              return {
                  "items": [{"id": i, "value": f"Item {i}"} for i in range(count)]
              }

          @server.tool()
          def process_data(data: Dict[str, Any], ctx: Context) -> str:
              """Process data generated by another tool."""
              items = data.get("items",)
              await ctx.info(f"Processing {len(items)} items")

              result = ", ".join([item["value"] for item in items])
              return f"Processed items: {result}"

          async with client_session(server._mcp_server) as client:
              # First call generate_data
              gen_result = await client.call_tool("generate_data", {"count": 3})
              assert not gen_result.isError

              # Extract the data from the result
              import json
              data = json.loads(gen_result.content[0].text)

              # Then call process_data with the result
              proc_result = await client.call_tool("process_data", {"data": data})
              assert not proc_result.isError
              assert "Processed items: Item 0, Item 1, Item 2" in proc_result.content[0].text
      ```

      ## Debugging Tips

      1.  **Use `-x` to Stop on First Failure**: When running pytest, use the `-x` flag to stop the test suite after the first failure. This helps you focus on the issue at hand without being overwhelmed by subsequent failures.
      2.  **Drop into the Debugger with `--pdb`**: If a test fails and you want to inspect the state of the program, use the `--pdb` flag. Pytest will drop you into a `pdb` (Python Debugger) session at the point of failure, allowing you to step through the code, inspect variables, and understand what went wrong.
      3.  **Capture Output with `--capture=no`**: By default, pytest captures stdout and stderr, which can be helpful for clean test output. However, during debugging, you might want to see the output in real-time. Use the `--capture=no` flag to disable output capturing and see the output directly in your terminal.
      4.  **Combine Flags for Efficient Debugging**: You can combine these flags for a more efficient debugging workflow. For example, `pytest -x --pdb --capture=no` will stop on the first failure, drop you into the debugger, and show the output in the terminal.
      5.  **Use `breakpoint()` for Targeted Debugging**:  Instead of relying solely on `--pdb`, you can insert `breakpoint()` calls directly into your test code or the tool's code. When pytest reaches a `breakpoint()` call, it will drop into a `pdb` session, allowing you to inspect the program's state at that specific point. This is useful when you have a general idea of where the issue might be.
      6.  **Leverage pytest's Rich Output**: Pytest provides detailed information about test failures, including assertions, expected values, and actual values. Carefully examine this output to understand the cause of the failure.
      7.  **Write Focused Tests**: Write small, focused tests that target specific functionality. This makes it easier to isolate and debug issues.
      8.  **Use Descriptive Test Names**: Give your tests descriptive names that clearly indicate what they are testing. This helps you quickly identify the relevant tests when debugging.
      9.  **Read the Tracebacks Carefully**:  When a test fails, pytest provides a traceback that shows the sequence of function calls that led to the failure. Read the traceback carefully to understand the flow of execution and identify the source of the error.
      10. **Use a Good IDE or Editor**:  A good IDE or editor can greatly enhance your debugging experience. Features like code completion, syntax highlighting,
