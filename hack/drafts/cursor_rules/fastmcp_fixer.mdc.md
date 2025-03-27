---
description:
globs:
alwaysApply: false
---

# FastMCP File Operations Fixer | Fast Python MCP Server Development

This rule provides guidance for refactoring FastMCP servers to avoid direct file operations, instead returning JSON instructions that allow clients to perform these operations. This enables MCP servers to run remotely while still supporting file system interactions.

<rule>
name: fastmcp_fixer
description: Guidelines for refactoring FastMCP servers to use client-side file operations instead of direct file system access
filters:
  # Match Python files
  - type: file_extension
    pattern: "\\.py$"
  # Match MCP server code
  - type: content
    pattern: "@mcp\\.tool|@mcp\\.resource|FastMCP\\(|from mcp\\.server\\.fastmcp import"

actions:
  - type: suggest
    message: |
      # FastMCP Remote Operation Best Practices

      ## Problem: Direct File Operations in MCP Tools

      MCP servers should avoid direct file system operations (reading files, creating directories, etc.) as they may run remotely from the client. Instead, tools should return JSON instructions for the client to perform these operations.

      ```python
      # ❌ PROBLEMATIC: Direct file operations
      @mcp.tool()
      def save_file(file_name: str, content: str) -> str:
          # This won't work when running remotely
          path = Path(file_name)
          path.parent.mkdir(parents=True, exist_ok=True)
          path.write_text(content)
          return f"Saved to {path}"
      ```

      ## Solution: Return Operation Instructions

      MCP tools should return structured JSON instructions that tell the client what file operations to perform:

      ```python
      # ✅ RECOMMENDED: Return operation instructions
      @mcp.tool()
      def save_file(file_name: str, content: str) -> dict[str, Any]:
          return {
              "operations": [
                  {
                      "type": "create_directory",
                      "path": str(Path(file_name).parent),
                      "options": {"parents": True, "exist_ok": True}
                  },
                  {
                      "type": "write_file",
                      "path": file_name,
                      "content": content,
                      "options": {"mode": "w"}
                  }
              ],
              "message": f"Instructions to save file to {file_name}"
          }
      ```

      ## Standard Operation Types

      Use these standard operation types in your JSON instructions:

      1. **`create_directory`**:
         ```python
         {
             "type": "create_directory",
             "path": "path/to/directory",
             "options": {"parents": True, "exist_ok": True}
         }
         ```

      2. **`write_file`**:
         ```python
         {
             "type": "write_file",
             "path": "path/to/file",
             "content": "file content",
             "options": {"mode": "w", "encoding": "utf-8"}
         }
         ```

      3. **`read_file`**:
         ```python
         {
             "type": "read_file",
             "path": "path/to/file",
             "options": {"encoding": "utf-8"}
         }
         ```

      4. **`execute_command`**:
         ```python
         {
             "type": "execute_command",
             "command": "make update-cursor-rules",
             "options": {"cwd": "working/directory"}
         }
         ```

      5. **`check_file_exists`**:
         ```python
         {
             "type": "check_file_exists",
             "path": "path/to/file"
         }
         ```

      ## Testing MCP File Operations

      Create helper functions to test tools that return file operation instructions:

      ```python
      from typing import Any, Dict, List, Optional, Union
      import os
      import json
      from pathlib import Path

      def apply_operations(operations: List[Dict[str, Any]], base_dir: Optional[Path] = None) -> Dict[str, Any]:
          """Apply file operations to a directory (default: temporary directory).

          Args:
              operations: List of operation objects to apply
              base_dir: Optional base directory (defaults to cwd)

          Returns:
              Dict with results of operations
          """
          results = {}
          if base_dir is None:
              base_dir = Path.cwd()

          for op in operations:
              op_type = op.get("type")
              path = op.get("path")
              if not path:
                  continue

              # Make path relative to base_dir
              full_path = base_dir / path

              if op_type == "create_directory":
                  options = op.get("options", {})
                  parents = options.get("parents", False)
                  exist_ok = options.get("exist_ok", False)
                  full_path.mkdir(parents=parents, exist_ok=exist_ok)
                  results[path] = {"type": "directory_created", "path": str(full_path)}

              elif op_type == "write_file":
                  content = op.get("content", "")
                  options = op.get("options", {})
                  mode = options.get("mode", "w")
                  encoding = options.get("encoding", "utf-8")

                  # Create parent directory if it doesn't exist
                  full_path.parent.mkdir(parents=True, exist_ok=True)

                  with open(full_path, mode, encoding=encoding) as f:
                      f.write(content)
                  results[path] = {"type": "file_written", "path": str(full_path)}

              elif op_type == "read_file":
                  options = op.get("options", {})
                  encoding = options.get("encoding", "utf-8")

                  if full_path.exists():
                      content = full_path.read_text(encoding=encoding)
                      results[path] = {"type": "file_read", "content": content}
                  else:
                      results[path] = {"type": "error", "message": f"File not found: {full_path}"}

              elif op_type == "check_file_exists":
                  exists = full_path.exists()
                  results[path] = {"type": "file_exists", "exists": exists}

          return results
      ```

      ### Using the Helper in Tests

      Here's how to use the helper function in your tests:

      ```python
      import pytest
      from pathlib import Path

      def test_save_cursor_rule(tmp_path: Path) -> None:
          """Test the save_cursor_rule tool returns correct operations."""
          # Call the function
          result = save_cursor_rule(rule_name="test_rule", rule_content="Test content")

          # Check that it returns operations
          assert "operations" in result
          assert isinstance(result["operations"], list)
          assert len(result["operations"]) > 0

          # Apply operations to a temporary directory
          applied = apply_operations(result["operations"], base_dir=tmp_path)

          # Verify the operations were applied correctly
          rule_path = tmp_path / "hack" / "drafts" / "cursor_rules" / "test_rule.mdc.md"
          assert rule_path.exists()
          assert rule_path.read_text() == "Test content"
      ```

      ## Handling Operation Results

      For operations that need to return results (like file reading):

      ```python
      @mcp.tool()
      def check_file_content(file_path: str) -> dict[str, Any]:
          """Check if a file exists and return instructions to read it."""
          return {
              "operations": [
                  {
                      "type": "check_file_exists",
                      "path": file_path
                  },
                  {
                      "type": "read_file",
                      "path": file_path,
                      "options": {"encoding": "utf-8"}
                  }
              ],
              "requires_result": True,
              "message": f"Instructions to read file {file_path}"
          }
      ```

      When `requires_result` is set to `True`, the client should apply the operations and then provide the results to the model to continue the conversation.

      ## Error Handling in MCP Tools

      According to MCP best practices, tool errors should be reported within the result object, not as protocol-level errors. This allows the LLM to see and potentially handle the error.

      ### Error Handling in Operation Results

      When an operation fails, include error information in the return structure:

      ```python
      @mcp.tool()
      def perform_risky_operation(file_path: str) -> dict[str, Any]:
          """Attempt an operation that might fail."""
          try:
              # Perform validation or preparation
              if not file_path.endswith('.txt'):
                  return {
                      "isError": True,
                      "content": [
                          {
                              "type": "text",
                              "text": "Error: Only .txt files are supported"
                          }
                      ],
                      "message": "Operation failed due to invalid file type"
                  }

              # Return successful operations
              return {
                  "operations": [
                      {
                          "type": "read_file",
                          "path": file_path,
                          "options": {"encoding": "utf-8"}
                      }
                  ],
                  "requires_result": True,
                  "message": f"Instructions to process file {file_path}"
              }
          except Exception as e:
              # Handle unexpected errors
              return {
                  "isError": True,
                  "content": [
                      {
                          "type": "text",
                          "text": f"Error: {str(e)}"
                      }
                  ],
                  "message": "Operation failed due to an unexpected error"
              }
      ```

      ### Client-Side Error Handling

      When implementing a client that processes operation instructions:

      ```python
      def process_tool_result(result: dict[str, Any]) -> Any:
          """Process a tool result from an MCP server."""
          # Check for server-reported errors
          if result.get("isError"):
              # Extract error message from content
              error_messages = [
                  content["text"] for content in result.get("content", [])
                  if content.get("type") == "text"
              ]
              error_text = " ".join(error_messages) or "Unknown error occurred"
              print(f"Tool error: {error_text}")
              return {"error": error_text}

          # Process operations
          operations = result.get("operations", [])
          if not operations:
              return result

          try:
              # Apply operations
              operation_results = apply_operations(operations)

              # Return results if required
              if result.get("requires_result"):
                  return operation_results
              else:
                  return {"success": True, "message": result.get("message")}
          except Exception as e:
              # Handle client-side errors
              return {
                  "error": f"Failed to execute operations: {str(e)}",
                  "operations": operations
              }
      ```

      ### Testing Error Handling

      Test both successful operations and error conditions:

      ```python
      def test_tool_error_handling() -> None:
          """Test that tools properly handle and report errors."""
          # Test with invalid input
          result = perform_risky_operation(file_path="data.csv")

          # Verify error structure
          assert "isError" in result
          assert result["isError"] is True
          assert "content" in result
          assert len(result["content"]) > 0
          assert result["content"][0]["type"] == "text"
          assert "Error" in result["content"][0]["text"]

          # Test with valid input
          valid_result = perform_risky_operation(file_path="data.txt")
          assert "isError" not in valid_result
          assert "operations" in valid_result
      ```

      ### MCP Error Handling Best Practices

      1. **Use Content Array**: Always return error details in the `content` array with `isError: true`
      2. **Descriptive Messages**: Provide clear, actionable error messages
      3. **Error Types**: Consider including error type information for categorization
      4. **Security**: Don't expose sensitive system details in error messages
      5. **Recovery Hints**: When possible, include suggestions on how to fix the issue
      6. **Logging**: Log detailed errors server-side while returning sanitized messages to clients

      ## FastMCP Development Feedback Loop

      Follow this iterative process when developing FastMCP tools that use file operations:

      ### 1. Identify Direct File Operations

      Start by identifying tools that perform direct file operations:

      ```bash
      # Find file operations in your codebase
      grep -r "open(" --include="*.py" .
      grep -r "write_text" --include="*.py" .
      grep -r "read_text" --include="*.py" .
      grep -r "mkdir" --include="*.py" .
      grep -r "Path(" --include="*.py" .
      ```

      Prioritize tools that:
      - Create or modify files
      - Read file contents
      - Check for file existence
      - Create directories
      - Execute shell commands

      ### 2. Refactor One Tool at a Time

      For each tool with direct file operations:

      1. **Write a test first**:
         ```python
         def test_tool_returns_operations():
             """Test that the tool returns operation instructions instead of performing direct actions."""
             result = my_file_tool(param="value")

             # Should return operations dictionary
             assert isinstance(result, dict)
             assert "operations" in result
             assert isinstance(result["operations"], list)

             # Verify operation types are correct
             operations = result["operations"]
             assert all("type" in op for op in operations)
             assert all("path" in op for op in operations)
         ```

      2. **Run the test** (it should fail):
         ```bash
         uv run pytest tests/path/to/test_file.py::test_tool_returns_operations -v
         ```

      3. **Refactor the tool** to return operations:
         ```python
         # Before:
         @mcp.tool()
         def my_file_tool(param: str) -> str:
             path = Path(f"{param}.txt")
             path.write_text("content")
             return f"Created {path}"

         # After:
         @mcp.tool()
         def my_file_tool(param: str) -> dict[str, Any]:
             return {
                 "operations": [
                     {
                         "type": "write_file",
                         "path": f"{param}.txt",
                         "content": "content",
                         "options": {"mode": "w"}
                     }
                 ],
                 "message": f"Instructions to create {param}.txt"
             }
         ```

      4. **Run the test again** (it should pass):
         ```bash
         uv run pytest tests/path/to/test_file.py::test_tool_returns_operations -v
         ```

      ### 3. Add Operation Application Test

      Now verify that the operations work as expected when applied:

      1. **Add an application test**:
         ```python
         def test_tool_operations_work_correctly(tmp_path: Path):
             """Test that the operations returned by the tool work correctly when applied."""
             # Get operations from tool
             result = my_file_tool(param="test")

             # Apply operations
             applied = apply_operations(result["operations"], base_dir=tmp_path)

             # Verify results
             file_path = tmp_path / "test.txt"
             assert file_path.exists()
             assert file_path.read_text() == "content"
         ```

      2. **Run the application test**:
         ```bash
         uv run pytest tests/path/to/test_file.py::test_tool_operations_work_correctly -v
         ```

      ### 4. Add Error Handling Tests

      Test error conditions to ensure they're handled properly:

      1. **Add error handling test**:
         ```python
         def test_tool_handles_errors():
             """Test that the tool properly reports errors."""
             # Test with invalid input that should cause an error
             result = my_file_tool(param="")

             # Should return error structure
             assert "isError" in result
             assert result["isError"] is True
             assert "content" in result
             assert len(result["content"]) > 0
             assert "Error" in result["content"][0]["text"]
         ```

      2. **Run the error handling test**:
         ```bash
         uv run pytest tests/path/to/test_file.py::test_tool_handles_errors -v
         ```

      3. **Update tool to handle errors properly** if needed:
         ```python
         @mcp.tool()
         def my_file_tool(param: str) -> dict[str, Any]:
             # Validate input
             if not param:
                 return {
                     "isError": True,
                     "content": [
                         {
                             "type": "text",
                             "text": "Error: Parameter cannot be empty"
                         }
                     ],
                     "message": "Operation failed due to invalid parameter"
                 }

             # Return operations for valid input
             return {
                 "operations": [
                     {
                         "type": "write_file",
                         "path": f"{param}.txt",
                         "content": "content",
                         "options": {"mode": "w"}
                     }
                 ],
                 "message": f"Instructions to create {param}.txt"
             }
         ```

      ### 5. Run Integration Tests

      After refactoring individual tools, test them together:

      ```bash
      # Run all tests for the module
      uv run pytest tests/path/to/module_tests/

      # Run with coverage to ensure all code paths are tested
      uv run pytest tests/path/to/module_tests/ --cov=src/path/to/module
      ```

      ### 6. Verify End-to-End

      Test the entire flow with a client that processes operations:

      1. **Create and run an end-to-end test**:
         ```python
         def test_client_tool_interaction(tmp_path: Path):
             """Test end-to-end tool execution via a client."""
             # Set up client with tmp_path as working directory
             client = TestClient(working_dir=tmp_path)

             # Call the tool via client
             result = client.call_tool("my_file_tool", {"param": "test"})

             # Verify the file was created via the client
             file_path = tmp_path / "test.txt"
             assert file_path.exists()
             assert file_path.read_text() == "content"
         ```

      2. **Run the end-to-end test**:
         ```bash
         uv run pytest tests/path/to/integration_tests.py::test_client_tool_interaction -v
         ```

      ### 7. Iterate and Improve

      For each test failure:

      1. **Analyze the failure** to understand what's wrong
      2. **Fix the issue** in the smallest possible increment
      3. **Run the specific test** that failed again
      4. **Run the full test suite** once the specific test passes

      ### FastMCP Testing Guidelines

      1. **Test Both Server and Client Sides**:
         - Test that tools return correct operation structures
         - Test that operations apply correctly
         - Test client-side operation processing

      2. **Test Error Handling Comprehensively**:
         - Test validation failures
         - Test operation failures
         - Test client-side error handling

      3. **Use Parameterized Tests** for different operation types:
         ```python
         @pytest.mark.parametrize("operation_type,params,expected", [
             ("write_file", {"path": "test.txt", "content": "hello"}, {"exists": True, "content": "hello"}),
             ("create_directory", {"path": "test_dir"}, {"exists": True, "is_dir": True}),
             # Add more test cases
         ])
         def test_apply_operations(operation_type, params, expected, tmp_path):
             """Test applying different types of operations."""
             # Create operation
             operation = {"type": operation_type, **params}

             # Apply operation
             result = apply_operations([operation], base_dir=tmp_path)

             # Verify results based on expected outcomes
             path = tmp_path / params["path"]
             assert path.exists() == expected["exists"]
             if "is_dir" in expected:
                 assert path.is_dir() == expected["is_dir"]
             if "content" in expected:
                 assert path.read_text() == expected["content"]
         ```

      4. **Mock External Services** but not file operations:
         - Use real file system operations in tests with `tmp_path`
         - Mock other external dependencies like APIs

      5. **Maintain Test Independence**:
         - Each test should set up its own environment
         - Clean up after tests to avoid interfering with other tests
         - Use fresh temporary directories for each test

examples:
  - input: |
      # This MCP tool performs direct file operations

      @mcp.tool(name="create_project_structure")
      def create_project_structure(
          project_name: str = Field(description="The name of the project")
      ) -> str:
          """Create a standard Python project structure."""
          # Create the project directory
          project_dir = Path(project_name)
          project_dir.mkdir(exist_ok=True)

          # Create project subdirectories
          (project_dir / "src").mkdir(exist_ok=True)
          (project_dir / "tests").mkdir(exist_ok=True)
          (project_dir / "docs").mkdir(exist_ok=True)

          # Create basic files
          (project_dir / "README.md").write_text(f"# {project_name}\n\nProject description.")
          (project_dir / "pyproject.toml").write_text("[build-system]\nrequires = [\"setuptools>=42\"]\nbuild-backend = \"setuptools.build_meta\"\n")

          return f"Created project structure for {project_name}"
    output: |
      This MCP tool directly performs file operations which won't work when running remotely. We should refactor it to return operation instructions instead:

      ```python
      @mcp.tool(name="create_project_structure")
      def create_project_structure(
          project_name: str = Field(description="The name of the project")
      ) -> dict[str, Any]:
          """Create a standard Python project structure."""
          operations = [
              # Create the project directory
              {
                  "type": "create_directory",
                  "path": project_name,
                  "options": {"exist_ok": True}
              },
              # Create project subdirectories
              {
                  "type": "create_directory",
                  "path": f"{project_name}/src",
                  "options": {"exist_ok": True}
              },
              {
                  "type": "create_directory",
                  "path": f"{project_name}/tests",
                  "options": {"exist_ok": True}
              },
              {
                  "type": "create_directory",
                  "path": f"{project_name}/docs",
                  "options": {"exist_ok": True}
              },
              # Create basic files
              {
                  "type": "write_file",
                  "path": f"{project_name}/README.md",
                  "content": f"# {project_name}\n\nProject description.",
                  "options": {"mode": "w"}
              },
              {
                  "type": "write_file",
                  "path": f"{project_name}/pyproject.toml",
                  "content": "[build-system]\nrequires = [\"setuptools>=42\"]\nbuild-backend = \"setuptools.build_meta\"\n",
                  "options": {"mode": "w"}
              }
          ]

          return {
              "operations": operations,
              "message": f"Instructions to create project structure for {project_name}"
          }
      ```

  - input: |
      # How do I test this MCP tool that checks file content?

      @mcp.tool()
      def check_config_file(config_path: str) -> dict[str, Any]:
          """Check if a configuration file exists and return its content if it does."""
          operations = [
              {
                  "type": "check_file_exists",
                  "path": config_path
              },
              {
                  "type": "read_file",
                  "path": config_path,
                  "options": {"encoding": "utf-8"}
              }
          ]

          return {
              "operations": operations,
              "requires_result": True,
              "message": f"Instructions to check configuration file {config_path}"
          }
    output: |
      Here's how to test this MCP tool using the helper function:

      ```python
      import pytest
      from pathlib import Path
      from typing import Dict, Any, List

      # First, implement the test helper function if not already available
      def apply_operations(operations: List[Dict[str, Any]], base_dir: Path) -> Dict[str, Any]:
          """Apply file operations and return results."""
          results = {}

          for op in operations:
              op_type = op.get("type")
              path = op.get("path")
              if not path:
                  continue

              # Make path relative to base_dir
              full_path = base_dir / path

              if op_type == "check_file_exists":
                  exists = full_path.exists()
                  results[path] = {"type": "file_exists", "exists": exists}

              elif op_type == "read_file":
                  if full_path.exists():
                      options = op.get("options", {})
                      encoding = options.get("encoding", "utf-8")
                      content = full_path.read_text(encoding=encoding)
                      results[path] = {"type": "file_read", "content": content}
                  else:
                      results[path] = {"type": "error", "message": f"File not found: {full_path}"}

          return results

      # Now the actual test
      def test_check_config_file(tmp_path: Path) -> None:
          """Test the check_config_file tool."""
          # Create a test config file
          config_content = "key = value\ndebug = true"
          config_path = tmp_path / "config.ini"
          config_path.write_text(config_content)

          # Call the function with relative path
          result = check_config_file(config_path=str(config_path))

          # Check that it returns operations
          assert "operations" in result
          assert isinstance(result["operations"], list)
          assert result.get("requires_result") is True

          # Apply operations to get results
          operation_results = apply_operations(result["operations"], tmp_path.parent)

          # Check that the file exists result is included
          assert str(config_path) in operation_results
          file_exists_result = operation_results.get(str(config_path))
          assert file_exists_result.get("exists") is True

          # Check that the file content matches
          read_result = operation_results.get(str(config_path))
          assert read_result.get("content") == config_content

          # Test with non-existent file
          nonexistent_path = tmp_path / "nonexistent.ini"
          result = check_config_file(config_path=str(nonexistent_path))
          operation_results = apply_operations(result["operations"], tmp_path.parent)

          # Check that the file does not exist
          file_exists_result = operation_results.get(str(nonexistent_path))
          assert file_exists_result.get("exists") is False
      ```

      This test verifies:
      1. The tool returns the correct operations structure
      2. When applied, the operations correctly check if the file exists and read its content
      3. The operation results match the expected values
      4. It also tests the negative case with a non-existent file

  - input: |
      # I need to test my updated tool with iterative development

      @mcp.tool()
      def generate_config_file(config_name: str, config_values: Dict[str, Any]) -> Dict[str, Any]:
          """Generate a configuration file with the provided values."""
          # Convert config values to a string
          config_content = "\n".join([f"{key} = {value}" for key, value in config_values.items()])

          return {
              "operations": [
                  {
                      "type": "write_file",
                      "path": f"{config_name}.cfg",
                      "content": config_content,
                      "options": {"mode": "w"}
                  }
              ],
              "message": f"Instructions to create {config_name}.cfg with the provided values"
          }
    output: |
      Follow this iterative process to test your updated tool:

      1. First, create a basic test for the operation structure:

      ```python
      import pytest
      from pathlib import Path
      from typing import Dict, Any, List

      def test_generate_config_file_returns_operations():
          """Test that generate_config_file returns proper operation instructions."""
          # Test data
          config_name = "app"
          config_values = {"debug": True, "port": 8080, "host": "localhost"}

          # Call the function
          result = generate_config_file(config_name=config_name, config_values=config_values)

          # Check basic structure
          assert isinstance(result, dict)
          assert "operations" in result
          assert isinstance(result["operations"], list)

          # Check operation details
          operations = result["operations"]
          assert len(operations) == 1
          assert operations[0]["type"] == "write_file"
          assert operations[0]["path"] == "app.cfg"
          assert "content" in operations[0]
          assert "options" in operations[0]

          # Run this test first
          # uv run pytest tests/path/to/test_file.py::test_generate_config_file_returns_operations -v
      ```

      2. Next, test that the operations work as expected when applied:

      ```python
      def test_generate_config_file_operations_work(tmp_path: Path):
          """Test that the operations from generate_config_file work correctly when applied."""
          # Test data
          config_name = "app"
          config_values = {"debug": True, "port": 8080, "host": "localhost"}

          # Get operations from tool
          result = generate_config_file(config_name=config_name, config_values=config_values)

          # Apply operations to temporary directory
          applied = apply_operations(result["operations"], base_dir=tmp_path)

          # Verify file was created
          config_path = tmp_path / f"{config_name}.cfg"
          assert config_path.exists()

          # Verify content is correct
          content = config_path.read_text()
          for key, value in config_values.items():
              assert f"{key} = {value}" in content

          # Run this test second
          # uv run pytest tests/path/to/test_file.py::test_generate_config_file_operations_work -v
      ```

      3. Test edge cases and error handling:

      ```python
      @pytest.mark.parametrize("config_name,config_values,is_valid", [
          ("app", {"debug": True}, True),                # Valid simple config
          ("", {"debug": True}, False),                  # Empty name - should fail
          ("app", {}, False),                            # Empty values - should fail
          ("app", {"key with spaces": "value"}, True),   # Keys with spaces - should work
          ("app.special", {"debug": True}, True),        # Name with extensions - should work
      ])
      def test_generate_config_file_edge_cases(config_name, config_values, is_valid, tmp_path: Path):
          """Test generate_config_file with various edge cases."""
          # Call the function
          result = generate_config_file(config_name=config_name, config_values=config_values)

          if not is_valid:
              # Should return error structure for invalid inputs
              assert "isError" in result
              assert result["isError"] is True
              assert "content" in result
              assert any("Error" in c["text"] for c in result["content"] if c["type"] == "text")
          else:
              # Should return valid operations for valid inputs
              assert "operations" in result

              # Apply operations
              applied = apply_operations(result["operations"], base_dir=tmp_path)

              # Verify file exists
              if config_name:
                  config_path = tmp_path / f"{config_name}.cfg"
                  assert config_path.exists()

                  # Verify content
                  content = config_path.read_text()
                  for key, value in config_values.items():
                      assert f"{key} = {value}" in content

          # Run this test after fixing the function to handle edge cases
          # uv run pytest tests/path/to/test_file.py::test_generate_config_file_edge_cases -v
      ```

      4. Update your tool to handle the edge cases:

      ```python
      @mcp.tool()
      def generate_config_file(config_name: str, config_values: Dict[str, Any]) -> Dict[str, Any]:
          """Generate a configuration file with the provided values."""
          # Validate inputs
          if not config_name:
              return {
                  "isError": True,
                  "content": [
                      {
                          "type": "text",
                          "text": "Error: Configuration name cannot be empty"
                      }
                  ],
                  "message": "Failed to generate configuration file"
              }

          if not config_values:
              return {
                  "isError": True,
                  "content": [
                      {
                          "type": "text",
                          "text": "Error: Configuration values cannot be empty"
                      }
                  ],
                  "message": "Failed to generate configuration file"
              }

          # Convert config values to a string
          config_content = "\n".join([f"{key} = {value}" for key, value in config_values.items()])

          return {
              "operations": [
                  {
                      "type": "write_file",
                      "path": f"{config_name}.cfg",
                      "content": config_content,
                      "options": {"mode": "w"}
                  }
              ],
              "message": f"Instructions to create {config_name}.cfg with the provided values"
          }
      ```

      5. Finally, run all the tests to verify everything works:

      ```bash
      # Run all tests for this file
      uv run pytest tests/path/to/test_file.py -v

      # Run with coverage
      uv run pytest tests/path/to/test_file.py --cov=src/path/to/module -v
      ```

      This iterative approach helps you:
      1. Start with basic functionality tests
      2. Verify operations work when applied
      3. Test edge cases and error conditions
      4. Improve your code to handle all cases
      5. Verify all tests pass together

metadata:
  priority: high
  version: 1.0
  tags:
    - fastmcp
    - file-operations
    - testing
    - remote-execution
    - mcp-server
</rule>
