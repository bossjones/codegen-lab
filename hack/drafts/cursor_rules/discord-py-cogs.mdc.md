---
description: Standards and best practices for discord.py cogs
globs: *.py
alwaysApply: false
---
# Discord.py Cogs Best Practices

This rule provides guidance for implementing cogs in discord.py applications.

<rule>
name: discord-py-cogs
description: Standards and best practices for implementing discord.py cogs
filters:
  # Match Python files that might contain cogs
  - type: file_extension
    pattern: "\\.py$"
  # Match files that look like they contain cogs
  - type: content
    pattern: "(?s)(commands\\.Cog|@commands\\.command|@commands\\.Cog\\.listener)"

actions:
  - type: suggest
    message: |
      # Discord.py Cogs Implementation Guide

      When implementing cogs in discord.py, follow these guidelines:

      ## 1. Cog Structure

      Each cog should be a class that inherits from `commands.Cog`:

      ```python
      from typing import Optional, List
      import discord
      from discord.ext import commands

      class ExampleCog(commands.Cog):
          """Example cog demonstrating best practices."""

          def __init__(self, bot: commands.Bot) -> None:
              """
              Initialize the cog.

              Args:
                  bot: The bot instance
              """
              self.bot = bot
              self._last_member = None  # Example of cog-level state

          @commands.Cog.listener()
          async def on_ready(self) -> None:
              """Called when the cog is ready."""
              print(f"{self.__class__.__name__} is ready.")

          async def cog_unload(self) -> None:
              """
              Clean up any resources used by the cog.
              Called automatically when the cog is unloaded.
              """
              # Clean up resources, close connections, etc.
              pass
      ```

      ## 2. Command Implementation

      Commands in cogs should be properly typed and documented:

      ```python
      from typing import Optional
      from discord.ext import commands
      from discord import Member, TextChannel

      class ModCog(commands.Cog):
          """Moderation commands cog."""

          @commands.command()
          @commands.has_permissions(kick_members=True)
          async def kick(
              self,
              ctx: commands.Context,
              member: Member,
              *,
              reason: Optional[str] = None
          ) -> None:
              """
              Kick a member from the server.

              Args:
                  ctx: The command context
                  member: The member to kick
                  reason: Optional reason for the kick
              """
              await member.kick(reason=reason)
              await ctx.send(f"Kicked {member.name}" +
                           (f" for {reason}" if reason else ""))

          @kick.error
          async def kick_error(
              self,
              ctx: commands.Context,
              error: commands.CommandError
          ) -> None:
              """
              Error handler for the kick command.

              Args:
                  ctx: The command context
                  error: The error that occurred
              """
              if isinstance(error, commands.MissingPermissions):
                  await ctx.send("You don't have permission to kick members!")
              else:
                  await ctx.send(f"An error occurred: {str(error)}")
      ```

      ## 3. Event Listeners

      Implement event listeners with proper typing:

      ```python
      from typing import Optional
      import discord
      from discord.ext import commands

      class EventsCog(commands.Cog):
          """Event handling cog."""

          @commands.Cog.listener()
          async def on_member_join(self, member: discord.Member) -> None:
              """
              Called when a member joins the server.

              Args:
                  member: The member who joined
              """
              channel = member.guild.system_channel
              if channel is not None:
                  await channel.send(f"Welcome {member.mention}!")

          @commands.Cog.listener()
          async def on_message(self, message: discord.Message) -> None:
              """
              Called when a message is sent.

              Args:
                  message: The message that was sent
              """
              # Don't respond to bot messages
              if message.author.bot:
                  return

              # Example: Auto-moderate messages
              if any(word in message.content.lower() for word in self.banned_words):
                  await message.delete()
                  await message.channel.send(f"{message.author.mention} "
                                          "That word is not allowed!")
      ```

      ## 4. Cog Setup

      Use the async setup function for cog registration:

      ```python
      from typing import Optional
      import discord
      from discord.ext import commands

      class MyCog(commands.Cog):
          """Example cog with setup function."""

          def __init__(self, bot: commands.Bot) -> None:
              self.bot = bot

      async def setup(bot: commands.Bot) -> None:
          """
          Set up the cog with the bot.

          Args:
              bot: The bot instance
          """
          await bot.add_cog(MyCog(bot))
      ```

      ## 5. Project Structure

      Organize cogs in a dedicated directory:

      ```
      bot/
      ├── cogs/
      │   ├── __init__.py
      │   ├── admin.py
      │   ├── moderation.py
      │   └── utilities.py
      ├── utils/
      │   └── helpers.py
      └── bot.py
      ```

      ## 6. State Management

      Handle cog-level state properly:

      ```python
      from typing import Dict, Optional, Set
      import discord
      from discord.ext import commands

      class StateCog(commands.Cog):
          """Example cog demonstrating state management."""

          def __init__(self, bot: commands.Bot) -> None:
              self.bot = bot
              self.active_polls: Dict[int, Set[int]] = {}  # message_id -> voter_ids
              self._last_member: Optional[discord.Member] = None

          async def cog_unload(self) -> None:
              """Clean up state when cog is unloaded."""
              # Cancel any active polls
              for message_id in self.active_polls.keys():
                  try:
                      message = await self.bot.get_message(message_id)
                      await message.edit(content="Poll cancelled - Cog unloaded")
                  except discord.NotFound:
                      pass
              self.active_polls.clear()
      ```

      ## 7. Error Handling

      Implement cog-level error handling:

      ```python
      from typing import Optional, Union
      import discord
      from discord.ext import commands

      class ErrorHandlerCog(commands.Cog):
          """Example cog with error handling."""

          async def cog_command_error(
              self,
              ctx: commands.Context,
              error: commands.CommandError
          ) -> None:
              """
              Handle errors for all commands in this cog.

              Args:
                  ctx: The command context
                  error: The error that occurred
              """
              if isinstance(error, commands.MissingPermissions):
                  await ctx.send("You don't have permission to use this command!")
              elif isinstance(error, commands.BadArgument):
                  await ctx.send("Invalid argument provided!")
              else:
                  # Log unexpected errors
                  print(f"Unexpected error in {ctx.command}: {error}")
                  await ctx.send("An unexpected error occurred!")
      ```

      ## 8. Resource Management

      Properly manage resources and connections:

      ```python
      from typing import Optional, Dict
      import aiohttp
      import discord
      from discord.ext import commands

      class APICog(commands.Cog):
          """Example cog demonstrating resource management."""

          def __init__(self, bot: commands.Bot) -> None:
              self.bot = bot
              self.session: Optional[aiohttp.ClientSession] = None

          async def cog_load(self) -> None:
              """Set up resources when cog is loaded."""
              self.session = aiohttp.ClientSession()

          async def cog_unload(self) -> None:
              """Clean up resources when cog is unloaded."""
              if self.session is not None:
                  await self.session.close()
                  self.session = None

          @commands.command()
          async def fetch_data(self, ctx: commands.Context, url: str) -> None:
              """
              Fetch data from a URL.

              Args:
                  ctx: The command context
                  url: The URL to fetch data from
              """
              if self.session is None:
                  await ctx.send("API service is not available!")
                  return

              async with self.session.get(url) as response:
                  data = await response.json()
                  await ctx.send(f"Fetched data: {data}")
      ```

      ## 9. Hybrid Commands

      Implement commands that work as both text and slash commands:

      ```python
      from typing import Optional
      import discord
      from discord.ext import commands

      class HybridCog(commands.Cog):
          """Example cog demonstrating hybrid commands."""

          def __init__(self, bot: commands.Bot) -> None:
              self.bot = bot

          @commands.hybrid_command(
              name="stats",
              description="Get server statistics"
          )
          async def stats(
              self,
              ctx: commands.Context,
              channel: Optional[discord.TextChannel] = None
          ) -> None:
              """
              Get statistics for the server or a specific channel.

              This command works as both a text command and a slash command.

              Args:
                  ctx: The command context
                  channel: Optional channel to get stats for. If None, gets server stats.
              """
              target = channel or ctx.channel
              msg = await ctx.send("Calculating statistics...")

              # Example stats calculation
              stats_data = {
                  "messages": sum(1 for _ in await target.history(limit=100).flatten()),
                  "members": len(ctx.guild.members),
                  "channels": len(ctx.guild.channels)
              }

              embed = discord.Embed(title="Server Statistics", color=discord.Color.blue())
              for key, value in stats_data.items():
                  embed.add_field(name=key.capitalize(), value=str(value))

              await msg.edit(content=None, embed=embed)

          @stats.error
          async def stats_error(
              self,
              ctx: commands.Context,
              error: commands.CommandError
          ) -> None:
              """
              Error handler for the stats command.

              Args:
                  ctx: The command context
                  error: The error that occurred
              """
              if isinstance(error, commands.ChannelNotFound):
                  await ctx.send("Could not find that channel!")
              else:
                  await ctx.send(f"An error occurred: {str(error)}")
      ```

      ## 10. Application Commands

      Implement various types of application commands:

      ```python
      from typing import Optional
      import discord
      from discord.ext import commands
      from discord import app_commands

      class ApplicationCommandsCog(commands.Cog):
          """Example cog demonstrating application commands."""

          def __init__(self, bot: commands.Bot) -> None:
              self.bot = bot

          @app_commands.command(
              name="profile",
              description="View a user's profile"
          )
          async def profile(
              self,
              interaction: discord.Interaction,
              user: Optional[discord.Member] = None
          ) -> None:
              """
              View a user's profile using a slash command.

              Args:
                  interaction: The interaction instance
                  user: Optional user to view profile of. If None, shows own profile.
              """
              target = user or interaction.user
              embed = discord.Embed(title=f"{target.name}'s Profile")
              embed.set_thumbnail(url=target.avatar.url)
              embed.add_field(name="Joined", value=target.joined_at.strftime("%Y-%m-%d"))
              embed.add_field(name="Roles", value=len(target.roles))

              await interaction.response.send_message(embed=embed)

          @app_commands.context_menu(name="Get Avatar")
          async def get_avatar(
              self,
              interaction: discord.Interaction,
              user: discord.User
          ) -> None:
              """
              Get a user's avatar using a context menu command.

              Args:
                  interaction: The interaction instance
                  user: The user whose avatar to get
              """
              embed = discord.Embed(title=f"{user.name}'s Avatar")
              embed.set_image(url=user.avatar.url)
              await interaction.response.send_message(embed=embed)

          @app_commands.context_menu(name="Report Message")
          async def report_message(
              self,
              interaction: discord.Interaction,
              message: discord.Message
          ) -> None:
              """
              Report a message using a context menu command.

              Args:
                  interaction: The interaction instance
                  message: The message to report
              """
              # Create a modal for the report
              class ReportModal(discord.ui.Modal, title="Report Message"):
                  reason = discord.ui.TextInput(
                      label="Reason",
                      placeholder="Why are you reporting this message?",
                      required=True
                  )

                  async def on_submit(self, modal_interaction: discord.Interaction) -> None:
                      """Handle modal submission."""
                      # Example: Send to a reports channel
                      reports_channel = interaction.guild.get_channel(REPORTS_CHANNEL_ID)
                      if reports_channel:
                          embed = discord.Embed(title="Message Report")
                          embed.add_field(name="Message", value=message.content)
                          embed.add_field(name="Author", value=message.author.mention)
                          embed.add_field(name="Reason", value=self.reason.value)
                          await reports_channel.send(embed=embed)
                          await modal_interaction.response.send_message(
                              "Report submitted!", ephemeral=True
                          )

              await interaction.response.send_modal(ReportModal())
      ```

      ## 11. Command Groups

      Organize related commands into groups:

      ```python
      from typing import Optional
      import discord
      from discord.ext import commands

      class ModGroupCog(commands.Cog):
          """Example cog demonstrating command groups."""

          def __init__(self, bot: commands.Bot) -> None:
              self.bot = bot

          @commands.group(invoke_without_command=True)
          async def mod(self, ctx: commands.Context) -> None:
              """
              Moderation command group. Shows help if no subcommand is invoked.

              Args:
                  ctx: The command context
              """
              embed = discord.Embed(title="Moderation Commands")
              embed.add_field(
                  name="Available Commands",
                  value="\n".join([
                      "`mod warn <user> [reason]` - Warn a user",
                      "`mod warnings <user>` - List user warnings",
                      "`mod clearwarns <user>` - Clear user warnings"
                  ])
              )
              await ctx.send(embed=embed)

          @mod.command(name="warn")
          @commands.has_permissions(manage_messages=True)
          async def mod_warn(
              self,
              ctx: commands.Context,
              member: discord.Member,
              *,
              reason: Optional[str] = "No reason provided"
          ) -> None:
              """
              Warn a user.

              Args:
                  ctx: The command context
                  member: The member to warn
                  reason: The reason for the warning
              """
              # Example: Store warning in database
              warning_id = await self.store_warning(member.id, reason)
              await ctx.send(
                  f"⚠️ {member.mention} has been warned. (ID: {warning_id})\n"
                  f"Reason: {reason}"
              )

          @mod.command(name="warnings")
          @commands.has_permissions(manage_messages=True)
          async def mod_warnings(
              self,
              ctx: commands.Context,
              member: discord.Member
          ) -> None:
              """
              List a user's warnings.

              Args:
                  ctx: The command context
                  member: The member to check warnings for
              """
              # Example: Fetch warnings from database
              warnings = await self.get_warnings(member.id)
              if not warnings:
                  await ctx.send(f"{member.mention} has no warnings.")
                  return

              embed = discord.Embed(title=f"Warnings for {member.name}")
              for warning in warnings:
                  embed.add_field(
                      name=f"Warning ID: {warning.id}",
                      value=f"Reason: {warning.reason}\nDate: {warning.date}",
                      inline=False
                  )
              await ctx.send(embed=embed)

          @mod.command(name="clearwarns")
          @commands.has_permissions(administrator=True)
          async def mod_clearwarns(
              self,
              ctx: commands.Context,
              member: discord.Member
          ) -> None:
              """
              Clear all warnings for a user.

              Args:
                  ctx: The command context
                  member: The member to clear warnings for
              """
              # Example: Clear warnings from database
              await self.clear_warnings(member.id)
              await ctx.send(f"Cleared all warnings for {member.mention}")
      ```

      ## 12. Task Loops

      Implement background tasks using task loops:

      ```python
      from typing import Optional, Dict, List
      import discord
      from discord.ext import commands, tasks
      from datetime import datetime, timedelta

      class TaskLoopCog(commands.Cog):
          """Example cog demonstrating task loops."""

          def __init__(self, bot: commands.Bot) -> None:
              """
              Initialize the cog.

              Args:
                  bot: The bot instance
              """
              self.bot = bot
              self.reminders: Dict[int, List[Dict]] = {}  # user_id -> reminders
              self.check_reminders.start()  # Start the reminder check loop

          def cog_unload(self) -> None:
              """Clean up when cog is unloaded."""
              self.check_reminders.cancel()  # Stop the reminder check loop

          @tasks.loop(minutes=1)
          async def check_reminders(self) -> None:
              """Check for due reminders every minute."""
              now = datetime.utcnow()
              for user_id, user_reminders in self.reminders.items():
                  # Find reminders that are due
                  due_reminders = [
                      r for r in user_reminders
                      if r["due_time"] <= now
                  ]
                  if not due_reminders:
                      continue

                  # Remove due reminders and notify users
                  self.reminders[user_id] = [
                      r for r in user_reminders
                      if r not in due_reminders
                  ]

                  user = self.bot.get_user(user_id)
                  if user:
                      for reminder in due_reminders:
                          try:
                              await user.send(
                                  f"⏰ Reminder: {reminder['message']}"
                              )
                          except discord.HTTPException:
                              # Handle failed DM
                              pass

          @check_reminders.before_loop
          async def before_check_reminders(self) -> None:
              """Wait for the bot to be ready before starting the loop."""
              await self.bot.wait_until_ready()

          @commands.command()
          async def remind(
              self,
              ctx: commands.Context,
              time: str,
              *,
              message: str
          ) -> None:
              """
              Set a reminder.

              Args:
                  ctx: The command context
                  time: Time until reminder (e.g., '1h30m', '2d')
                  message: The reminder message
              """
              # Parse time string
              total_seconds = 0
              time_units = {
                  's': 1,
                  'm': 60,
                  'h': 3600,
                  'd': 86400
              }

              import re
              time_parts = re.findall(r'(\d+)([smhd])', time.lower())
              for value, unit in time_parts:
                  total_seconds += int(value) * time_units[unit]

              if total_seconds <= 0:
                  await ctx.send("Please provide a valid time!")
                  return

              # Create reminder
              due_time = datetime.utcnow() + timedelta(seconds=total_seconds)
              reminder = {
                  "message": message,
                  "due_time": due_time
              }

              # Store reminder
              if ctx.author.id not in self.reminders:
                  self.reminders[ctx.author.id] = []
              self.reminders[ctx.author.id].append(reminder)

              # Confirm to user
              await ctx.send(
                  f"I'll remind you about '{message}' in {time}!"
              )

          @commands.command()
          async def listreminders(self, ctx: commands.Context) -> None:
              """
              List all your active reminders.

              Args:
                  ctx: The command context
              """
              if not self.reminders.get(ctx.author.id):
                  await ctx.send("You have no active reminders!")
                  return

              embed = discord.Embed(title="Your Reminders")
              for i, reminder in enumerate(self.reminders[ctx.author.id], 1):
                  time_left = reminder["due_time"] - datetime.utcnow()
                  hours = time_left.seconds // 3600
                  minutes = (time_left.seconds % 3600) // 60
                  embed.add_field(
                      name=f"Reminder {i}",
                      value=(
                          f"Message: {reminder['message']}\n"
                          f"Time left: {time_left.days}d {hours}h {minutes}m"
                      ),
                      inline=False
                  )
              await ctx.send(embed=embed)
      ```

      ## 13. Custom Converters and Checks

      Implement custom parameter converters and command checks:

      ```python
      from typing import Optional, Union, Type, Any
      import re
      import discord
      from discord.ext import commands
      from datetime import datetime, timedelta

      class DurationConverter(commands.Converter[timedelta]):
          """Convert duration strings like '1h30m' into timedelta objects."""

          time_regex = re.compile(
              r'^(?:(?P<days>\d+)d)?'
              r'(?:(?P<hours>\d+)h)?'
              r'(?:(?P<minutes>\d+)m)?'
              r'(?:(?P<seconds>\d+)s)?$'
          )

          async def convert(self, ctx: commands.Context, argument: str) -> timedelta:
              """
              Convert a duration string to timedelta.

              Args:
                  ctx: The command context
                  argument: The duration string to convert

              Returns:
                  A timedelta object representing the duration

              Raises:
                  commands.BadArgument: If the duration format is invalid
              """
              match = self.time_regex.match(argument)
              if not match:
                  raise commands.BadArgument(
                      'Invalid duration format. Use combinations of: #d, #h, #m, #s'
                  )

              params = {k: int(v) for k, v in match.groupdict().items() if v}
              if not params:
                  raise commands.BadArgument(
                      'Duration must not be zero or negative'
                  )

              return timedelta(**params)

      class ColorConverter(commands.Converter[discord.Color]):
          """Convert color strings into discord.Color objects."""

          async def convert(self, ctx: commands.Context, argument: str) -> discord.Color:
              """
              Convert a color string to discord.Color.

              Args:
                  ctx: The command context
                  argument: The color string (hex, rgb, or name)

              Returns:
                  A discord.Color object

              Raises:
                  commands.BadArgument: If the color format is invalid
              """
              # Handle hex colors
              if argument.startswith('#'):
                  try:
                      value = int(argument[1:], 16)
                      return discord.Color(value)
                  except ValueError:
                      raise commands.BadArgument('Invalid hex color')

              # Handle RGB format (r,g,b)
              if ',' in argument:
                  try:
                      r, g, b = map(int, argument.split(','))
                      return discord.Color.from_rgb(r, g, b)
                  except (ValueError, TypeError):
                      raise commands.BadArgument('Invalid RGB color')

              # Handle named colors
              color_name = argument.lower()
              if hasattr(discord.Color, color_name):
                  return getattr(discord.Color, color_name)()

              raise commands.BadArgument('Unknown color name')

      def is_moderator() -> commands.check:
          """Check if the user has moderator permissions."""
          async def predicate(ctx: commands.Context) -> bool:
              """
              Check moderator permissions.

              Args:
                  ctx: The command context

              Returns:
                  bool: True if user has required permissions
              """
              return (
                  ctx.author.guild_permissions.manage_messages or
                  ctx.author.guild_permissions.ban_members or
                  ctx.author.guild_permissions.kick_members
              )
          return commands.check(predicate)

      def in_voice() -> commands.check:
          """Check if the user is in a voice channel."""
          async def predicate(ctx: commands.Context) -> bool:
              """
              Check voice channel presence.

              Args:
                  ctx: The command context

              Returns:
                  bool: True if user is in a voice channel
              """
              if not ctx.author.voice or not ctx.author.voice.channel:
                  raise commands.CheckFailure("You must be in a voice channel!")
              return True
          return commands.check(predicate)

      class ModerationCog(commands.Cog):
          """Example cog demonstrating custom converters and checks."""

          def __init__(self, bot: commands.Bot) -> None:
              self.bot = bot

          @commands.command()
          @is_moderator()
          async def timeout(
              self,
              ctx: commands.Context,
              member: discord.Member,
              duration: DurationConverter,
              *,
              reason: Optional[str] = None
          ) -> None:
              """
              Timeout a member for a specified duration.

              Args:
                  ctx: The command context
                  member: The member to timeout
                  duration: The timeout duration (e.g., '1h30m')
                  reason: Optional reason for the timeout
              """
              try:
                  await member.timeout(
                      duration,
                      reason=f"Timeout by {ctx.author}: {reason}" if reason else None
                  )
                  await ctx.send(
                      f"✅ {member.mention} has been timed out for {duration}"
                      + (f"\nReason: {reason}" if reason else "")
                  )
              except discord.Forbidden:
                  await ctx.send("I don't have permission to timeout this member!")
              except discord.HTTPException as e:
                  await ctx.send(f"Failed to timeout member: {str(e)}")

          @commands.command()
          async def rolecolor(
              self,
              ctx: commands.Context,
              role: discord.Role,
              color: ColorConverter
          ) -> None:
              """
              Change a role's color.

              Args:
                  ctx: The command context
                  role: The role to modify
                  color: The new color (hex, rgb, or name)
              """
              if not ctx.author.guild_permissions.manage_roles:
                  await ctx.send("You don't have permission to modify roles!")
                  return

              try:
                  await role.edit(color=color)
                  await ctx.send(f"Updated color for role {role.name}")
              except discord.Forbidden:
                  await ctx.send("I don't have permission to modify this role!")
              except discord.HTTPException as e:
                  await ctx.send(f"Failed to update role color: {str(e)}")

          @commands.command()
          @in_voice()
          async def play(
              self,
              ctx: commands.Context,
              *,
              song: str
          ) -> None:
              """
              Play a song in the voice channel.

              Args:
                  ctx: The command context
                  song: The song to play
              """
              # Example implementation
              await ctx.send(
                  f"Playing {song} in {ctx.author.voice.channel.name}"
              )
      ```

examples:
  - input: |
      # Bad: No type hints or docstrings
      class MyCog(commands.Cog):
          def __init__(self, bot):
              self.bot = bot

          @commands.command()
          async def cmd(self, ctx):
              await ctx.send("Hello!")

      # Good: Proper type hints and docstrings
      class MyCog(commands.Cog):
          """A well-documented cog."""

          def __init__(self, bot: commands.Bot) -> None:
              """
              Initialize the cog.

              Args:
                  bot: The bot instance
              """
              self.bot = bot

          @commands.command()
          async def cmd(self, ctx: commands.Context) -> None:
              """
              Send a greeting message.

              Args:
                  ctx: The command context
              """
              await ctx.send("Hello!")
    output: "Cog implementation with proper typing and documentation"

  - input: |
      # Bad: No error handling
      @commands.command()
      async def ban(self, ctx, member: Member):
          await member.ban()

      # Good: Proper error handling
      @commands.command()
      async def ban(
          self,
          ctx: commands.Context,
          member: Member,
          *,
          reason: Optional[str] = None
      ) -> None:
          """
          Ban a member from the server.

          Args:
              ctx: The command context
              member: The member to ban
              reason: Optional reason for the ban
          """
          try:
              await member.ban(reason=reason)
              await ctx.send(f"Banned {member.name}" +
                           (f" for {reason}" if reason else ""))
          except discord.Forbidden:
              await ctx.send("I don't have permission to ban members!")
          except discord.HTTPException as e:
              await ctx.send(f"Failed to ban member: {str(e)}")
    output: "Command implementation with proper error handling"

metadata:
  priority: high
  version: 1.0
  tags:
    - discord.py
    - cogs
    - bot-development
</rule>
