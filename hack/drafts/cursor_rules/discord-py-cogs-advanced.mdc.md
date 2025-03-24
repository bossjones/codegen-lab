---
description: Advanced standards and best practices for discord.py cogs, building upon basic cog patterns
globs: *.py
alwaysApply: false
---
# Discord.py Advanced Cogs Best Practices

This rule provides advanced guidance for implementing cogs in discord.py applications, building upon the basic cog patterns.

@discord-py-cogs.mdc

<rule>
name: discord-py-cogs-advanced
description: Advanced standards and best practices for implementing discord.py cogs
filters:
  # Match Python files that might contain cogs
  - type: file_extension
    pattern: "\\.py$"
  # Match files that look like they contain advanced cog features
  - type: content
    pattern: "(?s)(commands\\.hybrid_command|app_commands\\.|tasks\\.loop|InteractionResponse|View|Modal|Select|Button)"

actions:
  - type: suggest
    message: |
      # Discord.py Advanced Cogs Implementation Guide

      ## 1. Hybrid Commands

      Implement hybrid commands that work as both slash and text commands:

      ```python
      from typing import Optional
      import discord
      from discord.ext import commands
      from discord import app_commands

      class HybridCog(commands.Cog):
          """Cog demonstrating hybrid commands."""

          def __init__(self, bot: commands.Bot) -> None:
              """Initialize the cog."""
              self.bot = bot

          @commands.hybrid_command()
          @app_commands.describe(
              target="The member to get info about",
              detailed="Whether to show detailed information"
          )
          async def userinfo(
              self,
              ctx: commands.Context,
              target: Optional[discord.Member] = None,
              detailed: bool = False
          ) -> None:
              """
              Get information about a user.

              Args:
                  ctx: The command context
                  target: The member to get info about, defaults to command user
                  detailed: Whether to show detailed information
              """
              target = target or ctx.author
              embed = discord.Embed(title=f"User Info - {target.name}")
              embed.add_field(name="ID", value=target.id)
              embed.add_field(name="Joined", value=target.joined_at.strftime("%Y-%m-%d"))

              if detailed:
                  embed.add_field(name="Roles", value=" ".join([r.mention for r in target.roles[1:]]))
                  embed.add_field(name="Created", value=target.created_at.strftime("%Y-%m-%d"))

              await ctx.send(embed=embed)

      ```

      ## 2. Application Commands Groups

      Organize related commands using app command groups:

      ```python
      from typing import Optional, List
      import discord
      from discord.ext import commands
      from discord import app_commands

      class AdminCog(commands.Cog):
          """Advanced admin commands using app command groups."""

          def __init__(self, bot: commands.Bot) -> None:
              """Initialize the cog."""
              self.bot = bot

          mod_group = app_commands.Group(
              name="mod",
              description="Moderation commands",
              guild_only=True
          )

          @mod_group.command(name="timeout")
          @app_commands.describe(
              member="The member to timeout",
              duration="Timeout duration in minutes",
              reason="Reason for the timeout"
          )
          async def timeout_member(
              self,
              interaction: discord.Interaction,
              member: discord.Member,
              duration: int,
              reason: Optional[str] = None
          ) -> None:
              """
              Timeout a member.

              Args:
                  interaction: The command interaction
                  member: The member to timeout
                  duration: Timeout duration in minutes
                  reason: Optional reason for the timeout
              """
              if not interaction.user.guild_permissions.moderate_members:
                  await interaction.response.send_message(
                      "You don't have permission to timeout members!",
                      ephemeral=True
                  )
                  return

              try:
                  await member.timeout(
                      duration=datetime.timedelta(minutes=duration),
                      reason=reason
                  )
                  await interaction.response.send_message(
                      f"Timed out {member.mention} for {duration} minutes" +
                      (f" for {reason}" if reason else "")
                  )
              except discord.Forbidden:
                  await interaction.response.send_message(
                      "I don't have permission to timeout that member!",
                      ephemeral=True
                  )
      ```

      ## 3. Task Loops

      Implement background tasks using task loops:

      ```python
      from typing import Optional, Dict
      import discord
      from discord.ext import commands, tasks
      import datetime

      class TasksCog(commands.Cog):
          """Cog demonstrating task loops."""

          def __init__(self, bot: commands.Bot) -> None:
              """
              Initialize the cog.

              Args:
                  bot: The bot instance
              """
              self.bot = bot
              self.reminder_queue: Dict[int, datetime.datetime] = {}
              self.check_reminders.start()

          def cog_unload(self) -> None:
              """Clean up when cog is unloaded."""
              self.check_reminders.cancel()

          @tasks.loop(minutes=1.0)
          async def check_reminders(self) -> None:
              """Check and send due reminders."""
              current_time = datetime.datetime.now()
              due_reminders = [
                  (user_id, time)
                  for user_id, time in self.reminder_queue.items()
                  if time <= current_time
              ]

              for user_id, _ in due_reminders:
                  user = self.bot.get_user(user_id)
                  if user:
                      await user.send("Your reminder is due!")
                  del self.reminder_queue[user_id]

          @check_reminders.before_loop
          async def before_check_reminders(self) -> None:
              """Wait for bot to be ready before starting loop."""
              await self.bot.wait_until_ready()

          @commands.hybrid_command()
          async def remind(
              self,
              ctx: commands.Context,
              minutes: int,
              *,
              reminder: str
          ) -> None:
              """
              Set a reminder.

              Args:
                  ctx: The command context
                  minutes: Minutes until the reminder
                  reminder: The reminder message
              """
              remind_time = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
              self.reminder_queue[ctx.author.id] = remind_time
              await ctx.send(f"I'll remind you about '{reminder}' in {minutes} minutes!")
      ```

      ## 4. UI Components

      Implement interactive UI components:

      ```python
      from typing import Optional, List
      import discord
      from discord.ext import commands
      from discord.ui import Button, View, Select

      class PollView(View):
          """Custom view for poll buttons."""

          def __init__(self, timeout: Optional[float] = 180) -> None:
              """
              Initialize the poll view.

              Args:
                  timeout: View timeout in seconds
              """
              super().__init__(timeout=timeout)
              self.votes: Dict[str, Set[int]] = {"yes": set(), "no": set()}

          @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
          async def yes_button(
              self,
              interaction: discord.Interaction,
              button: Button
          ) -> None:
              """
              Handle Yes vote.

              Args:
                  interaction: The button interaction
                  button: The button that was pressed
              """
              user_id = interaction.user.id
              self.votes["no"].discard(user_id)
              self.votes["yes"].add(user_id)
              await interaction.response.send_message(
                  "Voted Yes!", ephemeral=True
              )

          @discord.ui.button(label="No", style=discord.ButtonStyle.red)
          async def no_button(
              self,
              interaction: discord.Interaction,
              button: Button
          ) -> None:
              """
              Handle No vote.

              Args:
                  interaction: The button interaction
                  button: The button that was pressed
              """
              user_id = interaction.user.id
              self.votes["yes"].discard(user_id)
              self.votes["no"].add(user_id)
              await interaction.response.send_message(
                  "Voted No!", ephemeral=True
              )

      class UICog(commands.Cog):
          """Cog demonstrating UI components."""

          def __init__(self, bot: commands.Bot) -> None:
              """Initialize the cog."""
              self.bot = bot

          @commands.hybrid_command()
          async def poll(
              self,
              ctx: commands.Context,
              *,
              question: str
          ) -> None:
              """
              Create a poll with buttons.

              Args:
                  ctx: The command context
                  question: The poll question
              """
              view = PollView()
              embed = discord.Embed(
                  title="Poll",
                  description=question
              )
              await ctx.send(embed=embed, view=view)
      ```

      ## 5. Advanced Error Handling

      Implement comprehensive error handling for interactions:

      ```python
      from typing import Optional, Union, Type
      import discord
      from discord.ext import commands
      from discord import app_commands

      class ErrorHandlerCog(commands.Cog):
          """Advanced error handling for commands and interactions."""

          async def cog_app_command_error(
              self,
              interaction: discord.Interaction,
              error: app_commands.AppCommandError
          ) -> None:
              """
              Handle errors for application commands.

              Args:
                  interaction: The command interaction
                  error: The error that occurred
              """
              if isinstance(error, app_commands.CommandOnCooldown):
                  await interaction.response.send_message(
                      f"This command is on cooldown. Try again in {error.retry_after:.2f}s",
                      ephemeral=True
                  )
              elif isinstance(error, app_commands.MissingPermissions):
                  await interaction.response.send_message(
                      "You don't have permission to use this command!",
                      ephemeral=True
                  )
              else:
                  await interaction.response.send_message(
                      f"An error occurred: {str(error)}",
                      ephemeral=True
                  )

          @commands.Cog.listener()
          async def on_interaction_error(
              self,
              interaction: discord.Interaction,
              error: Exception
          ) -> None:
              """
              Handle errors for all interactions.

              Args:
                  interaction: The interaction that errored
                  error: The error that occurred
              """
              if not interaction.response.is_done():
                  await interaction.response.send_message(
                      "An error occurred while processing this interaction.",
                      ephemeral=True
                  )
      ```

      ## 6. Advanced State Management

      Handle complex state with persistence:

      ```python
      from typing import Dict, Optional, Any
      import json
      import discord
      from discord.ext import commands
      from pathlib import Path

      class PersistentStateCog(commands.Cog):
          """Cog demonstrating persistent state management."""

          def __init__(self, bot: commands.Bot) -> None:
              """
              Initialize the cog with persistent state.

              Args:
                  bot: The bot instance
              """
              self.bot = bot
              self.data_path = Path("data/cog_state.json")
              self.data_path.parent.mkdir(exist_ok=True)
              self.state: Dict[str, Any] = self.load_state()

          def load_state(self) -> Dict[str, Any]:
              """
              Load state from disk.

              Returns:
                  The loaded state dictionary
              """
              try:
                  with open(self.data_path, "r") as f:
                      return json.load(f)
              except (FileNotFoundError, json.JSONDecodeError):
                  return {}

          async def save_state(self) -> None:
              """Save current state to disk."""
              with open(self.data_path, "w") as f:
                  json.dump(self.state, f, indent=2)

          async def cog_unload(self) -> None:
              """Save state when cog is unloaded."""
              await self.save_state()

          @commands.Cog.listener()
          async def on_guild_join(self, guild: discord.Guild) -> None:
              """
              Initialize state for new guild.

              Args:
                  guild: The guild that was joined
              """
              if str(guild.id) not in self.state:
                  self.state[str(guild.id)] = {
                      "welcome_channel": None,
                      "auto_roles": [],
                      "custom_prefixes": []
                  }
                  await self.save_state()
      ```

      ## 7. Advanced Command Features

      Implement sophisticated command patterns with cooldowns, flags, and localization:

      ```python
      from typing import Optional, List, Union, Literal
      import discord
      from discord.ext import commands
      from discord import app_commands
      from discord.app_commands import locale_str as _
      import datetime
      from dataclasses import dataclass
      from typing_extensions import Annotated

      @dataclass
      class SearchFlags:
          """Flags for search command."""
          case_sensitive: bool
          limit: int
          before: Optional[datetime.datetime]
          content_type: Literal["text", "images", "files"]

      class AdvancedCommandsCog(commands.Cog):
          """Cog demonstrating advanced command features."""

          def __init__(self, bot: commands.Bot) -> None:
              """
              Initialize the cog.

              Args:
                  bot: The bot instance
              """
              self.bot = bot
              self._cooldowns: Dict[str, Dict[int, datetime.datetime]] = {}

          def get_command_cooldown(
              self,
              command_name: str,
              user_id: int
          ) -> Optional[float]:
              """
              Get remaining cooldown for a command.

              Args:
                  command_name: Name of the command
                  user_id: ID of the user

              Returns:
                  Remaining cooldown in seconds, or None if no cooldown
              """
              if command_name not in self._cooldowns:
                  return None

              last_use = self._cooldowns[command_name].get(user_id)
              if not last_use:
                  return None

              now = datetime.datetime.now()
              cooldown_time = datetime.timedelta(seconds=30)  # Example cooldown
              if now - last_use < cooldown_time:
                  return (last_use + cooldown_time - now).total_seconds()
              return None

          def update_cooldown(
              self,
              command_name: str,
              user_id: int
          ) -> None:
              """
              Update cooldown for a command.

              Args:
                  command_name: Name of the command
                  user_id: ID of the user
              """
              if command_name not in self._cooldowns:
                  self._cooldowns[command_name] = {}
              self._cooldowns[command_name][user_id] = datetime.datetime.now()

          @commands.hybrid_command()
          @commands.cooldown(1, 30, commands.BucketType.user)
          @app_commands.describe(
              query="The search query",
              case_sensitive="Whether to match case sensitively",
              limit="Maximum number of results",
              before="Only show messages before this many days ago",
              content_type="Type of content to search for"
          )
          async def search(
              self,
              ctx: commands.Context,
              query: str,
              case_sensitive: bool = False,
              limit: Optional[int] = 10,
              before: Optional[int] = None,
              content_type: Literal["text", "images", "files"] = "text"
          ) -> None:
              """
              Search for messages with advanced filtering.

              Args:
                  ctx: The command context
                  query: The search query
                  case_sensitive: Whether to match case sensitively
                  limit: Maximum number of results (default: 10)
                  before: Only show messages before this many days ago
                  content_type: Type of content to search for
              """
              # Create flags object for clean parameter handling
              flags = SearchFlags(
                  case_sensitive=case_sensitive,
                  limit=min(limit or 10, 100),  # Cap at 100
                  before=datetime.datetime.now() - datetime.timedelta(days=before) if before else None,
                  content_type=content_type
              )

              # Example search implementation
              messages = []
              async for message in ctx.channel.history(
                  limit=flags.limit * 5,  # Search more to account for filtering
                  before=flags.before
              ):
                  if len(messages) >= flags.limit:
                      break

                  # Apply content type filter
                  if flags.content_type == "images" and not message.attachments:
                      continue
                  elif flags.content_type == "files" and not any(
                      not a.is_image() for a in message.attachments
                  ):
                      continue

                  # Apply query filter
                  content = message.content if flags.case_sensitive else message.content.lower()
                  search_query = query if flags.case_sensitive else query.lower()
                  if search_query in content:
                      messages.append(message)

              if not messages:
                  await ctx.send("No results found.")
                  return

              # Create paginated response
              entries = []
              for msg in messages:
                  content = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
                  entries.append(
                      f"[{msg.created_at.strftime('%Y-%m-%d %H:%M')}] {msg.author}: {content}"
                  )

              # Send paginated results
              pages = [entries[i:i + 5] for i in range(0, len(entries), 5)]
              for i, page in enumerate(pages):
                  embed = discord.Embed(
                      title=f"Search Results (Page {i+1}/{len(pages)})",
                      description="\n\n".join(page)
                  )
                  await ctx.send(embed=embed)

          @commands.hybrid_group(fallback="list")
          @app_commands.guild_only()
          async def alias(self, ctx: commands.Context) -> None:
              """Manage command aliases for the server."""
              # Implementation for listing aliases
              pass

          @alias.command(name="add")
          @app_commands.describe(
              command="The command to create an alias for",
              alias_name="The new alias name"
          )
          async def alias_add(
              self,
              ctx: commands.Context,
              command: str,
              alias_name: str
          ) -> None:
              """
              Add a command alias.

              Args:
                  ctx: The command context
                  command: The command to create an alias for
                  alias_name: The new alias name
              """
              # Implementation for adding aliases
              pass

          # Example of a command with localization
          @commands.hybrid_command()
          @app_commands.describe(
              member="The member to get info about"
          )
          async def profile(
              self,
              ctx: commands.Context,
              member: Optional[discord.Member] = None
          ) -> None:
              """
              Get a member's profile information.

              Args:
                  ctx: The command context
                  member: The member to get info about
              """
              member = member or ctx.author

              # Example of using localized strings
              embed = discord.Embed(title=_("Member Profile"))
              embed.add_field(
                  name=_("Joined Server"),
                  value=discord.utils.format_dt(member.joined_at)
              )
              embed.add_field(
                  name=_("Account Created"),
                  value=discord.utils.format_dt(member.created_at)
              )

              roles = [role.mention for role in reversed(member.roles[1:])]
              embed.add_field(
                  name=_("Roles [{count}]").format(count=len(roles)),
                  value=" ".join(roles) if roles else _("None"),
                  inline=False
              )

              await ctx.send(embed=embed)

          @commands.hybrid_command()
          @app_commands.describe(
              command="The command to check cooldown for"
          )
          async def cooldown(
              self,
              ctx: commands.Context,
              command: str
          ) -> None:
              """
              Check remaining cooldown for a command.

              Args:
                  ctx: The command context
                  command: The command to check cooldown for
              """
              remaining = self.get_command_cooldown(command, ctx.author.id)
              if remaining:
                  await ctx.send(
                      f"You need to wait {remaining:.1f} seconds before using {command} again."
                  )
              else:
                  await ctx.send(f"You can use {command} now!")

          def cog_load(self) -> None:
              """Register command overrides when cog is loaded."""
              # Example of registering a command override
              @self.bot.tree.command()
              @app_commands.guilds(discord.Object(id=123456789))  # Replace with your guild ID
              async def override_example(interaction: discord.Interaction) -> None:
                  """An example of a command override for a specific guild."""
                  await interaction.response.send_message("This is an override!")

          def cog_unload(self) -> None:
              """Clean up command overrides when cog is unloaded."""
              # Remove command overrides
              self.bot.tree.remove_command("override_example")
      ```

      This section demonstrates:
      1. Command cooldowns with custom implementation
      2. Complex argument parsing with flags
      3. Command aliases and groups
      4. Localization support
      5. Command overrides for specific guilds
      6. Advanced parameter validation and processing
      7. Paginated command output
      8. Type hints and documentation for all features

      Key patterns shown:
      - Using dataclasses for structured command flags
      - Custom cooldown tracking and management
      - Command group organization
      - Localization with `locale_str`
      - Command overrides and guild-specific commands
      - Advanced error handling for complex commands
      - Proper type annotations for all parameters
      - Comprehensive command descriptions and help text

      ## 8. Testing Patterns

      Implement comprehensive testing for cogs:

      ```python
      from typing import Optional, Dict, Any, Generator, AsyncGenerator, TYPE_CHECKING
      import pytest
      import discord
      from discord.ext import commands
      import asyncio
      from datetime import datetime, timedelta

      if TYPE_CHECKING:
          from _pytest.capture import CaptureFixture
          from _pytest.fixtures import FixtureRequest
          from _pytest.logging import LogCaptureFixture
          from _pytest.monkeypatch import MonkeyPatch
          from pytest_mock.plugin import MockerFixture

      class MockBot(commands.Bot):
          """Mock bot class for testing."""

          def __init__(self) -> None:
              """Initialize the mock bot."""
              super().__init__(command_prefix="!", intents=discord.Intents.all())
              self.user = discord.Object(id=123)  # Mock bot user
              self.application_id = 123

      class MockGuild(discord.Guild):
          """Mock guild for testing."""

          def __init__(self, **kwargs: Any) -> None:
              """Initialize mock guild with default values."""
              self.id = kwargs.get('id', 123)
              self.name = kwargs.get('name', 'Test Guild')
              self.roles = [discord.Object(id=1)]  # Default @everyone role

      class MockMember(discord.Member):
          """Mock member for testing."""

          def __init__(self, **kwargs: Any) -> None:
              """Initialize mock member with default values."""
              self.id = kwargs.get('id', 456)
              self.name = kwargs.get('name', 'Test User')
              self.guild = kwargs.get('guild', MockGuild())
              self.roles = [discord.Object(id=1)]
              self.joined_at = kwargs.get('joined_at', datetime.now())
              self.created_at = kwargs.get('created_at', datetime.now())

      class MockContext:
          """Mock context for testing commands."""

          def __init__(
              self,
              bot: Optional[commands.Bot] = None,
              author: Optional[discord.Member] = None,
              guild: Optional[discord.Guild] = None,
              **kwargs: Any
          ) -> None:
              """Initialize mock context with configurable values."""
              self.bot = bot or MockBot()
              self.guild = guild or MockGuild()
              self.author = author or MockMember(guild=self.guild)
              self.channel = kwargs.get('channel', discord.Object(id=789))
              self.message = kwargs.get('message', discord.Object(id=101112))
              self.command = kwargs.get('command', None)

          async def send(self, *args: Any, **kwargs: Any) -> None:
              """Mock message sending."""
              return None

      @pytest.fixture
      def mock_bot() -> MockBot:
          """
          Fixture providing a mock bot instance.

          Returns:
              MockBot: A mock bot instance for testing
          """
          return MockBot()

      @pytest.fixture
      def mock_guild() -> MockGuild:
          """
          Fixture providing a mock guild.

          Returns:
              MockGuild: A mock guild instance for testing
          """
          return MockGuild()

      @pytest.fixture
      def mock_member(mock_guild: MockGuild) -> MockMember:
          """
          Fixture providing a mock member.

          Args:
              mock_guild: The mock guild fixture

          Returns:
              MockMember: A mock member instance for testing
          """
          return MockMember(guild=mock_guild)

      @pytest.fixture
      def mock_ctx(
          mock_bot: MockBot,
          mock_member: MockMember,
          mock_guild: MockGuild
      ) -> MockContext:
          """
          Fixture providing a mock context.

          Args:
              mock_bot: The mock bot fixture
              mock_member: The mock member fixture
              mock_guild: The mock guild fixture

          Returns:
              MockContext: A mock context instance for testing
          """
          return MockContext(
              bot=mock_bot,
              author=mock_member,
              guild=mock_guild
          )

      class TestHybridCog:
          """Tests for the HybridCog."""

          @pytest.fixture
          async def cog(self, mock_bot: MockBot) -> Generator[HybridCog, None, None]:
              """
              Fixture providing a HybridCog instance.

              Args:
                  mock_bot: The mock bot fixture

              Yields:
                  HybridCog: A cog instance for testing
              """
              cog = HybridCog(mock_bot)
              yield cog
              # Cleanup if needed
              if hasattr(cog, 'cleanup'):
                  await cog.cleanup()

          @pytest.mark.asyncio
          async def test_userinfo_command_basic(
              self,
              cog: HybridCog,
              mock_ctx: MockContext,
              mock_member: MockMember,
              mocker: MockerFixture
          ) -> None:
              """
              Test basic userinfo command functionality.

              Args:
                  cog: The cog fixture
                  mock_ctx: The mock context fixture
                  mock_member: The mock member fixture
                  mocker: The pytest-mock fixture
              """
              # Mock the send method to capture the output
              send_mock = mocker.patch.object(mock_ctx, 'send')

              # Call the command
              await cog.userinfo(mock_ctx, mock_member, detailed=False)

              # Verify the output
              send_mock.assert_called_once()
              call_args = send_mock.call_args[1]
              embed = call_args['embed']

              assert isinstance(embed, discord.Embed)
              assert embed.title == f"User Info - {mock_member.name}"
              assert any(field.name == "ID" for field in embed.fields)

      class TestTasksCog:
          """Tests for the TasksCog."""

          @pytest.fixture
          async def cog(
              self,
              mock_bot: MockBot,
              monkeypatch: MonkeyPatch
          ) -> AsyncGenerator[TasksCog, None]:
              """
              Fixture providing a TasksCog instance.

              Args:
                  mock_bot: The mock bot fixture
                  monkeypatch: The pytest monkeypatch fixture

              Yields:
                  TasksCog: A cog instance for testing
              """
              # Mock the task loop to prevent it from actually running
              monkeypatch.setattr(
                  'discord.ext.tasks.Loop.start',
                  lambda self: None
              )

              cog = TasksCog(mock_bot)
              yield cog

              # Cleanup
              if not cog.check_reminders.is_being_cancelled():
                  cog.check_reminders.cancel()

          @pytest.mark.asyncio
          async def test_reminder_scheduling(
              self,
              cog: TasksCog,
              mock_ctx: MockContext,
              mocker: MockerFixture
          ) -> None:
              """
              Test reminder scheduling functionality.

              Args:
                  cog: The cog fixture
                  mock_ctx: The mock context fixture
                  mocker: The pytest-mock fixture
              """
              # Mock the send method
              send_mock = mocker.patch.object(mock_ctx, 'send')

              # Test scheduling a reminder
              reminder_text = "Test reminder"
              await cog.remind(mock_ctx, 5, reminder=reminder_text)

              # Verify reminder was scheduled
              assert mock_ctx.author.id in cog.reminder_queue
              send_mock.assert_called_once()
              assert reminder_text in send_mock.call_args[0][0]

          @pytest.mark.asyncio
          async def test_reminder_execution(
              self,
              cog: TasksCog,
              mock_bot: MockBot,
              mocker: MockerFixture
          ) -> None:
              """
              Test reminder execution functionality.

              Args:
                  cog: The cog fixture
                  mock_bot: The mock bot fixture
                  mocker: The pytest-mock fixture
              """
              # Mock get_user and send methods
              user = MockMember()
              mocker.patch.object(mock_bot, 'get_user', return_value=user)
              send_mock = mocker.patch.object(user, 'send')

              # Add a due reminder
              cog.reminder_queue[user.id] = datetime.now() - timedelta(minutes=1)

              # Run the check
              await cog.check_reminders()

              # Verify reminder was sent and cleaned up
              send_mock.assert_called_once_with("Your reminder is due!")
              assert user.id not in cog.reminder_queue

      class TestUICog:
          """Tests for the UICog."""

          @pytest.fixture
          async def cog(self, mock_bot: MockBot) -> UICog:
              """
              Fixture providing a UICog instance.

              Args:
                  mock_bot: The mock bot fixture

              Returns:
                  UICog: A cog instance for testing
              """
              return UICog(mock_bot)

          @pytest.mark.asyncio
          async def test_poll_creation(
              self,
              cog: UICog,
              mock_ctx: MockContext,
              mocker: MockerFixture
          ) -> None:
              """
              Test poll creation functionality.

              Args:
                  cog: The cog fixture
                  mock_ctx: The mock context fixture
                  mocker: The pytest-mock fixture
              """
              # Mock the send method
              send_mock = mocker.patch.object(mock_ctx, 'send')

              # Create a poll
              question = "Test poll question?"
              await cog.poll(mock_ctx, question=question)

              # Verify the poll was created correctly
              send_mock.assert_called_once()
              call_args = send_mock.call_args[1]

              assert isinstance(call_args['embed'], discord.Embed)
              assert call_args['embed'].description == question
              assert isinstance(call_args['view'], PollView)

          @pytest.mark.asyncio
          async def test_poll_voting(
              self,
              mocker: MockerFixture
          ) -> None:
              """
              Test poll voting functionality.

              Args:
                  mocker: The pytest-mock fixture
              """
              # Create a poll view
              view = PollView()

              # Mock an interaction
              interaction = mocker.MagicMock()
              interaction.user.id = 123
              response_mock = mocker.MagicMock()
              interaction.response = response_mock

              # Test voting yes
              await view.yes_button.callback(interaction)
              assert 123 in view.votes["yes"]
              assert 123 not in view.votes["no"]
              response_mock.send_message.assert_called_with(
                  "Voted Yes!",
                  ephemeral=True
              )

              # Test changing vote to no
              await view.no_button.callback(interaction)
              assert 123 not in view.votes["yes"]
              assert 123 in view.votes["no"]
              response_mock.send_message.assert_called_with(
                  "Voted No!",
                  ephemeral=True
              )

      class TestErrorHandlerCog:
          """Tests for the ErrorHandlerCog."""

          @pytest.fixture
          async def cog(self, mock_bot: MockBot) -> ErrorHandlerCog:
              """
              Fixture providing an ErrorHandlerCog instance.

              Args:
                  mock_bot: The mock bot fixture

              Returns:
                  ErrorHandlerCog: A cog instance for testing
              """
              return ErrorHandlerCog(mock_bot)

          @pytest.mark.asyncio
          async def test_app_command_error_handling(
              self,
              cog: ErrorHandlerCog,
              mocker: MockerFixture
          ) -> None:
              """
              Test application command error handling.

              Args:
                  cog: The cog fixture
                  mocker: The pytest-mock fixture
              """
              # Mock interaction
              interaction = mocker.MagicMock()
              response_mock = mocker.MagicMock()
              interaction.response = response_mock

              # Test cooldown error
              error = app_commands.CommandOnCooldown(retry_after=5.0)
              await cog.cog_app_command_error(interaction, error)
              response_mock.send_message.assert_called_with(
                  "This command is on cooldown. Try again in 5.00s",
                  ephemeral=True
              )

              # Test permissions error
              error = app_commands.MissingPermissions(["manage_messages"])
              await cog.cog_app_command_error(interaction, error)
              response_mock.send_message.assert_called_with(
                  "You don't have permission to use this command!",
                  ephemeral=True
              )

      class TestPersistentStateCog:
          """Tests for the PersistentStateCog."""

          @pytest.fixture
          def temp_data_dir(self, tmp_path: Path) -> Path:
              """
              Fixture providing a temporary data directory.

              Args:
                  tmp_path: pytest's temporary path fixture

              Returns:
                  Path: Path to temporary data directory
              """
              data_dir = tmp_path / "data"
              data_dir.mkdir()
              return data_dir

          @pytest.fixture
          async def cog(
              self,
              mock_bot: MockBot,
              temp_data_dir: Path,
              monkeypatch: MonkeyPatch
          ) -> PersistentStateCog:
              """
              Fixture providing a PersistentStateCog instance with temporary storage.

              Args:
                  mock_bot: The mock bot fixture
                  temp_data_dir: The temporary data directory fixture
                  monkeypatch: The pytest monkeypatch fixture

              Returns:
                  PersistentStateCog: A cog instance for testing
              """
              cog = PersistentStateCog(mock_bot)
              monkeypatch.setattr(cog, 'data_path', temp_data_dir / "cog_state.json")
              return cog

          @pytest.mark.asyncio
          async def test_state_persistence(
              self,
              cog: PersistentStateCog,
              mock_guild: MockGuild
          ) -> None:
              """
              Test state persistence functionality.

              Args:
                  cog: The cog fixture
                  mock_guild: The mock guild fixture
              """
              # Trigger state initialization
              await cog.on_guild_join(mock_guild)

              # Verify state was initialized
              guild_id = str(mock_guild.id)
              assert guild_id in cog.state
              assert cog.state[guild_id]["welcome_channel"] is None
              assert isinstance(cog.state[guild_id]["auto_roles"], list)

              # Save state
              await cog.save_state()

              # Create new cog instance to test loading
              new_cog = PersistentStateCog(cog.bot)
              new_cog.data_path = cog.data_path

              # Verify state was loaded correctly
              loaded_state = new_cog.load_state()
              assert guild_id in loaded_state
              assert loaded_state[guild_id] == cog.state[guild_id]
      ```

      This section demonstrates:
      1. Mock classes for Discord objects (Bot, Guild, Member, Context)
      2. Fixtures for common test requirements
      3. Comprehensive test cases for different cog types
      4. Testing async code with pytest-asyncio
      5. Testing UI components and interactions
      6. Testing error handlers
      7. Testing persistent state with temporary files
      8. Type hints and documentation for all test code

      Key testing patterns shown:
      - Using pytest fixtures for test setup and cleanup
      - Mocking Discord.py objects and methods
      - Testing async code properly
      - Testing UI interactions and state
      - Testing error handling paths
      - Testing persistent state management
      - Proper type annotations for test code
      - Comprehensive test documentation
</rule>
