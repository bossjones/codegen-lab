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
</rule>
