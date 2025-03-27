---
description:
globs:
alwaysApply: false
---
# dpytest Voice Testing Guide

Guide to testing Discord voice channels and voice functionality with dpytest

Documentation for testing Discord voice channels and voice functionality using dpytest.

<rule>
name: dpytest_voice
description: Guide to testing Discord voice channel functionality
filters:
  # Match Python files
  - type: file_extension
    pattern: "\\.py$"
  # Match test files
  - type: file_path
    pattern: "tests?/"
  # Match voice-related content
  - type: content
    pattern: "(?i)(voice|audio|channel|vc)"

actions:
  - type: suggest
    message: |
      # dpytest Voice Testing Guide

      Guide to testing Discord voice channels and voice functionality using dpytest.

      ## Voice Channel Creation

      ### 1. Basic Voice Channel Creation

      ```python
      from typing import Optional, Dict, Any
      from discord.ext.test import backend
      import discord

      async def create_voice_channel(
          name: str = "test-voice",
          guild: Optional[discord.Guild] = None,
          **kwargs: Any
      ) -> discord.VoiceChannel:
          """
          Create a test voice channel.

          Args:
              name: Name of the voice channel
              guild: Guild to create channel in (uses default if None)
              **kwargs: Additional channel options

          Returns:
              discord.VoiceChannel: Created voice channel
          """
          if guild is None:
              guild = backend.get_default_guild()

          return await backend.make_voice_channel(
              name=name,
              guild=guild,
              **kwargs
          )
      ```

      ### 2. Voice Channel with Options

      ```python
      async def create_configured_voice_channel(
          name: str,
          user_limit: Optional[int] = None,
          bitrate: int = 64000,
          position: Optional[int] = None,
          **kwargs: Any
      ) -> discord.VoiceChannel:
          """
          Create a voice channel with specific configuration.

          Args:
              name: Channel name
              user_limit: Maximum users (None for unlimited)
              bitrate: Channel bitrate in bps
              position: Channel position
              **kwargs: Additional options

          Returns:
              discord.VoiceChannel: Configured voice channel
          """
          return await backend.make_voice_channel(
              name=name,
              user_limit=user_limit,
              bitrate=bitrate,
              position=position,
              **kwargs
          )
      ```

      ## Voice State Management

      ### 1. Voice State Updates

      ```python
      from discord.ext.test import backend

      async def connect_to_voice(
          member: discord.Member,
          channel: discord.VoiceChannel
      ) -> None:
          """
          Connect a member to a voice channel.

          Args:
              member: Member to connect
              channel: Voice channel to join
          """
          await backend.update_voice_state(
              member=member,
              channel=channel
          )

      async def disconnect_from_voice(
          member: discord.Member
      ) -> None:
          """
          Disconnect a member from voice.

          Args:
              member: Member to disconnect
          """
          await backend.update_voice_state(
              member=member,
              channel=None
          )
      ```

      ### 2. Voice State Verification

      ```python
      from typing import Optional
      import discord

      async def verify_voice_state(
          member: discord.Member,
          expected_channel: Optional[discord.VoiceChannel] = None
      ) -> bool:
          """
          Verify member's voice state.

          Args:
              member: Member to check
              expected_channel: Expected voice channel (None for disconnected)

          Returns:
              bool: True if state matches expectations
          """
          voice_state = member.voice

          if expected_channel is None:
              return voice_state is None

          return (
              voice_state is not None and
              voice_state.channel.id == expected_channel.id
          )
      ```

      ## Testing Voice Events

      ### 1. Voice State Update Events

      ```python
      import pytest
      from discord.ext.test import runner
      from typing import AsyncGenerator

      @pytest.fixture
      async def voice_setup() -> AsyncGenerator[discord.VoiceChannel, None]:
          """
          Set up voice testing environment.

          Yields:
              discord.VoiceChannel: Test voice channel
          """
          # Create voice channel
          channel = await create_voice_channel("test-voice")
          yield channel
          # Cleanup
          await runner.cleanup()

      async def test_voice_join(
          voice_setup: discord.VoiceChannel
      ) -> None:
          """
          Test voice channel join event.

          Args:
              voice_setup: Voice channel fixture
          """
          # Get test member
          member = await runner.get_member()

          # Connect to voice
          await connect_to_voice(member, voice_setup)

          # Verify state
          assert await verify_voice_state(member, voice_setup)
      ```

      ### 2. Voice Event Callbacks

      ```python
      from typing import Callable, Any
      from discord.ext.test import callbacks

      def register_voice_callback(
          callback: Callable[[discord.Member, discord.VoiceState], Any]
      ) -> None:
          """
          Register voice state update callback.

          Args:
              callback: Callback function
          """
          callbacks.register_callback(
              "voice_state_update",
              callback
          )
      ```

      ## Best Practices

      1. **Voice Channel Setup**
         ```python
         @pytest.fixture(scope="function")
         async def voice_env() -> AsyncGenerator[Dict[str, Any], None]:
             """Set up voice testing environment."""
             # Create guild and channel
             guild = backend.get_default_guild()
             channel = await create_voice_channel(
                 "test-voice",
                 guild=guild,
                 bitrate=64000
             )

             yield {
                 "guild": guild,
                 "channel": channel
             }

             # Cleanup
             await runner.cleanup()
         ```

      2. **Voice State Testing**
         ```python
         async def test_voice_state_changes(
             voice_env: Dict[str, Any]
         ) -> None:
             """Test voice state changes."""
             channel = voice_env["channel"]
             member = await runner.get_member()

             # Test connect
             await connect_to_voice(member, channel)
             assert await verify_voice_state(member, channel)

             # Test disconnect
             await disconnect_from_voice(member)
             assert await verify_voice_state(member, None)
         ```

      3. **Event Handling**
         ```python
         from typing import List, Tuple

         class VoiceEventCollector:
             """Collect voice events for testing."""

             def __init__(self) -> None:
                 """Initialize collector."""
                 self.events: List[Tuple[discord.Member, discord.VoiceState]] = []

             async def callback(
                 self,
                 member: discord.Member,
                 state: discord.VoiceState
             ) -> None:
                 """
                 Voice event callback.

                 Args:
                     member: Member involved
                     state: New voice state
                 """
                 self.events.append((member, state))

         async def test_voice_events(
             voice_env: Dict[str, Any]
         ) -> None:
             """Test voice event handling."""
             collector = VoiceEventCollector()
             register_voice_callback(collector.callback)

             channel = voice_env["channel"]
             member = await runner.get_member()

             # Trigger events
             await connect_to_voice(member, channel)
             await disconnect_from_voice(member)

             # Verify events
             assert len(collector.events) == 2
             assert collector.events[0][0] == member  # Join event
             assert collector.events[1][0] == member  # Leave event
         ```

examples:
  - input: |
      How do I test a bot command that moves users between voice channels?
    output: |
      Here's an example of testing a bot command that moves users between voice channels:

      ```python
      import pytest
      from discord.ext.test import runner, backend
      from typing import Dict, Any, AsyncGenerator

      @pytest.fixture
      async def voice_channels() -> AsyncGenerator[Dict[str, Any], None]:
          """Set up test voice channels."""
          guild = backend.get_default_guild()

          # Create two voice channels
          channel1 = await create_voice_channel("voice-1", guild)
          channel2 = await create_voice_channel("voice-2", guild)

          yield {
              "guild": guild,
              "channel1": channel1,
              "channel2": channel2
          }

          await runner.cleanup()

      async def test_move_command(
          voice_channels: Dict[str, Any]
      ) -> None:
          """Test command that moves users between channels."""
          # Get test member
          member = await runner.get_member()

          # Connect to first channel
          await connect_to_voice(member, voice_channels["channel1"])
          assert await verify_voice_state(member, voice_channels["channel1"])

          # Simulate move command
          await runner.message("!move #voice-2")

          # Verify member moved to second channel
          assert await verify_voice_state(member, voice_channels["channel2"])
      ```

metadata:
  priority: high
  version: 1.0
  tags:
    - discord
    - testing
    - pytest
    - voice
    - dpytest
</rule>
