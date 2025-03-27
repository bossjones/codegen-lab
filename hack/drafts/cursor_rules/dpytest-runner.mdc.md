---
description:
globs:
alwaysApply: false
---
# dpytest Test Runner System
Comprehensive guide to dpytest's test runner configuration and execution system

Detailed documentation of dpytest's test runner configuration and execution system.

<rule>
name: dpytest_runner
description: Guide to using dpytest's test runner system
filters:
  # Match Python files
  - type: file_extension
    pattern: "\\.py$"
  # Match test files
  - type: file_path
    pattern: "tests?/"
  # Match runner-related content
  - type: content
    pattern: "(?i)(runner|test|pytest|fixture|setup|configure|mark|async)"

actions:
  - type: suggest
    message: |
      # dpytest Test Runner System

      The test runner system in dpytest provides configuration and execution utilities for running Discord bot tests.

      ## Core Runner Components

      ```
      discord.ext.test.runner
      ├── TestRunner        # Core test runner
      ├── RunConfig        # Test run configuration
      ├── TestSetup        # Test environment setup
      └── TestCleanup      # Test environment cleanup
      ```

      ## Test Configuration

      ### 1. Basic Configuration

      ```python
      import pytest
      import discord
      from discord.ext.test import runner
      from typing import AsyncGenerator, Optional
      from typing import TYPE_CHECKING

      if TYPE_CHECKING:
          from _pytest.fixtures import FixtureRequest
          from pytest_mock.plugin import MockerFixture
          from _pytest.logging import LogCaptureFixture

      @pytest.fixture
      async def bot() -> AsyncGenerator[discord.Client, None]:
          """
          Create a bot instance for testing.

          Yields:
              discord.Client: The configured bot instance
          """
          # Configure test environment
          runner.configure(
              message_cache_size=100,
              guild_count=1,
              channel_count=2,
              member_count=5
          )

          # Create and configure bot
          bot = discord.Client()
          await runner.setup(bot)

          yield bot

          # Cleanup
          await runner.cleanup()
      ```

      ### 2. Advanced Configuration

      ```python
      @pytest.fixture
      async def configured_runner(
          request: "FixtureRequest"
      ) -> AsyncGenerator[None, None]:
          """
          Configure test runner with custom settings.

          Args:
              request: Pytest fixture request

          Yields:
              None
          """
          # Custom configuration
          runner.configure(
              message_cache_size=1000,
              guild_count=5,
              channel_count=10,
              member_count=20,
              dm_channel_count=2,
              user_token="test-token",
              client_id="test-client-id",
              enable_logging=True,
              log_level=logging.DEBUG
          )

          yield

          # Reset configuration
          await runner.reset()
      ```

      ## Test Environment Setup

      ### 1. Basic Setup

      ```python
      @pytest.fixture
      async def test_guild(bot: discord.Client) -> AsyncGenerator[discord.Guild, None]:
          """
          Create a test guild.

          Args:
              bot: The bot fixture

          Yields:
              discord.Guild: The created test guild
          """
          guild = await runner.create_guild()
          await runner.configure_guild(guild)
          yield guild

      @pytest.fixture
      async def test_channel(
          test_guild: discord.Guild
      ) -> AsyncGenerator[discord.TextChannel, None]:
          """
          Create a test channel.

          Args:
              test_guild: The test guild fixture

          Yields:
              discord.TextChannel: The created test channel
          """
          channel = await runner.create_text_channel(test_guild)
          yield channel
      ```

      ### 2. Complex Setup

      ```python
      @pytest.fixture
      async def test_environment(
          bot: discord.Client,
          request: "FixtureRequest"
      ) -> AsyncGenerator[dict, None]:
          """
          Set up a complete test environment.

          Args:
              bot: The bot fixture
              request: Pytest fixture request

          Yields:
              dict: Dictionary containing test environment objects
          """
          # Create guild
          guild = await runner.create_guild()

          # Create roles
          admin_role = await runner.create_role(
              guild,
              name="Admin",
              permissions=discord.Permissions.all()
          )
          user_role = await runner.create_role(
              guild,
              name="User"
          )

          # Create channels
          channels = {
              "general": await runner.create_text_channel(guild),
              "admin": await runner.create_text_channel(
                  guild,
                  overwrites={
                      admin_role: discord.PermissionOverwrite(read_messages=True),
                      user_role: discord.PermissionOverwrite(read_messages=False)
                  }
              )
          }

          # Create members
          members = {
              "admin": await runner.create_member(
                  guild,
                  roles=[admin_role]
              ),
              "user": await runner.create_member(
                  guild,
                  roles=[user_role]
              )
          }

          yield {
              "guild": guild,
              "roles": {"admin": admin_role, "user": user_role},
              "channels": channels,
              "members": members
          }

          # Cleanup is handled by runner.cleanup()
      ```

      ## Test Execution

      ### 1. Basic Test Structure

      ```python
      @pytest.mark.asyncio
      async def test_bot_command(
          bot: discord.Client,
          test_channel: discord.TextChannel,
          test_member: discord.Member
      ) -> None:
          """
          Test a bot command.

          Args:
              bot: The bot fixture
              test_channel: The test channel fixture
              test_member: The test member fixture
          """
          # Send command
          message = await runner.message("!help", channel=test_channel, member=test_member)

          # Verify response
          assert runner.verify().message().content("Here's the help menu")
          assert runner.verify().message().embed_count(1)
      ```

      ### 2. Advanced Test Patterns

      ```python
      @pytest.mark.asyncio
      class TestBotFeatures:
          """Test suite for bot features."""

          async def test_permission_checks(
              self,
              test_environment: dict,
              caplog: "LogCaptureFixture"
          ) -> None:
              """
              Test permission-based command access.

              Args:
                  test_environment: The test environment fixture
                  caplog: Pytest log capture fixture
              """
              admin = test_environment["members"]["admin"]
              user = test_environment["members"]["user"]
              admin_channel = test_environment["channels"]["admin"]

              # Test admin access
              await runner.message(
                  "!admin_command",
                  channel=admin_channel,
                  member=admin
              )
              assert runner.verify().message().content("Command executed")

              # Test user access denied
              with pytest.raises(discord.Forbidden):
                  await runner.message(
                      "!admin_command",
                      channel=admin_channel,
                      member=user
                  )

          async def test_message_cleanup(
              self,
              test_environment: dict,
              mocker: "MockerFixture"
          ) -> None:
              """
              Test message cleanup functionality.

              Args:
                  test_environment: The test environment fixture
                  mocker: Pytest mocker fixture
              """
              channel = test_environment["channels"]["general"]

              # Mock delay
              sleep_mock = mocker.patch("asyncio.sleep")

              # Send temporary message
              await runner.message("!tempmsg", channel=channel)

              # Verify message is deleted after delay
              assert runner.verify().message().deleted()
              assert sleep_mock.called_once_with(60)
      ```

      ## Best Practices

      1. **Use Fixtures for Common Setup**
         ```python
         @pytest.fixture(scope="module")
         async def bot_with_cogs(bot: discord.Client) -> AsyncGenerator[discord.Client, None]:
             """
             Set up bot with required cogs.

             Args:
                 bot: The bot fixture

             Yields:
                 discord.Client: The configured bot
             """
             # Add cogs
             await bot.add_cog(AdminCog(bot))
             await bot.add_cog(UserCog(bot))

             yield bot
         ```

      2. **Clean Up Resources**
         ```python
         @pytest.fixture(autouse=True)
         async def cleanup_after_test() -> AsyncGenerator[None, None]:
             """Ensure test environment is cleaned up after each test."""
             try:
                 yield
             finally:
                 await runner.cleanup()
                 runner.reset_state()
         ```

      3. **Handle Asynchronous Operations**
         ```python
         @pytest.mark.asyncio
         async def test_delayed_response(
             bot: discord.Client,
             test_channel: discord.TextChannel
         ) -> None:
             """
             Test bot responses with delays.

             Args:
                 bot: The bot fixture
                 test_channel: The test channel fixture
             """
             await runner.message("!slowcommand", channel=test_channel)

             # Wait for delayed response
             async with runner.timeout(2):
                 assert await runner.wait_for_message()
         ```

      4. **Group Related Tests**
         ```python
         @pytest.mark.asyncio
         class TestAdminCommands:
             """Test suite for admin commands."""

             @pytest.fixture(autouse=True)
             async def setup_admin(
                 self,
                 test_environment: dict
             ) -> AsyncGenerator[None, None]:
                 """
                 Set up admin test environment.

                 Args:
                     test_environment: The test environment fixture

                 Yields:
                     None
                 """
                 self.admin = test_environment["members"]["admin"]
                 self.admin_channel = test_environment["channels"]["admin"]
                 yield

             async def test_kick_command(self) -> None:
                 """Test the kick command."""
                 await runner.message(
                     "!kick @user",
                     channel=self.admin_channel,
                     member=self.admin
                 )
                 assert runner.verify().member().kicked()
         ```

examples:
  - input: |
      How do I set up a complete test environment for my bot?
    output: |
      Here's how to set up a complete test environment for your bot:

      ```python
      import pytest
      import discord
      from discord.ext.test import runner
      from typing import AsyncGenerator, Dict, Any
      from typing import TYPE_CHECKING

      if TYPE_CHECKING:
          from _pytest.fixtures import FixtureRequest
          from pytest_mock.plugin import MockerFixture
          from discord import Guild, TextChannel, Member, Role

      @pytest.fixture
      async def bot_environment() -> AsyncGenerator[Dict[str, Any], None]:
          """
          Set up a complete bot test environment.

          Yields:
              Dict[str, Any]: Dictionary containing all test environment objects
          """
          # Configure test environment
          runner.configure(
              message_cache_size=1000,
              guild_count=1,
              channel_count=5,
              member_count=10
          )

          # Create bot
          bot = discord.Client()
          await runner.setup(bot)

          # Create guild
          guild = await runner.create_guild()

          # Create roles
          roles = {
              "admin": await runner.create_role(
                  guild,
                  name="Admin",
                  permissions=discord.Permissions.all()
              ),
              "mod": await runner.create_role(
                  guild,
                  name="Moderator",
                  permissions=discord.Permissions(
                      manage_messages=True,
                      kick_members=True
                  )
              ),
              "user": await runner.create_role(
                  guild,
                  name="User"
              )
          }

          # Create channels
          channels = {
              "general": await runner.create_text_channel(
                  guild,
                  name="general"
              ),
              "admin": await runner.create_text_channel(
                  guild,
                  name="admin-only",
                  overwrites={
                      roles["admin"]: discord.PermissionOverwrite(read_messages=True),
                      roles["user"]: discord.PermissionOverwrite(read_messages=False)
                  }
              ),
              "announcements": await runner.create_text_channel(
                  guild,
                  name="announcements",
                  overwrites={
                      roles["user"]: discord.PermissionOverwrite(send_messages=False)
                  }
              )
          }

          # Create members
          members = {
              "admin": await runner.create_member(
                  guild,
                  roles=[roles["admin"]],
                  nick="Admin User"
              ),
              "mod": await runner.create_member(
                  guild,
                  roles=[roles["mod"]],
                  nick="Mod User"
              ),
              "user": await runner.create_member(
                  guild,
                  roles=[roles["user"]],
                  nick="Regular User"
              )
          }

          yield {
              "bot": bot,
              "guild": guild,
              "roles": roles,
              "channels": channels,
              "members": members
          }

          # Cleanup
          await runner.cleanup()

      @pytest.mark.asyncio
      async def test_bot_commands(
          bot_environment: Dict[str, Any]
      ) -> None:
          """
          Test bot commands in the complete environment.

          Args:
              bot_environment: The complete test environment fixture
          """
          # Test admin command
          await runner.message(
              "!admin_command",
              channel=bot_environment["channels"]["admin"],
              member=bot_environment["members"]["admin"]
          )
          assert runner.verify().message().content("Admin command executed")

          # Test user command
          await runner.message(
              "!user_command",
              channel=bot_environment["channels"]["general"],
              member=bot_environment["members"]["user"]
          )
          assert runner.verify().message().content("User command executed")

          # Test permission denial
          with pytest.raises(discord.Forbidden):
              await runner.message(
                  "!admin_command",
                  channel=bot_environment["channels"]["admin"],
                  member=bot_environment["members"]["user"]
              )
      ```

metadata:
  priority: high
  version: 1.0
  tags:
    - discord
    - testing
    - pytest
    - runner
    - configuration
    - dpytest
</rule>
