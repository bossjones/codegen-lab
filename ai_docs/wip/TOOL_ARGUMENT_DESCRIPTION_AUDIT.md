# MCP Tool Decorator Argument Description Audit for prompt_library.py

This checklist is designed to audit functions decorated with `@mcp.tool` in the `prompt_library.py` file to ensure they have proper descriptions, argument annotations, and follow best practices.

## Tool Decorator Checklist for prompt_library.py

### Basic Tool Configuration

- [ ] Tool has a descriptive name (either via `name` parameter or function name)
- [ ] Tool has a comprehensive description in the decorator or docstring
- [ ] Tool has a proper return type annotation
- [ ] Tool has a docstring that explains its purpose and behavior

### Function Arguments

- [ ] All arguments have type annotations
- [ ] All arguments have Field() with descriptions
- [ ] Complex arguments have examples provided
- [ ] Default values are provided where appropriate
- [ ] Arguments have appropriate validation (min_length, pattern, etc.)
- [ ] Context parameter is properly typed as `Context | None = None` if used

### Docstring Quality

- [ ] Docstring follows PEP 257 convention
- [ ] Docstring includes a summary line
- [ ] Docstring includes detailed description of functionality
- [ ] Docstring includes Args section with all parameters documented
- [ ] Docstring includes Returns section explaining return value
- [ ] Docstring includes any relevant Examples (optional but recommended)

### Error Handling

- [ ] Function handles potential errors appropriately
- [ ] Error messages are descriptive and helpful
- [ ] Function validates inputs before processing

### Code Style and Best Practices

- [ ] Function name follows snake_case convention
- [ ] Function is focused on a single responsibility
- [ ] Function is not overly complex (consider breaking down if needed)
- [ ] Function has appropriate logging if using Context

## Example from prompt_library.py

```python
@mcp.tool(
    name="get_static_cursor_rules",
    description="Get multiple static cursor rule files to be written to the caller's .cursor/rules directory",
)
def get_static_cursor_rules(rule_names: list[str]) -> dict[str, Any]:
    """Get multiple static cursor rule files by name.

    This tool returns the content of specific cursor rule files so they can be
    written to the calling repository's .cursor/rules directory.

    Args:
        rule_names: List of cursor rule names to retrieve (without .md extension)

    Returns:
        dict[str, Any]: A dictionary containing a list of rule data objects

    """
    results = []

    for rule_name in rule_names:
        # Get the rule data using get_static_cursor_rule
        rule_data = get_static_cursor_rule(rule_name)

        # Add the result to our list
        results.append(rule_data)

    # Return a single JSON object with the results array
    return {"rules": results}
```

## Common Issues Found in prompt_library.py Tool Decorators

- Missing descriptions in the decorator
- Missing Field() descriptions for arguments
- Incomplete or missing docstrings
- Missing type annotations
- No validation for user inputs
- No examples for complex arguments
- Inconsistent naming conventions
- Missing error handling
- Overly complex functions with multiple responsibilities

## Audit Process for prompt_library.py

1. Identify all functions with `@mcp.tool` decorators in prompt_library.py
2. Check each function against the checklist items
3. Document any issues found
4. Prioritize fixes based on severity and usage frequency
5. Implement fixes to ensure all tools are properly documented

## Tools to Audit in prompt_library.py

The following tools should be audited:

- [ ] Line 558-562: `get_static_cursor_rule`
- [ ] Line 591-595: `get_static_cursor_rules`
- [ ] Line 490: `list_cursor_rules`
- [ ] Line 204: `read_cursor_rule`
- [ ] Line 321: `generate_cursor_rule`
- [ ] Line 753-754: `save_cursor_rule`

Additional tool functions found in prompt_library.py:
- [ ] Line 793: Tool at line 793
- [ ] Line 1041: Tool at line 1041
- [ ] Line 1167: Tool at line 1167
- [ ] Line 1243: Tool at line 1243
- [ ] Line 1312: Tool at line 1312
- [ ] Line 1441: Tool at line 1441
- [ ] Line 1469: Tool at line 1469
- [ ] Line 1526: Tool at line 1526
- [ ] Line 1568: Tool at line 1568
- [ ] Line 1600: Tool at line 1600
- [ ] Line 1673: Tool at line 1673
- [ ] Line 1733: Tool at line 1733
- [ ] Line 1795: Tool at line 1795

Note: The functions `update_cursor_rule`, `delete_cursor_rule`, `search_cursor_rules`, and `execute_cursor_rule` were not found in prompt_library.py.
