---
description: Best practices and reference for working with Discord.py library
globs: *.py
alwaysApply: false
---
# Discord.py Library

Guidelines for working with the Discord.py library for building Discord bots and applications.

<rule>
name: discord_py_best_practices
description: Best practices for working with the Discord.py library
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
      # Discord.py Best Practices

      Discord.py is a modern, feature-rich, and asynchronous Python library for interacting with the Discord API.

      ## Core Components

      ### Client Interface

      The `discord.Client` class is the main entry point for interacting with Discord:

      ```python
      import discord

      intents = discord.Intents.default()
      intents.message_content = True
      client = discord.Client(intents=intents)

      @client.event
      async def on_ready():
          print(f'Logged in as {client.user}')

      client.run('token')
      ```

      ### Command Frameworks

      Discord.py offers two command frameworks:

      1. **Traditional Commands** (`discord.ext.commands`):
         ```python
         from discord.ext import commands

         bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())

         @bot.command()
         async def ping(ctx):
             await ctx.send('Pong!')

         bot.run('token')
         ```

      2. **Slash Commands** (`discord.app_commands`):
         ```python
         import discord
         from discord import app_commands

         intents = discord.Intents.default()
         client = discord.Client(intents=intents)
         tree = app_commands.CommandTree(client)

         @tree.command()
         async def ping(interaction: discord.Interaction):
             await interaction.response.send_message('Pong!')

         client.run('token')
         ```

      ### UI Components

      Discord.py provides classes for interactive UI elements:

      ```python
      class ConfirmView(discord.ui.View):
          def __init__(self):
              super().__init__(timeout=30)
              self.value = None

          @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
          async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
              await interaction.response.send_message("Confirmed!", ephemeral=True)
              self.value = True
              self.stop()

          @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
          async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
              await interaction.response.send_message("Cancelled!", ephemeral=True)
              self.value = False
              self.stop()
      ```

      ## Best Practices

      ### Asynchronous Programming

      1. **Always `await` coroutines**:
         ```python
         # Correct
         await channel.send("Hello")

         # Wrong - coroutine not awaited
         channel.send("Hello")  # This does nothing!
         ```

      2. **Use asynchronous libraries**:
         ```python
         # Correct
         async with aiohttp.ClientSession() as session:
             async with session.get(url) as response:
                 data = await response.json()

         # Wrong - blocks the event loop
         response = requests.get(url)
         data = response.json()
         ```

      3. **Proper task management**:
         ```python
         # Create and track tasks
         task = bot.loop.create_task(my_background_task())
         # Handle exceptions
         task.add_done_callback(lambda t: t.exception())
         ```

      ### Intents Configuration

      Always configure the appropriate intents:

      ```python
      intents = discord.Intents.default()
      intents.message_content = True  # Required for prefix commands
      intents.members = True  # Required for member events
      bot = commands.Bot(command_prefix='!', intents=intents)
      ```

      ### Error Handling

      Implement comprehensive error handling:

      ```python
      @bot.event
      async def on_command_error(ctx, error):
          if isinstance(error, commands.CommandNotFound):
              await ctx.send("Command not found.")
          elif isinstance(error, commands.MissingRequiredArgument):
              await ctx.send(f"Missing required argument: {error.param.name}")
          elif isinstance(error, commands.BadArgument):
              await ctx.send("Bad argument provided.")
          else:
              # Log the error
              print(f"Ignoring exception in command {ctx.command}: {error}")
      ```

      ### UI Component Best Practices

      1. **Handle timeouts**:
         ```python
         class MyView(discord.ui.View):
             def __init__(self):
                 super().__init__(timeout=60)  # 60 second timeout

             async def on_timeout(self):
                 # Disable all components when the view times out
                 for item in self.children:
                     item.disabled = True
         ```

      2. **Respond to interactions promptly**:
         ```python
         @discord.ui.button(label="Click Me")
         async def button_callback(self, interaction, button):
             # Must respond within 3 seconds
             await interaction.response.send_message("Button clicked!")
         ```

      ### Cogs for Organization

      Use Cogs to organize commands:

      ```python
      class ModerationCog(commands.Cog):
          def __init__(self, bot):
              self.bot = bot

          @commands.command()
          @commands.has_permissions(kick_members=True)
          async def kick(self, ctx, member: discord.Member, *, reason=None):
              await member.kick(reason=reason)
              await ctx.send(f'{member} has been kicked.')

      async def setup(bot):
          await bot.add_cog(ModerationCog(bot))
      ```

      ### Testing and Debugging

      Effective testing and debugging are essential for developing reliable Discord bots:

      #### Testing Strategies

      1. **Unit Testing Commands**:
         ```python
         import pytest
         import discord.ext.test as dpytest
         from typing import TYPE_CHECKING, Generator

         if TYPE_CHECKING:
             from pytest_mock import MockerFixture

         @pytest.fixture
         def bot(event_loop: Generator) -> Generator:
             """Create a bot fixture for testing."""
             bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

             # Configure the bot for testing
             dpytest.configure(bot)

             # Yield the bot for the test
             yield bot

             # Cleanup after the test
             dpytest.empty_queue()

         async def test_ping_command(bot: commands.Bot) -> None:
             """Test that the ping command responds with 'Pong!'."""
             # Add the command to test
             @bot.command()
             async def ping(ctx: commands.Context) -> None:
                 await ctx.send("Pong!")

             # Call the command
             await dpytest.message("!ping")

             # Verify the response
             assert dpytest.verify().message().content("Pong!")
         ```

      2. **Mocking Discord API**:
         ```python
         async def test_user_info(bot: commands.Bot, mocker: "MockerFixture") -> None:
             """Test the user info command with mocked data."""
             # Mock the Member object
             mock_member = mocker.MagicMock(spec=discord.Member)
             mock_member.display_name = "Test User"
             mock_member.id = 123456789
             mock_member.created_at = datetime.datetime.now()

             # Add the command to test
             @bot.command()
             async def userinfo(ctx: commands.Context, member: discord.Member = None) -> None:
                 member = member or ctx.author
                 await ctx.send(f"Name: {member.display_name}, ID: {member.id}")

             # Mock the get_context method to return our mock member
             mocker.patch("discord.ext.commands.Context.author", mock_member)

             # Call the command
             await dpytest.message("!userinfo")

             # Verify the response
             assert dpytest.verify().message().content(f"Name: Test User, ID: 123456789")
         ```

      3. **Integration Testing**:
         ```python
         # Create a test guild and channels
         @pytest.fixture
         async def test_guild(bot: commands.Bot) -> Generator:
             """Create a test guild with channels for integration testing."""
             guild = await dpytest.simulated_guild()
             text_channel = await dpytest.simulated_text_channel(guild, "general")
             await dpytest.simulated_member(guild, "TestUser")
             yield guild
             # Cleanup happens automatically with dpytest

         async def test_welcome_flow(bot: commands.Bot, test_guild: discord.Guild) -> None:
             """Test the entire welcome flow for new members."""
             # Add the event handler
             @bot.event
             async def on_member_join(member: discord.Member) -> None:
                 channel = discord.utils.get(member.guild.text_channels, name="general")
                 await channel.send(f"Welcome {member.display_name}!")

             # Simulate a member joining
             await dpytest.member_join(user_id=12345, guild=test_guild)

             # Verify the welcome message
             assert dpytest.verify().message().content("Welcome TestUser!")
         ```

      #### Debugging Techniques

      1. **Logging**:
         ```python
         import logging

         # Set up logging
         logger = logging.getLogger('discord')
         logger.setLevel(logging.DEBUG)
         handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
         handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
         logger.addHandler(handler)

         # Use logging in your code
         @bot.command()
         async def debug_command(ctx: commands.Context) -> None:
             logger.info(f"Command called by {ctx.author}")
             try:
                 # Some operation that might fail
                 result = await some_function()
                 logger.debug(f"Operation result: {result}")
                 await ctx.send("Command executed successfully")
             except Exception as e:
                 logger.error(f"Error in debug_command: {e}", exc_info=True)
                 await ctx.send("An error occurred")
         ```

      2. **Development Mode**:
         ```python
         import os

         # Check if we're in development mode
         DEV_MODE = os.getenv("BOT_ENV") == "development"

         @bot.command()
         async def test_feature(ctx: commands.Context) -> None:
             if DEV_MODE:
                 # Additional debug information in development
                 await ctx.send(f"Debug info: {bot.latency * 1000}ms latency")

             # Regular command logic
             await ctx.send("Feature executed")
         ```

      3. **Command Error Debugging**:
         ```python
         @bot.event
         async def on_command_error(ctx: commands.Context, error: commands.CommandError) -> None:
             """Handle command errors with detailed debugging information."""
             if isinstance(error, commands.CommandInvokeError):
                 # Log the original error
                 original = error.original
                 logger.error(f"Command {ctx.command} raised an exception: {original}", exc_info=original)

                 if DEV_MODE:
                     # In development, show the error details
                     await ctx.send(f"Error: {original.__class__.__name__}: {original}")
                     import traceback
                     formatted_tb = "".join(traceback.format_exception(type(original), original, original.__traceback__))
                     # Send the first 1900 characters of the traceback (Discord message limit)
                     await ctx.send(f"```py\n{formatted_tb[:1900]}```")
                 else:
                     # In production, show a user-friendly message
                     await ctx.send("An error occurred while executing the command.")
             else:
                 # Handle other command errors
                 # ...
         ```

      4. **Interactive Debugging**:
         ```python
         @bot.command()
         @commands.is_owner()  # Restrict to bot owner
         async def debug(ctx: commands.Context) -> None:
             """Interactive debugging command for the bot owner."""
             # Get bot status information
             guilds = len(bot.guilds)
             users = sum(g.member_count for g in bot.guilds)
             latency = round(bot.latency * 1000)

             embed = discord.Embed(title="Debug Information", color=discord.Color.blue())
             embed.add_field(name="Guilds", value=str(guilds))
             embed.add_field(name="Users", value=str(users))
             embed.add_field(name="Latency", value=f"{latency}ms")
             embed.add_field(name="Python Version", value=platform.python_version())
             embed.add_field(name="Discord.py Version", value=discord.__version__)

             await ctx.send(embed=embed)
         ```

      5. **Testing Slash Commands**:
         ```python
         # For testing slash commands, you can use a development guild
         TEST_GUILD_ID = discord.Object(id=123456789)  # Your test server ID

         @bot.event
         async def on_ready() -> None:
             # In development, sync commands to test guild only for faster updates
             if DEV_MODE:
                 try:
                     # This syncs only to your test guild
                     await bot.tree.sync(guild=TEST_GUILD_ID)
                     print(f"Synced commands to test guild: {TEST_GUILD_ID.id}")
                 except Exception as e:
                     print(f"Error syncing commands: {e}")
             else:
                 # In production, sync globally (but less frequently)
                 await bot.tree.sync()
                 print("Synced commands globally")
         ```

      ## Common Pitfalls to Avoid

      1. **Blocking the event loop**:
         - Use `asyncio.sleep()` instead of `time.sleep()`
         - Use asynchronous libraries (aiohttp) instead of synchronous ones (requests)
         - Offload CPU-intensive tasks to a thread pool

      2. **Improper interaction handling**:
         - Always respond to interactions within 3 seconds
         - Don't try to use an interaction response more than once

      3. **Context misuse**:
         - Don't store `ctx` for later use outside the command
         - Don't try to use `ctx` after the command has completed

      4. **Token security**:
         - Never hardcode tokens in your code
         - Use environment variables or secure configuration files
         - Rotate tokens if they're ever exposed

      5. **Rate limit issues**:
         - Avoid sending too many requests in a short time
         - Implement cooldowns for commands that make API requests

examples:
  - input: |
      # Creating a basic Discord bot
      I want to create a simple Discord bot with a few commands
    output: |
      Here's how to create a basic Discord bot with a few commands using discord.py:

      ```python
      import discord
      from discord.ext import commands
      import os

      # Set up intents
      intents = discord.Intents.default()
      intents.message_content = True  # Required for prefix commands

      # Create bot instance
      bot = commands.Bot(command_prefix='!', intents=intents)

      @bot.event
      async def on_ready():
          print(f'Logged in as {bot.user} (ID: {bot.user.id})')
          print('------')

      @bot.command()
      async def ping(ctx):
          """Responds with Pong!"""
          await ctx.send('Pong!')

      @bot.command()
      async def hello(ctx):
          """Greets the user"""
          await ctx.send(f'Hello, {ctx.author.mention}!')

      @bot.command()
      async def info(ctx, *, member: discord.Member = None):
          """Shows info about a member"""
          member = member or ctx.author

          embed = discord.Embed(title=f"User Info - {member}", color=member.color)
          embed.set_thumbnail(url=member.display_avatar.url)
          embed.add_field(name="ID", value=member.id)
          embed.add_field(name="Joined", value=discord.utils.format_dt(member.joined_at))
          embed.add_field(name="Created", value=discord.utils.format_dt(member.created_at))

          await ctx.send(embed=embed)

      # Error handling
      @bot.event
      async def on_command_error(ctx, error):
          if isinstance(error, commands.CommandNotFound):
              await ctx.send("Command not found.")
          elif isinstance(error, commands.MissingRequiredArgument):
              await ctx.send(f"Missing required argument: {error.param.name}")
          else:
              print(f"Error in {ctx.command}: {error}")

      # Run the bot (get token from environment variable)
      bot.run(os.getenv('DISCORD_TOKEN'))
      ```

      Make sure to:
      1. Set up a bot in the Discord Developer Portal
      2. Get your bot token and store it securely (environment variable)
      3. Enable the necessary intents in the Developer Portal
      4. Invite the bot to your server with appropriate permissions

  - input: |
      # Implementing slash commands
      How do I create slash commands with discord.py?
    output: |
      Here's how to implement slash commands with discord.py:

      ```python
      import discord
      from discord import app_commands
      import os

      # Set up the client and command tree
      intents = discord.Intents.default()
      client = discord.Client(intents=intents)
      tree = app_commands.CommandTree(client)

      @client.event
      async def on_ready():
          print(f'Logged in as {client.user} (ID: {client.user.id})')
          # Sync commands with Discord
          await tree.sync()
          print('Synced command tree')
          print('------')

      # Basic slash command
      @tree.command(name="ping", description="Responds with Pong!")
      async def ping(interaction: discord.Interaction):
          await interaction.response.send_message("Pong!")

      # Slash command with parameters
      @tree.command(name="echo", description="Echoes your message")
      @app_commands.describe(message="The message to echo")
      async def echo(interaction: discord.Interaction, message: str):
          await interaction.response.send_message(f"Echo: {message}")

      # Slash command with choices
      @tree.command(name="color", description="Shows a color")
      @app_commands.describe(choice="Choose a color")
      @app_commands.choices(choice=[
          app_commands.Choice(name="Red", value="red"),
          app_commands.Choice(name="Green", value="green"),
          app_commands.Choice(name="Blue", value="blue"),
      ])
      async def color(interaction: discord.Interaction, choice: str):
          await interaction.response.send_message(f"You chose: {choice}")

      # Run the client
      client.run(os.getenv('DISCORD_TOKEN'))
      ```

      If you want to use slash commands with a Bot instance:

      ```python
      from discord.ext import commands

      intents = discord.Intents.default()
      bot = commands.Bot(command_prefix='!', intents=intents)

      @bot.event
      async def on_ready():
          print(f'Logged in as {bot.user} (ID: {bot.user.id})')
          # Sync commands with Discord
          await bot.tree.sync()
          print('Synced command tree')
          print('------')

      @bot.tree.command(name="ping", description="Responds with Pong!")
      async def ping(interaction: discord.Interaction):
          await interaction.response.send_message("Pong!")

      bot.run(os.getenv('DISCORD_TOKEN'))
      ```

      Remember:
      1. Slash commands must be synced with Discord before they appear
      2. Syncing has rate limits, so don't sync on every restart in production
      3. Command names must be lowercase and follow Discord's naming rules
      4. You need the `applications.commands` scope when inviting your bot

  - input: |
      # Creating interactive UI components
      How do I add buttons and select menus to my bot?
    output: |
      Here's how to implement interactive UI components like buttons and select menus:

      ```python
      import discord
      from discord.ext import commands
      import os

      intents = discord.Intents.default()
      intents.message_content = True
      bot = commands.Bot(command_prefix='!', intents=intents)

      # Button example
      class ButtonView(discord.ui.View):
          def __init__(self):
              super().__init__(timeout=60)  # 60 second timeout

          @discord.ui.button(label="Primary", style=discord.ButtonStyle.primary)
          async def primary_button(self, interaction: discord.Interaction, button: discord.ui.Button):
              await interaction.response.send_message("You clicked the primary button!", ephemeral=True)

          @discord.ui.button(label="Secondary", style=discord.ButtonStyle.secondary)
          async def secondary_button(self, interaction: discord.Interaction, button: discord.ui.Button):
              await interaction.response.send_message("You clicked the secondary button!", ephemeral=True)

          @discord.ui.button(label="Success", style=discord.ButtonStyle.green)
          async def success_button(self, interaction: discord.Interaction, button: discord.ui.Button):
              await interaction.response.send_message("You clicked the success button!", ephemeral=True)

          async def on_timeout(self):
              # Disable all components when the view times out
              for item in self.children:
                  item.disabled = True

      # Select menu example
      class SelectView(discord.ui.View):
          def __init__(self):
              super().__init__(timeout=60)

          @discord.ui.select(
              placeholder="Choose a color",
              options=[
                  discord.SelectOption(label="Red", description="The color red", emoji="🔴"),
                  discord.SelectOption(label="Green", description="The color green", emoji="🟢"),
                  discord.SelectOption(label="Blue", description="The color blue", emoji="🔵"),
              ]
          )
          async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
              await interaction.response.send_message(f"You selected {select.values[0]}!", ephemeral=True)

      @bot.command()
      async def buttons(ctx):
          """Shows a message with buttons"""
          await ctx.send("Click a button:", view=ButtonView())

      @bot.command()
      async def select(ctx):
          """Shows a message with a select menu"""
          await ctx.send("Choose an option:", view=SelectView())

      # Modal example (for text input)
      class FeedbackModal(discord.ui.Modal, title="Feedback Form"):
          name = discord.ui.TextInput(label="Name", placeholder="Your name")
          feedback = discord.ui.TextInput(
              label="Feedback",
              placeholder="Your feedback here...",
              style=discord.TextStyle.paragraph
          )

          async def on_submit(self, interaction: discord.Interaction):
              await interaction.response.send_message(
                  f"Thank you for your feedback, {self.name.value}!",
                  ephemeral=True
              )

      class ModalView(discord.ui.View):
          @discord.ui.button(label="Open Form", style=discord.ButtonStyle.primary)
          async def open_form(self, interaction: discord.Interaction, button: discord.ui.Button):
              await interaction.response.send_modal(FeedbackModal())

      @bot.command()
      async def form(ctx):
          """Shows a button that opens a form"""
          await ctx.send("Click to open the form:", view=ModalView())

      bot.run(os.getenv('DISCORD_TOKEN'))
      ```

      Important tips:
      1. Always respond to interactions within 3 seconds
      2. Handle timeouts to prevent stale components
      3. Use ephemeral responses when appropriate for privacy
      4. For persistent components that work after restarts, use `bot.add_view()`
      5. Remember that modals can only be sent in response to an interaction

metadata:
  priority: high
  version: 1.0
  tags:
    - discord
    - discord.py
    - bot
    - async
    - python
</rule>

<rule>
name: discord_py_font_formatter
description: Formatter for consistent font styling in Discord.py code
filters:
  # Match Python files
  - type: file_extension
    pattern: "\\.py$"
  # Match discord.py related content
  - type: content
    pattern: "(?i)(discord\\.|discord\\.py|bot\\.run|client\\.run|commands\\.Bot|app_commands)"

actions:
  - type: format
    message: |
      # Discord.py Font Formatting

      This formatter ensures consistent styling for Discord.py code:

      1. **Class Names**: PascalCase
         - `Client`, `Bot`, `Intents`, `Embed`

      2. **Method Names**: snake_case
         - `on_ready`, `on_message`, `send_message`

      3. **Event Handlers**: Prefixed with `on_`
         - `on_ready`, `on_message`, `on_reaction_add`

      4. **Command Names**: snake_case
         - `ping`, `help_command`, `user_info`

      5. **Variable Names**: snake_case
         - `message_content`, `guild_id`, `channel_name`

      6. **Constants**: UPPER_SNAKE_CASE
         - `TOKEN`, `PREFIX`, `DEFAULT_COLOR`

      7. **Type Annotations**: Include for all parameters and return values
         - `def send(self, content: str) -> Message:`
         - `async def get_user(user_id: int) -> Optional[User]:`

      8. **Docstrings**: Include for all public methods and classes
         - Triple quotes with description and parameter documentation
         - Return value documentation when applicable

      9. **Imports**: Group and order imports
         - Standard library imports first
         - Third-party imports second (including discord)
         - Local imports last
         - Separate groups with a blank line

      10. **Async/Await**: Proper use of async/await keywords
          - All coroutines must be awaited
          - All event handlers and commands must be async

      Example of properly formatted code:

      ```python
      import asyncio
      from typing import Optional, List

      import discord
      from discord.ext import commands

      TOKEN = "your-token-here"
      PREFIX = "!"
      DEFAULT_COLOR = 0x3498db

      class ModerationCog(commands.Cog):
          """A cog for moderation commands."""

          def __init__(self, bot: commands.Bot) -> None:
              """Initialize the cog.

              Args:
                  bot: The bot instance.
              """
              self.bot = bot

          @commands.command()
          async def kick(self, ctx: commands.Context, member: discord.Member, *, reason: Optional[str] = None) -> None:
              """Kick a member from the server.

              Args:
                  ctx: The command context.
                  member: The member to kick.
                  reason: The reason for kicking.
              """
              await member.kick(reason=reason)
              await ctx.send(f"{member.display_name} has been kicked.")
      ```

examples:
  - input: |
      # Formatting Discord.py code
      import discord
      from discord.ext import commands

      bot = commands.Bot(command_prefix='!')

      @bot.event
      async def on_ready():
          print('Bot is ready')

      @bot.command()
      async def ping(ctx):
          await ctx.send('pong')

      bot.run('token')
    output: |
      Your code follows most Discord.py conventions, but could use some improvements:

      ```python
      import discord
      from discord.ext import commands
      from typing import Optional

      # Constants should be UPPER_SNAKE_CASE
      TOKEN = "your-token-here"

      # Set up intents (best practice)
      intents = discord.Intents.default()
      intents.message_content = True

      bot = commands.Bot(command_prefix='!', intents=intents)

      @bot.event
      async def on_ready() -> None:
          """Event handler called when the bot is ready."""
          print(f'Logged in as {bot.user} (ID: {bot.user.id})')
          print('------')

      @bot.command()
      async def ping(ctx: commands.Context) -> None:
          """Responds with the bot's latency."""
          await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

      # Use environment variables for tokens in production
      bot.run(TOKEN)
      ```

      Key improvements:
      1. Added type annotations
      2. Added docstrings
      3. Added proper intents configuration
      4. Improved the ping command to show latency
      5. Used a constant for the token
      6. Added more detailed on_ready output

  - input: |
      # Formatting a Discord.py cog
      class MusicCommands:
          def __init__(self, bot):
              self.bot = bot

          @commands.command()
          async def play(self, ctx, url):
              # Play music
              await ctx.send(f'Playing {url}')
    output: |
      Here's your code formatted according to Discord.py conventions:

      ```python
      from typing import Optional
      from discord.ext import commands

      class MusicCommands(commands.Cog):
          """A cog for music-related commands."""

          def __init__(self, bot: commands.Bot) -> None:
              """Initialize the music commands cog.

              Args:
                  bot: The bot instance.
              """
              self.bot = bot

          @commands.command()
          async def play(self, ctx: commands.Context, url: str) -> None:
              """Play music from the specified URL.

              Args:
                  ctx: The command context.
                  url: The URL of the music to play.
              """
              # Play music
              await ctx.send(f'Playing {url}')

      async def setup(bot: commands.Bot) -> None:
          """Set up the music commands cog.

          Args:
              bot: The bot instance.
          """
          await bot.add_cog(MusicCommands(bot))
      ```

      Key improvements:
      1. Made the class inherit from `commands.Cog`
      2. Added type annotations
      3. Added docstrings
      4. Added a setup function for the cog

metadata:
  priority: high
  version: 1.0
  tags:
    - discord
    - discord.py
    - formatting
    - style
    - python
</rule>
