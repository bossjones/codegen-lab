---
description: Fast Python MCP Server Development
globs: *.py
alwaysApply: false
---

# FastMCP Tool Argument Audit Guide

This rule provides a systematic approach for auditing, improving, and maintaining FastMCP tool decorators with proper argument descriptions and validation.

<rule>
name: fastmcp-tool-argument-audit
description: Guidelines for auditing and improving FastMCP tool decorator arguments with proper descriptions, validation, and documentation
filters:
  # Match Python files
  - type: file_extension
    pattern: "\\.py$"
  # Match FastMCP tool-related content
  - type: content
    pattern: "@mcp\\.tool|from mcp\\.server\\.fastmcp import|FastMCP\\("

actions:
  - type: suggest
    message: |
      # FastMCP Tool Argument Audit Process

      When auditing FastMCP tool decorators, follow this systematic process to ensure comprehensive argument descriptions, proper type annotations, and robust validation:

      ## 1. Preparation Phase

      1. **Create an Audit Checklist**:
         ```markdown
         # MCP Tool Decorator Argument Description Audit for [filename].py

         This checklist is designed to audit functions decorated with `@mcp.tool` in the `[filename].py` file to ensure they have proper descriptions, argument annotations, and follow best practices.

         ## Tool Decorator Checklist for [filename].py

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

         ## Tools to Audit in [filename].py

         The following tools should be audited:

         - [ ] Tool at line X
         - [ ] Tool at line Y
         - [ ] Tool at line Z
         ```

      2. **Identify All Tools**: Scan the target file to identify all `@mcp.tool` decorated functions and their locations.

      ## 2. Iterative Audit Process

      For each tool, perform this iterative audit:

      ### a. Analysis Phase

      1. **Basic Tool Configuration**:
         - Check if tool has a descriptive name (via `name` parameter or function name)
         - Verify tool has a comprehensive description
         - Confirm proper return type annotation is present
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
         - Verify Returns section explains return value
         - Look for Examples section (optional)

      4. **Error Handling**:
         - Check if function handles errors appropriately
         - Verify error messages are descriptive
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

      1. Basic Tool Configuration:
         - ✅/❌/⚠️ Has descriptive name via `name` parameter
         - ✅/❌/⚠️ Has comprehensive description in the decorator
         - ✅/❌/⚠️ Return type annotation
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
         - ✅/❌/⚠️ Includes Returns section explaining return value
         - ✅/❌/⚠️ Includes Examples section (optional)

      4. Error Handling:
         - ✅/❌/⚠️ Properly handles potential errors
         - ✅/❌/⚠️ Returns descriptive error messages
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
      @mcp.tool(
          name="example_tool",
          description="Comprehensive description of what the tool does"
      )
      def example_tool(
          param1: str = Field(
              description="Description of parameter 1",
              examples=["example1", "example2"],
              min_length=3,
              pattern="^[a-z0-9-]+$"
          ),
          param2: int = Field(
              description="Description of parameter 2",
              examples=[1, 42, 100],
              ge=0
          )
      ) -> dict[str, Any]:
          """Detailed description of the tool's functionality.

          Args:
              param1: Detailed explanation of parameter 1
              param2: Detailed explanation of parameter 2

          Returns:
              dict[str, Any]: Description of the return value structure

          Raises:
              ValueError: When parameters are invalid

          Examples:
              >>> result = example_tool("test", 42)
              >>> print(result["key"])
              'value'
          """
          # Implementation
      ```
      ```

      ### c. Improvement Phase

      1. **Implement Improvements**: Create an improved version of the function with:
         - Proper type annotations
         - Field() with descriptions for all arguments
         - Examples for complex arguments
         - Appropriate validation rules
         - Complete docstring following PEP 257
         - Proper error handling

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

      ## Best Practices for FastMCP Tool Arguments

      1. **Type Annotations**:
         - Use `dict[str, Any]` for complex return types
         - Use `Union[type1, type2]` instead of `type1 | type2` for better compatibility
         - Include proper type annotations for all parameters

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

      5. **Docstring Format**:
         - Follow PEP 257 conventions
         - Include a summary line and detailed description
         - Document all parameters in the Args section
         - Explain return value structure in Returns section
         - Document raised exceptions in Raises section (if applicable)
         - Include examples when helpful

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
              >>> print(result["rule_name"])
              'python-best-practices.md'
          """
          # Implementation
      ```

  - input: |
      # Looking at a FastMCP tool that returns errors instead of raising exceptions

      @mcp.tool()
      def check_config_file(config_path: str) -> dict[str, Any]:
          """Check if a configuration file exists."""
          if not os.path.exists(config_path):
              return {
                  "isError": True,
                  "content": [{"type": "text", "text": f"Error: Config file not found at {config_path}"}]
              }
          # Implementation
    output: |
      This tool follows the best practice of returning structured error objects instead of raising exceptions, but has several areas for improvement:

      1. Missing name and description in the decorator
      2. Missing Field() for the config_path parameter
      3. Incomplete docstring
      4. Return type lacks specificity

      Here's an improved version:

      ```python
      @mcp.tool(
          name="check_config_file",
          description="Check if a configuration file exists and return its contents if found",
      )
      def check_config_file(
          config_path: str = Field(
              description="Path to the configuration file to check",
              examples=["config.json", "settings.yaml", "/path/to/config.toml"],
              min_length=1,
          )
      ) -> dict[str, Union[str, bool, list[dict[str, str]]]]:
          """Check if a configuration file exists and return its contents if found.

          This tool validates that a configuration file exists at the specified path
          and returns either its contents or an error if not found.

          Args:
              config_path: Path to the configuration file to check

          Returns:
              dict[str, Union[str, bool, list[dict[str, str]]]]: A dictionary containing either:
                  - On success: {"content": str, "path": str}
                  - On error: {"isError": bool, "content": list[dict[str, str]]}
          """
          if not os.path.exists(config_path):
              return {
                  "isError": True,
                  "content": [{"type": "text", "text": f"Error: Config file not found at {config_path}"}]
              }
          # Implementation
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

The iterative audit process for FastMCP tool arguments follows a structured approach:

1. **Identify Tools**: Locate all `@mcp.tool` decorated functions in the codebase
2. **Analyze Each Tool**: Systematically evaluate each tool against the checklist
3. **Document Findings**: Record detailed observations about current state and needed improvements
4. **Implement Improvements**: Create enhanced versions with proper descriptions, validation, and documentation
5. **Verify Improvements**: Run code quality checks to confirm improvements meet standards
6. **Update Documentation**: Mark tasks as completed and document progress

This process ensures consistent quality across all FastMCP tools and promotes maintainable, well-documented code that follows best practices.

### Running Code Quality Checks

After implementing improvements, always validate your changes:

```bash
make ci
```

This will run linters, type checkers, and other code quality tools to ensure your improvements haven't introduced any issues.

### Notifying on Completion

When you've completed an audit cycle, update the checklist document and send a notification:

```bash
osascript -e 'display notification "Completed audit of prompt_library.py" with title "FastMCP Audit Complete"'
```

This provides clear feedback on progress and helps track the overall improvement of the codebase.
