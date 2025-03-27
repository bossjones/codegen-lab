---
description:
globs:
alwaysApply: false
---
# dpytest Utility Functions
Comprehensive guide to dpytest's utility functions and helper methods

Documentation of dpytest's utility functions, helpers, and common patterns.

<rule>
name: dpytest_utils
description: Guide to using dpytest's utility functions and helpers
filters:
  # Match Python files
  - type: file_extension
    pattern: "\\.py$"
  # Match test files
  - type: file_path
    pattern: "tests?/"
  # Match utility-related content
  - type: content
    pattern: "(?i)(util|helper|mock|generate|cleanup|wait|timeout)"

actions:
  - type: suggest
    message: |
      # dpytest Utility Functions

      Essential utility functions and helpers for testing Discord bots with dpytest.

      ## Time Utilities

      ### 1. Time Manipulation

      ```python
      from discord.ext.test import utils
      from typing import Optional, Union
      from datetime import datetime, timedelta

      # Fast forward time
      await utils.advance_time(seconds: float = 0.0) -> None:
          """
          Advance the internal clock by specified seconds.

          Args:
              seconds: Number of seconds to advance
          """

      # Set specific time
      await utils.set_time(
          target: Union[datetime, float]
      ) -> None:
          """
          Set the internal clock to a specific time.

          Args:
              target: Target time as datetime or timestamp
          """

      # Get current time
      current = utils.get_mock_time() -> float:
          """
          Get current mocked timestamp.

          Returns:
              float: Current mock timestamp
          """
      ```

      ### 2. Timeout Helpers

      ```python
      async with utils.timeout(seconds: float = 5.0) -> AsyncContextManager[None]:
          """
          Context manager for handling timeouts.

          Args:
              seconds: Timeout duration in seconds

          Raises:
              TimeoutError: If operation exceeds timeout
          """
          await long_operation()

      # Retry with timeout
      result = await utils.retry_until(
          callback: Callable[[], Awaitable[T]],
          timeout: float = 5.0,
          interval: float = 0.1
      ) -> T:
          """
          Retry an operation until success or timeout.

          Args:
              callback: Async function to retry
              timeout: Maximum time to wait
              interval: Time between retries

          Returns:
              T: Result of successful callback

          Raises:
              TimeoutError: If operation times out
          """
      ```

      ## Message Utilities

      ### 1. Content Generation

      ```python
      from typing import Optional, List, Dict, Any

      def generate_message_content(
          length: Optional[int] = None,
          words: Optional[List[str]] = None
      ) -> str:
          """
          Generate random message content.

          Args:
              length: Desired message length
              words: List of words to use

          Returns:
              str: Generated message content
          """

      def generate_embed_data(
          title: Optional[str] = None,
          description: Optional[str] = None,
          fields: Optional[List[Dict[str, str]]] = None
      ) -> Dict[str, Any]:
          """
          Generate embed data dictionary.

          Args:
              title: Embed title
              description: Embed description
              fields: List of field dictionaries

          Returns:
              Dict[str, Any]: Embed data dictionary
          """
      ```

      ### 2. Message Parsing

      ```python
      def parse_message_reference(
          message_id: int,
          channel_id: Optional[int] = None,
          guild_id: Optional[int] = None
      ) -> Dict[str, int]:
          """
          Create message reference dictionary.

          Args:
              message_id: ID of referenced message
              channel_id: Optional channel ID
              guild_id: Optional guild ID

          Returns:
              Dict[str, int]: Message reference data
          """

      def extract_message_content(
          message: discord.Message
      ) -> str:
          """
          Extract clean content from message.

          Args:
              message: Discord message object

          Returns:
              str: Clean message content
          """
      ```

      ## State Utilities

      ### 1. State Management

      ```python
      from typing import TypeVar, Generic, Optional

      T = TypeVar('T')

      class StateSnapshot(Generic[T]):
          """Snapshot of test state for restoration."""

          def __init__(self, state: T) -> None:
              """
              Initialize state snapshot.

              Args:
                  state: State to snapshot
              """

          async def restore(self) -> None:
              """Restore state from snapshot."""

      async def create_state_snapshot() -> StateSnapshot:
          """
          Create snapshot of current state.

          Returns:
              StateSnapshot: Current state snapshot
          """

      async def cleanup_state(
          full: bool = False
      ) -> None:
          """
          Clean up test state.

          Args:
              full: Whether to do full cleanup
          """
      ```

      ### 2. Cache Management

      ```python
      def clear_state_cache() -> None:
          """Clear all state caches."""

      def invalidate_cache(
          entity_type: str,
          entity_id: Optional[int] = None
      ) -> None:
          """
          Invalidate specific cache entries.

          Args:
              entity_type: Type of entity to invalidate
              entity_id: Optional specific entity ID
          """
      ```

      ## Debug Utilities

      ### 1. Logging

      ```python
      import logging
      from typing import Optional, Union, TextIO

      def setup_debug_logging(
          level: Union[int, str] = logging.DEBUG,
          output: Optional[TextIO] = None
      ) -> None:
          """
          Configure debug logging.

          Args:
              level: Logging level
              output: Optional output file
          """

      def get_debug_logger() -> logging.Logger:
          """
          Get debug logger instance.

          Returns:
              logging.Logger: Debug logger
          """
      ```

      ### 2. State Inspection

      ```python
      from typing import Dict, Any

      def dump_state() -> Dict[str, Any]:
          """
          Dump current state for inspection.

          Returns:
              Dict[str, Any]: Current state
          """

      def print_state_diff(
          before: Dict[str, Any],
          after: Dict[str, Any]
      ) -> None:
          """
          Print difference between states.

          Args:
              before: State before
              after: State after
          """
      ```

      ## Common Patterns

      ### 1. Resource Management

      ```python
      from contextlib import asynccontextmanager
      from typing import AsyncGenerator, TypeVar, Any

      T = TypeVar('T')

      @asynccontextmanager
      async def managed_resource(
          resource_type: str,
          **kwargs: Any
      ) -> AsyncGenerator[T, None]:
          """
          Manage resource lifecycle.

          Args:
              resource_type: Type of resource
              **kwargs: Resource configuration

          Yields:
              T: Managed resource
          """
          try:
              resource = await create_resource(resource_type, **kwargs)
              yield resource
          finally:
              await cleanup_resource(resource)
      ```

      ### 2. Event Waiting

      ```python
      from typing import Optional, Callable, Any

      async def wait_for_event(
          event_name: str,
          check: Optional[Callable[[Any], bool]] = None,
          timeout: float = 5.0
      ) -> Any:
          """
          Wait for specific event.

          Args:
              event_name: Name of event
              check: Optional check callback
              timeout: Wait timeout

          Returns:
              Any: Event data

          Raises:
              TimeoutError: If event not received
          """
      ```

      ## Best Practices

      1. **Resource Cleanup**
         ```python
         @pytest.fixture(autouse=True)
         async def cleanup_after_test() -> AsyncGenerator[None, None]:
             """Ensure resources are cleaned up."""
             try:
                 yield
             finally:
                 await utils.cleanup_state(full=True)
                 utils.clear_state_cache()
         ```

      2. **Error Handling**
         ```python
         async def safe_operation() -> None:
             """Handle operation errors safely."""
             try:
                 await potentially_failing_operation()
             except Exception as e:
                 utils.get_debug_logger().exception(
                     "Operation failed",
                     exc_info=e
                 )
                 raise
         ```

      3. **State Management**
         ```python
         async def test_with_state_restore() -> None:
             """Test with state restoration."""
             snapshot = await utils.create_state_snapshot()
             try:
                 await run_test()
             finally:
                 await snapshot.restore()
         ```

      4. **Timeout Handling**
         ```python
         async def test_with_timeout() -> None:
             """Test with proper timeout."""
             async with utils.timeout(5.0):
                 result = await utils.retry_until(
                     callback=check_condition,
                     interval=0.1
                 )
                 assert result
         ```

examples:
  - input: |
      How do I manage test state and handle timeouts?
    output: |
      Here's an example combining state management and timeout handling:

      ```python
      import pytest
      from discord.ext.test import utils
      from typing import AsyncGenerator, Optional

      @pytest.fixture
      async def managed_test_state() -> AsyncGenerator[None, None]:
          """
          Manage test state with automatic cleanup.

          Yields:
              None
          """
          # Create state snapshot
          snapshot = await utils.create_state_snapshot()

          try:
              yield
          finally:
              # Restore state with timeout
              async with utils.timeout(5.0):
                  await snapshot.restore()
                  await utils.cleanup_state(full=True)
                  utils.clear_state_cache()

      async def test_complex_operation(
          managed_test_state: None
      ) -> None:
          """
          Test complex operation with state management.

          Args:
              managed_test_state: State management fixture
          """
          # Set up test conditions
          await setup_test_conditions()

          # Run operation with timeout and retry
          async with utils.timeout(10.0):
              result = await utils.retry_until(
                  callback=check_operation_complete,
                  interval=0.2
              )

          # Verify results
          assert result
          assert await verify_state_correct()
      ```

metadata:
  priority: high
  version: 1.0
  tags:
    - discord
    - testing
    - pytest
    - utilities
    - helpers
    - dpytest
</rule>
