---
description:
globs:
alwaysApply: false
---
# dpytest Factories System
Comprehensive guide to dpytest's factory system for creating Discord objects in tests

Detailed documentation of dpytest's factory system for creating Discord objects in tests.

<rule>
name: dpytest_factories
description: Guide to using dpytest's factory system for test objects
filters:
  # Match Python files
  - type: file_extension
    pattern: "\\.py$"
  # Match test files
  - type: file_path
    pattern: "tests?/"
  # Match factory-related content
  - type: content
    pattern: "(?i)(factory|create|make|generate|discord.*object)"

actions:
  - type: suggest
    message: |
      # dpytest Factories System

      The factories system in dpytest provides methods for creating Discord objects for testing purposes.

      ## Core Factory Components

      ```
      discord.ext.test.factories
      ├── make_user           # Create user objects
      ├── make_member         # Create guild member objects
      ├── make_role          # Create role objects
      ├── make_channel       # Create channel objects
      ├── make_message       # Create message objects
      └── make_attachment    # Create attachment objects
      ```

      ## User and Member Factories

      ### 1. Creating Users

      ```python
      from discord.ext.test import factories

      # Create a basic user
      user = await factories.make_user(
          username="TestUser",
          discriminator="1234",
          avatar="default"
      )

      # Create a user with specific attributes
      user = await factories.make_user(
          username="TestUser",
          discriminator="1234",
          bot=True,
          system=False,
          verified=True
      )

      # Create multiple users
      users = await factories.make_users(
          count=5,
          prefix="TestUser"
      )
      ```

      ### 2. Creating Members

      ```python
      # Create a basic member
      member = await factories.make_member(
          guild=guild,
          user=user
      )

      # Create a member with roles
      member = await factories.make_member(
          guild=guild,
          user=user,
          roles=[role1, role2],
          nick="Nickname"
      )

      # Create member with specific attributes
      member = await factories.make_member(
          guild=guild,
          user=user,
          joined_at=datetime.utcnow(),
          deaf=False,
          mute=False,
          pending=False
      )
      ```

      ## Channel Factories

      ### 1. Text Channels

      ```python
      # Create a text channel
      text_channel = await factories.make_text_channel(
          name="general",
          guild=guild,
          position=0,
          category=category,
          topic="Channel topic",
          slowmode_delay=0,
          nsfw=False
      )

      # Create a news channel
      news_channel = await factories.make_news_channel(
          name="announcements",
          guild=guild,
          position=1
      )
      ```

      ### 2. Voice Channels

      ```python
      # Create a voice channel
      voice_channel = await factories.make_voice_channel(
          name="General Voice",
          guild=guild,
          position=0,
          user_limit=10,
          bitrate=64000,
          category=category
      )

      # Create a stage channel
      stage_channel = await factories.make_stage_channel(
          name="Stage Events",
          guild=guild,
          position=1
      )
      ```

      ### 3. Categories

      ```python
      # Create a category
      category = await factories.make_category(
          name="Text Channels",
          guild=guild,
          position=0
      )

      # Create category with channels
      category = await factories.make_category_with_channels(
          name="Voice Channels",
          guild=guild,
          channel_names=["voice-1", "voice-2"],
          channel_type="voice"
      )
      ```

      ## Message Factories

      ### 1. Basic Messages

      ```python
      # Create a text message
      message = await factories.make_message(
          content="Test message",
          author=member,
          channel=channel
      )

      # Create a message with mentions
      message = await factories.make_message(
          content="Hello @user",
          author=member,
          channel=channel,
          mentions=[mentioned_user]
      )
      ```

      ### 2. Messages with Embeds

      ```python
      # Create a message with embed
      embed = discord.Embed(title="Test Embed", description="Description")
      message = await factories.make_message(
          author=member,
          channel=channel,
          embeds=[embed]
      )

      # Create a message with multiple embeds
      message = await factories.make_message(
          author=member,
          channel=channel,
          embeds=[embed1, embed2]
      )
      ```

      ### 3. Messages with Attachments

      ```python
      # Create a message with attachment
      attachment = await factories.make_attachment(
          filename="test.txt",
          size=1024,
          url="http://example.com/test.txt"
      )
      message = await factories.make_message(
          author=member,
          channel=channel,
          attachments=[attachment]
      )
      ```

      ## Role Factories

      ```python
      # Create a basic role
      role = await factories.make_role(
          name="Moderator",
          guild=guild,
          permissions=discord.Permissions(
              manage_messages=True,
              kick_members=True
          )
      )

      # Create a role with specific attributes
      role = await factories.make_role(
          name="Admin",
          guild=guild,
          permissions=discord.Permissions.all(),
          color=discord.Color.red(),
          hoist=True,
          mentionable=True
      )
      ```

      ## Advanced Factory Usage

      ### 1. Factory Configuration

      ```python
      # Configure default factory settings
      factories.configure(
          user_prefix="Test",
          guild_prefix="Server",
          channel_prefix="channel"
      )

      # Reset factory configuration
      factories.reset_configuration()
      ```

      ### 2. Custom Factory Methods

      ```python
      async def make_admin_member(guild):
          """Factory method for creating admin members."""
          # Create admin role
          admin_role = await factories.make_role(
              name="Admin",
              guild=guild,
              permissions=discord.Permissions.all()
          )

          # Create user and member
          user = await factories.make_user(username="Admin")
          member = await factories.make_member(
              guild=guild,
              user=user,
              roles=[admin_role]
          )

          return member
      ```

      ### 3. Batch Creation

      ```python
      async def setup_guild_structure(guild):
          """Create multiple guild components at once."""
          # Create categories
          categories = await factories.make_categories(
              guild=guild,
              names=["Text Channels", "Voice Channels"]
          )

          # Create channels in categories
          text_channels = await factories.make_text_channels(
              guild=guild,
              category=categories[0],
              names=["general", "announcements", "chat"]
          )

          voice_channels = await factories.make_voice_channels(
              guild=guild,
              category=categories[1],
              names=["General", "Gaming", "Music"]
          )

          return categories, text_channels, voice_channels
      ```

      ## Best Practices

      1. **Use Factory Methods Over Direct Creation**
         ```python
         # Good: Use factory method
         member = await factories.make_member(guild=guild, user=user)

         # Avoid: Direct creation
         member = discord.Member(...)
         ```

      2. **Clean Up Created Objects**
         ```python
         # Create and clean up objects properly
         try:
             role = await factories.make_role(guild=guild)
             # Test code
         finally:
             await role.delete()
         ```

      3. **Use Meaningful Names**
         ```python
         # Good: Clear purpose
         admin_role = await factories.make_role(name="Admin")
         mod_role = await factories.make_role(name="Moderator")

         # Avoid: Generic names
         role1 = await factories.make_role(name="Role1")
         role2 = await factories.make_role(name="Role2")
         ```

      4. **Group Related Factory Calls**
         ```python
         async def setup_admin_structure(guild):
             """Group related factory calls in a helper function."""
             admin_role = await factories.make_role(
                 name="Admin",
                 permissions=discord.Permissions.all()
             )
             admin_channel = await factories.make_text_channel(
                 name="admin-only",
                 guild=guild
             )
             await admin_channel.set_permissions(
                 admin_role,
                 read_messages=True
             )
             return admin_role, admin_channel
         ```

examples:
  - input: |
      How do I create a complete guild hierarchy with roles and channels?
    output: |
      Here's how to create a complete guild hierarchy:

      ```python
      @pytest.mark.asyncio
      async def test_guild_hierarchy(bot):
          # Create the guild
          guild = await factories.make_guild(name="Test Server")

          # Create roles with hierarchy
          roles = {
              "admin": await factories.make_role(
                  name="Admin",
                  guild=guild,
                  permissions=discord.Permissions.all(),
                  color=discord.Color.red(),
                  hoist=True,
                  position=3
              ),
              "mod": await factories.make_role(
                  name="Moderator",
                  guild=guild,
                  permissions=discord.Permissions(
                      manage_messages=True,
                      kick_members=True
                  ),
                  color=discord.Color.blue(),
                  hoist=True,
                  position=2
              ),
              "member": await factories.make_role(
                  name="Member",
                  guild=guild,
                  permissions=discord.Permissions(
                      send_messages=True,
                      read_messages=True
                  ),
                  color=discord.Color.green(),
                  position=1
              )
          }

          # Create categories
          categories = {
              "text": await factories.make_category(
                  name="Text Channels",
                  guild=guild,
                  position=0
              ),
              "voice": await factories.make_category(
                  name="Voice Channels",
                  guild=guild,
                  position=1
              ),
              "admin": await factories.make_category(
                  name="Admin",
                  guild=guild,
                  position=2
              )
          }

          # Create text channels
          text_channels = {
              "general": await factories.make_text_channel(
                  name="general",
                  guild=guild,
                  category=categories["text"],
                  position=0
              ),
              "announcements": await factories.make_text_channel(
                  name="announcements",
                  guild=guild,
                  category=categories["text"],
                  position=1
              ),
              "admin": await factories.make_text_channel(
                  name="admin-only",
                  guild=guild,
                  category=categories["admin"],
                  position=0
              )
          }

          # Create voice channels
          voice_channels = {
              "general": await factories.make_voice_channel(
                  name="General",
                  guild=guild,
                  category=categories["voice"],
                  position=0
              ),
              "gaming": await factories.make_voice_channel(
                  name="Gaming",
                  guild=guild,
                  category=categories["voice"],
                  position=1
              )
          }

          # Set up permissions
          await text_channels["admin"].set_permissions(
              roles["admin"],
              read_messages=True,
              send_messages=True
          )
          await text_channels["admin"].set_permissions(
              roles["mod"],
              read_messages=False
          )
          await text_channels["announcements"].set_permissions(
              roles["member"],
              send_messages=False
          )

          # Create members with roles
          members = {
              "admin": await factories.make_member(
                  guild=guild,
                  roles=[roles["admin"]],
                  nick="Admin User"
              ),
              "mod": await factories.make_member(
                  guild=guild,
                  roles=[roles["mod"]],
                  nick="Mod User"
              ),
              "user": await factories.make_member(
                  guild=guild,
                  roles=[roles["member"]],
                  nick="Regular User"
              )
          }

          return guild, roles, categories, text_channels, voice_channels, members
      ```

metadata:
  priority: high
  version: 1.0
  tags:
    - discord
    - testing
    - pytest
    - factories
    - objects
    - dpytest
</rule>
