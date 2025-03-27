---
description:
globs:
alwaysApply: false
---
# Python Code Refactoring Guide

Python code refactoring and modularization guidelines with mandatory TDD practices

This rule provides mandatory guidance for refactoring Python code using Test-Driven Development (TDD), with a focus on breaking down large files into smaller, more manageable components.

<rule>
name: python-refactor
description: Mandatory TDD guidelines for refactoring Python code into modular components
filters:
  - type: file_extension
    pattern: "\\.py$"
  - type: content
    pattern: "(?i)(refactor|modularize|break down|split|large file)"

actions:
  - type: suggest
    message: |
      # Python Code Refactoring Guidelines

      ⚠️ IMPORTANT: Test-Driven Development (TDD) is MANDATORY for all refactoring work. No exceptions.

      ## TDD-First Development Loop

      Every refactoring task MUST follow this TDD-based workflow:

      1. Write failing tests for the desired behavior
      2. Implement minimal code to make tests pass
      3. Refactor while keeping tests green
      4. Repeat for each component

      ### Required Testing Setup

      Before ANY code changes:

      ```bash
      # 1. Create test directory structure
      mkdir -p tests/unit tests/integration || true

      # 2. Create test files first
      touch tests/unit/test_${component}.py
      touch tests/integration/test_${component}_integration.py

      # 3. Set up test fixtures and helpers
      touch tests/conftest.py
      ```

      ### Test Structure Template

      All test files MUST follow this structure:

      ```python
      """Unit tests for component functionality.

      This test suite verifies the behavior of the component
      in isolation from other system components.
      """
      from typing import TYPE_CHECKING

      import pytest

      if TYPE_CHECKING:
          from _pytest.capture import CaptureFixture
          from _pytest.fixtures import FixtureRequest
          from _pytest.logging import LogCaptureFixture
          from _pytest.monkeypatch import MonkeyPatch
          from pytest_mock.plugin import MockerFixture

      @pytest.fixture
      def component_fixture():
          """Create an isolated component instance for testing."""
          return ComponentUnderTest()

      def test_component_behavior(
          component_fixture: ComponentUnderTest,
          mocker: MockerFixture,
          caplog: LogCaptureFixture,
      ) -> None:
          """Test specific component behavior.

          This test verifies that the component behaves correctly
          under specific conditions.
          """
          # Given
          input_data = {"test": "data"}

          # When
          result = component_fixture.process(input_data)

          # Then
          assert result == expected_output
      ```

      ## Development Loop

      For each component you're refactoring, follow this TDD-based development loop:

      ### 0. Planning Phase
      - Create a scratch pad at the top of your module with a markdown checklist:
      ```python
      """Refactoring Plan:
      - [ ] Analyze code dependencies
      - [ ] Create directory structure
      - [ ] Create empty files with docstrings
      - [ ] Write tests for module 1
      - [ ] Implement module 1 (pseudocode first)
      - [ ] Write tests for module 2
      - [ ] Implement module 2 (pseudocode first)
      - [ ] Update imports
      - [ ] Verify tests pass
      """
      ```

      - Create a PLAN.md file for high-level implementation details:
      ```bash
      # Create a PLAN.md file in the project root
      touch PLAN.md
      ```

      ```markdown
      # Refactoring Plan

      ## Overview
      This document outlines the refactoring plan for [component/module]. It will be updated as the refactoring progresses.

      ## Goals
      - Improve maintainability by breaking down large files
      - Separate concerns into appropriate modules
      - Ensure backward compatibility
      - Maintain test coverage
      - Create a working POC without losing functionality

      ## XML Tag Structure
      Use XML-style tags to organize and track different aspects of the refactoring:

      <success_criteria>
      - All tests passing
      - No functionality loss
      - Improved code organization
      </success_criteria>

      <implementation>
      - Phase 1: Initial setup
      - Phase 2: Component extraction
      - Phase 3: Testing and validation
      </implementation>

      <dependencies>
      - Module A depends on Module B
      - Module C requires configuration from Module D
      </dependencies>

      <testing_strategy>
      - Unit tests for each component
      - Integration tests for module interactions
      - End-to-end tests for full workflows
      </testing_strategy>

      <documentation>
      - Update module docstrings
      - Add function/class documentation
      - Create usage examples
      </documentation>

      ## Architecture Changes
      - Create new module structure with the following components:
        - `models.py`: Data structures and schemas
        - `services.py`: Business logic and processing
        - `utils.py`: Helper functions and utilities
        - `resources.py`: API endpoints and interfaces

      ## Implementation Phases
      1. **POC Phase**
         - Identify minimal viable functionality
         - Create initial structure preserving core functionality
         - Ensure backward compatibility is maintained
         - Verify all existing functionality works

      2. **Setup Phase**
         - Create full directory structure
         - Add placeholder files with docstrings
         - Establish test scaffolding

      3. **Migration Phase**
         - Move models to models.py
         - Move business logic to services.py
         - Move utilities to utils.py
         - Move API endpoints to resources.py

      4. **Integration Phase**
         - Update imports
         - Set up proper exports
         - Ensure backward compatibility
         - Run full test suite

      ## Current Status
      <status>
      - [ ] Phase 1: POC (In Progress)
      - [ ] Phase 2: Setup
      - [ ] Phase 3: Migration
      - [ ] Phase 4: Integration
      </status>

      ## Notes
      <notes>
      - Any dependencies between components
      - Potential issues to be aware of
      - Design decisions made during refactoring
      </notes>
      ```

      - Set up the directory structure before making any code changes:
      ```bash
      # Create directory structure (with fallback if it exists)
      mkdir -p src/package_name/submodule || true

      # Initialize files before editing
      touch src/package_name/submodule/__init__.py
      touch src/package_name/submodule/models.py
      touch src/package_name/submodule/services.py
      touch src/package_name/submodule/resources.py
      ```

      - **Throughout the refactoring process**, reference and update the PLAN.md file:
        - Update the "Current Status" section after completing each phase
        - Add implementation details and decisions to the "Notes" section
        - Document any challenges encountered and their solutions
        - Track changes to the high-level architecture

      ### 1. POC Development

      When refactoring, it's critical to start with a proof of concept (POC) that preserves functionality:

      ```python
      # Start by creating a minimal working version that preserves existing functionality
      """POC Implementation:
      - [ ] Identify core functionality that must be preserved
      - [ ] Create minimal module structure with essential components
      - [ ] Implement bare minimum to maintain functionality
      - [ ] Verify behavior matches original implementation
      - [ ] Add tests that validate behavior equivalence
      """
      ```

      Example POC approach:
      ```python
      # Original monolithic file
      def process_data(input_data):
          # Complex processing logic
          return result

      # POC refactoring - first create the simplest working version
      # new_module.py
      def process_data(input_data):
          # Just forward to the original implementation initially
          # This ensures no functionality is lost during refactoring
          from original_module import process_data as original_process
          return original_process(input_data)

      # Then gradually move functionality while testing at each step
      ```

      POC testing:
      ```bash
      # Create test that verifies exact same behavior
      touch tests/test_equivalence.py

      # Run direct comparison test
      uv run pytest -v tests/test_equivalence.py
      ```

      POC verification:
      ```python
      # Example equivalence test
      def test_refactored_matches_original():
          """Verify the refactored implementation matches the original."""
          from original_module import process_data as original
          from new_module import process_data as refactored

          test_data = {"sample": "data"}

          # Both implementations should produce identical results
          assert refactored(test_data) == original(test_data)
      ```

      ### 2. Write Tests First
      ```bash
      # Create test directory if it doesn't exist
      mkdir -p tests || true

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

      ### 3. Extract Component
      - Start with pseudocode and docstrings for each module
      - Create placeholder functions and classes with detailed docstrings
      - Gradually implement each component, checking off items in your scratch pad
      - Update imports to use fully qualified paths
      - Add type hints and docstrings
      - Ensure backward compatibility

      Example of placeholder with docstring:
      ```python
      def process_data(data: Dict) -> List:
          """Process the input data and return a list of results.

          This function will:
          1. Validate input data
          2. Transform the data into the required format
          3. Apply business rules
          4. Return the processed results

          Args:
              data: Dictionary containing input data

          Returns:
              List of processed data items
          """
          # TODO: Implement data processing
          pass
      ```

      ### 4. Quality Checks
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

      ### 5. Documentation
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

      ### 6. Commit Changes
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
         ```bash
         mkdir -p src/package_name/submodule || true
         ```
         - Add `__init__.py` files to make directories packages
         ```bash
         touch src/package_name/__init__.py
         touch src/package_name/submodule/__init__.py
         ```
         - Plan the new file organization based on functionality
         ```bash
         touch src/package_name/submodule/models.py
         touch src/package_name/submodule/services.py
         touch src/package_name/submodule/utils.py
         touch src/package_name/submodule/resources.py
         ```
         - Set up test files for each new module
         ```bash
         mkdir -p tests || true
         touch tests/test_models.py
         touch tests/test_services.py
         ```

      3. **Extract Components**:
         - Begin with pseudocode and docstrings for each component
         - Gradually implement each module, testing as you go
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

      5. **POC-First Approach**:
         - Always start with a functioning POC that maintains compatibility
         - Test equivalence between original and refactored code
         - Verify no functionality is lost before proceeding with full refactoring
         - Create comparison tests that act as a safety net
         - Gradually replace compatibility layers with proper implementations
         - Keep original implementation accessible until fully verified

      ## Example Refactoring Workflow

      Starting with a large file:
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

      ### Step 1: Create a scratch pad and PLAN.md
      Add a planning docstring at the top of the file:
      ```python
      """Refactoring Plan for large_module.py:
      - [ ] Create POC with essential functionality
      - [ ] Verify POC preserves all behavior
      - [ ] Create directory structure
      - [ ] Set up __init__.py files
      - [ ] Extract DataModel to models.py
      - [ ] Extract process_data to services.py
      - [ ] Extract helper_function to utils.py
      - [ ] Extract api_endpoint to resources.py
      - [ ] Update imports in all files
      - [ ] Update large_module.py to re-export
      - [ ] Verify tests pass
      """

      # Rest of large_module.py...
      ```

      Create a PLAN.md file with high-level implementation details:
      ```bash
      # Create the PLAN.md file
      touch PLAN.md
      ```

      ```markdown
      # Refactoring Plan for large_module.py

      ## Overview
      This document outlines the plan for breaking down large_module.py into more manageable components.

      ## Goals
      - Separate concerns into appropriate modules
      - Improve code maintainability
      - Ensure backward compatibility
      - Create a working POC without losing functionality

      ## Architecture Changes
      - Extract data model into models.py
      - Move business logic to services.py
      - Move utility functions to utils.py
      - Place API endpoints in resources.py

      ## Implementation Phases
      1. **POC Phase** (Current)
         - Create minimal implementation that preserves functionality
         - Test equivalence to original code

      2. **Setup Phase**
         - Create directory structure
         - Add placeholder files

      3. **Migration Phase**
         - Move DataModel to models.py
         - Move process_data to services.py
         - Move helper_function to utils.py
         - Move api_endpoint to resources.py

      4. **Integration Phase**
         - Update imports
         - Set up re-exports in __init__.py
         - Update large_module.py to maintain compatibility

      ## Current Status
      - [x] Analysis completed
      - [ ] Phase 1: POC (In Progress)
      - [ ] Phase 2: Setup
      - [ ] Phase 3: Migration
      - [ ] Phase 4: Integration

      ## Notes
      - DataModel is used by process_data, so we need to ensure imports are correct
      - All exports should be maintained for backward compatibility
      ```

      ### Step 1.5: Create the POC

      ```python
      # src/package_name/submodule/__init__.py

      # Import and re-export everything from original module initially
      from package_name.large_module import DataModel, process_data, helper_function, api_endpoint

      __all__ = ['DataModel', 'process_data', 'helper_function', 'api_endpoint']
      ```

      Create an equivalence test:

      ```python
      # tests/test_equivalence.py

      def test_api_equivalence():
          """Test that the refactored module exports match the original."""
          # Import from original module
          from package_name.large_module import DataModel as OriginalDataModel
          from package_name.large_module import process_data as original_process

          # Import from new module structure
          from package_name.submodule import DataModel as NewDataModel
          from package_name.submodule import process_data as new_process

          # Verify classes are the same
          assert OriginalDataModel == NewDataModel

          # Verify functions behave the same
          test_data = {"test": "data"}
          assert original_process(test_data) == new_process(test_data)
      ```

      Update PLAN.md to reflect progress:
      ```markdown
      ## Current Status
      - [x] Analysis completed
      - [x] Phase 1: POC (Completed)
      - [ ] Phase 2: Setup (In Progress)
      - [ ] Phase 3: Migration
      - [ ] Phase 4: Integration

      ## Notes
      - POC implementation working with re-exports
      - Equivalence tests confirm no functionality loss
      - Moving to setup phase
      ```

      ### Step 2: Create directory structure
      ```bash
      # Create the required directories
      mkdir -p src/package_name/submodule || true

      # Initialize all the files
      touch src/package_name/__init__.py
      touch src/package_name/submodule/__init__.py
      touch src/package_name/submodule/models.py
      touch src/package_name/submodule/utils.py
      touch src/package_name/submodule/services.py
      touch src/package_name/submodule/resources.py
      ```

      Update PLAN.md to reflect progress:
      ```markdown
      ## Current Status
      - [x] Analysis completed
      - [x] Phase 1: POC (Completed)
      - [x] Phase 2: Setup (Completed)
      - [ ] Phase 3: Migration (In Progress)
      - [ ] Phase 4: Integration

      ## Notes
      - POC implementation completed
      - Equivalence tests confirmed
      - Setup phase completed
      - Ready to begin migration
      ```

      ### Step 3: Set up files with pseudocode
      ```python
      # src/package_name/submodule/models.py
      """Models module containing data structures.

      This module will contain:
      - [ ] DataModel class
      """
      from typing import Dict, List

      class DataModel:
          """Data model implementation.

          TODO: Implement this class with proper attributes and methods.
          """
          pass
      ```

      ```python
      # src/package_name/submodule/utils.py
      """Utilities module containing helper functions.

      This module will contain:
      - [ ] helper_function utility
      """
      def helper_function() -> None:
          """Helper utility.

          TODO: Implement the helper functionality.
          """
          pass
      ```

      ```python
      # src/package_name/submodule/services.py
      """Services module containing business logic.

      This module will contain:
      - [ ] process_data function
      """
      from typing import Dict, List
      from package_name.submodule.models import DataModel

      def process_data(data: Dict) -> List:
          """Process the data.

          TODO: Implement processing logic.
          """
          pass
      ```

      ```python
      # src/package_name/submodule/resources.py
      """Resources module containing API endpoints.

      This module will contain:
      - [ ] api_endpoint function
      """
      from typing import Dict
      from package_name.submodule.services import process_data

      def api_endpoint() -> Dict:
          """API endpoint handler.

          TODO: Implement endpoint logic.
          """
          pass
      ```

      Update PLAN.md to document implementation decisions:
      ```markdown
      ## Current Status
      - [x] Analysis completed
      - [x] Phase 1: POC (Completed)
      - [x] Phase 2: Setup (Completed)
      - [x] Phase 3: Migration (Initial)
      - [ ] Phase 3: Migration (Implementation)
      - [ ] Phase 4: Integration

      ## Notes
      - Initial placeholder implementations completed
      - Confirmed import structure: models -> services -> resources
      - Decided to use pass with TODO comments to document implementation plans
      - Decision: DataModel will be a fully typed class in the final implementation
      ```

      ### Step 4: Create the __init__.py file for re-exports
      ```python
      # src/package_name/submodule/__init__.py
      """Submodule package exports.

      This module exports:
      - [ ] DataModel from models
      - [ ] process_data from services
      - [ ] api_endpoint from resources
      """
      from package_name.submodule.models import DataModel
      from package_name.submodule.services import process_data
      from package_name.submodule.resources import api_endpoint

      __all__ = ['DataModel', 'process_data', 'api_endpoint']
      ```

      ### Step 5: Update the original module
      ```python
      # src/package_name/large_module.py
      """Original module now importing from submodules.

      This module re-exports:
      - [x] DataModel from submodule.models
      - [x] process_data from submodule.services
      - [x] helper_function from submodule.utils
      - [x] api_endpoint from submodule.resources
      """
      from package_name.submodule import DataModel, process_data, api_endpoint
      from package_name.submodule.utils import helper_function

      # Re-export for backward compatibility
      __all__ = ['DataModel', 'process_data', 'helper_function', 'api_endpoint']
      ```

      Update PLAN.md to reflect progress:
      ```markdown
      ## Current Status
      - [x] Analysis completed
      - [x] Phase 1: POC (Completed)
      - [x] Phase 2: Setup (Completed)
      - [x] Phase 3: Migration (Initial)
      - [ ] Phase 3: Migration (Implementation)
      - [ ] Phase 4: Integration

      ## Notes
      - Migration of all components completed
      - Re-exports established in __init__.py
      - Original module updated to maintain backward compatibility
      - Integration tests pending
      - Next steps: Implement full functionality for each component
      ```

      ### Step 6: Gradually implement each component
      After setting up the structure, go back and implement each component fully, updating the checklist in your scratch pad as you complete each task and regularly updating the PLAN.md file with your progress and decisions.

      Final update to PLAN.md after completion:
      ```markdown
      ## Current Status
      - [x] Analysis completed
      - [x] Phase 1: POC (Completed)
      - [x] Phase 2: Setup (Completed)
      - [x] Phase 3: Migration (Completed)
      - [x] Phase 4: Integration (Initial)
      - [ ] Phase 4: Integration (Testing)

      ## Notes
      - All components have been fully implemented
      - Tests passing for all modules
      - Backward compatibility confirmed
      - Refactoring complete and ready for review

      ## Lessons Learned
      - Models should be defined early as they are dependencies for other components
      - Type hints are essential for ensuring correct integration
      - Pseudocode approach made it easy to see the overall structure before diving into details
      - Incremental approach allowed for regular testing and validation
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
      Let's refactor this into a cleaner structure. I'll walk you through the complete process:

      ### Step 1: Create a scratch pad and plan

      First, add a refactoring plan to the top of your file:

      ```python
      """Refactoring Plan for big_module.py:
      - [ ] Create directory structure
      - [ ] Create __init__.py files
      - [ ] Extract UserModel to models.py
      - [ ] Extract process_user to services.py
      - [ ] Extract api_endpoint to resources.py
      - [ ] Set up exports in __init__.py
      - [ ] Update big_module.py to re-export
      - [ ] Verify functionality
      """

      # Rest of big_module.py continues...
      ```

      Next, create a PLAN.md file with high-level implementation details:

      ```bash
      # Create the PLAN.md file
      touch PLAN.md
      ```

      ```markdown
      # Refactoring Plan for big_module.py

      ## Overview
      This document outlines the plan for refactoring big_module.py into a modular structure.

      ## Goals
      - Break down the monolithic module into smaller components
      - Create a clear separation of concerns
      - Improve maintainability and testability
      - Maintain backward compatibility

      ## Architecture Changes
      - Create a promptlib package with specialized modules:
        - models.py: Will contain UserModel
        - services.py: Will contain process_user
        - resources.py: Will contain api_endpoint

      ## Implementation Phases
      1. **Setup Phase**
         - Create directory structure
         - Initialize files

      2. **Migration Phase**
         - Move each component to its appropriate file
         - Add proper typing and docstrings

      3. **Integration Phase**
         - Set up exports in __init__.py
         - Update original file for backward compatibility
         - Test functionality

      ## Current Status
      - [x] Analysis completed
      - [ ] Phase 1: Setup (In Progress)
      - [ ] Phase 2: Migration
      - [ ] Phase 3: Integration

      ## Notes
      - UserModel is used by process_user and api_endpoint
      - Need to ensure consistent return types across all functions
      ```

      ### Step 2: Create the directory structure

      ```bash
      # Create the directory structure
      mkdir -p src/codegen_lab/promptlib || true

      # Initialize files
      touch src/codegen_lab/__init__.py
      touch src/codegen_lab/promptlib/__init__.py
      touch src/codegen_lab/promptlib/models.py
      touch src/codegen_lab/promptlib/services.py
      touch src/codegen_lab/promptlib/resources.py
      ```

      Update the PLAN.md to reflect progress:

      ```markdown
      ## Current Status
      - [x] Analysis completed
      - [x] Phase 1: Setup (Completed)
      - [ ] Phase 2: Migration (In Progress)
      - [ ] Phase 3: Integration

      ## Notes
      - Directory structure created
      - Empty files initialized
      - Ready to begin component migration
      ```

      ### Step 3: Set up files with pseudocode and docstrings

      ```python
      # src/codegen_lab/promptlib/models.py
      """Models for the promptlib module.

      This module contains:
      - [ ] UserModel class
      """
      from typing import Dict, Any

      class UserModel:
          """User model implementation.

          TODO: Add proper attributes and methods
          """
          pass
      ```

      ```python
      # src/codegen_lab/promptlib/services.py
      """Services for the promptlib module.

      This module contains:
      - [ ] process_user function
      """
      from typing import Dict, Any
      from codegen_lab.promptlib.models import UserModel

      def process_user(user: UserModel) -> Dict[str, Any]:
          """Process the user data.

          TODO: Implement user processing logic
          """
          pass
      ```

      ```python
      # src/codegen_lab/promptlib/resources.py
      """Resources for the promptlib module.

      This module contains:
      - [ ] api_endpoint function
      """
      from typing import Dict, Any
      from codegen_lab.promptlib.models import UserModel
      from codegen_lab.promptlib.services import process_user

      def api_endpoint() -> Dict[str, Any]:
          """API endpoint handler.

          TODO: Implement API endpoint logic
          """
          pass
      ```

      Update PLAN.md to document implementation decisions:

      ```markdown
      ## Current Status
      - [x] Analysis completed
      - [x] Phase 1: Setup (Completed)
      - [x] Phase 2: Migration (Initial)
      - [ ] Phase 2: Migration (Implementation)
      - [ ] Phase 3: Integration

      ## Notes
      - Added type hints to all functions (Dict[str, Any] for return types)
      - Created pseudocode implementations with TODO comments
      - Established import relationships between modules
      - Decision: UserModel will need proper attributes in the final implementation
      ```

      ### Step 4: Set up the package exports

      ```python
      # src/codegen_lab/promptlib/__init__.py
      """Promptlib module exports.

      This module exports:
      - [ ] UserModel from models
      - [ ] process_user from services
      - [ ] api_endpoint from resources
      """
      from codegen_lab.promptlib.models import UserModel
      from codegen_lab.promptlib.services import process_user
      from codegen_lab.promptlib.resources import api_endpoint

      __all__ = ['UserModel', 'process_user', 'api_endpoint']
      ```

      ### Step 5: Update the original module

      ```python
      # src/codegen_lab/big_module.py
      """Original module now re-exporting from submodules.

      This module re-exports:
      - [x] UserModel from promptlib.models
      - [x] process_user from promptlib.services
      - [x] api_endpoint from promptlib.resources
      """
      from codegen_lab.promptlib import UserModel, process_user, api_endpoint

      # Re-export for backward compatibility
      __all__ = ['UserModel', 'process_user', 'api_endpoint']
      ```

      Update PLAN.md to reflect progress:

      ```markdown
      ## Current Status
      - [x] Analysis completed
      - [x] Phase 1: Setup (Completed)
      - [x] Phase 2: Migration (Completed)
      - [x] Phase 3: Integration (Initial)
      - [ ] Phase 3: Integration (Testing)

      ## Notes
      - All components have been migrated to their respective files
      - Package exports configured in __init__.py
      - Original module updated to maintain backward compatibility
      - Next steps: Implement full functionality and test
      ```

      ### Step 6: Implement the actual functionality

      Now that you have the structure set up, go back and implement each component fully, checking off items in your scratch pad as you complete them. Remember to update the PLAN.md file as you make progress:

      ```markdown
      ## Current Status
      - [x] Analysis completed
      - [x] Phase 1: Setup (Completed)
      - [x] Phase 2: Migration (Completed)
      - [x] Phase 3: Integration (Completed)

      ## Notes
      - Full implementation completed for all components
      - All tests passing
      - Backward compatibility verified
      - Refactoring completed successfully

      ## Lessons Learned
      - Pseudocode approach made development more structured
      - Maintaining the PLAN.md file helped track progress
      - Type hints were essential for ensuring correct integration
      ```

      The refactored directory structure will look like:

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

metadata:
  priority: critical
  version: 2.0
  enforce_tdd: true
  tags:
  - python
  - refactoring
  - code-organization
  - best-practices
  - tdd
  - testing
</rule>
