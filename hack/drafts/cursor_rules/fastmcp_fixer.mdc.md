---
description: Fast Python MCP Server Development
globs: *.py
alwaysApply: false
---

# FastMCP File Operations Fixer

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
