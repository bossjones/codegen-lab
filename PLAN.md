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

## Current Status
- [ ] Phase 1: POC (Not Started)
- [ ] Phase 2: Migration - Models & Utils (Not Started)
- [ ] Phase 3: Migration - Resources, Tools & Prompts (Not Started)
- [ ] Phase 4: Migration - Workflows (Not Started)
- [ ] Phase 5: Integration (Not Started)

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
