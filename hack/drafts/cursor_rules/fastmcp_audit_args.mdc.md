---
description:
globs:
alwaysApply: false
---

# FastMCP Tool and Resource Argument Audit Guide

Fast Python MCP Server Development

This rule provides a systematic approach for auditing, improving, and maintaining FastMCP tool and resource decorators with proper argument descriptions, return type annotations, and error handling.

<rule>
name: fastmcp-tool-argument-audit
description: Guidelines for auditing and improving FastMCP tool and resource decorator arguments with proper descriptions, validation, documentation, and error handling
filters:
  # Match Python files
  - type: file_extension
    pattern: "\\.py$"
  # Match FastMCP tool and resource-related content
  - type: content
    pattern: "@mcp\\.(tool|resource)|from mcp\\.server\\.fastmcp import|FastMCP\\("

actions:
  - type: suggest
    message: |
      # FastMCP Tool and Resource Argument Audit Process

      When auditing FastMCP tool and resource decorators, follow this systematic process to ensure comprehensive argument descriptions, proper type annotations, and robust validation:

      ## 1. Preparation Phase

      1. **Create an Audit Checklist**:
         ```markdown
         # MCP Tool/Resource Decorator Argument Description Audit for [filename].py

         This checklist is designed to audit functions decorated with `@mcp.tool` or `@mcp.resource` in the `[filename].py` file to ensure they have proper descriptions, argument annotations, and follow best practices.

         ## Tool/Resource Decorator Checklist for [filename].py

         ### Basic Configuration

         - [ ] Has descriptive name (either via `name` parameter or function name)
         - [ ] Has comprehensive description in the decorator or docstring
         - [ ] Has proper return type annotation (using Union for error/success return types)
         - [ ] Has docstring that explains its purpose and behavior

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
         - [ ] Docstring includes Examples section with error handling examples
         - [ ] Docstring explains both success and error return structures

         ### Error Handling

         - [ ] Function handles potential errors appropriately
         - [ ] Error messages are descriptive and helpful
         - [ ] Uses structured MCP error objects (`{"isError": True, "content": [...]}`)
         - [ ] Function validates inputs before processing

         ### Code Style and Best Practices

         - [ ] Function name follows snake_case convention
         - [ ] Function is focused on a single responsibility
         - [ ] Function is not overly complex (consider breaking down if needed)
         - [ ] Function has appropriate logging if using Context

         ## Tools/Resources to Audit in [filename].py

         The following tools/resources should be audited:

         - [ ] Tool/Resource at line X
         - [ ] Tool/Resource at line Y
         - [ ] Tool/Resource at line Z
         ```

      2. **Identify All Tools and Resources**: Scan the target file to identify all `@mcp.tool` and `@mcp.resource` decorated functions and their locations.

      ## 2. Iterative Audit Process

      For each tool or resource, perform this iterative audit:

      ### a. Analysis Phase

      1. **Basic Configuration**:
         - Check if it has a descriptive name (via `name` parameter or function name)
         - Verify it has a comprehensive description
         - Confirm proper return type annotation is present (using Union types for success/error returns)
         - Ensure docstring explains purpose and behavior

      2. **Function Arguments**:
         - Verify all arguments have type annotations
         - Check if arguments use Field() with descriptions
         - Look for examples in complex arguments
         - Check for default values where appropriate
         - Verify validation rules (min_length, pattern, etc.)
         - Ensure Context parameter is typed correctly if used

      3. **Docstring Quality**:
         - Confirm docstring follows PEP 257
         - Verify presence of summary line
         - Check for detailed description
         - Ensure Args section documents all parameters
         - Verify Returns section explains both success and error return structures
         - Look for Examples section with error handling examples

      4. **Error Handling**:
         - Check if function returns structured error objects instead of raising exceptions
         - Verify error objects follow MCP format: `{"isError": True, "content": [{"type": "text", "text": "Error message"}]}`
         - Ensure input validation occurs before processing

      5. **Code Style and Best Practices**:
         - Confirm function name follows snake_case
         - Verify function has a single responsibility
         - Check for excessive complexity
         - Verify appropriate logging if using Context

      ### b. Documentation Phase

      Document findings in a structured format:

      ```markdown
      ### [function_name] (Lines X-Y)

      **Audit Status**: Completed ✅/In Progress ⏳

      **Findings**:

      1. Basic Configuration:
         - ✅/❌/⚠️ Has descriptive name via `name` parameter
         - ✅/❌/⚠️ Has comprehensive description in the decorator
         - ✅/❌/⚠️ Return type annotation uses Union for error/success returns
         - ✅/❌/⚠️ Has detailed docstring explaining purpose and behavior

      2. Function Arguments:
         - ✅/❌/⚠️ All parameters have type annotations
         - ✅/❌/⚠️ All parameters have Field() with descriptions
         - ✅/❌/⚠️ Complex arguments have examples
         - ✅/❌/⚠️ Default values provided where appropriate
         - ✅/❌/⚠️ Validation for arguments (pattern, min_length, etc.)
         - ✅/❌/⚠️ Context parameter properly typed (if applicable)

      3. Docstring Quality:
         - ✅/❌/⚠️ Follows PEP 257 convention
         - ✅/❌/⚠️ Includes summary line
         - ✅/❌/⚠️ Includes detailed description
         - ✅/❌/⚠️ Includes Args section documenting parameters
         - ✅/❌/⚠️ Includes Returns section explaining both success and error structures
         - ✅/❌/⚠️ Includes Examples section with error handling

      4. Error Handling:
         - ✅/❌/⚠️ Returns structured error objects (not raising exceptions)
         - ✅/❌/⚠️ Error objects follow MCP format
         - ✅/❌/⚠️ Validates inputs before processing

      5. Code Style and Best Practices:
         - ✅/❌/⚠️ Function name follows snake_case convention
         - ✅/❌/⚠️ Function is focused on single responsibility
         - ✅/❌/⚠️ Function is not overly complex
         - ✅/❌/⚠️ Appropriate logging if using Context

      **Recommended Improvements**:
      - Improvement 1
      - Improvement 2
      - Improvement 3

      **Code Sample with Suggested Improvements**:
      ```python
      # Code sample with improvements
      ```
      ```

      ### c. Improvement Phase

      1. **Implement Improvements**: Create an improved version of the function with:
         - Proper type annotations using Union for success/error returns
         - Field() with descriptions for all arguments
         - Examples for complex arguments
         - Appropriate validation rules
         - Complete docstring following PEP 257
         - Proper error handling with structured MCP error objects

      2. **Code Review**: Review the improved version to ensure it meets all requirements.

      ## 3. Reflection and Validation

      After completing all audits, perform a reflection and validation step:

      1. **Run Code Quality Checks**:
         ```bash
         make ci
         ```

      2. **Verify No New Issues**:
         - Check that improved code passes all linters
         - Verify type checking passes
         - Ensure formatting is consistent

      3. **Update Audit Checklist**:
         - Mark completed items ✓
         - Document any open issues
         - Add notes for future improvements

      4. **Send Notification**:
         ```bash
         osascript -e 'display notification "Completed audit of [filename].py" with title "FastMCP Audit Complete"'
         ```

      ## Best Practices for FastMCP Tool and Resource Arguments

      1. **Type Annotations**:
         - Use `Union[success_type, dict[str, Any]]` for functions that might return either success data or error objects
         - Use `Union[type1, type2]` instead of `type1 | type2` for broader Python version compatibility
         - Include proper type annotations for all parameters
         - For resources that might return errors: `Union[list[dict[str, str]], dict[str, Any]]`

      2. **Field Descriptions**:
         - Make descriptions clear and concise
         - Explain parameter purpose and constraints
         - Provide examples for complex parameters
         - Include validation rules appropriate to the parameter type

      3. **Validation Rules**:
         - String parameters: `min_length`, `max_length`, `pattern`
         - Numeric parameters: `ge`, `gt`, `le`, `lt`
         - List parameters: `min_items`, `max_items`

      4. **Error Handling**:
         - Return structured error objects instead of raising exceptions
         - Format error responses with `{"isError": True, "content": [{"type": "text", "text": "Error message"}]}`
         - Provide specific, actionable error messages
         - Use try/except blocks to catch potential exceptions and convert them to MCP error objects

      5. **Docstring Format**:
         - Follow PEP 257 conventions
         - Include a summary line and detailed description
         - Document all parameters in the Args section
         - Explain both success and error return structures in Returns section
         - Include examples that show how to check for and handle errors

examples:
  - input: |
      # Analyzing a FastMCP tool without proper argument descriptions

      @mcp.tool(
          name="get_static_cursor_rule",
          description="Get a static cursor rule file by name",
      )
      def get_static_cursor_rule(rule_name: str) -> dict[str, str | bool | list[dict[str, str]]]:
          """Get a static cursor rule file by name.

          Args:
              rule_name: Name of the cursor rule to retrieve

          Returns:
              dict with rule data
          """
          # Implementation
    output: |
      This tool needs improvement in several areas:

      1. The tool description is too brief
      2. Arguments lack Field() with descriptions and examples
      3. Return type uses Python 3.10+ Union operator instead of typing.Union
      4. Return value description is too vague
      5. No validation for rule_name
      6. No error handling guidance in docstring

      Here's an improved version:

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

          Examples:
              >>> result = get_static_cursor_rule("python-best-practices")
              >>> if not result.get("isError"):
              >>>     print(result["rule_name"])
              >>>     'python-best-practices.md'
              >>> else:
              >>>     print(f"Error: {result['content'][0]['text']}")
          """
          try:
              # Implementation
              return {"rule_name": rule_name, "content": "Rule content here"}
          except Exception as e:
              return {
                  "isError": True,
                  "content": [{"type": "text", "text": f"Error retrieving cursor rule: {str(e)}"}]
              }
      ```

  - input: |
      # Looking at a FastMCP resource without proper error handling

      @mcp.resource(
          "cursor-rules://list",
          name="list_cursor_rules",
          description="List all available cursor rules",
      )
      def list_cursor_rules() -> list[dict[str, str]]:
          """List all available cursor rules.

          Returns:
              list[dict[str, str]]: List of cursor rules with name, description, and title
          """
          rules = []
          for rule_name in get_cursor_rule_names():
              content = read_cursor_rule(rule_name)
              if content:
                  parsed = parse_cursor_rule(content)
                  rules.append({
                      "name": rule_name,
                      "description": parsed.get("description", ""),
                      "title": parsed.get("title", "")
                  })
          return rules
    output: |
      This resource needs improvement in several areas:

      1. Return type doesn't account for potential errors
      2. No error handling for exceptions
      3. Docstring doesn't explain error returns
      4. No examples showing how to handle potential errors

      Here's an improved version:

      ```python
      @mcp.resource(
          "cursor-rules://list",
          name="list_cursor_rules",
          description="List all available cursor rules with their names and descriptions",
      )
      def list_cursor_rules() -> Union[list[dict[str, str]], dict[str, Any]]:
          """List all available cursor rules.

          This resource retrieves all available cursor rules and returns them as a list
          of dictionaries containing the rule name, description, and title.

          Returns:
              Union[list[dict[str, str]], dict[str, Any]]: Either:
                  - On success: List of cursor rules with the following structure:
                      - "name": The rule name (without extension)
                      - "description": The rule description (empty string if not found)
                      - "title": The rule title (empty string if not found)
                  - On error: Error object with the following structure:
                      - "isError": True
                      - "content": List of content objects with error message

          Examples:
              >>> rules = list_cursor_rules()
              >>> if not isinstance(rules, dict) or not rules.get("isError"):
              >>>     print(rules[0]["name"])
              >>>     'example-rule'
              >>> else:
              >>>     print(f"Error: {rules['content'][0]['text']}")
          """
          try:
              rules = []
              for rule_name in get_cursor_rule_names():
                  content = read_cursor_rule(rule_name)
                  if content:
                      parsed = parse_cursor_rule(content)
                      rules.append(
                          {
                              "name": rule_name,
                              "description": parsed.get("description", ""),
                              "title": parsed.get("title", "")
                          }
                      )
              return rules
          except Exception as e:
              return {
                  "isError": True,
                  "content": [{"type": "text", "text": f"Error retrieving cursor rules: {str(e)}"}]
              }
      ```

metadata:
  priority: high
  version: 1.0
  tags:
    - fastmcp
    - documentation
    - best-practices
    - code-quality
    - type-annotations
</rule>

## Reflection on Iterative Audit Process

The iterative audit process for FastMCP tool and resource arguments follows a structured approach:

1. **Identify Tools and Resources**: Locate all `@mcp.tool` and `@mcp.resource` decorated functions in the codebase
2. **Analyze Each Function**: Systematically evaluate each against the checklist
3. **Document Findings**: Record detailed observations about current state and needed improvements
4. **Implement Improvements**: Create enhanced versions with proper descriptions, validation, and documentation
5. **Verify Improvements**: Run code quality checks to confirm improvements meet standards
6. **Update Documentation**: Mark tasks as completed and document progress

This process ensures consistent quality across all FastMCP tools and resources, promoting maintainable, well-documented code that follows best practices.

## Error Handling Options

When implementing error handling in FastMCP tools and resources, choose from these options:

### Option 1: Return Structured Error Object (Recommended)

```python
try:
    # Implementation code
    return success_result
except Exception as e:
    return {
        "isError": True,
        "content": [{"type": "text", "text": f"Error message: {str(e)}"}]
    }
```

This approach:
- Follows MCP protocol conventions
- Provides structured, parseable errors
- Makes error handling predictable for clients
- Avoids exceptions bubbling up to FastMCP's global handler

### Option 2: Let Exceptions Bubble Up to FastMCP Handler

If the function might raise exceptions, document them properly:

```python
def function_name() -> return_type:
    """Function description.

    Returns:
        return_type: Description of return value

    Raises:
        ValueError: When input is invalid
        FileNotFoundError: When resource cannot be found
    """
    # Implementation that might raise exceptions
```

This approach is less preferred as it relies on FastMCP's error handling, which may be less customized.

## Running Code Quality Checks

After implementing improvements, always validate your changes:

```bash
make ci
```

This will run linters, type checkers, and other code quality tools to ensure your improvements haven't introduced any issues.

## Checking for Completion

When you've completed an audit cycle, update the checklist document and send a notification:

```bash
osascript -e 'display notification "Completed audit of prompt_library.py" with title "FastMCP Audit Complete"'
```

This provides clear feedback on progress and helps track the overall improvement of the codebase.

## Sample Audit Results

The following are examples of completed audits from the `prompt_library.py` file:

### list_cursor_rules (Lines 486-527)

**Audit Status**: Completed ✅

**Findings**:

1. Basic Configuration:
   - ✅ Has descriptive name via `name` parameter: "list_cursor_rules"
   - ✅ Has comprehensive description in the decorator: "List all available cursor rules with their names and descriptions"
   - ✅ Return type annotation uses Union for error/success returns: `list[dict[str, str]] | dict[str, Any]`
   - ✅ Has detailed docstring explaining purpose and behavior

2. Function Arguments:
   - ✅ No parameters required
   - ✅ Context parameter not used (N/A)

3. Docstring Quality:
   - ✅ Follows PEP 257 convention
   - ✅ Includes summary line
   - ✅ Includes detailed description
   - ✅ No Args section needed (no parameters)
   - ✅ Includes Returns section explaining both success and error structures
   - ✅ Includes Raises section documenting exception handling

4. Error Handling:
   - ✅ Returns structured error objects (not raising exceptions)
   - ✅ Error objects follow MCP format
   - ✅ No input validation needed (no parameters)

5. Code Style and Best Practices:
   - ✅ Function name follows snake_case convention
   - ✅ Function is focused on single responsibility
   - ✅ Function is not overly complex
   - ✅ No Context used (N/A)

### get_static_cursor_rules (Lines 613-667)

**Audit Status**: Completed ✅

**Findings**:

1. Basic Configuration:
   - ✅ Has descriptive name via `name` parameter: "get_static_cursor_rules"
   - ✅ Has comprehensive description in the decorator: "Get multiple static cursor rule files to be written to the caller's .cursor/rules directory"
   - ✅ Has proper return type annotation: `dict[str, list[dict[str, str | bool | list[dict[str, str]]]]]`
   - ✅ Has docstring that explains its purpose and behavior

2. Function Arguments:
   - ✅ All arguments have type annotations: `rule_names: list[str]`
   - ✅ All arguments have Field() with descriptions
   - ✅ Complex arguments have examples provided: `examples=[["python-best-practices", "react-patterns"], ["error-handling"]]`
   - ✅ Default values are provided where appropriate
   - ✅ Arguments have appropriate validation: `min_items=1`

3. Docstring Quality:
   - ✅ Docstring follows PEP 257 convention
   - ✅ Docstring includes a summary line
   - ✅ Docstring includes detailed description of functionality
   - ✅ Docstring includes Args section with all parameters documented
   - ✅ Docstring includes Returns section explaining return value
   - ✅ Docstring includes Examples section with error handling examples
   - ✅ Docstring explains both success and error return structures

4. Error Handling:
   - ✅ Function handles potential errors appropriately
   - ✅ Error messages are descriptive and helpful
   - ✅ Uses structured MCP error objects (`{"isError": True, "content": [...]}`)
   - ✅ Function validates inputs before processing
   - ✅ Added additional validation for rule name format

5. Code Style and Best Practices:
   - ✅ Function name follows snake_case convention
   - ✅ Function is focused on a single responsibility
   - ✅ Function is not overly complex
   - ✅ Added metadata in the return value to provide additional context

**Implemented Improvements**:
- Added an optional `ignore_missing` parameter to allow skipping missing rules
- Enhanced input validation for rule names
- Added tracking of valid rule count in the results
- Added specialized error handling for when all rules are missing
- Improved docstring with more examples

### save_cursor_rule (Lines 798-837)

**Audit Status**: Completed ✅

**Findings**:

1. Basic Configuration:
   - ✅ Has descriptive name: "save_cursor_rule"
   - ✅ Has comprehensive description in the decorator: "Save a cursor rule to the cursor rules directory in the project"
   - ❌ Return type annotation was too generic: `dict[str, Any]`
   - ❌ Docstring was minimal and lacked detailed explanation

2. Function Arguments:
   - ✅ All arguments have type annotations: `rule_name: str`, `rule_content: str`
   - ✅ All arguments have Field() with descriptions
   - ✅ Complex arguments have examples provided
   - ✅ Default values are provided where appropriate
   - ✅ Arguments have appropriate validation: `min_length`, `pattern` for rule_name

3. Docstring Quality:
   - ✅ Docstring follows PEP 257 convention
   - ✅ Docstring includes a summary line
   - ❌ Docstring lacked detailed description of functionality
   - ✅ Docstring includes Args section with all parameters documented
   - ❌ Docstring Returns section was too generic
   - ❌ Docstring did not include Examples section
   - ❌ Docstring did not explain both success and error return structures

4. Error Handling:
   - ❌ Function did not handle potential errors
   - ❌ No error messages for potential failure scenarios
   - ❌ Didn't use structured MCP error objects for error cases
   - ❌ No input validation beyond Field decorators

5. Code Style and Best Practices:
   - ✅ Function name follows snake_case convention
   - ✅ Function is focused on a single responsibility
   - ✅ Function is not overly complex

**Implemented Improvements**:
- Enhanced return type annotation to be more specific
- Added comprehensive docstring with detailed description
- Improved parameter documentation in the Args section
- Added detailed Returns section explaining both success and error structures
- Added Examples section with error handling examples
- Added additional input validation beyond Field decorators
- Implemented error handling with try/except
- Added structured MCP error objects for error reporting
- Added validation for markdown content format

## Patterns and Best Practices Identified

Based on the audits conducted, we've identified several patterns and best practices for FastMCP tool and resource functions:

1. **Comprehensive Error Handling**:
   - Always return structured error objects instead of raising exceptions
   - Use the format `{"isError": True, "content": [{"type": "text", "text": "Error message"}]}`
   - Provide specific, actionable error messages
   - Use try/except blocks to catch potential exceptions

2. **Detailed Return Type Annotations**:
   - Use specific type annotations that accurately describe the return structure
   - For functions that return either success or error data, use Union types
   - Document the exact return structure in the docstring

3. **Input Validation**:
   - Validate inputs both through Field parameters and additional code checks
   - Return descriptive error messages for invalid inputs
   - Check for edge cases like empty strings, improper formats, etc.

4. **Comprehensive Docstrings**:
   - Follow PEP 257 convention
   - Include a summary line and detailed description
   - Document all parameters in the Args section
   - Provide a detailed Returns section that explains both success and error structures
   - Include Examples section showing both success and error scenarios

5. **Consistent Function Structure**:
   - Begin with input validation
   - Implement core functionality in a try/except block
   - Return structured results or error objects
