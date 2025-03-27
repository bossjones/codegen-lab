---
description:
globs:
alwaysApply: false
---
# dpytest Configuration System
Comprehensive guide to dpytest's configuration system and options
Documentation of dpytest's configuration system, options, and best practices.

<rule>
name: dpytest_config
description: Guide to configuring dpytest for Discord bot testing
filters:
  # Match Python files
  - type: file_extension
    pattern: "\\.py$"
  # Match test files
  - type: file_path
    pattern: "tests?/"
  # Match configuration-related content
  - type: content
    pattern: "(?i)(config|configure|setup|settings|options)"

actions:
  - type: suggest
    message: |
      # dpytest Configuration Guide

      Comprehensive guide to configuring dpytest for Discord bot testing.

      ## Configuration System

      ### 1. Basic Configuration

      ```python
      from typing import Optional, Dict, Any, Union
      from discord.ext.test import runner

      def configure(
          client_config: Optional[Dict[str, Any]] = None,
          state_config: Optional[Dict[str, Any]] = None,
          runner_config: Optional[Dict[str, Any]] = None
      ) -> None:
          """
          Configure dpytest with specified options.

          Args:
              client_config: Discord client configuration
              state_config: State management configuration
              runner_config: Test runner configuration
          """
          if client_config:
              runner.configure_client(**client_config)
          if state_config:
              runner.configure_state(**state_config)
          if runner_config:
              runner.configure_runner(**runner_config)
      ```

      ### 2. Client Configuration

      ```python
      def configure_client(
          intents: Optional[discord.Intents] = None,
          token: Optional[str] = None,
          prefix: Union[str, List[str]] = "!",
          owner_id: Optional[int] = None,
          **kwargs: Any
      ) -> None:
          """
          Configure Discord client settings.

          Args:
              intents: Discord intents configuration
              token: Bot token (mock token for testing)
              prefix: Command prefix(es)
              owner_id: Bot owner's user ID
              **kwargs: Additional client settings
          """
      ```

      ### 3. State Configuration

      ```python
      def configure_state(
          guild_id: Optional[int] = None,
          channel_id: Optional[int] = None,
          message_cache_size: int = 1000,
          member_cache_flags: Optional[discord.MemberCacheFlags] = None,
          **kwargs: Any
      ) -> None:
          """
          Configure state management settings.

          Args:
              guild_id: Default guild ID
              channel_id: Default channel ID
              message_cache_size: Size of message cache
              member_cache_flags: Member caching configuration
              **kwargs: Additional state settings
          """
      ```

      ### 4. Runner Configuration

      ```python
      def configure_runner(
          timeout: float = 5.0,
          tick_rate: float = 0.1,
          start_callbacks: bool = True,
          **kwargs: Any
      ) -> None:
          """
          Configure test runner settings.

          Args:
              timeout: Default operation timeout
              tick_rate: State update interval
              start_callbacks: Auto-start event callbacks
              **kwargs: Additional runner settings
          """
      ```

      ## Configuration Options

      ### 1. Client Options

      ```python
      # Intents Configuration
      intents = discord.Intents.default()
      intents.members = True
      intents.message_content = True

      client_config = {
          "intents": intents,
          "prefix": "!",  # or ["!", "?"] for multiple
          "owner_id": 123456789,
          "case_insensitive": True,
          "strip_after_prefix": True,
          "allowed_mentions": discord.AllowedMentions(
              everyone=False,
              users=True,
              roles=False
          )
      }
      ```

      ### 2. State Options

      ```python
      # State Management Configuration
      state_config = {
          "guild_id": 123456789,
          "channel_id": 987654321,
          "message_cache_size": 2000,
          "member_cache_flags": discord.MemberCacheFlags.all(),
          "max_messages": 5000,
          "fetch_offline_members": True,
          "chunk_guilds_at_startup": True
      }
      ```

      ### 3. Runner Options

      ```python
      # Test Runner Configuration
      runner_config = {
          "timeout": 10.0,
          "tick_rate": 0.05,
          "start_callbacks": True,
          "error_on_timeout": True,
          "raise_on_error": True,
          "verify_state": True
      }
      ```

      ## Advanced Configuration

      ### 1. Custom Cache Configuration

      ```python
      from typing import Optional, Dict, Any
      from discord.ext.test import backend

      class CustomCacheConfig:
          """Custom cache configuration."""

          def __init__(
              self,
              message_cache_size: int = 1000,
              member_cache_size: Optional[int] = None
          ) -> None:
              """
              Initialize custom cache config.

              Args:
                  message_cache_size: Size of message cache
                  member_cache_size: Size of member cache
              """
              self.message_cache_size = message_cache_size
              self.member_cache_size = member_cache_size

      def configure_cache(config: CustomCacheConfig) -> None:
          """
          Configure custom caching behavior.

          Args:
              config: Custom cache configuration
          """
          backend.configure_cache(
              message_cache_size=config.message_cache_size,
              member_cache_size=config.member_cache_size
          )
      ```

      ### 2. Event Configuration

      ```python
      from typing import Callable, Any, List
      from discord.ext.test import callbacks

      def configure_events(
          event_handlers: Dict[str, List[Callable[..., Any]]]
      ) -> None:
          """
          Configure custom event handlers.

          Args:
              event_handlers: Mapping of events to handlers
          """
          for event, handlers in event_handlers.items():
              for handler in handlers:
                  callbacks.register_callback(event, handler)
      ```

      ### 3. State Verification Configuration

      ```python
      from typing import Callable, Any
      from discord.ext.test import state

      def configure_verification(
          verify_func: Callable[[Any], bool]
      ) -> None:
          """
          Configure custom state verification.

          Args:
              verify_func: Custom verification function
          """
          state.set_verification_callback(verify_func)
      ```

      ## Best Practices

      1. **Fixture-Based Configuration**
         ```python
         import pytest
         from typing import AsyncGenerator
         from discord.ext.test import runner

         @pytest.fixture
         async def configured_bot() -> AsyncGenerator[None, None]:
             """Configure bot for testing."""
             runner.configure(
                 client_config={
                     "intents": discord.Intents.all(),
                     "prefix": "!"
                 },
                 state_config={
                     "message_cache_size": 1000
                 },
                 runner_config={
                     "timeout": 5.0
                 }
             )
             yield
             await runner.cleanup()
         ```

      2. **Environment-Based Configuration**
         ```python
         import os
         from typing import Dict, Any

         def load_config() -> Dict[str, Any]:
             """Load configuration from environment."""
             return {
                 "client_config": {
                     "prefix": os.getenv("BOT_PREFIX", "!"),
                     "owner_id": int(os.getenv("OWNER_ID", "0"))
                 },
                 "state_config": {
                     "message_cache_size": int(
                         os.getenv("CACHE_SIZE", "1000")
                     )
                 }
             }
         ```

      3. **Modular Configuration**
         ```python
         from typing import Dict, Any

         def create_test_config(
             feature: str
         ) -> Dict[str, Any]:
             """
             Create feature-specific configuration.

             Args:
                 feature: Feature being tested

             Returns:
                 Dict[str, Any]: Feature configuration
             """
             base_config = get_base_config()
             feature_config = get_feature_config(feature)
             return {
                 **base_config,
                 **feature_config
             }
         ```

      4. **Configuration Validation**
         ```python
         from typing import Dict, Any
         from discord.ext.test import errors

         def validate_config(
             config: Dict[str, Any]
         ) -> None:
             """
             Validate configuration values.

             Args:
                 config: Configuration to validate

             Raises:
                 ConfigurationError: If config is invalid
             """
             if "client_config" in config:
                 validate_client_config(config["client_config"])
             if "state_config" in config:
                 validate_state_config(config["state_config"])
             if "runner_config" in config:
                 validate_runner_config(config["runner_config"])
         ```

examples:
  - input: |
      How do I configure intents and caching for my bot tests?
    output: |
      Here's an example of configuring intents and caching for bot testing:

      ```python
      import pytest
      import discord
      from discord.ext.test import runner
      from typing import AsyncGenerator

      @pytest.fixture
      async def configured_bot() -> AsyncGenerator[None, None]:
          """Configure bot with specific intents and caching."""
          # Set up intents
          intents = discord.Intents.default()
          intents.members = True
          intents.message_content = True
          intents.guilds = True

          # Configure the bot
          runner.configure(
              client_config={
                  "intents": intents,
                  "prefix": "!"
              },
              state_config={
                  "message_cache_size": 2000,
                  "member_cache_flags": discord.MemberCacheFlags.all(),
                  "fetch_offline_members": True
              },
              runner_config={
                  "timeout": 5.0
              }
          )

          yield

          # Cleanup after tests
          await runner.cleanup()

      async def test_member_cache(
          configured_bot: None
      ) -> None:
          """Test that member caching works."""
          # Your test code here
          guild = await runner.get_guild()
          member = await runner.add_member(guild)

          # Verify member is cached
          assert member in guild.members
      ```

metadata:
  priority: high
  version: 1.0
  tags:
    - discord
    - testing
    - pytest
    - configuration
    - dpytest
</rule>
