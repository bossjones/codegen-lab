---
description: Router rule for discord.py files that recommends the most appropriate rule to follow
globs: *.py
alwaysApply: false
---
# Discord.py Router Rule

This rule analyzes discord.py files and recommends the most appropriate rule to follow based on the file's content and complexity.

<rule>
name: discord-py-router
description: Router rule that recommends the most appropriate discord.py cursor rule
filters:
  # Match Python files
  - type: file_extension
    pattern: "\\.py$"
  # Match discord.py related content
  - type: content
    pattern: "(?i)(discord\\.|discord\\.py|bot\\.run|client\\.run|commands\\.Bot|app_commands)"

actions:
  - type: suggest
    message: |
      Based on the content of this file, I recommend following these discord.py rules:

      1. If the file contains hybrid commands, task loops, or advanced UI components (View, Modal, Select, Button):
         - Use `discord-py-cogs-advanced` for guidance on implementing advanced features
         - Example patterns detected:
           * Hybrid commands (@commands.hybrid_command)
           * Task loops (@tasks.loop)
           * UI components (View, Modal, Select, Button classes)
           * Advanced error handling
           * Complex state management
           * Advanced command features (cooldowns, flags, localization)

      2. If the file contains basic commands or command organization:
         - Use `discord-py-commands` for guidance on command implementation
         - Example patterns detected:
           * Basic commands (@bot.command, @commands.command)
           * Command groups (@commands.group)
           * Parameter converters
           * Basic error handling
           * Command registration patterns

      3. For general discord.py code:
         - Use `discord_py_best_practices` for general guidance
         - Example patterns detected:
           * Basic bot setup
           * Event handlers
           * Client configuration
           * Basic intents setup
           * Logging patterns
           * Development practices

      The rule will be chosen based on these criteria:
      1. If the file contains ANY advanced patterns (hybrid commands, task loops, UI components), use `discord-py-cogs-advanced`
      2. If the file contains command patterns but NO advanced features, use `discord-py-commands`
      3. Otherwise, use `discord_py_best_practices` for general guidance

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

metadata:
  priority: high
  version: 1.0
  tags:
    - discord.py
    - router
    - best-practices
