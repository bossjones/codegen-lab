---
description: Python code refactoring and modularization guidelines
globs: "*.py"
alwaysApply: false
---
# Python Code Refactoring Guide

This rule provides guidance for refactoring Python code, particularly focusing on breaking down large files into smaller, more manageable components.

<rule>
name: python-refactor
description: Guidelines for refactoring Python code into modular components
filters:
  - type: file_extension
    pattern: "\\.py$"
  - type: content
    pattern: "(?i)(refactor|modularize|break down|split|large file)"

actions:
  - type: suggest
    message: |
      # Python Code Refactoring Guidelines

      When refactoring Python code, particularly large files, follow these guidelines and development loop:

      ## Development Loop

      For each component you're refactoring, follow this TDD-based development loop:

      ### 1. Write Tests First
      ```bash
      # Create test file for the component you're extracting
      touch tests/test_component.py

      # Run tests with specific filtering and verbose output
      uv run pytest -v -k "test_component" tests/test_component.py

      # For more debugging information:
      uv run pytest -s --verbose --showlocals --tb=short tests/test_component.py::TestComponent::test_specific_function
      ```

      Example test structure:
      ```python
      # tests/test_component.py
      from typing import TYPE_CHECKING
      import pytest
      from your_package.component import YourComponent

      if TYPE_CHECKING:
          from _pytest.fixtures import FixtureRequest
          from _pytest.monkeypatch import MonkeyPatch
          from pytest_mock.plugin import MockerFixture

      @pytest.fixture
      def component():
          """Create a component instance for testing."""
          return YourComponent()

      def test_component_behavior(component: YourComponent):
          """Test the component's core behavior."""
          result = component.do_something()
          assert result == "expected"
      ```

      #### FastMCP Testing
      For components that involve FastMCP, MCP tools, or similar technologies, please refer to the `@fastmcp-testing.mdc` rule for specialized testing guidance. MCP tools require specific test setups including:

      - Using `client_session` from `mcp.server.fastmcp.testing`
      - Properly testing synchronous and asynchronous tools
      - Testing tool lifecycle and error handling
      - Validating complex return types
      - Setting up proper context and progress reporting tests

      ```python
      # Example of a basic FastMCP tool test
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
              assert not result.isError
              assert result.content[0].text == "Processed test"
      ```

      #### Handling Persistent Test Failures

      If you encounter 5 or more consecutive test failures during refactoring:

      1. **Check Code Synchronization**: Have Cursor read the implementation files to ensure it's aware of the most up-to-date code:
         ```
         Please read the current implementation of [filename] to ensure you're aware of the most up-to-date code.
         ```

      2. **Check Test vs Implementation**: Verify that your tests and implementation match. Focus on input/output types, function signatures, and expected behavior.

      3. **Look for Hidden Dependencies**: Check for implicit dependencies that weren't migrated during refactoring:
         ```bash
         # Find where this symbol is imported or referenced
         grep -r "SymbolName" --include="*.py" .
         ```

      4. **Simplify Test Scope**: Temporarily simplify the test to isolate the issue:
         ```python
         # Instead of complex assertions, test existence first
         assert hasattr(module, "function_name")

         # Test basic functionality before complex cases
         assert isinstance(result, dict)
         ```

      5. **Use Debug Tooling**: Add debugging output or use bpdb:
         ```python
         import bpdb; bpdb.set_trace()  # Add before failure point


         # Or use print debugging
         print(f"Variable state: {variable}")
         ```

      ### 2. Extract Component
      - Move the code to its new location
      - Update imports to use fully qualified paths
      - Add type hints and docstrings
      - Ensure backward compatibility

      ### 3. Quality Checks
      Run through these checks after each significant change:

      ```bash
      # 1. Format code
      uv run ruff format .

      # 2. Run tests
      uv run pytest

      # 3. Check and fix linting
      uv run ruff check . --fix --show-fixes

      # 4. Check types
      uv run mypy

      # 5. Verify tests again
      uv run pytest
      ```

      ### 4. Documentation
      - Add docstrings in reStructuredText format
      - Include doctests for usage examples
      - Update any affected documentation

      Example docstring:
      ```python
      """Handle user authentication and authorization.

      This module provides functionality for user authentication,
      authorization, and session management.

      Examples
      --------
      Create an auth handler:

      >>> handler = AuthHandler()
      >>> handler.authenticate("user", "pass")
      True

      Parameters
      ----------
      config : Dict[str, Any]
          Configuration dictionary for auth settings
      """
      ```

      ### 5. Commit Changes
      Make atomic commits for each refactoring step:
      1. Tests first
      2. Component extraction
      3. Quality fixes (if needed)

      ## Directory Structure

      Organize your code into a simplified directory structure:

      ```
      src/package_name/
      ├── __init__.py
      ├── submodule/
      │   ├── __init__.py
      │   ├── models.py       # Data models and types
      │   ├── utils.py        # Utility functions
      │   ├── services.py     # Business logic
      │   └── resources.py    # API endpoints/resources
      └── main_module.py      # Original entry point
      ```

      ## Refactoring Steps

      1. **Analyze Dependencies**:
         - Map out function and class dependencies
         - Identify natural groupings of functionality
         - Note shared utilities and helper functions
         - Write tests for existing behavior before moving code

      2. **Create Module Structure**:
         - Create appropriate directories for the submodule
         - Add `__init__.py` files to make directories packages
         - Plan the new file organization based on functionality
         - Set up test files for each new module

      3. **Extract Components**:
         - Move related functions/classes to appropriate new files
         - Update imports in all affected files
         - Maintain backward compatibility in the original entry point

      4. **Update Entry Point**:
         - Keep the original file as the main entry point
         - Import and re-export necessary components
         - Provide backward compatibility if needed

      ## Best Practices

      1. **Module Organization**:
         - Group related functionality together
         - Keep files focused on specific types of functionality
         - Use clear, descriptive file names
         - Maintain test files that mirror the module structure

      2. **Import Management**:
         - Use fully qualified imports (e.g., `from package_name.module import Class`)
         - Import only what's needed
         - Avoid circular dependencies
         - Use `typing.TYPE_CHECKING` for test-only imports

      3. **Testing Standards**:
         - Write tests before moving code
         - Use pytest fixtures over unittest.mock
         - Include type hints in test files
         - Add docstrings to test classes and functions
         - Use doctest for simple examples
         - Move complex examples to dedicated test files

      4. **Documentation**:
         - Use reStructuredText format for docstrings
         - Document module purposes in __init__.py
         - Include usage examples in doctests
         - Update import examples in documentation
         - Add type hints for all functions and classes

      ## Example Refactoring

      Original large file:
      ```python
      # large_module.py
      from typing import Dict, List, Optional

      class DataModel:
          """Data model implementation."""
          pass

      def process_data(data: Dict) -> List:
          """Process the data."""
          pass

      def helper_function() -> None:
          """Helper utility."""
          pass

      def api_endpoint() -> Dict:
          """API endpoint handler."""
          pass
      ```

      Refactored structure (Simplified Approach):
      ```python
      # src/package_name/submodule/models.py
      from typing import Dict, List

      class DataModel:
          """Data model implementation."""
          pass

      # src/package_name/submodule/utils.py
      def helper_function() -> None:
          """Helper utility."""
          pass

      # src/package_name/submodule/services.py
      from typing import Dict, List
      from package_name.submodule.models import DataModel

      def process_data(data: Dict) -> List:
          """Process the data."""
          pass

      # src/package_name/submodule/resources.py
      from typing import Dict
      from package_name.submodule.services import process_data

      def api_endpoint() -> Dict:
          """API endpoint handler."""
          pass

      # src/package_name/submodule/__init__.py
      from package_name.submodule.models import DataModel
      from package_name.submodule.services import process_data
      from package_name.submodule.resources import api_endpoint

      __all__ = ['DataModel', 'process_data', 'api_endpoint']

      # src/package_name/large_module.py becomes:
      from package_name.submodule import DataModel, process_data, api_endpoint
      from package_name.submodule.utils import helper_function

      # Re-export for backward compatibility
      __all__ = ['DataModel', 'process_data', 'helper_function', 'api_endpoint']
      ```

examples:
  - input: |
      This file is getting too big and needs to be split up:
      ```python
      # big_module.py
      class UserModel:
          pass

      def process_user(user):
          pass

      def api_endpoint():
          pass
      ```
    output: |
      Let's refactor this into a cleaner structure:

      ```
      src/codegen_lab/
      ├── __init__.py
      ├── promptlib/
      │   ├── __init__.py
      │   ├── models.py          # Contains UserModel
      │   ├── services.py        # Contains process_user
      │   └── resources.py       # Contains api_endpoint
      └── big_module.py          # Now just imports and re-exports
      ```

      With the following implementation:

      ```python
      # src/codegen_lab/promptlib/models.py
      from typing import Dict, Any

      class UserModel:
          """User model implementation."""
          pass

      # src/codegen_lab/promptlib/services.py
      from typing import Dict, Any
      from codegen_lab.promptlib.models import UserModel

      def process_user(user: UserModel) -> Dict[str, Any]:
          """Process the user data."""
          pass

      # src/codegen_lab/promptlib/resources.py
      from typing import Dict, Any
      from codegen_lab.promptlib.models import UserModel
      from codegen_lab.promptlib.services import process_user

      def api_endpoint() -> Dict[str, Any]:
          """API endpoint handler."""
          pass

      # src/codegen_lab/promptlib/__init__.py
      from codegen_lab.promptlib.models import UserModel
      from codegen_lab.promptlib.services import process_user
      from codegen_lab.promptlib.resources import api_endpoint

      __all__ = ['UserModel', 'process_user', 'api_endpoint']

      # src/codegen_lab/big_module.py
      from codegen_lab.promptlib import UserModel, process_user, api_endpoint

      # Re-export for backward compatibility
      __all__ = ['UserModel', 'process_user', 'api_endpoint']
      ```

metadata:
  priority: high
  version: 1.0
  tags:
    - python
    - refactoring
    - code-organization
    - best-practices
    - tdd
    - testing
</rule>
