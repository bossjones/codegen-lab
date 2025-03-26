---
description: Router rule for discord.py files that recommends the most appropriate rule to follow
globs: *.py
alwaysApply: false
---

# Discord.py Tasks Best Practices

This rule provides guidance for implementing and managing background tasks in Discord.py bots using the `@tasks.loop` decorator.

<rule>
name: discord-py-tasks
description: Best practices for implementing background tasks in Discord.py bots
filters:
  - type: file_extension
    pattern: "\\.py$"
  - type: content
    pattern: "(?s)@tasks\\.loop|from discord\\.ext import tasks"

actions:
  - type: suggest
    message: |
      # Discord.py Tasks Implementation Guide

      When implementing background tasks in Discord.py bots:

      ## Core Concepts

      1. **Task Decorator Usage**:
         - Use `@tasks.loop` for scheduling recurring tasks
         - Available intervals: seconds, minutes, hours, or specific times
         - Can specify count for limited iterations
         - Handles reconnection logic automatically

      2. **Task Lifecycle Management**:
         - Start tasks in `__init__` or `setup_hook`
         - Cancel tasks in `cog_unload`
         - Use before/after loop hooks for setup/cleanup
         - Handle exceptions appropriately

      ## Best Practices

      1. **Task Organization with Type Hints**:
         ```python
         from typing import List
         from discord.ext import tasks, commands
         import discord
         import datetime

         class TaskCog(commands.Cog):
             def __init__(self, bot: commands.Bot) -> None:
                 self.bot = bot
                 self.my_task.start()  # Start the task

             def cog_unload(self) -> None:
                 self.my_task.cancel()  # Cleanup on unload

             @tasks.loop(minutes=5.0)  # Run every 5 minutes
             async def my_task(self) -> None:
                 """Execute the task every 5 minutes.

                 This task demonstrates proper type hints and documentation.
                 """
                 # Task implementation
                 pass

             @my_task.before_loop
             async def before_my_task(self) -> None:
                 """Wait until the bot is ready before starting the task."""
                 await self.bot.wait_until_ready()
         ```

      2. **Time-based Tasks with Multiple Times**:
         ```python
         from typing import List
         from discord.ext import tasks
         import datetime

         class ScheduledTaskCog(commands.Cog):
             def __init__(self, bot: commands.Bot) -> None:
                 self.bot = bot
                 self.scheduled_task.start()

             # Run at multiple specific times
             @tasks.loop(time=[
                 datetime.time(hour=8, minute=30, tzinfo=datetime.timezone.utc),  # 8:30 UTC
                 datetime.time(hour=16, minute=30, tzinfo=datetime.timezone.utc)  # 16:30 UTC
             ])
             async def scheduled_task(self) -> None:
                 """Execute task at specific times during the day."""
                 await self.process_scheduled_work()
         ```

      3. **Comprehensive Error Handling**:
         ```python
         from typing import Optional, List
         from discord.ext import tasks
         import asyncio
         import logging

         logger = logging.getLogger(__name__)

         class RobustTaskCog(commands.Cog):
             def __init__(self, bot: commands.Bot) -> None:
                 self.bot = bot
                 self.retry_count: int = 0
                 self.max_retries: int = 3
                 self.robust_task.start()

             @tasks.loop(minutes=5.0)
             async def robust_task(self) -> None:
                 """Execute task with comprehensive error handling and retries."""
                 try:
                     await self.process_data()
                     # Reset retry count on success
                     self.retry_count = 0
                 except asyncio.TimeoutError:
                     logger.warning("Task timed out, will retry...")
                     await self.handle_timeout()
                 except Exception as e:
                     await self.handle_error(e)

             async def handle_timeout(self) -> None:
                 """Handle timeout errors with exponential backoff."""
                 if self.retry_count < self.max_retries:
                     self.retry_count += 1
                     backoff = 2 ** self.retry_count
                     logger.info(f"Retrying in {backoff} seconds...")
                     await asyncio.sleep(backoff)
                     await self.robust_task.restart()
                 else:
                     logger.error("Max retries exceeded, stopping task")
                     self.robust_task.cancel()

             async def handle_error(self, error: Exception) -> None:
                 """Handle general errors with logging and notifications."""
                 logger.error(f"Task error: {error}", exc_info=True)
                 # Notify administrators
                 admin_channel = self.bot.get_channel(ADMIN_CHANNEL_ID)
                 if admin_channel:
                     await admin_channel.send(f"Task error: {error}")
         ```

      4. **Advanced Task State Management**:
         ```python
         from typing import Dict, Any, Optional
         from discord.ext import tasks
         import json
         import asyncio

         class StatefulTaskCog(commands.Cog):
             def __init__(self, bot: commands.Bot) -> None:
                 self.bot = bot
                 self.state: Dict[str, Any] = {}
                 self.last_run: Optional[datetime.datetime] = None
                 self.stateful_task.start()

             @tasks.loop(minutes=10.0)
             async def stateful_task(self) -> None:
                 """Execute task with state management."""
                 current_time = datetime.datetime.utcnow()

                 # First run initialization
                 if self.stateful_task.current_loop == 0:
                     self.state = await self.load_initial_state()
                     self.last_run = current_time
                     return

                 # Regular run
                 try:
                     # Process only new data since last run
                     new_data = await self.get_new_data(self.last_run)
                     self.state.update(await self.process_data(new_data))
                     self.last_run = current_time

                     # Persist state periodically
                     if self.stateful_task.current_loop % 6 == 0:  # Every hour
                         await self.save_state()
                 except Exception as e:
                     logger.error(f"State processing error: {e}")
                     await self.handle_error(e)

             async def load_initial_state(self) -> Dict[str, Any]:
                 """Load the initial state from persistent storage."""
                 try:
                     async with aiofiles.open('task_state.json', 'r') as f:
                         return json.loads(await f.read())
                 except FileNotFoundError:
                     return {}

             async def save_state(self) -> None:
                 """Save the current state to persistent storage."""
                 async with aiofiles.open('task_state.json', 'w') as f:
                     await f.write(json.dumps(self.state))
         ```

      ## Advanced Scheduling Patterns

      1. **Dynamic Interval Task**:
         ```python
         class DynamicTaskCog(commands.Cog):
             def __init__(self, bot: commands.Bot) -> None:
                 self.bot = bot
                 self.base_interval: float = 60.0  # 1 minute
                 self.dynamic_task.start()

             @tasks.loop(seconds=60.0)
             async def dynamic_task(self) -> None:
                 """Task with dynamic interval based on load."""
                 start_time = datetime.datetime.utcnow()

                 # Process task
                 load = await self.check_system_load()

                 # Adjust interval based on load
                 if load > 80:  # High load
                     self.dynamic_task.change_interval(seconds=self.base_interval * 2)
                 elif load < 20:  # Low load
                     self.dynamic_task.change_interval(seconds=self.base_interval / 2)
                 else:  # Normal load
                     self.dynamic_task.change_interval(seconds=self.base_interval)
         ```

      2. **Conditional Task Execution**:
         ```python
         class ConditionalTaskCog(commands.Cog):
             def __init__(self, bot: commands.Bot) -> None:
                 self.bot = bot
                 self.should_run: bool = True
                 self.conditional_task.start()

             @tasks.loop(minutes=1.0)
             async def conditional_task(self) -> None:
                 """Task that only executes under certain conditions."""
                 if not self.should_run:
                     return

                 if not await self.check_conditions():
                     logger.info("Conditions not met, skipping task")
                     return

                 await self.process_task()

             async def check_conditions(self) -> bool:
                 """Check if conditions are met for task execution."""
                 # Example conditions
                 return (
                     self.bot.is_ready() and
                     len(self.bot.guilds) > 0 and
                     await self.check_database_connection()
                 )
         ```

      ## Implementation Guidelines

      1. **Wait Until Ready**:
         - Always wait for the bot to be ready before starting tasks
         - Use `@before_loop` decorator with `wait_until_ready()`

      2. **Resource Management**:
         - Clean up resources in `after_loop`
         - Cancel tasks properly in `cog_unload`
         - Handle database connections carefully

      3. **Error Handling**:
         - Add appropriate exception types
         - Log errors for debugging
         - Implement retry logic if needed

      4. **Performance**:
         - Choose appropriate intervals
         - Avoid CPU-intensive operations
         - Use asyncio for I/O operations

examples:
  - input: |
      # Need to implement a status rotation task with error handling
      class MyCog(commands.Cog):
          def __init__(self, bot):
              self.bot = bot
    output: |
      Here's how to implement a robust status rotation task with error handling:

      ```python
      from typing import List
      from discord.ext import tasks, commands
      import discord
      import logging
      import asyncio

      logger = logging.getLogger(__name__)

      class MyCog(commands.Cog):
          def __init__(self, bot: commands.Bot) -> None:
              self.bot = bot
              self.statuses: List[str] = ["Playing with commands", "Helping users", "Running tasks"]
              self.current_status: int = 0
              self.error_count: int = 0
              self.rotate_status.start()

          def cog_unload(self) -> None:
              self.rotate_status.cancel()

          @tasks.loop(minutes=1.0)
          async def rotate_status(self) -> None:
              """Rotate through status messages with error handling."""
              try:
                  status = self.statuses[self.current_status]
                  await self.bot.change_presence(activity=discord.Game(status))
                  self.current_status = (self.current_status + 1) % len(self.statuses)
                  self.error_count = 0  # Reset error count on success
              except discord.HTTPException as e:
                  self.error_count += 1
                  logger.error(f"Failed to update status: {e}")
                  if self.error_count >= 3:
                      logger.critical("Too many errors, stopping status rotation")
                      self.rotate_status.cancel()
              except Exception as e:
                  logger.error(f"Unexpected error: {e}")
                  await asyncio.sleep(5)  # Brief pause before retry

          @rotate_status.before_loop
          async def before_rotate_status(self) -> None:
              """Ensure bot is ready before starting status rotation."""
              await self.bot.wait_until_ready()

          @rotate_status.after_loop
          async def after_rotate_status(self) -> None:
              """Clean up after the status rotation task ends."""
              if self.rotate_status.is_being_cancelled():
                  try:
                      await self.bot.change_presence(activity=None)
                  except Exception as e:
                      logger.error(f"Failed to clear status: {e}")
      ```

metadata:
  priority: high
  version: 1.0
  tags:
    - discord.py
    - tasks
    - background-tasks
    - scheduling
    - error-handling
    - type-hints
</rule>
