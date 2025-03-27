---
description:
globs:
alwaysApply: false
---
# dpytest Error Handling
Comprehensive guide to dpytest's error handling and custom exceptions
Documentation of dpytest's error handling system, custom exceptions, and error recovery patterns.

<rule>
name: dpytest_errors
description: Guide to using dpytest's error handling system and custom exceptions
filters:
  # Match Python files
  - type: file_extension
    pattern: "\\.py$"
  # Match test files
  - type: file_path
    pattern: "tests?/"
  # Match error-related content
  - type: content
    pattern: "(?i)(error|exception|raise|try|except|finally|catch|handle)"

actions:
  - type: suggest
    message: |
      # dpytest Error Handling System

      Comprehensive guide to handling errors and exceptions in dpytest.

      ## Core Exceptions

      ### 1. Base Exception

      ```python
      from typing import Optional, Any

      class DPyTestError(Exception):
          """Base exception for all dpytest errors."""

          def __init__(
              self,
              message: str,
              *args: Any,
              original_error: Optional[Exception] = None
          ) -> None:
              """
              Initialize the base error.

              Args:
                  message: Error message
                  *args: Additional arguments
                  original_error: Original exception if wrapping
              """
              super().__init__(message, *args)
              self.original_error = original_error
      ```

      ### 2. State Management Errors

      ```python
      class StateError(DPyTestError):
          """Error in test state management."""

          pass

      class StateNotFoundError(StateError):
          """Requested state does not exist."""

          def __init__(self, state_id: str) -> None:
              """
              Initialize state not found error.

              Args:
                  state_id: ID of state that wasn't found
              """
              super().__init__(f"State '{state_id}' not found")

      class StateCorruptedError(StateError):
          """Test state is corrupted and cannot be used."""

          def __init__(self, reason: str) -> None:
              """
              Initialize state corrupted error.

              Args:
                  reason: Reason for state corruption
              """
              super().__init__(f"State corrupted: {reason}")
      ```

      ### 3. Verification Errors

      ```python
      class VerificationError(DPyTestError):
          """Error in test verification."""

          pass

      class MessageNotFoundError(VerificationError):
          """Expected message was not found."""

          def __init__(self, content: Optional[str] = None) -> None:
              """
              Initialize message not found error.

              Args:
                  content: Optional expected message content
              """
              msg = "Message not found"
              if content:
                  msg += f": {content}"
              super().__init__(msg)

      class TimeoutError(VerificationError):
          """Operation timed out."""

          def __init__(self, operation: str, timeout: float) -> None:
              """
              Initialize timeout error.

              Args:
                  operation: Operation that timed out
                  timeout: Timeout duration in seconds
              """
              super().__init__(
                  f"Operation '{operation}' timed out after {timeout} seconds"
              )
      ```

      ### 4. Backend Errors

      ```python
      class BackendError(DPyTestError):
          """Error in backend operations."""

          pass

      class ConnectionError(BackendError):
          """Error establishing connection."""

          def __init__(self, reason: str) -> None:
              """
              Initialize connection error.

              Args:
                  reason: Reason for connection failure
              """
              super().__init__(f"Connection failed: {reason}")

      class HTTPError(BackendError):
          """Error in HTTP operations."""

          def __init__(
              self,
              status: int,
              message: str,
              endpoint: Optional[str] = None
          ) -> None:
              """
              Initialize HTTP error.

              Args:
                  status: HTTP status code
                  message: Error message
                  endpoint: Optional endpoint that failed
              """
              msg = f"HTTP {status}: {message}"
              if endpoint:
                  msg += f" (endpoint: {endpoint})"
              super().__init__(msg)
      ```

      ## Error Handling Patterns

      ### 1. Basic Error Handling

      ```python
      from typing import Optional, AsyncGenerator
      import pytest
      from discord.ext.test import errors

      async def handle_operation() -> None:
          """Handle potential operation errors."""
          try:
              await perform_operation()
          except errors.StateError as e:
              # Handle state errors
              await cleanup_state()
              raise
          except errors.VerificationError as e:
              # Handle verification errors
              log_verification_failure(e)
              raise
          except Exception as e:
              # Handle unexpected errors
              raise errors.DPyTestError(
                  "Unexpected error during operation",
                  original_error=e
              ) from e
      ```

      ### 2. Resource Cleanup

      ```python
      @pytest.fixture
      async def error_cleanup() -> AsyncGenerator[None, None]:
          """
          Ensure cleanup on error.

          Yields:
              None
          """
          try:
              yield
          except errors.StateError:
              # Clean up state on error
              await cleanup_state(full=True)
          except errors.BackendError:
              # Reset backend on error
              await reset_backend()
          except Exception:
              # Full cleanup on unexpected errors
              await full_cleanup()
              raise
      ```

      ### 3. Error Recovery

      ```python
      async def with_recovery(
          retries: int = 3,
          cleanup: bool = True
      ) -> None:
          """
          Attempt operation with recovery.

          Args:
              retries: Number of retry attempts
              cleanup: Whether to clean up on failure
          """
          for attempt in range(retries):
              try:
                  await perform_operation()
                  break
              except errors.StateError:
                  if cleanup:
                      await cleanup_state()
                  if attempt == retries - 1:
                      raise
                  continue
              except errors.ConnectionError:
                  if attempt == retries - 1:
                      raise
                  await asyncio.sleep(1 * (attempt + 1))
                  continue
      ```

      ## Best Practices

      1. **Use Custom Exceptions**
         ```python
         # Instead of generic exceptions
         raise Exception("Message not found")

         # Use specific custom exceptions
         raise errors.MessageNotFoundError("Expected: Hello World")
         ```

      2. **Proper Error Wrapping**
         ```python
         try:
             await discord_operation()
         except discord.HTTPException as e:
             raise errors.HTTPError(
                 status=e.status,
                 message=str(e),
                 endpoint=e.endpoint
             ) from e
         ```

      3. **Error Context**
         ```python
         class OperationError(errors.DPyTestError):
             """Error during operation."""

             def __init__(
                 self,
                 operation: str,
                 reason: str,
                 **context: Any
             ) -> None:
                 """
                 Initialize operation error.

                 Args:
                     operation: Operation that failed
                     reason: Failure reason
                     **context: Additional context
                 """
                 self.operation = operation
                 self.context = context
                 super().__init__(
                     f"Operation '{operation}' failed: {reason}"
                 )
         ```

      4. **Cleanup in Finally**
         ```python
         async def safe_operation() -> None:
             """Ensure cleanup even on error."""
             snapshot = None
             try:
                 snapshot = await create_snapshot()
                 await perform_operation()
             except errors.DPyTestError:
                 # Handle known errors
                 raise
             except Exception as e:
                 # Wrap unknown errors
                 raise errors.DPyTestError(
                     "Unexpected error",
                     original_error=e
                 ) from e
             finally:
                 if snapshot:
                     await snapshot.cleanup()
         ```

examples:
  - input: |
      How do I handle timeouts and state errors in my tests?
    output: |
      Here's an example combining timeout and state error handling:

      ```python
      import pytest
      from discord.ext.test import errors
      from typing import AsyncGenerator, Optional

      @pytest.fixture
      async def managed_state() -> AsyncGenerator[None, None]:
          """
          Manage test state with error handling.

          Yields:
              None
          """
          try:
              yield
          except errors.TimeoutError as e:
              # Log timeout and clean up
              logger.error(f"Operation timed out: {e}")
              await cleanup_state(full=True)
              raise
          except errors.StateError as e:
              # Log state error and attempt recovery
              logger.error(f"State error: {e}")
              try:
                  await recover_state()
              except errors.StateError:
                  await cleanup_state(full=True)
                  raise

      async def test_with_timeout_handling(
          managed_state: None
      ) -> None:
          """
          Test with proper timeout and state handling.

          Args:
              managed_state: State management fixture
          """
          try:
              async with timeout(5.0):
                  await perform_operation()
          except errors.TimeoutError:
              # Check if operation partially completed
              state = await get_current_state()
              if state.is_partial():
                  await cleanup_partial_state(state)
              raise
      ```

metadata:
  priority: high
  version: 1.0
  tags:
    - discord
    - testing
    - pytest
    - errors
    - exceptions
    - dpytest
</rule>
