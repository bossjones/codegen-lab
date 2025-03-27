---
description:
globs:
alwaysApply: false
---
# dpytest Verification System
Comprehensive guide to dpytest's verification system for Discord bot testing

Detailed documentation of dpytest's verification system for asserting bot responses and behavior.

<rule>
name: dpytest_verify
description: Guide to using dpytest's verification system
filters:
  # Match Python files
  - type: file_extension
    pattern: "\\.py$"
  # Match test files
  - type: file_path
    pattern: "tests?/"
  # Match verification-related content
  - type: content
    pattern: "(?i)(verify|assert|check|test|expect)"

actions:
  - type: suggest
    message: |
      # dpytest Verification System

      The verification system in dpytest provides a fluent interface for asserting bot responses and behavior.

      ## Verification Chain Basics

      The verification system uses method chaining to build assertions:

      ```python
      # Basic structure
      dpytest.verify().message().content("expected content")

      # With multiple conditions
      dpytest.verify().message().contains().content("partial")\
                                .has().attachment()\
                                .equals().embed(expected_embed)
      ```

      ## Message Verification

      ### 1. Content Verification

      ```python
      # Exact content match
      assert dpytest.verify().message().content("Expected message")

      # Partial content match
      assert dpytest.verify().message().contains().content("partial")

      # Regular expression match
      assert dpytest.verify().message().matches().content(r"regex pattern")

      # Case-insensitive match
      assert dpytest.verify().message().contains().content("CASE", case_sensitive=False)
      ```

      ### 2. Message Properties

      ```python
      # Verify author
      assert dpytest.verify().message().author(bot.user)

      # Verify channel
      assert dpytest.verify().message().in_channel(channel_id)

      # Verify message type
      assert dpytest.verify().message().of_type(discord.MessageType.default)
      ```

      ## Embed Verification

      ### 1. Basic Embed Checks

      ```python
      # Verify embed exists
      assert dpytest.verify().message().has().embed()

      # Verify specific embed
      expected_embed = discord.Embed(title="Test", description="Description")
      assert dpytest.verify().message().embed(expected_embed)

      # Verify embed count
      assert dpytest.verify().message().has().num_embeds(2)
      ```

      ### 2. Detailed Embed Verification

      ```python
      # Verify embed properties
      assert dpytest.verify().message().embed().has_title().equals("Expected Title")
      assert dpytest.verify().message().embed().has_description().contains("partial")
      assert dpytest.verify().message().embed().has_author().equals("Author Name")
      assert dpytest.verify().message().embed().has_field("Field Name").equals("Field Value")
      ```

      ### 3. Multiple Embeds

      ```python
      # Verify specific embed in a message with multiple embeds
      assert dpytest.verify().message().nth_embed(1).equals(expected_embed)

      # Verify all embeds
      assert dpytest.verify().message().all_embeds().equals([embed1, embed2])
      ```

      ## Attachment Verification

      ```python
      # Verify attachment presence
      assert dpytest.verify().message().has().attachment()

      # Verify attachment properties
      assert dpytest.verify().message().attachment().filename("test.txt")
      assert dpytest.verify().message().attachment().size(1024)
      assert dpytest.verify().message().attachment().content_type("text/plain")
      ```

      ## Reaction Verification

      ```python
      # Verify reaction presence
      assert dpytest.verify().message().has().reaction("👍")

      # Verify reaction count
      assert dpytest.verify().message().reaction("👍").count(2)

      # Verify user reaction
      assert dpytest.verify().message().reaction("👍").by_user(user_id)
      ```

      ## Message Queue Verification

      ```python
      # Verify message count
      assert dpytest.verify().message_count(2)

      # Verify no messages
      assert dpytest.verify().message_count(0)

      # Verify messages in order
      assert dpytest.verify().messages([
          lambda m: m.content == "First message",
          lambda m: m.content == "Second message"
      ])
      ```

      ## Advanced Verification

      ### 1. Custom Verifiers

      ```python
      def custom_verify(message):
          """Custom verification function."""
          return message.content.startswith("!") and len(message.embeds) > 0

      assert dpytest.verify().message().satisfies(custom_verify)
      ```

      ### 2. Timeout Handling

      ```python
      # Verify with timeout
      assert dpytest.verify(timeout=5.0).message().content("Expected")

      # Verify no response within timeout
      with pytest.raises(asyncio.TimeoutError):
          await dpytest.verify(timeout=1.0).message().content("Should not appear")
      ```

      ### 3. Error Messages

      ```python
      # Custom error messages
      assert dpytest.verify().message().content(
          "Expected",
          failure_message="Bot did not respond with expected message"
      )
      ```

      ## Best Practices

      1. **Chain Verifications Logically**
         ```python
         # Good: Clear, logical chain
         assert dpytest.verify().message()\
             .contains().content("partial")\
             .has().embed()\
             .has_title().equals("Title")

         # Avoid: Hard to read chains
         assert dpytest.verify().message().contains().content("partial").has().embed().has_title().equals("Title")
         ```

      2. **Use Appropriate Matchers**
         ```python
         # Good: Use contains() for partial matches
         assert dpytest.verify().message().contains().content("partial")

         # Good: Use equals() for exact matches
         assert dpytest.verify().message().content("exact match")
         ```

      3. **Handle Timeouts**
         ```python
         # Set appropriate timeouts for async operations
         assert dpytest.verify(timeout=2.0).message().content("Expected")
         ```

      4. **Group Related Verifications**
         ```python
         # Verify multiple aspects of the same message
         assert dpytest.verify().message()\
             .content("Command response")\
             .has().embed()\
             .has().attachment()
         ```

examples:
  - input: |
      How do I verify a complex embed response from my bot?
    output: |
      Here's how to verify a complex embed response:

      ```python
      @pytest.mark.asyncio
      async def test_complex_embed(bot):
          # Send command that generates an embed
          await dpytest.message("!serverinfo")

          # Create expected embed
          expected_embed = discord.Embed(
              title="Server Information",
              description="Server details",
              color=discord.Color.blue()
          )
          expected_embed.add_field(name="Members", value="2")
          expected_embed.add_field(name="Channels", value="1")
          expected_embed.set_footer(text="Requested by Test User")

          # Verify the embed
          assert dpytest.verify().message()\
              .has().embed()\
              .equals(expected_embed)\
              .has_title().equals("Server Information")\
              .has_field("Members").equals("2")\
              .has_field("Channels").equals("1")\
              .has_footer().contains("Requested by")

          # Alternative: Verify specific parts
          assert dpytest.verify().message().embed()\
              .has_title().equals("Server Information")\
              .has_description().contains("Server details")\
              .has_color().equals(discord.Color.blue())\
              .has_field("Members")\
              .has_footer()
      ```

metadata:
  priority: high
  version: 1.0
  tags:
    - discord
    - testing
    - pytest
    - verification
    - assertions
    - dpytest
</rule>
