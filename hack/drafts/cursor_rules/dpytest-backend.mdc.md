---
description:
globs:
alwaysApply: false
---
# dpytest Backend System
Comprehensive guide to dpytest's backend simulation system for Discord bot testing
Detailed documentation of how dpytest simulates Discord's backend for testing.

<rule>
name: dpytest_backend
description: Guide to understanding dpytest's backend simulation
filters:
  # Match Python files
  - type: file_extension
    pattern: "\\.py$"
  # Match test files
  - type: file_path
    pattern: "tests?/"
  # Match backend-related content
  - type: content
    pattern: "(?i)(backend|websocket|state|discord.*gateway|simulation)"

actions:
  - type: suggest
    message: |
      # dpytest Backend System

      The backend system in dpytest simulates Discord's server-side behavior without requiring an actual Discord connection.

      ## Core Components

      ```
      discord.ext.test.backend
      ├── BackendState          # Manages the simulated Discord state
      ├── FakeHttp             # Simulates Discord HTTP API
      ├── FakeWebSocket        # Simulates Discord WebSocket gateway
      ├── GlobalState          # Manages global test state
      └── MessageQueue        # Handles message processing
      ```

      ## Backend State Management

      ### 1. Global State

      ```python
      from discord.ext.test import backend

      # Access global state
      state = backend.get_state()

      # Get current guilds
      guilds = state.guilds

      # Get current channels
      channels = state.channels

      # Get current members
      members = state.members
      ```

      ### 2. Guild Management

      ```python
      # Create a new guild
      guild = await backend.make_guild(
          name="Test Guild",
          owner_id=user_id
      )

      # Add channels to guild
      text_channel = await backend.make_text_channel(
          name="general",
          guild=guild
      )
      voice_channel = await backend.make_voice_channel(
          name="Voice",
          guild=guild
      )

      # Add roles to guild
      role = await backend.make_role(
          name="Admin",
          guild=guild,
          permissions=discord.Permissions.all()
      )
      ```

      ### 3. Channel Management

      ```python
      # Create different channel types
      text_channel = await backend.make_text_channel(name="text")
      voice_channel = await backend.make_voice_channel(name="voice")
      category = await backend.make_category(name="category")

      # Set channel permissions
      await backend.set_channel_permission_overrides(
          channel=text_channel,
          target=role_or_member,
          allow=discord.Permissions(send_messages=True),
          deny=discord.Permissions(manage_messages=True)
      )
      ```

      ## WebSocket Simulation

      ### 1. Event Dispatch

      ```python
      # Dispatch a custom event
      await backend.dispatch_event(
          name="custom_event",
          data={"key": "value"}
      )

      # Dispatch standard Discord events
      await backend.dispatch_message(message)
      await backend.dispatch_member_join(member)
      await backend.dispatch_reaction_add(reaction)
      ```

      ### 2. Gateway Events

      ```python
      # Simulate connection events
      await backend.connect()
      await backend.disconnect()

      # Simulate gateway events
      await backend.dispatch_ready()
      await backend.dispatch_resumed()
      ```

      ## HTTP API Simulation

      ### 1. Message Operations

      ```python
      # Send a message
      message = await backend.send_message(
          channel=channel,
          content="Test message",
          author=member
      )

      # Edit a message
      await backend.edit_message(
          message=message,
          new_content="Edited content"
      )

      # Delete a message
      await backend.delete_message(message)
      ```

      ### 2. Member Operations

      ```python
      # Add member to guild
      member = await backend.make_member(
          name="Test User",
          guild=guild,
          roles=[role]
      )

      # Update member
      await backend.update_member(
          member=member,
          nick="New Nick",
          roles=[new_role]
      )

      # Remove member
      await backend.remove_member(member)
      ```

      ## Message Queue System

      ### 1. Queue Management

      ```python
      # Get message queue
      queue = backend.get_message_queue()

      # Clear message queue
      await backend.clear_message_queue()

      # Wait for messages
      messages = await backend.wait_for_messages(count=2)
      ```

      ### 2. Message Processing

      ```python
      # Process a single message
      await backend.process_message(message)

      # Process multiple messages
      await backend.process_messages(messages)
      ```

      ## Advanced Backend Features

      ### 1. State Snapshots

      ```python
      # Create state snapshot
      snapshot = backend.create_state_snapshot()

      # Restore state
      await backend.restore_state(snapshot)
      ```

      ### 2. Error Simulation

      ```python
      # Simulate API errors
      await backend.set_error_state(
          error_type="http",
          status=429,
          message="Rate limited"
      )

      # Simulate connection errors
      await backend.set_error_state(
          error_type="websocket",
          code=4004,
          message="Authentication failed"
      )
      ```

      ### 3. Rate Limit Simulation

      ```python
      # Configure rate limits
      await backend.set_rate_limit(
          route="/channels/{channel_id}/messages",
          limit=5,
          reset_after=5.0
      )
      ```

      ## Best Practices

      1. **Clean State Between Tests**
         ```python
         @pytest.fixture(autouse=True)
         async def cleanup():
             yield
             await backend.clear_state()
         ```

      2. **Handle Async Operations**
         ```python
         # Wait for state updates
         await backend.wait_for_state_update()

         # Use timeouts for operations
         await backend.wait_for_event("message", timeout=5.0)
         ```

      3. **Manage Resources**
         ```python
         # Create and cleanup resources properly
         guild = await backend.make_guild()
         try:
             # Test code
             pass
         finally:
             await backend.cleanup_guild(guild)
         ```

      4. **Error Handling**
         ```python
         # Handle backend errors appropriately
         try:
             await backend.process_action()
         except backend.BackendError as e:
             # Handle error
             pass
         ```

examples:
  - input: |
      How do I simulate a complex guild setup with channels and roles?
    output: |
      Here's how to create a complex guild setup:

      ```python
      @pytest.mark.asyncio
      async def test_complex_guild_setup(bot):
          # Create guild with specific settings
          guild = await backend.make_guild(
              name="Test Server",
              owner_id=bot.user.id,
              member_count=5
          )

          # Create categories
          text_category = await backend.make_category(
              name="Text Channels",
              guild=guild
          )
          voice_category = await backend.make_category(
              name="Voice Channels",
              guild=guild
          )

          # Create text channels
          general = await backend.make_text_channel(
              name="general",
              guild=guild,
              category=text_category
          )
          admin = await backend.make_text_channel(
              name="admin-only",
              guild=guild,
              category=text_category
          )

          # Create voice channels
          voice = await backend.make_voice_channel(
              name="General Voice",
              guild=guild,
              category=voice_category
          )

          # Create roles
          admin_role = await backend.make_role(
              name="Admin",
              guild=guild,
              permissions=discord.Permissions.all()
          )
          mod_role = await backend.make_role(
              name="Moderator",
              guild=guild,
              permissions=discord.Permissions(
                  manage_messages=True,
                  kick_members=True
              )
          )

          # Set channel permissions
          await backend.set_channel_permission_overrides(
              channel=admin,
              target=admin_role,
              allow=discord.Permissions(read_messages=True),
              deny=discord.Permissions(mention_everyone=True)
          )

          # Add members with roles
          admin_member = await backend.make_member(
              name="Admin User",
              guild=guild,
              roles=[admin_role]
          )
          mod_member = await backend.make_member(
              name="Mod User",
              guild=guild,
              roles=[mod_role]
          )

          # Test your bot's functionality with this setup
          await dpytest.message("!serverinfo")
          assert dpytest.verify().message().contains().content("Test Server")
          assert dpytest.verify().message().contains().content("5 members")
      ```

metadata:
  priority: high
  version: 1.0
  tags:
    - discord
    - testing
    - pytest
    - backend
    - simulation
    - dpytest
</rule>
