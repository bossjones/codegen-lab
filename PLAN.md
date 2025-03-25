<project>
<overview>
# Refactoring Plan for prompt_library.py

## Overview
This document outlines the plan for refactoring the prompt_library.py module into a more modular and maintainable structure. The current file is very large (2791 lines) and mixes multiple concerns including data models, utilities, API endpoints, and business logic.
</overview>

<goals>
## Goals
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

<current_status>
## Current Status
- [x] Phase 1: POC (Completed)
- [x] Phase 2: Migration - Models & Utils (Completed)
  - [x] Migrated all data models to models.py
  - [x] Migrated utility functions to utils.py
  - [x] Implemented full parse_cursor_rule function
  - [x] Implemented full generate_cursor_rule function
  - [x] Updated imports between modules
- [ ] Phase 3: Migration - Resources, Tools & Prompts (Not Started)
- [ ] Phase 4: Migration - Workflows (Not Started)
- [ ] Phase 5: Integration (Not Started)

## Notes
- Successfully migrated all models and utility functions
- Maintained backward compatibility through re-exports
- Next step is to begin Phase 3: Migration of Resources, Tools & Prompts
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
</project>
