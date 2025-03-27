---
description:
globs:
alwaysApply: false
---
# dpytest Callbacks System
Comprehensive guide to dpytest's callback system for handling Discord events in tests
Detailed documentation of dpytest's callback system for handling Discord events in tests.

<rule>
name: dpytest_callbacks
description: Guide to using dpytest's callback system for event handling
filters:
  # Match Python files
  - type: file_extension
    pattern: "\\.py$"
  # Match test files
  - type: file_path
    pattern: "tests?/"
  # Match callback-related content
  - type: content
    pattern: "(?i)(callback|event|handler|listener|dispatch|on_)"

actions:
  - type: suggest
    message: |
      # dpytest Callbacks System

      The callbacks system in dpytest allows you to test Discord event handlers and simulate Discord events in your tests.

      ## Core Callback Components

      ```
      discord.ext.test.callbacks
      ├── EventCallback      # Base event callback handler
      ├── MessageCallback    # Message event handling
      ├── ReactionCallback  # Reaction event handling
      └── StateCallback     # State change event handling
      ```

      ## Event Handling

      ### 1. Basic Event Callbacks

      ```python
      from discord.ext.test import callbacks
      import discord

      # Register event callback
      @callbacks.event_callback
      async def on_message(message: discord.Message) -> None:
          """
          Handle message events in tests.

          Args:
              message: The message that triggered the event
          """
          print(f"Message received: {message.content}")

      # Register reaction callback
      @callbacks.reaction_callback
      async def on_reaction_add(
          reaction: discord.Reaction,
          user: discord.User
      ) -> None:
          """
          Handle reaction addition events in tests.

          Args:
              reaction: The reaction that was added
              user: The user who added the reaction
          """
          print(f"Reaction added: {reaction.emoji}")
      ```

      ### 2. State Change Callbacks

      ```python
      # Register state change callback
      @callbacks.state_callback
      async def on_guild_channel_create(channel: discord.abc.GuildChannel) -> None:
          """
          Handle channel creation events in tests.

          Args:
              channel: The channel that was created
          """
          print(f"Channel created: {channel.name}")

      # Register member update callback
      @callbacks.state_callback
      async def on_member_update(
          before: discord.Member,
          after: discord.Member
      ) -> None:
          """
          Handle member update events in tests.

          Args:
              before: The member state before the update
              after: The member state after the update
          """
          print(f"Member updated: {after.display_name}")
      ```

      ## Event Simulation

      ### 1. Message Events

      ```python
      # Simulate message creation
      await callbacks.dispatch_message(
          content="Test message",
          author=member,
          channel=channel
      )

      # Simulate message edit
      await callbacks.dispatch_message_edit(
          before=original_message,
          after=edited_message
      )

      # Simulate message delete
      await callbacks.dispatch_message_delete(message)
      ```

      ### 2. Reaction Events

      ```python
      # Simulate reaction add
      await callbacks.dispatch_reaction_add(
          message=message,
          emoji="👍",
          user=member
      )

      # Simulate reaction remove
      await callbacks.dispatch_reaction_remove(
          message=message,
          emoji="👍",
          user=member
      )
      ```

      ### 3. State Change Events

      ```python
      # Simulate channel creation
      await callbacks.dispatch_channel_create(channel)

      # Simulate member join
      await callbacks.dispatch_member_join(member)

      # Simulate role update
      await callbacks.dispatch_guild_role_update(
          before=old_role,
          after=new_role
      )
      ```

      ## Event Verification

      ### 1. Event Assertions

      ```python
      # Verify event was dispatched
      assert callbacks.event_dispatched("on_message")

      # Verify event count
      assert callbacks.event_dispatch_count("on_reaction_add") == 1

      # Verify event arguments
      event_args = callbacks.get_event_args("on_message")
      assert event_args[0].content == "Test message"
      ```

      ### 2. Event History

      ```python
      # Get event history
      history = callbacks.get_event_history()

      # Clear event history
      callbacks.clear_event_history()

      # Get specific event history
      message_events = callbacks.get_event_history_for("on_message")
      ```

      ## Best Practices

      1. **Clean Event History**
         ```python
         @pytest.fixture(autouse=True)
         async def cleanup_events() -> None:
             """Clean up event history after each test."""
             try:
                 yield
             finally:
                 callbacks.clear_event_history()
         ```

      2. **Use Event Fixtures**
         ```python
         @pytest.fixture
         def message_callback() -> AsyncGenerator[None, None]:
             """Set up message event callback for testing."""
             @callbacks.event_callback
             async def on_message(message: discord.Message) -> None:
                 # Handle message
                 pass

             yield

             # Clean up callback
             callbacks.remove_callback("on_message")
         ```

      3. **Group Related Events**
         ```python
         class TestMessageEvents:
             """Test message-related events."""

             async def test_message_create(
                 self,
                 message_callback: None,
                 test_channel: discord.TextChannel
             ) -> None:
                 """
                 Test message creation events.

                 Args:
                     message_callback: Message callback fixture
                     test_channel: Test channel fixture
                 """
                 await callbacks.dispatch_message(
                     content="Test",
                     channel=test_channel
                 )
                 assert callbacks.event_dispatched("on_message")
         ```

      4. **Handle Event Timeouts**
         ```python
         async def test_delayed_event(
             self,
             event_callback: None
         ) -> None:
             """
             Test events with timeouts.

             Args:
                 event_callback: Event callback fixture
             """
             with pytest.raises(asyncio.TimeoutError):
                 await callbacks.wait_for_event(
                     "on_specific_event",
                     timeout=1.0
                 )
         ```

examples:
  - input: |
      How do I test a bot's reaction to messages?
    output: |
      Here's how to test a bot's reaction to messages:

      ```python
      import pytest
      from discord.ext.test import callbacks
      from typing import AsyncGenerator, Optional
      from typing import TYPE_CHECKING

      if TYPE_CHECKING:
          from _pytest.fixtures import FixtureRequest
          from pytest_mock.plugin import MockerFixture
          from discord import Message, TextChannel, Member

      @pytest.fixture
      async def message_handler() -> AsyncGenerator[None, None]:
          """
          Set up message event handler for testing.

          Yields:
              None
          """
          @callbacks.event_callback
          async def on_message(message: discord.Message) -> None:
              if message.content.startswith("!hello"):
                  response = await message.channel.send("Hi there!")
                  await response.add_reaction("👋")

          yield

          # Clean up callback
          callbacks.remove_callback("on_message")

      @pytest.mark.asyncio
      async def test_bot_greeting(
          message_handler: None,
          test_channel: discord.TextChannel,
          test_member: discord.Member
      ) -> None:
          """
          Test bot's greeting response and reaction.

          Args:
              message_handler: Message handler fixture
              test_channel: Test channel fixture
              test_member: Test member fixture
          """
          # Simulate user message
          await callbacks.dispatch_message(
              content="!hello",
              author=test_member,
              channel=test_channel
          )

          # Verify bot's response
          assert callbacks.event_dispatched("on_message")
          assert callbacks.event_dispatched("on_message_send")
          assert callbacks.event_dispatched("on_reaction_add")

          # Get bot's response
          response = await callbacks.wait_for_event("on_message_send")
          assert response.content == "Hi there!"

          # Verify reaction
          reaction_event = await callbacks.wait_for_event("on_reaction_add")
          assert reaction_event.emoji == "👋"
      ```

metadata:
  priority: high
  version: 1.0
  tags:
    - discord
    - testing
    - pytest
    - callbacks
    - events
    - dpytest
</rule>
