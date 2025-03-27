---
description:
globs:
alwaysApply: false
---
# dpytest Core Concepts and Basic Usage
Core concepts and basic usage of dpytest for Discord bot testing
Core documentation for dpytest, a testing framework for Discord bots built with discord.py.

<rule>
name: dpytest_core
description: Core concepts and basic usage of dpytest
filters:
  # Match Python files
  - type: file_extension
    pattern: "\\.py$"
  # Match test files
  - type: file_path
    pattern: "tests?/"
  # Match dpytest-related content
  - type: content
    pattern: "(?i)(discord\\.py|dpytest|bot test|discord bot|pytest)"

actions:
  - type: suggest
    message: |
      # dpytest Core Framework

      dpytest is a testing framework for Discord bots that simulates Discord's environment without connecting to the actual Discord API.

      ## Version Compatibility

      - discord.py 1.7.X: Use `dpytest 0.5.3`
      - discord.py 2.X.X: Use `dpytest>=0.6`
      - Python 3.8+ required

      ## Installation

      ```bash
      # For discord.py 2.X
      pip install dpytest>=0.6

      # For discord.py 1.7.X
      pip install dpytest==0.5.3
      ```

      ## Core Concepts

      1. **Test Environment**
         - Simulated Discord guilds, channels, and users
         - No actual Discord connection needed
         - Controlled test environment

      2. **Message Simulation**
         - Send messages as users
         - Trigger bot commands
         - Verify responses

      3. **Event System**
         - Simulate Discord events
         - Test event handlers
         - Verify event responses

      4. **State Management**
         - Manage test guild state
         - Control member presence
         - Handle permissions

      5. **Verification System**
         - Assert bot responses
         - Verify message content
         - Check embed structure

      ## Basic Setup

      ```python
      import discord
      import discord.ext.commands as commands
      import pytest
      import pytest_asyncio
      import discord.ext.test as dpytest

      @pytest_asyncio.fixture
      async def bot():
          """
          Create a bot instance for testing.

          Returns:
              commands.Bot: Configured bot instance for testing
          """
          # Setup
          intents = discord.Intents.default()
          intents.members = True
          intents.message_content = True

          bot = commands.Bot(
              command_prefix="!",
              intents=intents
          )

          await bot._async_setup_hook()  # setup the loop

          # Configure dpytest
          dpytest.configure(bot)

          yield bot

          # Cleanup
          await dpytest.empty_queue()
      ```

      ## Basic Test Structure

      ```python
      @pytest.mark.asyncio
      async def test_basic_command(bot):
          """Test a basic bot command."""
          # Send a command
          await dpytest.message("!command")

          # Verify response
          assert dpytest.verify().message().content("Expected response")
      ```

      ## Essential Features

      ### 1. Sending Messages

      ```python
      # Send a basic message
      await dpytest.message("Hello!")

      # Send a command
      await dpytest.message("!command")

      # Send a message with mentions
      await dpytest.message("!kick @user")
      ```

      ### 2. Basic Verification

      ```python
      # Verify exact content
      assert dpytest.verify().message().content("Expected message")

      # Verify partial content
      assert dpytest.verify().message().contains().content("partial")

      # Verify message count
      assert dpytest.verify().message_count(1)
      ```

      ### 3. Message Queue Management

      ```python
      # Clear message queue between tests
      await dpytest.empty_queue()

      # Get last message
      message = dpytest.get_message()

      # Get all messages
      messages = dpytest.get_message(count=-1)
      ```

      ## Best Practices

      1. **Test Isolation**
         ```python
         # Always clean up between tests
         await dpytest.empty_queue()
         ```

      2. **Use Fixtures**
         ```python
         @pytest_asyncio.fixture
         async def guild():
             return dpytest.get_config().guilds[0]

         @pytest_asyncio.fixture
         async def channel():
             return dpytest.get_config().channels[0]
         ```

      3. **Group Related Tests**
         ```python
         class TestCommandGroup:
             @pytest.mark.asyncio
             async def test_command_success(self, bot):
                 # Test successful command

             @pytest.mark.asyncio
             async def test_command_failure(self, bot):
                 # Test command failure
         ```

      4. **Error Handling**
         ```python
         @pytest.mark.asyncio
         async def test_command_error(bot):
             await dpytest.message("!invalid")
             assert dpytest.verify().message().contains().content("error")
         ```

examples:
  - input: |
      How do I set up a basic test for my Discord bot?
    output: |
      Here's a complete example of setting up a basic test:

      ```python
      import discord
      import discord.ext.commands as commands
      import pytest
      import pytest_asyncio
      import discord.ext.test as dpytest

      # Define a simple cog
      class BasicCommands(commands.Cog):
          @commands.command()
          async def ping(self, ctx):
              await ctx.send("Pong!")

      @pytest_asyncio.fixture
      async def bot():
          intents = discord.Intents.default()
          intents.members = True
          intents.message_content = True

          bot = commands.Bot(command_prefix="!", intents=intents)
          await bot._async_setup_hook()
          await bot.add_cog(BasicCommands())

          dpytest.configure(bot)

          yield bot

          await dpytest.empty_queue()

      @pytest.mark.asyncio
      async def test_ping(bot):
          await dpytest.message("!ping")
          assert dpytest.verify().message().content("Pong!")
      ```

      Run with: `pytest -v test_bot.py`

metadata:
  priority: high
  version: 1.0
  tags:
    - discord
    - testing
    - pytest
    - discord.py
    - bot-testing
    - core-concepts
</rule>
