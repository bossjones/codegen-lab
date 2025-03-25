---
description: Best practices and reference for working with Discord.py library
globs: *.py
alwaysApply: false
---
# Discord.py Development Guide

This rule serves as a comprehensive router to direct you to the most appropriate Discord.py-specific rules and patterns based on your current task and code context.

<rule>
name: discord-py-router
description: Router rule for Discord.py development that recommends the most appropriate rules and patterns to follow
filters:
  - type: file_extension
    pattern: "\\.py$"
  - type: content
    pattern: "(?s)(discord\\.|discord\\.py|bot\\.run|client\\.run|commands\\.Bot|app_commands|import discord|from discord\\.)"

actions:
  - type: suggest
    message: |
      # Discord.py Development Router

      Based on the content of this file and your current task, follow these guidelines:

      ## Rule Selection

      1. **Advanced Features** - Use `discord-py-cogs-advanced` if working with:
         - Hybrid commands (@commands.hybrid_command)
         - Task loops (@tasks.loop)
         - UI components (View, Modal, Select, Button)
         - Advanced error handling
         - Complex state management
         - Advanced command features (cooldowns, flags, localization)

      2. **Basic Commands** - Use `discord-py-commands` if working with:
         - Basic commands (@bot.command, @commands.command)
         - Command groups (@commands.group)
         - Parameter converters
         - Basic error handling
         - Command registration patterns

      3. **Task and Background Jobs** - Use `discord-py-tasks` if working with:
         - Background tasks using @tasks.loop
         - Scheduled operations
         - Periodic cleanup tasks
         - Status rotation
         - Scheduled announcements

      4. **General Development** - Use `discord_py_best_practices` for:
         - Basic bot setup
         - Event handlers
         - Client configuration
         - Basic intents setup
         - Logging patterns
         - Development practices

      ## Common Development Patterns

      ### 1. Command Development
      When creating bot commands:
      ```python
      @commands.command()
      async def my_command(self, ctx: commands.Context) -> None:
          """Command description.

          Args:
              ctx: The command context
          """
          # Command implementation
          pass
      ```

      ### 2. Event Handling
      When handling Discord events:
      ```python
      @commands.Cog.listener()
      async def on_message(self, message: discord.Message) -> None:
          """Handle message events.

          Args:
              message: The message that triggered the event
          """
          # Event handling
          pass
      ```

      ### 3. Error Handling
      For command error handling:
      ```python
      @commands.Cog.listener()
      async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
          """Handle command errors.

          Args:
              ctx: The command context
              error: The error that occurred
          """
          if isinstance(error, commands.CommandNotFound):
              await ctx.send("Command not found!")
      ```

      ## Best Practices

      1. **Type Hints**
         - Always use type hints for function parameters and return types
         - Import types from `discord.ext.commands` and `typing`
         - Use proper Discord.py type annotations

      2. **Documentation**
         - Add docstrings to all commands and event handlers
         - Include parameter descriptions and usage examples
         - Document command requirements and permissions

      3. **Error Handling**
         - Implement proper error handling for commands
         - Use appropriate exception types
         - Provide user-friendly error messages
         - Handle Discord-specific exceptions

      4. **Resource Management**
         - Clean up resources in `cog_unload`
         - Use context managers for file operations
         - Handle database connections properly
         - Manage task lifecycles

      5. **Code Organization**
         - Use Cogs for organizing related commands
         - Follow consistent naming conventions
         - Separate concerns appropriately
         - Use dependency injection when possible

  - type: analyze
    pattern: |
      # Check for advanced patterns
      (?s)(
        commands\\.hybrid_command|
        tasks\\.loop|
        discord\\.ui\\.(View|Modal|Select|Button)|
        app_commands\\.Group|
        InteractionResponse
      )
    message: Use discord-py-cogs-advanced for implementing advanced discord.py features.

  - type: analyze
    pattern: |
      # Check for command patterns (but not advanced)
      (?s)(
        @(commands|bot)\\.command|
        @commands\\.group|
        commands\\.Cog|
        commands\\.Context
      )
    message: Use discord-py-commands for implementing discord.py commands.

  - type: analyze
    pattern: |
      # Check for task patterns
      (?s)(
        tasks\\.loop|
        @tasks|
        before_loop|
        after_loop
      )
    message: Use discord-py-tasks for implementing background tasks and loops.

  - type: analyze
    pattern: |
      # Check for basic discord.py patterns
      (?s)(
        discord\\.|
        discord\\.py|
        bot\\.run|
        client\\.run|
        commands\\.Bot|
        discord\\.Intents
      )
    message: Use discord_py_best_practices for general discord.py development.

examples:
  - input: |
      # Working on a background task for my Discord bot
      from discord.ext import tasks
    output: |
      You're working with Discord.py tasks. Please refer to the `discord-py-tasks` rule for comprehensive guidance on implementing background tasks.

      Key points from that rule:
      1. Use `@tasks.loop` decorator for scheduling
      2. Implement proper error handling
      3. Use lifecycle hooks (`before_loop`, `after_loop`)
      4. Manage task state appropriately

  - input: |
      # Creating a new Discord bot command
      @commands.command()
      async def hello(self, ctx):
          await ctx.send("Hello!")
    output: |
      You're implementing a Discord bot command. Follow these best practices:

      1. Add type hints:
      ```python
      @commands.command()
      async def hello(self, ctx: commands.Context) -> None:
          """Send a greeting message.

          Args:
              ctx: The command context
          """
          await ctx.send("Hello!")
      ```

      2. Consider error handling if needed
      3. Add proper documentation
      4. Follow command naming conventions

  - input: |
      # Implementing a hybrid command with UI components
      @commands.hybrid_command()
      async def settings(self, ctx):
          view = SettingsView()
          await ctx.send("Bot settings:", view=view)
    output: |
      You're implementing advanced Discord.py features. Use the `discord-py-cogs-advanced` rule for guidance on:

      1. Hybrid commands implementation
      2. UI component best practices
      3. View lifecycle management
      4. Interaction handling
      5. Component state persistence

metadata:
  priority: high
  version: 1.0
  tags:
    - discord.py
    - bot-development
    - routing
    - best-practices
</rule>
