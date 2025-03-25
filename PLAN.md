# Refactoring Plan for prompt_library.py

## Overview
This document outlines the plan for refactoring the prompt_library.py module into a more modular and maintainable structure. The current file is very large (2791 lines) and mixes multiple concerns including data models, utilities, API endpoints, and business logic.

## Goals
- Improve maintainability by breaking down the large file into smaller components
- Separate concerns into appropriate modules
- Ensure backward compatibility
- Maintain test coverage
- Create a working POC without losing functionality
- Improve code organization and readability
- Make future extensions easier

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

## Architecture Changes

We'll refactor the code into the following modules:

```
src/codegen_lab/prompt_library/
├── __init__.py           # Exports for backward compatibility
├── models.py             # Data structures and TypedDict classes
├── utils.py              # Helper functions and utilities for cursor rules
├── resources.py          # MCP resources (endpoints) for cursor rules
├── tools.py              # MCP tools for cursor rule operations
├── prompts.py            # MCP prompts for cursor rule generation
└── workflows.py          # Functions for executing cursor rule workflows
```

## Implementation Phases

### 1. POC Phase (Create Structure with Essential Re-exports)
- ✅ Create directory structure and empty files with docstrings
- ✅ Set up `__init__.py` to re-export all functionality from original file
- ✅ Add type hints and docstrings to all module files
- ✅ Verify original functionality is preserved via re-exports

### 2. Migration Phase - Core Models and Utilities
- [ ] Move data models to `models.py`
- [ ] Move utility functions to `utils.py`
- [ ] Update imports between these modules
- [ ] Verify functionality via manual tests or existing tests

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

### Deployment Timeline

| Phase | Description | Testing | Deployment Environment | Rollback Method |
|-------|-------------|---------|------------------------|-----------------|
| Phase 1 | POC with re-exports | Smoke tests | Development only | Revert code changes |
| Phase 2 | Core Models & Utils | Unit tests | Development only | Revert code changes |
| Phase 3 | Resources, Tools & Prompts | Integration tests | Test environment | Toggle feature flag |
| Phase 4 | Workflows | System tests | Staging environment | Toggle feature flag |
| Phase 5 | Complete Integration | Full test suite | Production | Toggle feature flag, then gradual adoption |

## Current Status
- [x] Phase 1: POC (Completed)
- [ ] Phase 2: Migration - Models & Utils (Not Started)
- [ ] Phase 3: Migration - Resources, Tools & Prompts (Not Started)
- [ ] Phase 4: Migration - Workflows (Not Started)
- [ ] Phase 5: Integration (Not Started)

## Phase 1 Implementation Details

For Phase 1, we have created the directory structure and set up the initial module files:

1. Created the `src/codegen_lab/prompt_library/` directory
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

Next steps: Begin implementing Phase 2 by moving the actual implementations of data models and utility functions to their respective modules.

## Testing Strategy
1. Ensure all existing tests pass after each phase
2. Write additional tests for new modules if needed
3. Create comparison tests to verify behavior equivalence before and after refactoring
4. Manually test the MCP server functionality

## Notes
- The FastMCP server instance (mcp) is defined at the top level, so we need to ensure it continues to work properly
- Path constants like CURSOR_RULES_DIR will need to be moved to utils.py
- Type hints and docstrings must be preserved during refactoring

## Success Criteria
- All existing functionality works without modifications to client code
- Code is more modular and easier to maintain
- File sizes are reduced to reasonable lengths
- Type hints and docstrings are preserved or improved
- Tests pass without modification
