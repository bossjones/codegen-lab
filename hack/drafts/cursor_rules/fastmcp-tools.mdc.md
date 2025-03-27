---
description:
globs:
alwaysApply: false
---

# FastMCP Tool Development Guide

This rule provides expert guidance for writing MCP server tools using the FastMCP framework.


This rule provides expert guidance for writing MCP server tools using the FastMCP framework.

<rule>
name: fastmcp-tools
description: Expert guidance for writing MCP server tools using the FastMCP framework
filters:
  - type: file_extension
    pattern: "\\.py$"
  - type: content
    pattern: "(?s)(from mcp\\.server\\.fastmcp|import mcp\\.server\\.fastmcp|@mcp\\.tool|FastMCP)"

actions:
  - type: suggest
    message: |
      # FastMCP Tool Development Guide

      ## Core Concepts

      FastMCP tools are functions decorated with `@mcp.tool()` that can be called by MCP clients. They follow these principles:

      1.  **Type Safety**: All parameters and return values should be properly typed.
      2.  **Validation**: Input validation is handled automatically via Pydantic.
      3.  **Context Access**: Tools can access MCP capabilities via the `Context` object.
      4.  **Async Support**: Both synchronous and asynchronous functions are supported.
      5.  **Return Value Conversion**: Return values are automatically converted to MCP content types.

      ## Tool Decorator Syntax

      ```python
      from mcp.server.fastmcp import FastMCP, Context

      mcp = FastMCP("your_server_name")

      @mcp.tool(name=None, description=None)
      def my_tool(param1: type1, param2: type2 = default_value) -> return_type:
          """Docstring becomes the tool description if not provided explicitly."""
          # Implementation
          return result
      ```

      -   `name`: Optional name for the tool (defaults to function name)
      -   `description`: Optional description (defaults to function docstring)

      ## Parameter Validation

      FastMCP uses Pydantic for parameter validation. You can use Pydantic's validation features:

      ```python
      from pydantic import Field, field_validator
      from typing import Annotated

      @mcp.tool()
      def validate_parameters(
          name: Annotated[str, Field(min_length=2, max_length=50)],
          age: Annotated[int, Field(ge=0, lt=150)],
          email: str
      ) -> str:
          """Tool with parameter validation."""
          return f"Valid user: {name}, {age}, {email}"

      # You can also use Pydantic's validators
      from pydantic import BaseModel

      class UserData(BaseModel):
          name: str
          age: int
          email: str

          @field_validator('email')
          def validate_email(cls, v):
              if '@' not in v:
                  raise ValueError('Invalid email address')
              return v

      @mcp.tool()
      def process_user(user: UserData) -> str:
          """Process user data with validation."""
          return f"Valid user: {user.name}, {user.age}, {user.email}"
      ```

      ### Comprehensive Type Safety and Validation Guide

      Type safety and validation are critical for building robust FastMCP tools. This section provides a comprehensive guide to using type hints and Pydantic validation effectively.

      #### Type Hints for Parameters and Return Values

      Always use type hints for all parameters and return values:

      ```python
      from typing import Dict, List, Optional, Union, Any, Tuple
      from mcp.server.fastmcp import FastMCP, Context, Image

      mcp = FastMCP("your_server_name")

      @mcp.tool()
      def process_data(
          input_data: Dict[str, Any],
          options: Optional[List[str]] = None,
          verbose: bool = False
      ) -> Dict[str, Any]:
          """
          Process input data with optional parameters.

          Args:
              input_data: The data to process
              options: Optional processing options
              verbose: Whether to include detailed output

          Returns:
              Dict containing the processed results
          """
          # Implementation
          result = {"processed": True, "data": input_data}
          if options:
              result["options_used"] = options
          if verbose:
              result["details"] = "Detailed processing information"
          return result
      ```

      #### Using Pydantic Models for Complex Types

      For complex parameter types, use Pydantic models:

      ```python
      from pydantic import BaseModel, Field, field_validator
      from typing import List, Optional, Dict, Any
      from datetime import datetime
      from enum import Enum

      class TaskStatus(str, Enum):
          PENDING = "pending"
          IN_PROGRESS = "in_progress"
          COMPLETED = "completed"
          FAILED = "failed"

      class TaskItem(BaseModel):
          name: str = Field(..., min_length=1, max_length=100)
          priority: int = Field(default=1, ge=1, le=5)
          tags: List[str] = Field(default_factory=list)

          @field_validator('tags')
          def validate_tags(cls, v):
              return [tag.lower() for tag in v]

      class TaskList(BaseModel):
          title: str
          description: Optional[str] = None
          created_at: datetime = Field(default_factory=datetime.now)
          items: List[TaskItem] = Field(default_factory=list)
          metadata: Dict[str, Any] = Field(default_factory=dict)
          status: TaskStatus = TaskStatus.PENDING

      @mcp.tool()
      def create_task_list(task_list: TaskList) -> Dict[str, Any]:
          """
          Create a new task list.

          Args:
              task_list: The task list to create

          Returns:
              Dict containing the created task list information
          """
          # Implementation
          return {
              "id": "task_list_123",
              "created": True,
              "task_list": task_list.model_dump()
          }
      ```

      #### Advanced Validation with Annotated Types

      Use `Annotated` for adding metadata to type hints:

      ```python
      from typing import Annotated, List, Dict, Any
      from pydantic import Field, field_validator, BeforeValidator
      import re

      # Custom validator function
      def validate_email_format(email: str) -> str:
          if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
              raise ValueError("Invalid email format")
          return email.lower()

      # Type with multiple validators
      EmailType = Annotated[
          str,
          BeforeValidator(validate_email_format),
          Field(min_length=5, max_length=100)
      ]

      @mcp.tool()
      def register_user(
          username: Annotated[str, Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")],
          email: EmailType,
          age: Annotated[int, Field(ge=18, lt=120)],
          interests: Annotated[List[str], Field(min_length=1, max_length=10)]
      ) -> Dict[str, Any]:
          """
          Register a new user with validated fields.

          Args:
              username: Username (alphanumeric and underscore only)
              email: Valid email address
              age: User age (must be 18 or older)
              interests: List of user interests

          Returns:
              Dict containing the registration result
          """
          # Implementation
          return {
              "success": True,
              "user_id": "user_123",
              "username": username,
              "email": email,
              "age": age,
              "interests": interests
          }
      ```

      #### Nested Validation with Model Composition

      For complex nested structures, compose models:

      ```python
      from pydantic import BaseModel, Field, field_validator
      from typing import List, Dict, Any, Optional
      from datetime import datetime

      class Address(BaseModel):
          street: str
          city: str
          state: str
          postal_code: str
          country: str = "US"

          @field_validator('postal_code')
          def validate_postal_code(cls, v, info):
              country = info.data.get('country', 'US')
              if country == 'US' and not re.match(r'^\d{5}(-\d{4})?$', v):
                  raise ValueError("Invalid US postal code")
              return v

      class ContactInfo(BaseModel):
          email: str
          phone: Optional[str] = None
          address: Address

      class User(BaseModel):
          id: Optional[str] = None
          name: str
          contact: ContactInfo
          created_at: datetime = Field(default_factory=datetime.now)
          metadata: Dict[str, Any] = Field(default_factory=dict)

      @mcp.tool()
      def create_user_profile(user: User) -> Dict[str, Any]:
          """
          Create a user profile with nested validation.

          Args:
              user: The user profile to create

          Returns:
              Dict containing the created user profile
          """
          # Implementation
          return {
              "success": True,
              "user_id": "user_456",
              "profile": user.model_dump()
          }
      ```

      #### Union Types and Discriminated Unions

      For parameters that can accept multiple types:

      ```python
      from typing import Union, Dict, List, Any, Literal
      from pydantic import BaseModel, Field

      class TextInput(BaseModel):
          type: Literal["text"] = "text"
          content: str

      class FileInput(BaseModel):
          type: Literal["file"] = "file"
          file_path: str
          encoding: str = "utf-8"

      class UrlInput(BaseModel):
          type: Literal["url"] = "url"
          url: str
          headers: Dict[str, str] = Field(default_factory=dict)

      # Union type for input
      InputType = Union[TextInput, FileInput, UrlInput]

      @mcp.tool()
      def process_input(input_data: InputType) -> Dict[str, Any]:
          """
          Process different types of input data.

          Args:
              input_data: The input data to process (text, file, or URL)

          Returns:
              Dict containing the processing results
          """
          # Implementation based on input type
          if isinstance(input_data, TextInput):
              return {"source": "text", "length": len(input_data.content)}
          elif isinstance(input_data, FileInput):
              return {"source": "file", "path": input_data.file_path}
          elif isinstance(input_data, UrlInput):
              return {"source": "url", "url": input_data.url}
          else:
              # This should never happen due to Pydantic validation
              raise ValueError(f"Unsupported input type: {type(input_data)}")
      ```

      #### Validation Best Practices

      1. **Always Use Type Hints**: Include type hints for all parameters and return values
      2. **Be Specific**: Use the most specific type possible (e.g., `List[str]` instead of just `List`)
      3. **Document Constraints**: Include validation constraints in docstrings
      4. **Use Pydantic Models**: For complex types, create dedicated Pydantic models
      5. **Validate Early**: Catch invalid inputs as early as possible
      6. **Provide Clear Error Messages**: Ensure validation errors are clear and actionable
      7. **Use Annotated for Metadata**: Combine type hints with validation metadata using `Annotated`
      8. **Consider Performance**: For high-volume tools, optimize validation logic
      9. **Test Validation Logic**: Write tests specifically for validation edge cases

      ## Context Usage

      Tools can request a Context object to access MCP capabilities:

      ```python
      from mcp.server.fastmcp import FastMCP, Context

      mcp = FastMCP("your_server_name")

      @mcp.tool()
      def tool_with_context(param1: str, ctx: Context) -> str:
          """Tool that uses context for logging and progress reporting."""
          ctx.info(f"Processing {param1}")
          return f"Processed {param1}"
      ```

      The Context parameter:

      * Can have any name as long as it's typed as `Context`
      * Is automatically injected when the tool is called
      * Provides access to logging, progress reporting, resource access, request information, and the session.

      ## Async Tools

      For long-running operations, use async tools:

      ```python
      import asyncio
      from mcp.server.fastmcp import FastMCP, Context

      mcp = FastMCP("your_server_name")

      @mcp.tool()
      async def async_tool(param1: str, ctx: Context) -> str:
          """Asynchronous tool implementation."""
          # Report progress to the client
          await ctx.report_progress(50, 100)

          # Perform async operations
          await asyncio.sleep(1)

          return f"Processed {param1}"
      ```

      ## Return Value Handling

      FastMCP automatically converts return values to MCP content types:

      1.  **Strings**: Converted to `TextContent`
      2.  **Images**: Use the `Image` helper class
      3.  **Dictionaries/Objects**: Converted to JSON strings then to `TextContent`
      4.  **Lists/Tuples**: Each item is converted and flattened
      5.  **None**: Returns empty content list

      ### Image Return Example

      ```python
      from mcp.server.fastmcp import FastMCP, Image

      mcp = FastMCP("your_server_name")

      @mcp.tool()
      def generate_image(width: int, height: int) -> Image:
          """Generate an image with the specified dimensions."""
          # Create or load an image
          image_path = create_image(width, height)
          return Image(path=image_path)
      ```

      ### Multiple Content Return Example

      ```python
      from mcp.server.fastmcp import FastMCP

      mcp = FastMCP("your_server_name")

      @mcp.tool()
      def mixed_content() -> list:
          """Return multiple content items."""
          return [
              "Text content",
              Image(path="path/to/image.png"),
              {"key": "value"}  # Will be converted to JSON string
          ]
      ```

      ## Error Handling

      Tools should use exceptions to indicate errors:

      ```python
      from mcp.server.fastmcp import FastMCP, Context

      mcp = FastMCP("your_server_name")

      @mcp.tool()
      def tool_with_error_handling(param1: str, ctx: Context) -> str:
          """Tool with proper error handling."""
          try:
              # Implementation that might fail
              result = process_data(param1)
              return result
          except ValueError as e:
              # Client will receive this error message
              await ctx.warning(f"Processing error: {e}")
              return f"Could not process data: {e}"
          except Exception as e:
              # Log unexpected errors
              logger.error(f"Unexpected error: {e}")
              raise RuntimeError(f"An unexpected error occurred: {e}")
      ```

      Errors are returned to the client with:

      * The error message as text content
      * `isError` flag set to `True`

      ## Advanced Error Handling and Status Tracking

      The MCP Python SDK provides robust mechanisms for managing tool call failures and tracking operation status. This section outlines comprehensive implementation strategies for error handling, progress reporting, and integration with MCP's standardized protocols.

      ### Structured Error Responses

      MCP tools should return structured error responses with `isError: True` per the specification. The SDK simplifies this through Pythonic error handling patterns:

      ```python
      from mcp.server.fastmcp import FastMCP, Context
      from typing import Dict, Any, Optional

      mcp = FastMCP("Error Handling Demo")

      @mcp.tool()
      def calculate_bmi(weight_kg: float, height_m: float) -> Dict[str, Any]:
          """
          Calculate BMI with comprehensive error handling.

          Args:
              weight_kg: Weight in kilograms
              height_m: Height in meters

          Returns:
              Dictionary containing BMI or error information
          """
          try:
              if weight_kg <= 0:
                  raise ValueError("Weight must be positive")
              if height_m <= 0:
                  raise ValueError("Height must be positive")

              return {"bmi": weight_kg / (height_m ** 2)}
          except ZeroDivisionError:
              return {
                  "isError": True,
                  "errorType": "ZeroDivisionError",
                  "message": "Height cannot be zero"
              }
          except ValueError as e:
              return {
                  "isError": True,
                  "errorType": "ValidationError",
                  "message": str(e)
              }
          except Exception as e:
              return {
                  "isError": True,
                  "errorType": "UnexpectedError",
                  "message": f"An unexpected error occurred: {str(e)}"
              }
      ```

      This implementation ensures errors are explicitly flagged and categorized, enabling downstream systems to differentiate between validation errors, runtime exceptions, and other failures.

      ### Centralized Error Handling with Decorators

      Use decorators to standardize error handling across multiple tools:

      ```python
      from functools import wraps
      from typing import Callable, Any, Dict, TypeVar, cast

      T = TypeVar('T')

      def error_handler(func: Callable[..., T]) -> Callable[..., Dict[str, Any]]:
          """
          Decorator that wraps a function to standardize error handling.

          Args:
              func: The function to wrap with error handling

          Returns:
              Wrapped function that catches exceptions and returns standardized error responses
          """
          @wraps(func)
          def wrapper(*args: Any, **kwargs: Any) -> Dict[str, Any]:
              try:
                  result = func(*args, **kwargs)
                  return cast(Dict[str, Any], result)
              except ValueError as e:
                  return {
                      "isError": True,
                      "errorType": "ValidationError",
                      "message": str(e)
                  }
              except Exception as e:
                  return {
                      "isError": True,
                      "errorType": type(e).__name__,
                      "message": str(e)
                  }
          return wrapper

      @mcp.tool()
      @error_handler
      def sensitive_operation(input_data: str) -> Dict[str, Any]:
          """
          Handle risky operations with automatic error capture.

          Args:
              input_data: The input data to process

          Returns:
              Dictionary containing operation results or error information
          """
          if not input_data:
              raise ValueError("Input cannot be empty")
          # Implementation...
          return {"status": "success", "result": f"Processed: {input_data}"}
      ```

      This pattern ensures consistent error formatting without duplicating try-except blocks.

      ### Asynchronous Error Handling

      For async operations, combine `asyncio` with MCP's error model:

      ```python
      import httpx
      from mcp.server.fastmcp import FastMCP, Context
      from typing import Dict, Any

      mcp = FastMCP("Async Error Handling Demo")

      @mcp.tool()
      async def async_fetch_data(url: str, ctx: Context) -> Dict[str, Any]:
          """
          Fetch data with progress and error handling.

          Args:
              url: The URL to fetch data from
              ctx: MCP context for progress reporting

          Returns:
              Dictionary containing fetched data or error information
          """
          try:
              await ctx.info(f"Fetching data from {url}")
              async with httpx.AsyncClient() as client:
                  response = await client.get(url)
                  response.raise_for_status()
                  await ctx.report_progress(1, 1)
                  return {"data": response.json()}
          except httpx.HTTPStatusError as e:
              await ctx.error(f"HTTP error: {e.response.status_code}")
              await ctx.report_progress(1, 1)
              return {
                  "isError": True,
                  "errorType": "HTTPStatusError",
                  "message": f"HTTP {e.response.status_code}: {e.response.reason_phrase}",
                  "details": {
                      "status_code": e.response.status_code,
                      "url": str(e.request.url)
                  }
              }
          except httpx.RequestError as e:
              await ctx.error(f"Request error: {str(e)}")
              await ctx.report_progress(1, 1)
              return {
                  "isError": True,
                  "errorType": "RequestError",
                  "message": str(e)
              }
          except Exception as e:
              await ctx.error(f"Unexpected error: {str(e)}")
              await ctx.report_progress(1, 1)
              return {
                  "isError": True,
                  "errorType": "UnexpectedError",
                  "message": str(e)
              }
      ```

      ### Comprehensive Status Tracking

      The `Context` object provides methods for detailed progress reporting and logging during tool execution:

      ```python
      import asyncio
      from mcp.server.fastmcp import FastMCP, Context
      from typing import List, Dict, Any

      mcp = FastMCP("Status Tracking Demo")

      @mcp.tool()
      async def long_task(files: List[str], ctx: Context) -> Dict[str, Any]:
          """
          Process files with detailed progress updates.

          Args:
              files: List of files to process
              ctx: MCP context for progress reporting

          Returns:
              Dictionary containing processing results
          """
          total = len(files)
          await ctx.info(f"Processing {total} files")

          results = []
          errors = []

          for i, file in enumerate(files):
              try:
                  # Update progress with current file information
                  await ctx.info(f"Processing file {i+1}/{total}: {file}")
                  await ctx.report_progress(i + 1, total)

                  # Simulate processing time
                  await asyncio.sleep(0.5)

                  # Simulate processing logic
                  result = f"Processed {file}"
                  results.append(result)

              except Exception as e:
                  await ctx.error(f"Error processing {file}: {str(e)}")
                  errors.append({"file": file, "error": str(e)})

          # Final status report
          if errors:
              await ctx.warning(f"Completed with {len(errors)} errors")
          else:
              await ctx.info("Processing complete - all files successful")

          return {
              "status": "completed",
              "processed": len(results),
              "errors": len(errors),
              "results": results,
              "error_details": errors
          }
      ```

      Key features:
      - **Progress tokens**: Automatically managed via `report_progress` when a client includes a `progressToken` in requests.
      - **Logging**: `ctx.info`, `ctx.warning`, and `ctx.error` provide standardized logging channels visible in MCP Inspector.
      - **Detailed status**: Return comprehensive status information including success and error counts.

      ### Progress Granularity for Multi-Stage Operations

      For multi-stage operations, use intermediate progress updates:

      ```python
      from mcp.server.fastmcp import FastMCP, Context
      from typing import Dict, Any

      mcp = FastMCP("Multi-Phase Demo")

      @mcp.tool()
      async def multi_phase_operation(ctx: Context) -> Dict[str, Any]:
          """
          Track progress across multiple phases with detailed reporting.

          Args:
              ctx: MCP context for progress reporting

          Returns:
              Dictionary containing operation results
          """
          # Phase 1: Data collection
          await ctx.info("Starting phase 1/3: Data collection")
          await ctx.report_progress(1, 3)
          # Phase 1 implementation
          await asyncio.sleep(1)

          # Phase 2: Processing
          await ctx.info("Starting phase 2/3: Data processing")
          await ctx.report_progress(2, 3)
          # Phase 2 implementation
          await asyncio.sleep(1)

          # Phase 3: Finalization
          await ctx.info("Starting phase 3/3: Finalization")
          await ctx.report_progress(3, 3)
          # Phase 3 implementation
          await asyncio.sleep(0.5)

          await ctx.info("Operation completed successfully")
          return {
              "status": "completed",
              "phases_completed": 3,
              "result": "Operation successful"
          }
      ```

      ### Error Propagation in Tool Pipelines

      Handle errors in tool chains while maintaining progress:

      ```python
      from mcp.server.fastmcp import FastMCP, Context
      from typing import Dict, Any, Optional

      mcp = FastMCP("Pipeline Demo")

      @mcp.tool()
      async def pipeline_tool(input_data: str, ctx: Context) -> Dict[str, Any]:
          """
          Execute multiple tools with error recovery and detailed status tracking.

          Args:
              input_data: The input data to process
              ctx: MCP context for progress reporting

          Returns:
              Dictionary containing pipeline results or error information
          """
          pipeline_status = {
              "steps_completed": 0,
              "steps_total": 3,
              "current_step": "initialization",
              "errors": []
          }

          # Step 1: Validation
          try:
              await ctx.info("Step 1/3: Validating input data")
              pipeline_status["current_step"] = "validation"

              if not input_data:
                  raise ValueError("Input data cannot be empty")

              # Simulate validation
              await asyncio.sleep(0.5)

              pipeline_status["steps_completed"] = 1
              await ctx.report_progress(1, 3)

          except Exception as e:
              await ctx.error(f"Validation failed: {str(e)}")
              pipeline_status["errors"].append({
                  "step": "validation",
                  "error": str(e)
              })
              return {
                  "isError": True,
                  "errorType": "ValidationError",
                  "message": f"Pipeline failed at validation step: {str(e)}",
                  "pipeline_status": pipeline_status
              }

          # Step 2: Processing
          try:
              await ctx.info("Step 2/3: Processing data")
              pipeline_status["current_step"] = "processing"

              # Simulate processing
              await asyncio.sleep(1)
              processed_data = f"Processed: {input_data}"

              pipeline_status["steps_completed"] = 2
              await ctx.report_progress(2, 3)

          except Exception as e:
              await ctx.error(f"Processing failed: {str(e)}")
              pipeline_status["errors"].append({
                  "step": "processing",
                  "error": str(e)
              })
              return {
                  "isError": True,
                  "errorType": "ProcessingError",
                  "message": f"Pipeline failed at processing step: {str(e)}",
                  "pipeline_status": pipeline_status
              }

          # Step 3: Finalization
          try:
              await ctx.info("Step 3/3: Finalizing results")
              pipeline_status["current_step"] = "finalization"

              # Simulate finalization
              await asyncio.sleep(0.5)
              final_result = f"Finalized: {processed_data}"

              pipeline_status["steps_completed"] = 3
              await ctx.report_progress(3, 3)

          except Exception as e:
              await ctx.error(f"Finalization failed: {str(e)}")
              pipeline_status["errors"].append({
                  "step": "finalization",
                  "error": str(e)
              })
              return {
                  "isError": True,
                  "errorType": "FinalizationError",
                  "message": f"Pipeline failed at finalization step: {str(e)}",
                  "pipeline_status": pipeline_status
              }

          # All steps completed successfully
          await ctx.info("Pipeline completed successfully")
          return {
              "status": "success",
              "result": final_result,
              "pipeline_status": pipeline_status
          }
      ```

      ### Testing Error Handling and Status Tracking

      ```python
      import pytest
      from mcp.server.fastmcp import FastMCP, Context
      from mcp.server.fastmcp.testing import client_session
      from typing import Dict, Any, List, Tuple

      @pytest.mark.anyio
      async def test_error_handling_and_status_tracking():
          """Test comprehensive error handling and status tracking."""
          server = FastMCP()

          @server.tool()
          async def process_with_status(
              items: List[str],
              fail_on_item: Optional[str] = None,
              ctx: Context
          ) -> Dict[str, Any]:
              """Process items with status tracking and optional failure."""
              results = []
              errors = []
              total = len(items)

              for i, item in enumerate(items):
                  await ctx.info(f"Processing item {i+1}/{total}: {item}")
                  await ctx.report_progress(i + 1, total)

                  # Simulate processing with optional failure
                  if item == fail_on_item:
                      await ctx.error(f"Failed to process item: {item}")
                      errors.append({"item": item, "reason": "Requested failure"})
                  else:
                      await asyncio.sleep(0.01)
                      results.append(f"Processed: {item}")

              if errors:
                  return {
                      "isError": len(errors) == total,  # Only mark as error if all items failed
                      "status": "partial_success" if results else "failed",
                      "processed": len(results),
                      "failed": len(errors),
                      "results": results,
                      "errors": errors
                  }
              else:
                  return {
                      "status": "success",
                      "processed": len(results),
                      "results": results
                  }

          # Capture progress updates and log messages
          progress_updates: List[Tuple[int, int]] = []
          log_messages: List[Tuple[str, str]] = []

          async with client_session(server._mcp_server) as client:
              # Set up callbacks
              async def progress_callback(progress: int, total: int) -> None:
                  progress_updates.append((progress, total))

              async def log_callback(level: str, message: str, logger: str = None) -> None:
                  log_messages.append((level, message))

              # Register callbacks
              client.session.on_progress = progress_callback
              client.session.on_log_message = log_callback

              # Test successful processing
              items = ["item1", "item2", "item3"]
              result = await client.call_tool(
                  "process_with_status",
                  {"items": items}
              )

              assert not result.isError
              assert "success" in result.content[0].text
              assert len(progress_updates) == 3
              assert progress_updates[-1] == (3, 3)

              # Reset tracking
              progress_updates.clear()
              log_messages.clear()

              # Test with failure
              result = await client.call_tool(
                  "process_with_status",
                  {"items": items, "fail_on_item": "item2"}
              )

              # Should be partial success (not marked as error)
              assert not result.isError
              assert "partial_success" in result.content[0].text

              # Check for error log
              error_logs = [msg for level, msg in log_messages if level == "error"]
              assert len(error_logs) == 1
              assert "Failed to process item: item2" in error_logs[0]
      ```

      ### Debugging with MCP Inspector

      The SDK's debugging tools enable real-time monitoring of errors and status:

      ```bash
      # Launch MCP Inspector for detailed error/status tracking
      mcp dev server.py
      ```

      Key features:
      - **Error inspection**: View complete error stacks and response payloads.
      - **Progress visualization**: Track real-time progress updates for long-running operations.
      - **Tool call replay**: Re-execute failed calls with modified inputs for debugging.
      - **Log filtering**: Filter logs by level (debug, info, warning, error) for focused debugging.

      ### Error Handling and Status Tracking Best Practices

      1. **Structured Error Responses**: Always return structured error responses with `isError`, `errorType`, and `message`.
      2. **Granular Progress Updates**: Report progress at meaningful intervals, especially for long-running operations.
      3. **Informative Logging**: Use appropriate log levels (debug, info, warning, error) to provide context.
      4. **Graceful Degradation**: Design tools to continue partial processing when possible, rather than failing completely.
      5. **Detailed Status Information**: Return comprehensive status information including success counts, error counts, and specific error details.
      6. **Error Categorization**: Categorize errors by type to help clients handle them appropriately.
      7. **Context Preservation**: Include relevant context in error messages to aid debugging.
      8. **Async Error Handling**: Use proper async error handling patterns for asynchronous tools.
      9. **Pipeline Recovery**: Implement recovery strategies for multi-step pipelines.
      10. **Testing Error Paths**: Thoroughly test both success and error paths in your tools.

      ## Context Capabilities

      The Context object provides these capabilities:

      ### Logging

      ```python
      from mcp.server.fastmcp import Context

      @mcp.tool()
      async def log_message(ctx: Context):
          # Send log messages to the client
          await ctx.debug("Debug message")
          await ctx.info("Info message")
          await ctx.warning("Warning message")
          await ctx.error("Error message")
      ```

      ### Progress Reporting

      ```python
      from mcp.server.fastmcp import Context

      @mcp.tool()
      async def report_progress(ctx: Context):
          # Report progress (current, total)
          await ctx.report_progress(50, 100)
      ```

      ### Resource Access

      ```python
      from mcp.server.fastmcp import Context

      @mcp.tool()
      async def read_resource(ctx: Context):
          # Read a resource by URI
          data = await ctx.read_resource("resource://example")
      ```

      ### Request Information

      ```python
      from mcp.server.fastmcp import Context

      @mcp.tool()
      async def get_request_info(ctx: Context):
          # Get request information
          request_id = ctx.request_id
          client_id = ctx.client_id
      ```

      ## Best Practices

      1.  **Descriptive Names**: Use clear, descriptive names for tools and parameters.
      2.  **Comprehensive Docstrings**: Include purpose, parameters, and return value details.
      3.  **Type Annotations**: Always use proper type annotations for all parameters and return values. Emphasize that all parameters and return types should have type hints.
      4.  **Default Values**: Provide sensible defaults for optional parameters.
      5.  **Validation Examples**: Include more examples of using Pydantic for validation, including `Annotated` and `field_validator`.
      6.  **Error Messages**: Return clear, actionable error messages.
      7.  **Progress Updates**: For long-running operations, report progress.
      8.  **Resource Cleanup**: Properly clean up resources (files, connections, etc.).
      9.  **Testing**: Write comprehensive tests for all tools.

      ## Testing Tools

      Test tools using the client_session helper:

      ```python
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
              assert len(result.content) == 1
              assert result.content[0].text == "Processed test"
      ```

      ### Comprehensive Testing Guide

      Testing is crucial for ensuring your FastMCP tools work correctly. Here's a comprehensive guide to testing different types of tools:

      #### Testing Synchronous Tools

      ```python
      import pytest
      from mcp.server.fastmcp import FastMCP
      from mcp.server.fastmcp.testing import client_session
      from typing import Dict, Any

      @pytest.mark.anyio
      async def test_sync_tool_with_validation():
          """Test a synchronous tool with input validation."""
          server = FastMCP()

          @server.tool()
          def validate_user(name: str, age: int) -> Dict[str, Any]:
              """Validate user data."""
              if len(name) < 2:
                  raise ValueError("Name must be at least 2 characters")
              if age < 0 or age > 120:
                  raise ValueError("Age must be between 0 and 120")
              return {"status": "valid", "name": name, "age": age}

          async with client_session(server._mcp_server) as client:
              # Test valid input
              result = await client.call_tool("validate_user", {"name": "Alice", "age": 30})
              assert not result.isError
              assert "valid" in result.content[0].text

              # Test invalid input - name too short
              result = await client.call_tool("validate_user", {"name": "A", "age": 30})
              assert result.isError
              assert "Name must be at least 2 characters" in result.content[0].text

              # Test invalid input - age out of range
              result = await client.call_tool("validate_user", {"name": "Bob", "age": 150})
              assert result.isError
              assert "Age must be between 0 and 120" in result.content[0].text
      ```

      #### Testing Asynchronous Tools

      ```python
      import pytest
      import asyncio
      from mcp.server.fastmcp import FastMCP
      from mcp.server.fastmcp.testing import client_session

      @pytest.mark.anyio
      async def test_async_tool():
          """Test an asynchronous tool with delay."""
          server = FastMCP()

          @server.tool()
          async def delayed_response(delay_seconds: float, message: str) -> str:
              """Return a message after a delay."""
              await asyncio.sleep(delay_seconds)
              return f"Delayed {delay_seconds}s: {message}"

          async with client_session(server._mcp_server) as client:
              # Test with short delay
              result = await client.call_tool(
                  "delayed_response",
                  {"delay_seconds": 0.1, "message": "Hello"}
              )
              assert not result.isError
              assert "Delayed 0.1s: Hello" in result.content[0].text

              # Test with timeout
              with pytest.raises(asyncio.TimeoutError):
                  # Set a short timeout to test timeout handling
                  await asyncio.wait_for(
                      client.call_tool(
                          "delayed_response",
                          {"delay_seconds": 1.0, "message": "Timeout"}
                      ),
                      timeout=0.5
                  )
      ```

      #### Testing Tools with Context

      ```python
      import pytest
      from mcp.server.fastmcp import FastMCP, Context
      from mcp.server.fastmcp.testing import client_session
      from typing import List, Tuple, Any

      @pytest.mark.anyio
      async def test_tool_with_context():
          """Test a tool that uses the Context object."""
          server = FastMCP()

          @server.tool()
          async def logging_tool(message: str, level: str, ctx: Context) -> str:
              """Log a message with the specified level."""
              if level == "debug":
                  await ctx.debug(message)
              elif level == "info":
                  await ctx.info(message)
              elif level == "warning":
                  await ctx.warning(message)
              elif level == "error":
                  await ctx.error(message)
              else:
                  raise ValueError(f"Unknown log level: {level}")
              return f"Logged: {message} at {level} level"

          # Capture log messages
          log_messages: List[Tuple[str, str, Any]] = []

          async with client_session(server._mcp_server) as client:
              # Set up logging callback
              async def log_callback(level: str, message: str, logger: str = None) -> None:
                  log_messages.append((level, message, logger))

              # Register callback
              client.session.on_log_message = log_callback

              # Test different log levels
              levels = ["debug", "info", "warning", "error"]
              for level in levels:
                  message = f"Test {level} message"
                  result = await client.call_tool(
                      "logging_tool",
                      {"message": message, "level": level}
                  )
                  assert not result.isError
                  assert f"Logged: {message} at {level} level" in result.content[0].text

              # Verify log messages were captured
              assert len(log_messages) == len(levels)
              for i, level in enumerate(levels):
                  assert log_messages[i][0] == level
                  assert f"Test {level} message" in log_messages[i][1]
      ```

      #### Testing Progress Reporting

      ```python
      import pytest
      import asyncio
      from mcp.server.fastmcp import FastMCP, Context
      from mcp.server.fastmcp.testing import client_session
      from typing import List, Tuple, Optional

      @pytest.mark.anyio
      async def test_progress_reporting():
          """Test a tool that reports progress."""
          server = FastMCP()

          @server.tool()
          async def process_with_progress(steps: int, ctx: Context) -> str:
              """Process a task with progress reporting."""
              for i in range(steps):
                  # Report progress
                  await ctx.report_progress(i, steps)
                  # Do some work
                  await asyncio.sleep(0.01)
              # Final progress
              await ctx.report_progress(steps, steps)
              return f"Completed {steps} steps"

          # Capture progress updates
          progress_updates: List[Tuple[int, Optional[int]]] = []

          async with client_session(server._mcp_server) as client:
              # Set up progress callback
              async def progress_callback(progress: int, total: Optional[int] = None) -> None:
                  progress_updates.append((progress, total))

              # Register callback
              client.session.on_progress = progress_callback

              # Test with 5 steps
              result = await client.call_tool("process_with_progress", {"steps": 5})
              assert not result.isError
              assert "Completed 5 steps" in result.content[0].text

              # Verify progress updates
              assert len(progress_updates) == 6  # 0 through 4, plus final update
              assert progress_updates[0] == (0, 5)
              assert progress_updates[-1] == (5, 5)
      ```

      #### Testing Error Handling

      ```python
      import pytest
      from mcp.server.fastmcp import FastMCP
      from mcp.server.fastmcp.testing import client_session

      @pytest.mark.anyio
      async def test_error_handling():
          """Test a tool with error handling."""
          server = FastMCP()

          @server.tool()
          def division_tool(numerator: float, denominator: float) -> float:
              """Divide two numbers with error handling."""
              try:
                  if denominator == 0:
                      raise ZeroDivisionError("Cannot divide by zero")
                  return numerator / denominator
              except Exception as e:
                  # Re-raise with clear message
                  raise ValueError(f"Division error: {str(e)}")

          async with client_session(server._mcp_server) as client:
              # Test valid division
              result = await client.call_tool(
                  "division_tool",
                  {"numerator": 10.0, "denominator": 2.0}
              )
              assert not result.isError
              assert "5.0" in result.content[0].text

              # Test division by zero
              result = await client.call_tool(
                  "division_tool",
                  {"numerator": 10.0, "denominator": 0.0}
              )
              assert result.isError
              assert "Division error: Cannot divide by zero" in result.content[0].text
      ```

      #### Testing Complex Return Types

      ```python
      import pytest
      from mcp.server.fastmcp import FastMCP, Image
      from mcp.server.fastmcp.testing import client_session
      from typing import List, Dict, Any, Union
      import tempfile
      import os

      @pytest.mark.anyio
      async def test_complex_return_types():
          """Test a tool that returns complex data types."""
          server = FastMCP()

          @server.tool()
          def mixed_return_types() -> List[Union[str, Dict[str, Any], Image]]:
              """Return multiple content types."""
              # Create a temporary image file
              with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                  tmp_path = tmp.name
                  # In a real test, you might create an actual image here
                  with open(tmp_path, "wb") as f:
                      f.write(b"MOCK_IMAGE_DATA")

              # Return mixed content types
              return [
                  "Text content",
                  {"key1": "value1", "key2": 42},
                  Image(path=tmp_path)
              ]

          async with client_session(server._mcp_server) as client:
              result = await client.call_tool("mixed_return_types", {})
              assert not result.isError

              # Check number of content items
              assert len(result.content) == 3

              # Check text content
              assert result.content[0].text == "Text content"

              # Check JSON content
              assert "key1" in result.content[1].text
              assert "value1" in result.content[1].text

              # Check image content
              assert result.content[2].type == "image"
              assert result.content[2].mimeType == "image/png"

              # Clean up temporary file
              os.unlink(tmp_path)
      ```

      #### Integration Testing with Multiple Tools

      ```python
      import pytest
      from mcp.server.fastmcp import FastMCP, Context
      from mcp.server.fastmcp.testing import client_session
      from typing import Dict, Any

      @pytest.mark.anyio
      async def test_tool_integration():
          """Test integration between multiple tools."""
          server = FastMCP()

          @server.tool()
          def generate_data(count: int) -> Dict[str, Any]:
              """Generate test data."""
              return {
                  "items": [{"id": i, "value": f"Item {i}"} for i in range(count)]
              }

          @server.tool()
          def process_data(data: Dict[str, Any], ctx: Context) -> str:
              """Process data generated by another tool."""
              items = data.get("items", [])
              await ctx.info(f"Processing {len(items)} items")

              result = ", ".join([item["value"] for item in items])
              return f"Processed items: {result}"

          async with client_session(server._mcp_server) as client:
              # First call generate_data
              gen_result = await client.call_tool("generate_data", {"count": 3})
              assert not gen_result.isError

              # Extract the data from the result
              import json
              data = json.loads(gen_result.content[0].text)

              # Then call process_data with the result
              proc_result = await client.call_tool("process_data", {"data": data})
              assert not proc_result.isError
              assert "Processed items: Item 0, Item 1, Item 2" in proc_result.content[0].text
      ```

      #### Testing Best Practices

      1. **Isolate Tests**: Each test should focus on a specific aspect of functionality
      2. **Use Fixtures**: Create reusable fixtures for common setup
      3. **Test Edge Cases**: Include tests for boundary conditions and error cases
      4. **Mock External Dependencies**: Use mocks for external services and resources
      5. **Verify All Outputs**: Check return values, logs, and progress updates
      6. **Clean Up Resources**: Ensure all resources are properly cleaned up after tests
      7. **Use Type Annotations**: Add proper typing to all test functions
      8. **Include Docstrings**: Document the purpose of each test

      ## Advanced FastMCP Tool Development

      ### Dependency Injection

      ```python
      from mcp.server.fastmcp import FastMCP, Context

      mcp = FastMCP("your_server_name")

      class Database:
          def query(self, param):
              return f"Query result for: {param}"

      # Create a database instance (in a real app, you might get this from a config)
      db = Database()

      # Add lifespan support for startup/shutdown with strong typing
      from dataclasses import dataclass
      from typing import AsyncIterator
      from contextlib import asynccontextmanager

      @dataclass
      class AppContext:
          db: Database  # Replace with your actual DB type

      @asynccontextmanager
      async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
          """Manage application lifecycle with type-safe context"""
          try:
              # Initialize on startup
              # In this example, we're simply passing the db instance
              yield AppContext(db=db)
          finally:
              # Cleanup on shutdown
              pass

      # Pass lifespan to server
      mcp = FastMCP("My App", lifespan=app_lifespan)

      @mcp.tool()
      async def tool_with_dependencies(param: str, ctx: Context) -> str:
          """Tool that uses dependencies via context."""
          # Access shared resources
          db = ctx.request_context.lifespan_context.db

          # Use the dependency
          result = db.query(param)

          return result
      ```

      ### Streaming Results

      ```python
      import asyncio
      from mcp.server.fastmcp import FastMCP, Context

      mcp = FastMCP("your_server_name")

      @mcp.tool()
      async def stream_results(count: int, ctx: Context) -> list:
          """Generate results incrementally with progress updates."""
          results = []

          for i in range(count):
              # Report progress
              await ctx.report_progress(i, count)

              # Generate result
              result = f"Result {i}"
              results.append(result)

              # Log intermediate result
              await ctx.info(f"Generated: {result}")

              # Simulate processing time
              await asyncio.sleep(0.5)

          return results
      ```

      ### Resource Management

      ```python
      import contextlib
      from tempfile import NamedTemporaryFile
      from mcp.server.fastmcp import FastMCP, Context

      mcp = FastMCP("your_server_name")

      @mcp.tool()
      async def tool_with_resource_management(data: str, ctx: Context) -> str:
          """Tool that properly manages resources."""
          # Create temporary resources
          with contextlib.closing(NamedTemporaryFile(mode='w+', suffix='.txt')) as temp_file:
              try:
                  # Write data to file
                  temp_file.write(data)
                  temp_file.flush()

                  # Process the file
                  result = await process_file(temp_file.name)

                  return result
              except Exception as e:
                  await ctx.error(f"Error processing file: {e}")
                  raise
          # File is automatically cleaned up when the with block exits
      ```
