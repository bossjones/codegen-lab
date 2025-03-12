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

- [x] Line 558-562: `get_static_cursor_rule`
- [x] Line 591-595: `get_static_cursor_rules`
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

## Completed Audits

### get_static_cursor_rule (Lines 558-562)

**Audit Status**: Completed ✅

**Findings**:

1. Basic Tool Configuration:
   - ✅ Has descriptive name via `name` parameter
   - ✅ Has comprehensive description in the decorator
   - ⚠️ Return type annotation using Python 3.10+ Union operator (`|`) instead of `Union` from typing
   - ✅ Has detailed docstring explaining purpose and behavior

2. Function Arguments:
   - ✅ `rule_name` parameter has type annotation (string)
   - ❌ Missing Field() with description for `rule_name`
   - ❌ No examples provided for the `rule_name` parameter
   - ❌ No validation for `rule_name` (e.g., pattern, min_length)
   - ✅ No Context parameter needed for this function

3. Docstring Quality:
   - ✅ Follows PEP 257 convention
   - ✅ Includes summary line
   - ✅ Includes detailed description
   - ✅ Includes Args section documenting the parameter
   - ✅ Includes Returns section explaining return value structure
   - ✅ Explicitly mentions that no exceptions are raised
   - ❌ No Examples section (optional)

4. Error Handling:
   - ✅ Properly handles case when rule is not found
   - ✅ Returns descriptive error message
   - ⚠️ Limited input validation before processing

5. Code Style and Best Practices:
   - ✅ Function name follows snake_case convention
   - ✅ Function is focused on single responsibility
   - ✅ Function is not overly complex
   - ✅ No logging needed for this function

**Implemented Improvements**:
- Updated return type annotation from `dict[str, str | bool | list[dict[str, str]]]` to `dict[str, Union[str, bool, list[dict[str, str]]]]` for better compatibility
- Enhanced docstring to explicitly state that no exceptions are raised

**Recommended Further Improvements**:
- Add Field() with description for the `rule_name` parameter
- Add examples for the `rule_name` parameter
- Add validation for `rule_name` (e.g., pattern, min_length)
- Add input validation to prevent potential path traversal
- Consider adding an Examples section to the docstring

**Code Sample with Suggested Improvements**:
```python
@mcp.tool(
    name="get_static_cursor_rule",
    description="Get a static cursor rule file by name to be written to the caller's .cursor/rules directory",
)
def get_static_cursor_rule(
    rule_name: str = Field(
        description="Name of the cursor rule to retrieve (with or without .md extension)",
        examples=["python-best-practices", "react-patterns", "error-handling"],
        min_length=2,
        pattern="^[a-zA-Z0-9-_]+(\\.md)?$",  # Validate to prevent path traversal
    )
) -> dict[str, Union[str, bool, list[dict[str, str]]]]:
    """Get a static cursor rule file by name.

    This tool retrieves the content of a specific cursor rule file so it can be
    written to the calling repository's .cursor/rules directory.

    Args:
        rule_name: Name of the cursor rule to retrieve (with or without .md extension)

    Returns:
        dict[str, Union[str, bool, list[dict[str, str]]]]: A dictionary containing either:
            - On success: {"rule_name": str, "content": str}
            - On error: {"isError": bool, "content": list[dict[str, str]]}

    Raises:
        No exceptions are raised; errors are returned in the result object.

    Examples:
        >>> result = get_static_cursor_rule("python-best-practices")
        >>> print(result["rule_name"])
        'python-best-practices.md'
    """
    # Validate input to prevent path traversal
    if "/" in rule_name or "\\" in rule_name:
        return {
            "isError": True,
            "content": [{"type": "text", "text": "Error: Invalid rule name format"}],
        }

    # Add .md extension if not already present
    full_rule_name = rule_name if rule_name.endswith(".md") else f"{rule_name}.md"

    content = read_cursor_rule(rule_name.replace(".md", ""))
    if not content:
        # Return an error result object instead of raising an exception
        return {
            "isError": True,
            "content": [{"type": "text", "text": f"Error: Static cursor rule '{rule_name}' not found"}],
        }

    return {"rule_name": full_rule_name, "content": content}
```

### get_static_cursor_rules (Lines 595-622)

**Audit Status**: Completed ✅

**Findings**:

1. Basic Tool Configuration:
   - ✅ Has descriptive name via `name` parameter
   - ✅ Has comprehensive description in the decorator
   - ⚠️ Return type annotation is vague using `Any` and not properly documenting return structure
   - ✅ Has detailed docstring explaining purpose and behavior

2. Function Arguments:
   - ✅ `rule_names` parameter has type annotation (list[str])
   - ✅ Has Field() with description for `rule_names`
   - ✅ Has examples provided for the `rule_names` parameter
   - ✅ Has appropriate validation (min_items=1)
   - ✅ No Context parameter needed for this function

3. Docstring Quality:
   - ✅ Follows PEP 257 convention
   - ✅ Includes summary line
   - ✅ Includes detailed description
   - ✅ Includes Args section documenting the parameter
   - ⚠️ Returns section lacks specific details about structure
   - ❌ No Raises section (though no exceptions are explicitly raised)
   - ❌ No Examples section (optional)

4. Error Handling:
   - ⚠️ Indirectly handles errors through `get_static_cursor_rule`
   - ❌ No explicit validation for an empty `rule_names` list
   - ❌ No explicit error handling in this function itself

5. Code Style and Best Practices:
   - ✅ Function name follows snake_case convention
   - ✅ Function is focused on single responsibility
   - ✅ Function is not overly complex
   - ✅ Reuses existing function (`get_static_cursor_rule`) instead of duplicating code
   - ✅ No logging needed for this function

**Recommended Improvements**:
- Specify return type more precisely instead of using `Any`
- Enhance Returns section to detail the exact structure of returned data
- Consider adding explicit error handling for edge cases
- Add a Raises section to document that no exceptions are raised
- Consider adding an Examples section to the docstring

**Code Sample with Suggested Improvements**:
```python
@mcp.tool(
    name="get_static_cursor_rules",
    description="Get multiple static cursor rule files to be written to the caller's .cursor/rules directory",
)
def get_static_cursor_rules(
    rule_names: list[str] = Field(
        description="List of cursor rule names to retrieve (with or without .md extension)",
        examples=[["python-best-practices", "react-patterns"], ["error-handling"]],
        min_items=1,
    ),
) -> dict[str, list[dict[str, Union[str, bool, list[dict[str, str]]]]]]:
    """Get multiple static cursor rule files by name.

    This tool returns the content of specific cursor rule files so they can be
    written to the calling repository's .cursor/rules directory.

    Args:
        rule_names: List of cursor rule names to retrieve (with or without .md extension)

    Returns:
        dict[str, list[dict[str, Union[str, bool, list[dict[str, str]]]]]]: A dictionary containing:
            - "rules": A list of rule data objects, where each object is either:
                - On success: {"rule_name": str, "content": str}
                - On error: {"isError": bool, "content": list[dict[str, str]]}

    Raises:
        No exceptions are raised; errors are returned in the result object.

    Examples:
        >>> result = get_static_cursor_rules(["python-best-practices", "react-patterns"])
        >>> print(len(result["rules"]))
        2
        >>> print(result["rules"][0]["rule_name"])
        'python-best-practices.md'
    """
    # Validation happens through Field() with min_items=1

    results = []

    for rule_name in rule_names:
        # Get the rule data using get_static_cursor_rule
        rule_data = get_static_cursor_rule(rule_name)

        # Add the result to our list
        results.append(rule_data)

    # Return a single JSON object with the results array
    return {"rules": results}
```
