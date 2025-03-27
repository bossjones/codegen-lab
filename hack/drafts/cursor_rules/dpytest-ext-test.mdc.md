---
description:
globs:
alwaysApply: false
---
# dpytest Discord Bot Testing Framework
Best practices and reference for testing Discord bots with dpytest
Guidelines for testing Discord bots using the dpytest framework with discord.py.

<rule>
name: dpytest_discord_testing
description: Guidelines for testing Discord bots with dpytest
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
      # dpytest Discord Bot Testing Framework

      dpytest is a Python library designed for testing Discord bots built with discord.py. It provides a framework for simulating Discord interactions in a controlled environment without connecting to the actual Discord API.

      ## Version Compatibility

      - For discord.py 1.7.X, use `dpytest 0.5.3`
      - For discord.py 2.X.X, use `dpytest>=0.6`
      - Requires Python 3.8+

      ## Core Concepts

      1. **Test Environment**: A simulated Discord environment with guilds, channels, and users.
      2. **Message Simulation**: Sending messages as if from users to trigger bot commands.
      3. **Verification**: Asserting that the bot responds correctly to inputs.
      4. **Event Simulation**: Simulating Discord events like reactions, member joins, etc.
      5. **Pytest Integration**: Using pytest fixtures for setup and teardown.

      ## Key Components

      ```
      discord.ext.test
      ├── runner.py       # Main entry point for test configuration and execution
      ├── backend.py      # Core simulation of Discord's backend
      ├── verify.py       # Assertion utilities for verifying bot responses
      ├── factories.py    # Factory methods for creating Discord objects
      ├── callbacks.py    # Event callback management
      ├── state.py        # State management for the test environment
      ├── utils.py        # Utility functions
      ├── voice.py        # Voice channel simulation
      └── websocket.py    # WebSocket simulation
      ```

      ## Basic Usage

      ### Setting Up Tests

      ```python
      import discord
      import discord.ext.commands as commands
      import pytest
      import pytest_asyncio
      import discord.ext.test as dpytest

      @pytest_asyncio.fixture
      async def bot():
          # Setup
          intents = discord.Intents.default()
          intents.members = True
          intents.message_content = True
          b = commands.Bot(command_prefix="!",
                          intents=intents)
          await b._async_setup_hook()  # setup the loop
          await b.add_cog(YourCog())

          dpytest.configure(b)

          yield b

          # Teardown
          await dpytest.empty_queue()  # empty the global message queue as test teardown
      ```

      ### Writing Tests

      ```python
      @pytest.mark.asyncio
      async def test_ping(bot):
          await dpytest.message("!ping")
          assert dpytest.verify().message().content("Pong!")
      ```

      ## Key Features

      ### 1. Message Testing

      ```python
      # Send a message as a user
      await dpytest.message("!command")

      # Verify bot response
      assert dpytest.verify().message().content("Expected response")

      # Verify partial content
      assert dpytest.verify().message().contains().content("partial response")

      # Get the message for custom verification
      message = dpytest.get_message()
      ```

      ### 2. Embed Testing

      ```python
      # Send a command that returns an embed
      await dpytest.message("!embed")

      # Verify the embed
      expected_embed = discord.Embed(title="Expected Title")
      assert dpytest.verify().message().embed(expected_embed)

      # Get the embed for custom verification
      embed = dpytest.get_embed()
      ```

      ### 3. Reaction Testing

      ```python
      # Send a message
      message = await dpytest.message("!react")

      # Add a reaction to the message
      await dpytest.add_reaction(bot.user, message, "👍")

      # Remove a reaction
      await dpytest.remove_reaction(bot.user, message, "👍")
      ```

      ### 4. Member Management

      ```python
      # Simulate a new member joining
      member = await dpytest.member_join()

      # Add a role to a member
      await dpytest.add_role(member, role)

      # Remove a role from a member
      await dpytest.remove_role(member, role)
      ```

      ### 5. Permission Testing

      ```python
      # Set permission overrides for a channel
      await dpytest.set_permission_overrides(
          target=member_or_role,
          channel=channel,
          send_messages=False,
          read_messages=True
      )
      ```

      ## Best Practices

      ### 1. Use Fixtures for Setup

      Create pytest fixtures to handle bot setup and teardown:

      ```python
      # conftest.py
      import pytest_asyncio
      import discord.ext.test as dpytest

      @pytest_asyncio.fixture
      async def bot():
          # Bot setup code
          dpytest.configure(bot)
          yield bot
          await dpytest.empty_queue()
      ```

      ### 2. Clean Message Queue Between Tests

      Always clear the message queue between tests to prevent cross-test contamination:

      ```python
      # At the end of each test or in fixture teardown
      await dpytest.empty_queue()
      ```

      ### 3. Group Related Tests

      Organize tests by functionality or command:

      ```python
      class TestAdminCommands:
          @pytest.mark.asyncio
          async def test_ban(self, bot):
              # Test ban command

          @pytest.mark.asyncio
          async def test_kick(self, bot):
              # Test kick command
      ```

      ### 4. Test Error Handling

      Test how your bot handles errors:

      ```python
      @pytest.mark.asyncio
      async def test_command_error(bot):
          await dpytest.message("!invalid_command")
          assert dpytest.verify().message().content("Command not found")
      ```

      ### 5. Use Verification Chains

      Chain verification methods for clearer assertions:

      ```python
      assert dpytest.verify().message().contains().content("partial").embed(expected_embed)
      ```

examples:
  - input: |
      # Testing a simple ping command
      I want to test my Discord bot's ping command
    output: |
      Here's how to test a simple ping command with dpytest:

      First, set up your test fixture:

      ```python
      import discord
      import discord.ext.commands as commands
      import pytest
      import pytest_asyncio
      import discord.ext.test as dpytest

      class Misc(commands.Cog):
          @commands.command()
          async def ping(self, ctx):
              await ctx.send("Pong!")

      @pytest_asyncio.fixture
      async def bot():
          # Setup
          intents = discord.Intents.default()
          intents.members = True
          intents.message_content = True
          b = commands.Bot(command_prefix="!",
                          intents=intents)
          await b._async_setup_hook()  # setup the loop
          await b.add_cog(Misc())

          dpytest.configure(b)

          yield b

          # Teardown
          await dpytest.empty_queue()
      ```

      Then write your test:

      ```python
      @pytest.mark.asyncio
      async def test_ping(bot):
          await dpytest.message("!ping")
          assert dpytest.verify().message().content("Pong!")
      ```

      Run the test with pytest:

      ```bash
      pytest -xvs test_bot.py
      ```

      This will simulate a user sending "!ping" in a channel and verify that the bot responds with "Pong!".

  - input: |
      # Testing a command with embeds
      How do I test a command that returns an embed?
    output: |
      To test a command that returns an embed, you can use dpytest's embed verification:

      First, define your command that returns an embed:

      ```python
      class InfoCommands(commands.Cog):
          @commands.command()
          async def serverinfo(self, ctx):
              embed = discord.Embed(
                  title="Server Information",
                  description=f"Information about {ctx.guild.name}",
                  color=discord.Color.blue()
              )
              embed.add_field(name="Members", value=str(len(ctx.guild.members)))
              embed.add_field(name="Channels", value=str(len(ctx.guild.channels)))
              await ctx.send(embed=embed)
      ```

      Then write your test:

      ```python
      @pytest.mark.asyncio
      async def test_serverinfo(bot):
          # Send the command
          await dpytest.message("!serverinfo")

          # Create the expected embed
          expected_embed = discord.Embed(
              title="Server Information",
              description="Information about Test Guild 0",
              color=discord.Color.blue()
          )
          expected_embed.add_field(name="Members", value="2")  # Bot + default test user
          expected_embed.add_field(name="Channels", value="2")  # Default text + voice channel

          # Verify the response
          assert dpytest.verify().message().embed(expected_embed)
      ```

      If you need more flexibility in checking the embed:

      ```python
      @pytest.mark.asyncio
      async def test_serverinfo_flexible(bot):
          await dpytest.message("!serverinfo")

          # Get the message and check its embed
          message = dpytest.get_message()
          assert len(message.embeds) == 1

          embed = message.embeds[0]
          assert embed.title == "Server Information"
          assert "Information about" in embed.description
          assert len(embed.fields) == 2
          assert embed.fields[0].name == "Members"
          assert embed.fields[1].name == "Channels"
      ```

  - input: |
      # Testing permission-based commands
      How do I test commands that require specific permissions?
    output: |
      To test permission-based commands, you can use dpytest's permission override functionality:

      First, define a permission-based command:

      ```python
      class AdminCommands(commands.Cog):
          @commands.command()
          @commands.has_permissions(ban_members=True)
          async def ban(self, ctx, member: discord.Member, *, reason=None):
              await ctx.guild.ban(member, reason=reason)
              await ctx.send(f"{member.name} has been banned.")

          @ban.error
          async def ban_error(self, ctx, error):
              if isinstance(error, commands.MissingPermissions):
                  await ctx.send("You don't have permission to ban members.")
      ```

      Then write tests for both success and failure cases:

      ```python
      @pytest.mark.asyncio
      async def test_ban_with_permissions(bot):
          # Get the guild, channel, and a member to ban
          guild = dpytest.get_config().guilds[0]
          channel = dpytest.get_config().channels[0]
          member = dpytest.get_config().members[0]

          # Get the bot member
          bot_member = guild.get_member(bot.user.id)

          # Create a role with ban permissions
          admin_role = await guild.create_role(name="Admin", permissions=discord.Permissions(ban_members=True))

          # Add the role to the bot member
          await dpytest.add_role(bot_member, admin_role)

          # Set permission overrides for the channel
          await dpytest.set_permission_overrides(bot_member, channel, ban_members=True)

          # Test the ban command
          await dpytest.message(f"!ban {member.name} Testing ban command")
          assert dpytest.verify().message().content(f"{member.name} has been banned.")

      @pytest.mark.asyncio
      async def test_ban_without_permissions(bot):
          # Get a member to ban
          member = dpytest.get_config().members[0]

          # Test the ban command without permissions
          # The bot doesn't have ban_members permission by default
          await dpytest.message(f"!ban {member.name} Testing ban command")
          assert dpytest.verify().message().content("You don't have permission to ban members.")
      ```

      This tests both the successful case (when the bot has ban permissions) and the failure case (when it doesn't).

metadata:
  priority: high
  version: 1.0
  tags:
    - discord
    - testing
    - pytest
    - discord.py
    - bot-testing
</rule>
