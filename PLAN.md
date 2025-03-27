<project>
<overview>
# Refactoring Plan for ./src/codegen_lab/prompt_library.py

## Overview
This document outlines the plan for refactoring the prompt_library.py module into a more modular and maintainable structure. The current file is very large (2791 lines) and mixes multiple concerns including data models, utilities, API endpoints, and business logic.
</overview>

<goals>
## Goals
- You are a TDD Master, so you will run tests and ensure tests pass before going to the next subtask or story.
- Improve maintainability by breaking down the large file into smaller components
- Separate concerns into appropriate modules
- Ensure backward compatibility
- Maintain test coverage
- Create a working POC without losing functionality
- Improve code organization and readability
- Make future extensions easier
</goals>

<analysis>
## Current Code Analysis

### Main Components Identified
1. **Data Models**: Multiple TypedDict classes for cursor rules and their components
2. **Utility Functions**: Functions for accessing and manipulating cursor rules
3. **Resource Endpoints**: MCP resources for exposing cursor rules
4. **Tool Functions**: MCP tools for various cursor rule operations
5. **Prompt Functions**: MCP prompts for cursor rule generation
6. **Workflow Functions**: Functions for executing phases of cursor rule workflows

### Dependencies
- The resource endpoints depend on the utility functions
- The tool functions depend on the utility functions
- The workflow functions depend on the tool functions
- The prompt functions depend on the utility functions
- Most functions depend on the data models
</analysis>

<architecture>
## Architecture Changes

We'll refactor the code into the following modules:

```
src/codegen_lab/promptlib/
├── __init__.py           # Exports for backward compatibility
├── models.py             # Data structures and TypedDict classes
├── utils.py              # Helper functions and utilities for cursor rules
├── resources.py          # MCP resources (endpoints) for cursor rules
├── tools.py              # MCP tools for cursor rule operations
├── prompts.py            # MCP prompts for cursor rule generation
└── workflows.py          # Functions for executing cursor rule workflows
```
</architecture>

<implementation_phases>
## Implementation Phases

### 1. POC Phase (Create Structure with Essential Re-exports)
- ✅ Create directory structure and empty files with docstrings
- ✅ Set up `__init__.py` to re-export all functionality from original file
- ✅ Add type hints and docstrings to all module files
- ✅ Verify original functionality is preserved via re-exports

### 2. Migration Phase - Core Models and Utilities
- [x] Move data models to `models.py`
- [x] Move utility functions to `utils.py`
- [x] Update imports between these modules
- [x] Verify functionality via manual tests or existing tests

### 3. Migration Phase - MCP Resources, Tools, and Prompts
- [ ] Move resource endpoints to `resources.py`
- [ ] Move tool functions to `tools.py`
- [ ] Move prompt functions to `prompts.py`
- [ ] Update imports to use newly migrated modules
- [ ] Verify MCP server functionality

### 4. Migration Phase - Workflows
- [ ] Move workflow functions to `workflows.py`
- [ ] Update imports to use previously migrated modules
- [ ] Verify workflow functionality

### 5. Integration Phase
- [ ] Update main `__init__.py` to provide backward compatibility
- [ ] Refactor the original `prompt_library.py` to import and re-export from new modules
- [ ] Run full test suite
- [ ] Verify all functionality is preserved
</implementation_phases>

<file_structure>
## File Structure Details

### models.py
- `CursorRuleMetadata`
- `CursorRuleExample`
- `CursorRuleFilter`
- `CursorRuleAction`
- `CursorRule`

### utils.py
- `get_cursor_rule_files`
- `get_cursor_rule_names`
- `read_cursor_rule`
- `parse_cursor_rule`
- `generate_cursor_rule`

### resources.py
- `list_cursor_rules`
- `get_cursor_rule`
- `get_cursor_rule_raw`

### tools.py
- `instruct_repo_analysis`
- `instruct_custom_repo_rules_generation`
- `get_static_cursor_rule`
- `get_static_cursor_rules`
- `save_cursor_rule`
- `recommend_cursor_rules`
- `prep_workspace`
- `create_cursor_rule_files`
- `ensure_makefile_task`
- `ensure_ai_report`
- `run_update_cursor_rules`
- `update_dockerignore`
- `cursor_rules_workflow`

### prompts.py
- `repo_analysis_prompt`
- `generate_cursor_rule_prompt`

### workflows.py
- `plan_and_execute_prompt_library_workflow`
- `execute_phase_1`
- `execute_phase_2`
- `execute_phase_3`
- `execute_phase_4`
- `execute_phase_5`
</file_structure>

<dependency_strategy>
## Strategy for Handling Circular Dependencies

Potential circular dependencies are a common issue in refactoring monolithic code. We'll use the following strategies to prevent and resolve them:

1. **Dependency Analysis First**:
   - Before actual code migration, map out the complete dependency graph of functions/classes
   - Identify potential circular import risks (e.g., if tools.py and workflows.py might import each other)

2. **Forward References**:
   - Use string-based type annotations for forward references: `def function(param: "TypeFromAnotherModule")`
   - Leverage `from __future__ import annotations` where appropriate
   - Use `if TYPE_CHECKING:` blocks for import statements only needed for type checking

3. **Interface Segregation**:
   - Create minimal interfaces in models.py that other modules can depend on
   - Move implementation details to appropriate modules

4. **Dependency Inversion**:
   - Where circular dependencies are unavoidable, refactor to depend on abstractions
   - Consider using dependency injection patterns for complex interactions

5. **Strategic Re-exports**:
   - Use __init__.py to re-export symbols that might cause circular dependencies
   - Example: If module A needs a function from module B, but B imports A, move the function to __init__.py

6. **Migration Order Optimization**:
   - Start with modules that have the fewest outgoing dependencies (models.py, utils.py)
   - Gradually move to more complex modules (resources.py, tools.py)
   - Leave modules with the most dependencies for last (workflows.py)


For each module being refactored, we'll:
1. Document suspected circular dependencies in a comment at the top of the file
2. Apply the appropriate strategy from above
3. Verify imports work correctly after each module is migrated
</dependency_strategy>

<deployment_plan>
## Incremental Deployment Plan

To minimize disruption and ensure the system remains functional throughout refactoring, we'll implement an incremental deployment approach:

### Phase-by-Phase Deployment

1. **Parallel Implementation**:
   - Keep the original prompt_library.py file intact and functional during development
   - Create the new modular structure in parallel
   - Implement thorough behavior equivalence tests before switching

2. **Feature Flags**:
   - Add a feature flag to control whether to use the original monolithic module or the refactored version
   - Example: `USE_REFACTORED_PROMPT_LIBRARY=True` in environment variables or config

3. **Gradual Transition Strategy**:
   - After completing Phase 1 (POC): Deploy with re-exports only, validate zero behavior change
   - After Phase 2 (Models & Utils): Run automated tests with new modules, but keep using original file in production
   - After Phase 3 (Resources, Tools & Prompts): Enable the feature flag in a test environment
   - After Phase 4 (Workflows): Enable the feature flag in a staging environment
   - After Phase 5 (Integration): Switch to refactored version in production

4. **Rollback Plan**:
   - At each deployment step, maintain ability to switch back to original implementation
   - Document exact steps for reverting to previous version
   - Ensure database/state compatibility between original and refactored versions

5. **Verification Checkpoints**:
   - Before each phase deployment: Run full test suite against refactored code
   - After each phase deployment: Monitor logs for errors and unexpected behavior
   - Define specific metrics to confirm successful deployment (e.g., error rates, response times)

6. **Communication Plan**:
   - Inform team members about the refactoring schedule
   - Document API stability guarantees during transition
   - Provide regular status updates at each deployment phase

7. **Post-Deployment Validation**:
   - Run comprehensive comparison tests in production environment
   - Verify logs show expected behavior
   - Check all integrations are functioning as expected
</deployment_plan>

<deployment_timeline>
### Deployment Timeline

| Phase | Description | Testing | Deployment Environment | Rollback Method |
|-------|-------------|---------|------------------------|-----------------|
| Phase 1 | POC with re-exports | Smoke tests | Development only | Revert code changes |
| Phase 2 | Core Models & Utils | Unit tests | Development only | Revert code changes |
| Phase 3 | Resources, Tools & Prompts | Integration tests | Test environment | Toggle feature flag |
| Phase 4 | Workflows | System tests | Staging environment | Toggle feature flag |
| Phase 5 | Complete Integration | Full test suite | Production | Toggle feature flag, then gradual adoption |
</deployment_timeline>

<testing_strategy>
## Testing Strategy

### Test Structure
- All test files will follow the pytest convention and be located in `tests/` directory
- Test files will mirror the module structure:
  ```
  tests/
  ├── __init__.py
  ├── conftest.py              # Shared fixtures
  ├── test_models.py          # Tests for models.py
  ├── test_utils.py           # Tests for utils.py
  ├── test_resources.py       # Tests for resources.py
  ├── test_tools.py           # Tests for tools.py
  ├── test_prompts.py         # Tests for prompts.py
  └── test_workflows.py       # Tests for workflows.py
  ```

### Test Types
1. **Unit Tests**
   - Test each component in isolation
   - Mock external dependencies
   - Focus on edge cases and error handling
   - Include type checking tests

2. **Integration Tests**
   - Test interactions between modules
   - Test MCP server integration
   - Test file system operations
   - Test actual cursor rule parsing/generation

3. **Behavior Equivalence Tests**
   - Compare output of refactored code with original
   - Ensure no functionality is lost
   - Run against real cursor rule examples

### Test Fixtures
```python
# conftest.py
import pytest
from typing import TYPE_CHECKING, Dict, Any

if TYPE_CHECKING:
    from pytest_mock import MockerFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture

@pytest.fixture
def sample_cursor_rule() -> Dict[str, Any]:
    """Provide a sample cursor rule for testing."""
    return {
        "name": "test-rule",
        "description": "Test rule for testing",
        "filters": [],
        "actions": []
    }

@pytest.fixture
def mcp_server():
    """Provide a configured MCP server for testing."""
    from mcp.server.fastmcp import FastMCP
    return FastMCP()
```

### Test Examples
```python
# test_models.py
import pytest
from typing import TYPE_CHECKING
from codegen_lab.promptlib.models import CursorRule

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

def test_cursor_rule_validation(sample_cursor_rule: dict):
    """Test cursor rule validation logic."""
    rule = CursorRule(**sample_cursor_rule)
    assert rule.name == "test-rule"
    assert rule.description == "Test rule for testing"

# test_resources.py
@pytest.mark.anyio
async def test_list_cursor_rules(
    mcp_server,
    mocker: MockerFixture
):
    """Test the list_cursor_rules endpoint."""
    result = await mcp_server.call_tool(
        "list_cursor_rules",
        {}
    )
    assert not result.isError
    assert isinstance(result.content, list)
```

### Test Coverage Requirements
- Minimum 90% code coverage for all modules
- 100% coverage for critical paths:
  - Cursor rule parsing
  - MCP tool execution
  - File system operations

### Test Execution
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_models.py

# Run with coverage
uv run pytest --cov=codegen_lab

# Run with verbose output and local variables
uv run pytest -s --verbose --showlocals --tb=short tests/test_models.py::test_cursor_rule_validation
```

### Continuous Integration
- All tests must pass before merging
- Coverage reports generated on each PR
- Integration tests run in CI environment
- Performance benchmarks for critical operations
</testing_strategy>

<poc_development>
## POC Development Strategy

### Initial POC Setup
1. **Create Minimal Working Structure**
   ```bash
   # Create directory structure
   mkdir -p src/codegen_lab/promptlib || true
   touch src/codegen_lab/promptlib/__init__.py
   ```

2. **Setup Initial Re-exports**
   ```python
   # src/codegen_lab/promptlib/__init__.py
   """
   Prompt Library Module - POC Implementation

   This module provides a backward-compatible interface while
   the refactoring is in progress. It re-exports all functionality
   from the original prompt_library.py module.
   """
   from typing import TYPE_CHECKING
   from ..prompt_library import (
       CursorRule,
       CursorRuleMetadata,
       get_cursor_rule_files,
       get_cursor_rule_names,
       # ... other exports
   )

   if TYPE_CHECKING:
       from typing import List, Dict, Any
   ```

### POC Testing Strategy
1. **Create Equivalence Tests**
   ```python
   # tests/test_equivalence.py
   """Test suite for verifying behavior equivalence during refactoring."""
   import pytest
   from typing import TYPE_CHECKING, Dict, Any

   if TYPE_CHECKING:
       from pytest_mock import MockerFixture

   def test_cursor_rule_equivalence():
       """Verify refactored cursor rule handling matches original."""
       from codegen_lab.prompt_library import get_cursor_rule
       from codegen_lab.promptlib.utils import get_cursor_rule as new_get_cursor_rule

       rule_name = "test-rule"

       # Get results from both implementations
       original_result = get_cursor_rule(rule_name)
       refactored_result = new_get_cursor_rule(rule_name)

       # Compare results
       assert original_result == refactored_result

   @pytest.mark.anyio
   async def test_mcp_tool_equivalence(
       mcp_server,
       mocker: MockerFixture
   ):
       """Verify refactored MCP tools match original behavior."""
       # Test with original implementation
       original_result = await mcp_server.call_tool(
           "list_cursor_rules",
           {}
       )

       # Test with refactored implementation
       refactored_result = await mcp_server.call_tool(
           "list_cursor_rules_new",
           {}
       )

       # Compare results
       assert original_result.content == refactored_result.content
   ```

2. **Implement Verification Tests**
   ```python
   # tests/test_verification.py
   """Test suite for verifying critical functionality during refactoring."""
   import pytest
   from typing import TYPE_CHECKING

   if TYPE_CHECKING:
       from pytest_mock import MockerFixture

   def test_imports_work():
       """Verify all re-exports are working."""
       from codegen_lab.promptlib import (
           CursorRule,
           get_cursor_rule_files,
           get_cursor_rule_names
       )
       assert CursorRule is not None
       assert get_cursor_rule_files is not None
       assert get_cursor_rule_names is not None

   def test_type_checking():
       """Verify type hints are working correctly."""
       from codegen_lab.promptlib.models import CursorRule

       rule = CursorRule(
           name="test",
           description="test rule",
           filters=[],
           actions=[]
       )
       assert isinstance(rule.name, str)
       assert isinstance(rule.filters, list)
   ```

### POC Validation Steps
1. **Functionality Verification**
   ```bash
   # Run equivalence tests
   uv run pytest tests/test_equivalence.py

   # Run verification tests
   uv run pytest tests/test_verification.py

   # Run type checking
   uv run mypy src/codegen_lab/promptlib/
   ```

2. **Performance Benchmarking**
   ```python
   # tests/test_performance.py
   """Performance benchmarks for critical operations."""
   import pytest
   import time
   from typing import TYPE_CHECKING

   if TYPE_CHECKING:
       from pytest_mock import MockerFixture

   def test_cursor_rule_parsing_performance():
       """Benchmark cursor rule parsing performance."""
       from codegen_lab.prompt_library import parse_cursor_rule
       from codegen_lab.promptlib.utils import parse_cursor_rule as new_parse_cursor_rule

       rule_content = "..."  # Sample rule content

       # Benchmark original implementation
       start = time.time()
       original_result = parse_cursor_rule(rule_content)
       original_time = time.time() - start

       # Benchmark refactored implementation
       start = time.time()
       refactored_result = new_parse_cursor_rule(rule_content)
       refactored_time = time.time() - start

       # Verify refactored version is not significantly slower
       assert refactored_time <= original_time * 1.1  # Allow 10% overhead
   ```

### POC Deployment Checklist
- [ ] Directory structure created
- [ ] Re-exports implemented in __init__.py
- [ ] Equivalence tests passing
- [ ] Verification tests passing
- [ ] Type checking passing
- [ ] Performance benchmarks within acceptable range
- [ ] No regressions in existing functionality
- [ ] Documentation updated to reflect POC status
</poc_development>

<quality_assurance>
## Quality Assurance

### Code Quality Standards
1. **Type Hints**
   - All functions must have complete type hints
   - Use `typing` module for complex types
   - Enable strict mypy checking
   ```python
   from typing import Dict, List, Optional, TypedDict, Union

   def process_rule(rule: Dict[str, Any]) -> Optional[CursorRule]:
       """Process a cursor rule dictionary into a CursorRule object."""
   ```

2. **Documentation**
   - All modules must have docstrings
   - All public functions must have docstrings
   - Use reStructuredText format
   ```python
   def parse_cursor_rule(content: str) -> CursorRule:
       """Parse cursor rule content into a CursorRule object.

       Args:
           content: Raw cursor rule content as string

       Returns:
           CursorRule object representing the parsed rule

       Raises:
           ValueError: If the rule content is invalid
       """
   ```

3. **Code Style**
   - Follow PEP 8 guidelines
   - Use ruff for linting
   - Maximum line length of 88 characters
   - Use consistent import ordering
   ```bash
   # Run style checks
   uv run ruff check .
   uv run ruff format .
   ```

4. **Error Handling**
   - Use custom exceptions for domain-specific errors
   - Provide detailed error messages
   - Include context in exceptions
   ```python
   class CursorRuleError(Exception):
       """Base exception for cursor rule operations."""

   class CursorRuleParseError(CursorRuleError):
       """Raised when parsing a cursor rule fails."""
       def __init__(self, message: str, line_number: int):
           self.line_number = line_number
           super().__init__(f"Parse error at line {line_number}: {message}")
   ```

### Quality Gates
1. **Pre-commit Checks**
   ```bash
   # Run before committing changes
   uv run ruff check .
   uv run ruff format .
   uv run mypy .
   uv run pytest
   ```

2. **Continuous Integration**
   ```yaml
   # .github/workflows/quality.yml
   name: Quality Checks
   on: [push, pull_request]
   jobs:
     quality:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - name: Set up Python
           uses: actions/setup-python@v2
         - name: Install dependencies
           run: |
             python -m pip install uv
             uv pip install -r requirements.txt
         - name: Run style checks
           run: |
             uv run ruff check .
             uv run ruff format --check .
         - name: Run type checks
           run: uv run mypy .
         - name: Run tests
           run: uv run pytest
   ```

3. **Code Review Checklist**
   - [ ] All tests pass
   - [ ] Type hints are complete
   - [ ] Documentation is updated
   - [ ] No style violations
   - [ ] Error handling is appropriate
   - [ ] Performance impact is acceptable
   - [ ] Backward compatibility maintained

### Monitoring and Metrics
1. **Test Coverage**
   ```bash
   # Generate coverage report
   uv run pytest --cov=codegen_lab --cov-report=html
   ```

2. **Performance Metrics**
   - Track execution time of critical operations
   - Monitor memory usage
   - Compare with baseline metrics

3. **Error Tracking**
   - Log all exceptions
   - Track error rates
   - Monitor for new error types

### Documentation Requirements
1. **API Documentation**
   - Document all public interfaces
   - Include usage examples
   - Document type hints

2. **Architecture Documentation**
   - Document module dependencies
   - Explain design decisions
   - Provide component diagrams

3. **Migration Guide**
   - Document breaking changes
   - Provide upgrade instructions
   - Include compatibility notes
</quality_assurance>

<current_status>
## Current Status
- [x] Phase 1: POC (Completed)
  - [x] Created directory structure
  - [x] Implemented re-exports
  - [x] Added equivalence tests
  - [x] Added verification tests
  - [x] Added performance benchmarks
  - [x] Verified functionality preservation
  - [x] Created test_poc_exports.py (empty, ready for implementation)
- [x] Phase 2: Migration - Models & Utils (Completed)
  - [x] Migrated all data models to models.py
  - [x] Migrated utility functions to utils.py
  - [x] Implemented full parse_cursor_rule function
  - [x] Implemented full generate_cursor_rule function
  - [x] Updated imports between modules
  - [x] Created test_promptlib_models.py (4.5KB, 153 lines)
  - [x] Created test_promptlib_utils.py (5.5KB, 185 lines)
- [ ] Phase 3: Migration - Resources, Tools & Prompts (In Progress)
  - [x] Created detailed migration plans for all Phase 3 files:
    - [x] Added migration plan for resources.py
    - [x] Added migration plan for tools.py
    - [x] Added migration plan for prompts.py
  - [x] Implement resource endpoints in resources.py
    - [x] list_cursor_rules
    - [x] Created test_promptlib_resources.py (5.9KB, 203 lines)
  - [x] Implement tools in tools.py
    - [x] Created test_promptlib_tools.py (8.1KB, 278 lines)
  - [x] Implement prompts in prompts.py
    - [x] Created test_promptlib_prompts.py (6.7KB, 219 lines)
  - [ ] Update imports and dependencies
- [ ] Phase 4: Migration - Workflows
  - [x] Created test_promptlib_workflows.py (9.4KB, 295 lines)
  - [ ] Move workflow functions to workflows.py
  - [ ] Update imports to use new modules
  - [ ] Verify workflow functionality
- [ ] Phase 5: Integration
  - [ ] Update main __init__.py
  - [ ] Refactor prompt_library.py
  - [ ] Run full test suite
  - [ ] Verify all functionality

### Test Suite Status
- [x] test_promptlib_tools.py (8.1KB, 278 lines) - Implemented
- [x] test_promptlib_utils.py (5.5KB, 185 lines) - Implemented
- [x] test_promptlib_workflows.py (9.4KB, 295 lines) - Implemented
- [x] test_promptlib_prompts.py (6.7KB, 219 lines) - Implemented
- [x] test_promptlib_resources.py (5.9KB, 203 lines) - Implemented
- [x] test_promptlib_models.py (4.5KB, 153 lines) - Implemented
- [ ] test_poc_exports.py (empty) - Ready for implementation

### Next Steps
1. Complete Phase 3 implementation:
   - [ ] Finish updating imports and dependencies
   - [ ] Verify all tests pass after import updates
2. Begin Phase 4 implementation:
   - [ ] Implement workflow functions in workflows.py
   - [ ] Verify workflow tests pass
3. Update documentation:
   - [ ] Add API documentation for completed modules
   - [ ] Update architecture diagrams
   - [ ] Begin migration guide
4. Implement test_poc_exports.py:
   - [ ] Add tests to verify re-exports
   - [ ] Verify backward compatibility
   - [ ] Add performance comparison tests
</current_status>

<phase1_details>
## Phase 1 Implementation Details

For Phase 1, we have created the directory structure and set up the initial module files:

1. Created the `src/codegen_lab/promptlib/` directory
2. Created the following files with appropriate docstrings and type hints:
   - `__init__.py`: Re-exports all functionality from the original file
   - `models.py`: Contains TypedDict class definitions for cursor rule components
   - `utils.py`: Contains utility functions for working with cursor rules
   - `resources.py`: Contains MCP resource endpoints for cursor rules
   - `tools.py`: Contains MCP tool functions for cursor rule operations
   - `prompts.py`: Contains MCP prompt functions for cursor rule generation
   - `workflows.py`: Contains workflow functions for executing cursor rule tasks

3. Used the following strategies to handle circular dependencies:
   - Added `from __future__ import annotations` to all files
   - Used `if TYPE_CHECKING:` blocks for type checking imports
   - Used string-based type annotations for forward references
   - Set up re-exports through `__init__.py`

4. Current implementation still relies on the original file for actual functionality:
   - Each function contains a placeholder that imports and calls the original implementation
   - This ensures that the refactored code is functionally equivalent to the original
</phase1_details>

<phase2_details>
## Phase 2 Implementation Details

For Phase 2, we will focus on migrating the core data models and utility functions. This phase is critical as these components form the foundation that other modules will build upon.

### Step 1: Data Models Migration

1. **Preparation**:
   - Create a scratch pad at the top of models.py:
   ```python
   """Migration Plan for models.py:
   - [ ] Import all required typing modules
   - [ ] Move CursorRuleMetadata TypedDict
   - [ ] Move CursorRuleExample TypedDict
   - [ ] Move CursorRuleFilter TypedDict
   - [ ] Move CursorRuleAction TypedDict
   - [ ] Move CursorRule TypedDict
   - [ ] Add proper docstrings and type hints
   - [ ] Add validation functions if needed
   - [ ] Update imports in __init__.py
   - [ ] Verify type checking passes
   """
   ```

2. **Implementation Order**:
   - Start with base types that have no dependencies
   - Move to more complex types that depend on the base types
   - Add any missing type hints or documentation
   - Implement any necessary validation logic

3. **Type Safety**:
   - Use literal types where appropriate
   - Add runtime type checking where needed
   - Include proper TypeVar definitions
   - Add type guards if necessary

### Step 2: Utility Functions Migration

1. **Preparation**:
   - Create a scratch pad at the top of utils.py:
   ```python
   """Migration Plan for utils.py:
   - [ ] Import all required dependencies
   - [ ] Move get_cursor_rule_files function
   - [ ] Move get_cursor_rule_names function
   - [ ] Move read_cursor_rule function
   - [ ] Move parse_cursor_rule function
   - [ ] Move generate_cursor_rule function
   - [ ] Add proper error handling
   - [ ] Add logging
   - [ ] Update type hints
   - [ ] Add/update docstrings
   - [ ] Add unit tests
   """
   ```

2. **Implementation Order**:
   - Start with file system operations (get_cursor_rule_files, get_cursor_rule_names)
   - Move to parsing functions (read_cursor_rule, parse_cursor_rule)
   - Finally, implement generation functions (generate_cursor_rule)
   - Add comprehensive error handling and logging

3. **Error Handling**:
   - Create custom exception classes if needed
   - Add proper error messages and logging
   - Implement graceful fallbacks where appropriate
   - Add retry logic for file system operations
</phase2_details>

<testing_strategy>
### Step 3: Testing Strategy

1. **Unit Tests**:
   - Create test_models.py:
   ```python
   """Test Plan for models.py:
   - [ ] Test CursorRuleMetadata validation
   - [ ] Test CursorRuleExample validation
   - [ ] Test CursorRuleFilter validation
   - [ ] Test CursorRuleAction validation
   - [ ] Test CursorRule validation
   - [ ] Test edge cases and error conditions
   """
   ```

   - Create test_utils.py:
   ```python
   """Test Plan for utils.py:
   - [ ] Test get_cursor_rule_files with various paths
   - [ ] Test get_cursor_rule_names with different rule sets
   - [ ] Test read_cursor_rule with valid/invalid files
   - [ ] Test parse_cursor_rule with various formats
   - [ ] Test generate_cursor_rule with different inputs
   - [ ] Test error handling and edge cases
   """
   ```

2. **Integration Tests**:
   - Test interaction between models and utils
   - Verify file system operations work correctly
   - Test with actual cursor rule files
   - Verify backward compatibility
</testing_strategy>

<documentation>
### Step 4: Documentation

1. **API Documentation**:
   - Document all public functions and classes
   - Include usage examples in docstrings
   - Add type information to docstrings
   - Document error conditions and handling

2. **Internal Documentation**:
   - Add implementation notes where needed
   - Document any non-obvious design decisions
   - Include references to relevant issues/PRs
   - Document performance considerations
</documentation>

<verification>
### Step 5: Verification

1. **Type Checking**:
   ```bash
   # Run type checking on new modules
   uv run mypy src/codegen_lab/promptlib/models.py
   uv run mypy src/codegen_lab/promptlib/utils.py
   ```

2. **Linting**:
   ```bash
   # Run linting on new modules
   uv run ruff check src/codegen_lab/promptlib/models.py
   uv run ruff check src/codegen_lab/promptlib/utils.py
   ```

3. **Testing**:
   ```bash
   # Run tests for new modules
   uv run pytest tests/test_models.py -v
   uv run pytest tests/test_utils.py -v
   ```
</verification>

<integration>
### Step 6: Integration

1. **Update Imports**:
   - Update __init__.py to use new modules
   - Verify no circular dependencies
   - Check all re-exports work correctly

2. **Verification**:
   - Run full test suite
   - Check type checking passes
   - Verify linting passes
   - Manual testing of key functionality
</integration>

<success_criteria>
### Success Criteria

Phase 2 will be considered complete when:
1. All data models are properly migrated with full type safety
2. All utility functions are migrated with proper error handling
3. All tests pass with good coverage
4. Type checking and linting pass
5. Documentation is complete and accurate
6. Backward compatibility is maintained
7. No regressions in existing functionality
</success_criteria>

<next_steps>
### Next Steps After Completion
1. Review and update the migration plan for Phase 3
2. Document any lessons learned
3. Update project documentation
4. Plan the deployment of Phase 2 changes
</next_steps>

<prd_analysis>
## PRD Analysis and Implementation Checklist

### Priority Levels
- P0: Must have for MVP
- P1: Important but not blocking MVP
- P2: Nice to have, can be implemented post-MVP
- P3: Future optimization

### Core Infrastructure (P0)
- [ ] Project Structure
  - [ ] Initialize with proper packaging
  - [ ] Set up UV workspace
  - [ ] Configure development tools
  - [ ] Basic documentation structure
  - [ ] Simple logging

- [ ] Basic Service Layer
  - [ ] Simple service container
  - [ ] Basic configuration management
  - [ ] Health check endpoint
  - [ ] Error handling foundation

- [ ] LLM Integration (Basic)
  - [ ] API key management
  - [ ] Simple request/response handling
  - [ ] Basic error handling
  - [ ] Simple caching

- [ ] Data Management (Basic)
  - [ ] Workspace state tracking
  - [ ] Basic file operations
  - [ ] Simple caching layer

### Testing Framework (P0)
- [ ] Basic Test Setup
  - [ ] pytest configuration
  - [ ] Essential fixtures
  - [ ] Basic test utilities
  - [ ] Simple assertions

- [ ] Coverage Tracking
  - [ ] Basic coverage collection
  - [ ] Simple report generation
  - [ ] Coverage threshold checks

### Cursor Integration (P0)
- [ ] Basic IDE Integration
  - [ ] File watching
  - [ ] Command routing
  - [ ] Basic error reporting

- [ ] Rule Processing
  - [ ] MDC file parsing
  - [ ] Basic rule validation
  - [ ] Simple rule caching

### Post-MVP Features (P1)
- [ ] Enhanced Testing
  - [ ] More comprehensive fixtures
  - [ ] Advanced assertions
  - [ ] Test templates
  - [ ] Mock data utilities

- [ ] Advanced Rule Processing
  - [ ] Rule inheritance
  - [ ] Rule composition
  - [ ] Dynamic updates

- [ ] Improved LLM Integration
  - [ ] Rate limiting
  - [ ] Advanced caching
  - [ ] Retry logic
  - [ ] Response optimization

### Future Optimizations (P2)
- [ ] Advanced Features
  - [ ] Automated code review
  - [ ] Enhanced LLM integration
  - [ ] Workflow automation
  - [ ] Plugin system

### Performance Optimizations (P3)
- [ ] Response Time Optimization
  - [ ] LLM response < 2 seconds
  - [ ] Task execution < 500ms
  - [ ] Command validation < 50ms

- [ ] Resource Usage Optimization
  - [ ] Memory < 256MB
  - [ ] CPU < 30% active
  - [ ] Efficient caching

### Implementation Notes and Questions

1. **Scope Clarification Needed**
   - What constitutes "reasonable response times" in MVP phase?
   - Definition of "code quality score" metrics?
   - Specific requirements for "security vulnerability scanning"?

2. **Technical Gaps**
   - Error handling strategy between components
   - Rollback procedures for failed operations
   - Data persistence strategy
   - Cache invalidation policies
   - Integration test strategy

3. **Junior Developer Considerations**
   - Start with basic file operations and pytest setup
   - Defer complex caching and optimization
   - Focus on clear interfaces before implementations
   - Build incrementally with frequent testing
   - Document setup steps thoroughly

4. **Story Sequencing Recommendations**
   - Begin with project structure and basic tools
   - Add simple test framework next
   - Implement basic file operations
   - Add basic LLM integration
   - Then layer in more complex features

5. **Risk Areas**
   - LLM response time variability
   - API key security management
   - Test coverage maintenance
   - Performance requirements in MVP
   - Complex rule interactions
</prd_analysis>

# Test Refactoring Plan

## Overview
This section outlines the plan for breaking down unit tests in the `tests/unit` directory into smaller, more manageable files with a maximum of 150 lines per file.

## Goals
- Improve test maintainability by breaking down large test files
- Keep each test file focused on a specific feature or component
- Maintain a maximum of 150 lines per test file
- Ensure proper test organization and naming conventions
- Preserve all existing test coverage
- Make it easier to locate and update specific tests

## Test Organization Strategy

### Directory Structure
```
tests/
├── unit/                           # Unit tests directory (150 line limit enforced)
│   ├── test_models/               # Tests for data models
│   │   ├── __init__.py
│   │   ├── test_user_model.py
│   │   ├── test_message_model.py
│   │   └── test_rule_model.py
│   ├── test_services/             # Tests for service layer
│   │   ├── __init__.py
│   │   ├── test_auth_service.py
│   │   └── test_message_service.py
│   └── test_utils/                # Tests for utilities
│       ├── __init__.py
│       ├── test_string_utils.py
│       └── test_file_utils.py
├── unittests/                     # Legacy unit tests directory (excluded from 150 line limit)
├── integration/                    # Integration tests
└── conftest.py                    # Shared test fixtures
```

### Scope
1. The 150-line limit applies only to tests in the `tests/unit/` directory
2. The `tests/unittests/` directory is considered legacy code and is excluded from this refactoring
3. New tests should be written in `tests/unit/` following the 150-line limit
4. Legacy tests in `tests/unittests/` will be migrated gradually in future sprints

### File Organization Rules
1. Each test file in `tests/unit/` should focus on a single component or feature
2. Maximum of 150 lines per test file (applies only to `tests/unit/`)
3. Group related tests in subdirectories
4. Use clear, descriptive file names
5. Include __init__.py in each test directory
6. Share fixtures via conftest.py files

### Implementation Steps
1. **Analysis Phase**
   - [ ] Identify all test files in `tests/unit/` over 150 lines
   - [ ] Analyze test groupings and dependencies
   - [ ] Map out new directory structure
   - [ ] Create list of new test files needed
   - [ ] Exclude `tests/unittests/` from analysis

2. **Setup Phase**
   - [ ] Create new test directories under `tests/unit/`
   - [ ] Add __init__.py files
   - [ ] Set up conftest.py files for shared fixtures
   - [ ] Update pytest configuration if needed

3. **Migration Phase**
   - [ ] Move tests to new files based on functionality (only for `tests/unit/`)
   - [ ] Update imports and dependencies
   - [ ] Ensure fixtures are properly shared
   - [ ] Verify all tests still pass

4. **Verification Phase**
   - [ ] Run full test suite
   - [ ] Check coverage reports
   - [ ] Verify no tests were lost
   - [ ] Update documentation
   - [ ] Verify `tests/unittests/` remains unchanged

### Test File Template
```python
"""Unit tests for [component name].

This module contains tests for [specific functionality]
within the [component name] module.
"""
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture

@pytest.fixture
def component_fixture():
    """Create an isolated component instance for testing."""
    return ComponentUnderTest()

def test_specific_functionality(
    component_fixture: ComponentUnderTest,
    mocker: MockerFixture,
) -> None:
    """Test a specific aspect of the component's behavior."""
    # Test implementation
```

### Success Criteria
- All test files are 150 lines or less
- All tests pass after migration
- Coverage remains the same or improves
- Directory structure is clear and logical
- Documentation is updated to reflect new structure
- No duplicate test code or fixtures

### Quality Checks
1. **Before Migration**
   ```bash
   # Get baseline metrics
   uv run pytest --cov=codegen_lab
   ```

2. **After Each File Migration**
   ```bash
   # Run affected tests
   uv run pytest path/to/new/test_file.py -v
   ```

3. **After Complete Migration**
   ```bash
   # Run full test suite
   uv run pytest
   # Check coverage
   uv run pytest --cov=codegen_lab
   # Verify no files exceed line limit
   find tests/unit -name "test_*.py" -exec wc -l {} \; | sort -nr
   ```
</project>
