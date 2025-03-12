# MCP Server Remote Compatibility Audit

This document tracks issues related to direct file system operations in MCP tool functions that would be problematic when running the MCP server remotely from the client.

## Issue Summary

When an MCP server runs remotely, it doesn't have access to the client's file system. Functions that perform direct file system operations will fail in a remote setup.

## Functions Requiring Refactoring

### Functions with Direct File Operations

1. **`create_cursor_rule_files`** (in `prompt_library.py`)
   - [x] **Direct File Operations**:
     - ~~Creates directories with `cursor_rules_dir.mkdir(parents=True, exist_ok=True)`~~
     - ~~Creates empty files with `file_path.touch()`~~
     - ~~Reads file content with `makefile_path.read_text()`~~
     - Now returns operation instructions for the client to perform

2. **`ensure_makefile_task`** (in `prompt_library.py`)
   - [x] **Direct File Operations**:
     - ~~Gets current working directory with `Path.cwd()`~~
     - ~~Checks if file exists with `makefile_path.exists()`~~
     - ~~Reads file content with `makefile_path.read_text()`~~
     - ~~Writes to file with `open(makefile_path, "a")` and `f.write()`~~
     - ~~Creates new file with `open(makefile_path, "w")` and `f.write()`~~
     - Now returns operation instructions for checking and updating the Makefile
     - Added improved error handling for invalid file paths and edge cases
     - Enhanced validation of input parameters

3. **`run_update_cursor_rules`** (in `prompt_library.py`)
   - [x] **Direct File Operations**:
     - ~~Gets current working directory with `Path.cwd()`~~
     - ~~Checks if file exists with `makefile_path.exists()`~~
     - ~~Reads file content with `makefile_path.read_text()`~~
     - ~~Executes shell commands with `subprocess.run()`~~
     - ~~Lists directory contents with `cursor_rules_dir.glob("*")`~~
     - Now uses a two-step process with `process_update_cursor_rules_result` to handle operations remotely

4. **`update_dockerignore`** (in `prompt_library.py`)
   - [x] **Direct File Operations**:
     - ~~Gets current working directory with `Path.cwd()`~~
     - ~~Checks if file exists with `dockerignore_path.exists()`~~
     - ~~Reads file content with `dockerignore_path.read_text()`~~
     - ~~Writes to file with `dockerignore_path.write_text()`~~
     - Now returns operation instructions for checking and updating .dockerignore

5. **`execute_phase_4`** (part of `plan_and_execute_prompt_library_workflow` in `prompt_library.py`)
   - [x] **Direct File Operations**:
     - Uses `save_cursor_rule()` which returns file operation instructions
     - No direct file operations performed

### Functions That Return Operation Instructions (Safe for Remote Execution)

1. **`save_cursor_rule`** (in `prompt_library.py`)
   - [x] **Safe Implementation**: Returns a dictionary with file operation instructions instead of performing them directly
   - Returns operations for directory creation and file writing that the client should perform

2. **`prep_workspace`** (in `prompt_library.py`)
   - [x] **Safe Implementation**: Returns instructions for workspace preparation without actually creating directories
   - Sets `workspace_prepared` to `False` to indicate no direct operations were performed

3. **`create_cursor_rule_files`** (in `prompt_library.py`)
   - [x] **Safe Implementation**: Returns a dictionary with file operation instructions instead of performing them directly
   - Returns operations for directory creation and file writing that the client should perform
   - Added alternative implementations:
     - `create_cursor_rule_files_rpc`: Uses an RPC pattern for remote execution
     - `create_cursor_rule_files_hybrid`: Detects environment and adapts behavior accordingly

## Recommended Refactoring Pattern

Each function should follow the pattern used in `save_cursor_rule`, which returns a dictionary with:
- `operations`: A list of operations to perform (create_directory, write_file, etc.)
- `message`: A description of the operations

Example refactoring for `save_cursor_rule`:

```python
@mcp.tool(name="save_cursor_rule", description="Save a cursor rule to the cursor rules directory in the project")
def save_cursor_rule(
    rule_name: str = Field(
        description="The name of the cursor rule file (without extension)",
        examples=["python-best-practices", "react-component-patterns", "error-handling"],
        min_length=3,
        pattern="^[a-z0-9-]+$",
    ),
    rule_content: str = Field(
        description="The complete content of the cursor rule in mdc.md format",
        examples=[
            "# Python Best Practices\n\nWhen writing Python code, follow these guidelines:\n\n1. Use type hints\n2. Write docstrings\n3. Follow PEP 8"
        ],
        min_length=10,
    ),
) -> dict[str, Any]:
    """Save a cursor rule to the cursor rules directory.

    Args:
        rule_name: The name of the cursor rule file (without extension)
        rule_content: The complete content of the cursor rule in mdc.md format

    Returns:
        dict: Dictionary containing file operation instructions

    """
    # Define the path for the cursor rules directory
    cursor_rules_dir_path = "hack/drafts/cursor_rules"
    rule_file_path = f"{cursor_rules_dir_path}/{rule_name}.mdc.md"

    # Return operations for the client to perform
    return {
        "operations": [
            {
                "type": "create_directory",
                "path": cursor_rules_dir_path,
                "options": {"parents": True, "exist_ok": True}
            },
            {
                "type": "write_file",
                "path": rule_file_path,
                "content": rule_content,
                "options": {"mode": "w"}
            }
        ],
        "message": f"Instructions to save cursor rule to {rule_file_path}"
    }
```

## Testing Coverage and Verification

### Test Status for Refactored Functions

1. **`save_cursor_rule`**
   - [x] Unit tests verifying operation structure
   - [x] Integration tests with client application
   - [x] Error handling tests

2. **`create_cursor_rule_files`**
   - [x] Unit tests for remote compatibility
   - [x] Tests for RPC implementation
   - [x] Tests for hybrid mode

3. **`ensure_makefile_task`**
   - [x] Unit tests for operation structure
   - [x] Integration tests with process_makefile_result
   - [x] Error handling tests
   - [x] Remote compatibility tests
   - [x] Edge case tests
   - [x] Invalid file path handling tests
   - [x] Input parameter validation tests

4. **`run_update_cursor_rules`**
   - [ ] Add unit tests for two-step process
   - [ ] Add integration tests
   - [ ] Add error handling tests

5. **`update_dockerignore`**
   - [ ] Add unit tests for operation structure
   - [ ] Add integration tests
   - [ ] Add error handling tests

6. **`execute_phase_4`**
   - [ ] Add unit tests for operation structure
   - [ ] Add integration tests
   - [ ] Add error handling tests

### Test Implementation Guidelines

Each function's tests should verify:
1. Correct operation structure returned (following FastMCP format)
2. Proper error handling and reporting
3. No direct file system operations
4. Integration with client-side operation handlers
5. Proper handling of edge cases and invalid inputs

## Progress Tracking

- [x] Refactor `create_cursor_rule_files`
- [x] Refactor `ensure_makefile_task`
- [x] Refactor `run_update_cursor_rules`
- [x] Refactor `update_dockerignore`
- [x] Refactor `execute_phase_4`
- [x] Add tests to verify remote compatibility for `create_cursor_rule_files`
- [x] Update documentation to reflect remote execution capabilities
- [x] Add error handling for invalid file paths in `ensure_makefile_task`
- [x] Add input validation tests for `ensure_makefile_task`
- [ ] Add comprehensive test suite for all refactored functions
- [ ] Implement integration tests with client operation handlers
- [ ] Add error handling test cases for remaining functions
