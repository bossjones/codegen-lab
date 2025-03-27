---
description:
globs:
alwaysApply: false
---
# dpytest State Management System
Comprehensive guide to dpytest's state management system for maintaining test environment state

Detailed documentation of dpytest's state management system for maintaining test environment state.

<rule>
name: dpytest_state
description: Guide to using dpytest's state management system
filters:
  # Match Python files
  - type: file_extension
    pattern: "\\.py$"
  # Match test files
  - type: file_path
    pattern: "tests?/"
  # Match state-related content
  - type: content
    pattern: "(?i)(state|backend|environment|context|cleanup|reset)"

actions:
  - type: suggest
    message: |
      # dpytest State Management System

      The state management system in dpytest maintains the test environment's state, handling guilds, channels, messages, and other Discord objects during testing.

      ## Core State Components

      ```
      discord.ext.test.state
      ├── GlobalState        # Global test environment state
      ├── BackendState      # Backend simulation state
      ├── MessageQueue      # Message queue management
      └── StateCleanup      # State cleanup utilities
      ```

      ## Global State Management

      ### 1. Accessing Global State

      ```python
      from discord.ext.test import state

      # Get current global state
      current_state = state.get_state()

      # Access specific state components
      guilds = current_state.guilds
      channels = current_state.channels
      messages = current_state.messages
      ```

      ### 2. State Configuration

      ```python
      # Configure state settings
      state.configure(
          message_cache_size=1000,
          guild_count_limit=10,
          channel_count_limit=50
      )

      # Reset state configuration
      state.reset_configuration()
      ```

      ## State Cleanup and Reset

      ### 1. Basic Cleanup

      ```python
      # Clean up all state
      await state.cleanup()

      # Reset to initial state
      await state.reset()
      ```

      ### 2. Selective Cleanup

      ```python
      # Clean up specific guild
      await state.cleanup_guild(guild_id)

      # Clean up specific channel
      await state.cleanup_channel(channel_id)

      # Clean up messages
      await state.cleanup_messages()
      ```

      ## Message Queue Management

      ### 1. Message Queue Operations

      ```python
      # Get message queue
      queue = state.get_message_queue()

      # Get next message
      message = await queue.get()

      # Check queue size
      size = queue.size()

      # Clear queue
      await queue.clear()
      ```

      ### 2. Message Queue Configuration

      ```python
      # Configure queue settings
      queue.configure(
          max_size=100,
          timeout=5.0
      )

      # Reset queue configuration
      queue.reset_configuration()
      ```

      ## State Persistence

      ### 1. State Snapshots

      ```python
      # Create state snapshot
      snapshot = await state.create_snapshot()

      # Restore from snapshot
      await state.restore_snapshot(snapshot)

      # Clean up old snapshots
      await state.cleanup_snapshots()
      ```

      ### 2. State Export/Import

      ```python
      # Export state to dictionary
      state_data = state.export_state()

      # Import state from dictionary
      await state.import_state(state_data)
      ```

      ## State Verification

      ### 1. State Assertions

      ```python
      # Verify guild exists
      assert state.has_guild(guild_id)

      # Verify channel exists
      assert state.has_channel(channel_id)

      # Verify message exists
      assert state.has_message(message_id)
      ```

      ### 2. State Queries

      ```python
      # Get all guilds
      guilds = state.get_all_guilds()

      # Get guild channels
      channels = state.get_guild_channels(guild_id)

      # Get channel messages
      messages = state.get_channel_messages(channel_id)
      ```

      ## Best Practices

      1. **Clean Up After Tests**
         ```python
         @pytest.mark.asyncio
         async def test_bot_command():
             try:
                 # Test code
                 pass
             finally:
                 await state.cleanup()
         ```

      2. **Use Fixtures for Common State**
         ```python
         @pytest.fixture
         async def test_guild():
             guild = await factories.make_guild()
             yield guild
             await state.cleanup_guild(guild.id)
         ```

      3. **Manage State Explicitly**
         ```python
         # Good: Explicit state management
         current_state = state.get_state()
         await current_state.add_guild(guild)

         # Avoid: Relying on implicit state
         await send_message(channel)  # Don't assume channel exists in state
         ```

      4. **Use State Snapshots for Complex Tests**
         ```python
         @pytest.mark.asyncio
         async def test_complex_scenario():
             # Set up initial state
             guild = await factories.make_guild()

             # Create snapshot
             snapshot = await state.create_snapshot()

             try:
                 # Run multiple test scenarios
                 await test_scenario_1()
                 await state.restore_snapshot(snapshot)
                 await test_scenario_2()
             finally:
                 await state.cleanup()
         ```

examples:
  - input: |
      How do I manage state for a complex test scenario?
    output: |
      Here's how to manage state for a complex test scenario:

      ```python
      import pytest
      from discord.ext.test import state, factories
      from typing import Dict, Any, AsyncGenerator
      from typing import TYPE_CHECKING

      if TYPE_CHECKING:
          from _pytest.fixtures import FixtureRequest
          from pytest_mock.plugin import MockerFixture
          from discord import Guild, TextChannel, Role, Member

      @pytest.fixture
      async def complex_guild_state() -> AsyncGenerator[Dict[str, Any], None]:
          """
          Set up a complex guild state with roles, channels, and members.

          Yields:
              Dict[str, Any]: Dictionary containing the created guild objects
          """
          # Create guild
          guild = await factories.make_guild(name="Test Server")

          # Create roles
          roles = {
              "admin": await factories.make_role(
                  name="Admin",
                  guild=guild,
                  permissions=discord.Permissions.all()
              ),
              "user": await factories.make_role(
                  name="User",
                  guild=guild
              )
          }

          # Create channels
          channels = {
              "general": await factories.make_text_channel(
                  name="general",
                  guild=guild
              ),
              "admin": await factories.make_text_channel(
                  name="admin-only",
                  guild=guild
              )
          }

          # Create members
          members = {
              "admin": await factories.make_member(
                  guild=guild,
                  roles=[roles["admin"]]
              ),
              "user": await factories.make_member(
                  guild=guild,
                  roles=[roles["user"]]
              )
          }

          # Create state snapshot
          snapshot = await state.create_snapshot()

          # Yield state objects
          yield {
              "guild": guild,
              "roles": roles,
              "channels": channels,
              "members": members,
              "snapshot": snapshot
          }

          # Cleanup
          await state.cleanup()

      @pytest.mark.asyncio
      async def test_complex_permissions(
          complex_guild_state: Dict[str, Any],
          bot: discord.Client
      ) -> None:
          """
          Test complex permission scenarios.

          Args:
              complex_guild_state: The complex guild state fixture
              bot: The bot client fixture
          """
          guild = complex_guild_state["guild"]
          channels = complex_guild_state["channels"]
          members = complex_guild_state["members"]
          snapshot = complex_guild_state["snapshot"]

          # Test scenario 1: Admin can send message
          await bot.process_commands(
              await factories.make_message(
                  content="!admin_command",
                  author=members["admin"],
                  channel=channels["admin"]
              )
          )
          # Verify admin command worked
          assert state.get_message_queue().size() > 0

          # Restore state for next scenario
          await state.restore_snapshot(snapshot)

          # Test scenario 2: Regular user cannot access admin channel
          with pytest.raises(discord.Forbidden):
              await factories.make_message(
                  content="!admin_command",
                  author=members["user"],
                  channel=channels["admin"]
              )
      ```

metadata:
  priority: high
  version: 1.0
  tags:
    - discord
    - testing
    - pytest
    - state-management
    - dpytest
</rule>
