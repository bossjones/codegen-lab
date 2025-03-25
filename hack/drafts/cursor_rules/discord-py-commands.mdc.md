---
description: Standards and best practices for discord.py commands
globs: *.py
alwaysApply: false
---
# Discord.py Commands Best Practices

This rule provides guidance for implementing commands in discord.py applications.

<rule>
name: discord-py-commands
description: Standards and best practices for implementing discord.py commands
filters:
  # Match Python files that might contain commands
  - type: file_extension
    pattern: "\\.py$"
  # Match files that look like they contain commands
  - type: content
    pattern: "(?s)(commands\\.|@bot\\.command|@commands\\.command)"

actions:
  - type: suggest
    message: |
      # Discord.py Commands Implementation Guide

      When implementing commands in discord.py, follow these guidelines:

      ## 1. Bot Setup and Configuration

      Initialize your bot with proper intents and configuration:

      ```python
      import discord
      from discord.ext import commands
      from typing import Optional, List

      # Set up intents
      intents = discord.Intents.default()
      intents.message_content = True  # Required for message commands
      intents.members = True  # Required for member-related commands

      # Initialize bot with configuration
      class CustomBot(commands.Bot):
          """Custom bot class with additional functionality."""

          def __init__(
              self,
              command_prefix: str,
              intents: discord.Intents,
              description: Optional[str] = None
          ) -> None:
              """
              Initialize the bot with custom configuration.

              Args:
                  command_prefix: The prefix for bot commands
                  intents: Discord intents configuration
                  description: Optional bot description
              """
              super().__init__(
                  command_prefix=command_prefix,
                  intents=intents,
                  description=description
              )

          async def setup_hook(self) -> None:
              """
              Called when the bot is started.
              Set up any necessary connections or resources here.
              """
              # Example: Load extensions
              await self.load_extension("cogs.admin")
              await self.load_extension("cogs.music")

          async def on_ready(self) -> None:
              """Called when the bot is ready and connected to Discord."""
              print(f"Logged in as {self.user} (ID: {self.user.id})")
              print("------")

      # Create bot instance
      bot = CustomBot(command_prefix="!", intents=intents)
      ```

      ## 2. Command Structure

      Commands should be defined as coroutines (async functions) with proper type hints and docstrings:

      ```python
      from typing import Optional
      from discord.ext import commands
      from discord import Member, TextChannel

      @bot.command()
      async def example(
          ctx: commands.Context,
          member: Member,
          channel: Optional[TextChannel] = None
      ) -> None:
          """
          Example command that mentions a member in a specific channel.

          Args:
              ctx: The command context
              member: The member to mention
              channel: Optional channel to send the message in, defaults to current channel
          """
          target_channel = channel or ctx.channel
          await target_channel.send(f"Hello {member.mention}!")
      ```

      ## 3. Command Organization

      Organize commands using groups and cogs:

      ```python
      from discord.ext import commands
      from typing import Optional, List

      class AdminCommands(commands.Cog):
          """Administrative commands for server management."""

          def __init__(self, bot: commands.Bot) -> None:
              """
              Initialize the cog.

              Args:
                  bot: The bot instance
              """
              self.bot = bot

          @commands.group()
          async def admin(self, ctx: commands.Context) -> None:
              """Administrative command group."""
              if ctx.invoked_subcommand is None:
                  await ctx.send("Invalid admin command. Use !help admin for help.")

          @admin.command()
          @commands.has_permissions(manage_roles=True)
          async def role(
              self,
              ctx: commands.Context,
              member: Member,
              role: discord.Role
          ) -> None:
              """
              Add or remove a role from a member.

              Args:
                  ctx: The command context
                  member: The member to modify
                  role: The role to add/remove
              """
              if role in member.roles:
                  await member.remove_roles(role)
                  await ctx.send(f"Removed {role.name} from {member.name}")
              else:
                  await member.add_roles(role)
                  await ctx.send(f"Added {role.name} to {member.name}")

      async def setup(bot: commands.Bot) -> None:
          """
          Set up the cog with the bot.

          Args:
              bot: The bot instance
          """
          await bot.add_cog(AdminCommands(bot))
      ```

      ## 4. Modern Discord Features

      Implement modern Discord UI features using views and modals:

      ```python
      import discord
      from discord.ext import commands
      from typing import Optional

      class RoleButton(discord.ui.Button):
          """Button for role assignment."""

          def __init__(
              self,
              role: discord.Role,
              style: discord.ButtonStyle = discord.ButtonStyle.primary
          ) -> None:
              """
              Initialize the button.

              Args:
                  role: The role to assign
                  style: The button style to use
              """
              super().__init__(
                  label=role.name,
                  style=style,
                  custom_id=f"role_{role.id}"
              )
              self.role = role

          async def callback(self, interaction: discord.Interaction) -> None:
              """
              Handle button click.

              Args:
                  interaction: The button interaction
              """
              assert interaction.user is not None  # for type checker
              if self.role in interaction.user.roles:
                  await interaction.user.remove_roles(self.role)
                  await interaction.response.send_message(
                      f"Removed {self.role.name} role",
                      ephemeral=True
                  )
              else:
                  await interaction.user.add_roles(self.role)
                  await interaction.response.send_message(
                      f"Added {self.role.name} role",
                      ephemeral=True
                  )

      class RoleView(discord.ui.View):
          """Persistent view for role management."""

          def __init__(self, roles: List[discord.Role]) -> None:
              """
              Initialize the view.

              Args:
                  roles: List of roles to include in the view
              """
              super().__init__(timeout=None)  # Make the view persistent
              for role in roles:
                  self.add_item(RoleButton(role))

      @bot.command()
      @commands.has_permissions(manage_roles=True)
      async def setup_roles(
          ctx: commands.Context,
          *roles: discord.Role
      ) -> None:
          """
          Set up a role selection menu.

          Args:
              ctx: The command context
              roles: Roles to include in the menu
          """
          view = RoleView(list(roles))
          await ctx.send("Select roles:", view=view)
      ```

      ## 5. Bot Lifecycle Management

      Implement proper startup and shutdown handling:

      ```python
      import signal
      import sys
      from typing import Optional, Set
      import asyncio

      class Bot(commands.Bot):
          """Custom bot with lifecycle management."""

          def __init__(self, *args, **kwargs) -> None:
              super().__init__(*args, **kwargs)
              self._cleanup_tasks: Set[asyncio.Task] = set()

          async def setup_hook(self) -> None:
              """Set up the bot's initial state and connections."""
              # Set up signal handlers
              for sig in (signal.SIGTERM, signal.SIGINT):
                  self.loop.add_signal_handler(
                      sig,
                      lambda s=sig: asyncio.create_task(self.shutdown(s))
                  )

              # Load extensions
              await self.load_extensions()

          async def shutdown(self, signal: Optional[signal.Signals] = None) -> None:
              """
              Clean shutdown of the bot.

              Args:
                  signal: Optional signal that triggered the shutdown
              """
              if signal:
                  print(f"Received signal {signal.name}, shutting down...")

              # Cancel all tasks
              for task in self._cleanup_tasks:
                  task.cancel()

              # Wait for tasks to complete
              await asyncio.gather(*self._cleanup_tasks, return_exceptions=True)

              # Close all connections
              await self.close()

          def run(self, *args, **kwargs) -> None:
              """Run the bot with error handling."""
              try:
                  asyncio.run(self.start(*args, **kwargs))
              except KeyboardInterrupt:
                  asyncio.run(self.shutdown())
              finally:
                  sys.exit(0)
      ```

      ## 6. Command Registration

      Two ways to register commands:

      ```python
      # Method 1: Direct decorator
      @bot.command()
      async def test(ctx: commands.Context) -> None:
          await ctx.send("Test successful!")

      # Method 2: Manual registration
      @commands.command()
      async def test(ctx: commands.Context) -> None:
          await ctx.send("Test successful!")

      bot.add_command(test)
      ```

      ## 7. Parameter Types and Converters

      Use type hints and converters for automatic argument conversion:

      ```python
      from discord.ext import commands
      from discord import Member, TextChannel, Role

      @bot.command()
      async def promote(
          ctx: commands.Context,
          member: Member,  # Automatically converts mention/ID to Member
          role: Role,      # Automatically converts name/ID to Role
          channel: Optional[TextChannel] = None  # Optional parameter
      ) -> None:
          """
          Promote a member by giving them a role.

          Args:
              ctx: The command context
              member: The member to promote
              role: The role to give
              channel: Optional channel to announce in
          """
          await member.add_roles(role)
          announce_channel = channel or ctx.channel
          await announce_channel.send(f"{member.mention} has been promoted to {role.name}!")
      ```

      ## 8. Custom Converters

      Create custom converters for complex parameter types:

      ```python
      from discord.ext import commands
      from datetime import datetime

      class JoinDistance:
          """Converter that calculates member join/creation time difference."""

          def __init__(self, joined: datetime, created: datetime) -> None:
              self.joined = joined
              self.created = created

          @classmethod
          async def convert(cls, ctx: commands.Context, argument: str) -> "JoinDistance":
              """
              Convert a member mention/ID to JoinDistance.

              Args:
                  ctx: The command context
                  argument: The member mention/ID

              Returns:
                  JoinDistance: Object containing join and creation times
              """
              member = await commands.MemberConverter().convert(ctx, argument)
              return cls(member.joined_at, member.created_at)

          @property
          def delta(self) -> timedelta:
              """Calculate time difference between join and creation."""
              return self.joined - self.created

      @bot.command()
      async def member_age(ctx: commands.Context, *, member: JoinDistance) -> None:
          """
          Check if a member is new to the server.

          Args:
              ctx: The command context
              member: The member to check (converted to JoinDistance)
          """
          is_new = member.delta.days < 100
          await ctx.send("You're pretty new!" if is_new else "You're not so new.")
      ```

      ## 9. Error Handling

      Implement error handlers for commands:

      ```python
      from discord.ext import commands
      from discord.ext.commands import CommandError, MissingPermissions

      @bot.event
      async def on_command_error(ctx: commands.Context, error: CommandError) -> None:
          """
          Global error handler for command errors.

          Args:
              ctx: The command context
              error: The error that occurred
          """
          if isinstance(error, MissingPermissions):
              await ctx.send("You don't have permission to use this command!")
          else:
              await ctx.send(f"An error occurred: {str(error)}")

      @example.error
      async def example_error(ctx: commands.Context, error: CommandError) -> None:
          """
          Command-specific error handler.

          Args:
              ctx: The command context
              error: The error that occurred
          """
          await ctx.send(f"Error in example command: {str(error)}")
      ```

      ## 10. Command Checks

      Use checks to control command access:

      ```python
      from discord.ext import commands
      from typing import Callable

      def is_mod() -> Callable:
          """Check if user has moderator role."""
          async def predicate(ctx: commands.Context) -> bool:
              return discord.utils.get(ctx.author.roles, name="Moderator") is not None
          return commands.check(predicate)

      @bot.command()
      @is_mod()
      async def kick(ctx: commands.Context, member: Member) -> None:
          """
          Kick a member (requires Moderator role).

          Args:
              ctx: The command context
              member: The member to kick
          """
          await member.kick()
          await ctx.send(f"{member.name} has been kicked.")
      ```

examples:
  - input: |
      # Basic bot setup without proper configuration
      bot = commands.Bot(command_prefix="!")

      # Good: Properly configured bot with intents and error handling
      intents = discord.Intents.default()
      intents.message_content = True
      intents.members = True

      class CustomBot(commands.Bot):
          async def setup_hook(self) -> None:
              await self.load_extensions()

          async def on_error(self, event: str, *args, **kwargs) -> None:
              """Handle any unhandled errors."""
              print(f"Error in {event}: {sys.exc_info()[1]}")

      bot = CustomBot(command_prefix="!", intents=intents)
    output: "Bot setup with proper configuration and error handling"

  - input: |
      # Basic command implementation
      @bot.command()
      async def greet(ctx):
          await ctx.send("Hello!")

      # Good: Properly typed command with docstring
      @bot.command()
      async def greet(ctx: commands.Context) -> None:
          """
          Send a greeting message.

          Args:
              ctx: The command context
          """
          await ctx.send("Hello!")
    output: "Command implementation with proper typing and documentation"

  - input: |
      # Missing error handling
      @bot.command()
      async def ban(ctx, member: Member):
          await member.ban()

      # Good: Command with error handling
      @bot.command()
      async def ban(ctx: commands.Context, member: Member) -> None:
          """
          Ban a member from the server.

          Args:
              ctx: The command context
              member: The member to ban
          """
          try:
              await member.ban()
              await ctx.send(f"{member.name} has been banned.")
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
    - commands
    - bot-development
</rule>
