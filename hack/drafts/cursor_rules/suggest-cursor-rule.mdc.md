---
description:
globs:
alwaysApply: false
---

# Cursor Rule Recommender

Intelligent cursor rule recommendation based on user queries

This rule intelligently analyzes user queries and suggests the most appropriate cursor rules to apply, optimizing queries for Claude and providing contextual recommendations.

<rule>
name: cursor-rule-recommender
description: Recommends appropriate cursor rules based on user queries and provides optimized prompts
filters:
  - type: message
    pattern: "(?i)(how|help|need|want|looking for|suggest|recommend|which rule|find rule|any rule)"
  - type: context
    pattern: "(?i)(python|refactor|discord|dpytest|fastmcp|github actions|testing|code|modify|documentation)"

actions:
  - type: instructions
    message: |
      # Cursor Rule Recommendation System

      I'll analyze your query and suggest the most appropriate cursor rules for your task, along with an optimized version of your query for Claude.

      ## Task Analysis

      I'll help you find the most relevant cursor rules by:
      1. Identifying key tasks and technologies in your query
      2. Matching them to available cursor rules
      3. Recommending the most appropriate rules
      4. Optimizing your query for Claude's understanding

      ## Python Development Rules

      If your task involves Python development, consider:

      - **Code Refactoring**: `python-refactor.mdc` for comprehensive refactoring guidelines with TDD
      - **Documentation**: `python-documentation-standards.mdc` for docstring and typing standards
      - **TDD Basics**: `python-tdd-basics.mdc` for test-driven development fundamentals
      - **Modularization**: `python-modularization.mdc` for breaking down monolithic code
      - **POC Development**: `python-poc-development.mdc` for proof-of-concept development
      - **Refactoring Planning**: `python-refactoring-planning.mdc` for planning refactors
      - **Refactoring Workflow**: `python-refactoring-workflow.mdc` for step-by-step refactoring

      ## Discord.py Development Rules

      For Discord bot development with discord.py:

      - **Core Concepts**: `discord-py-cogs.mdc` for cog-based architecture basics
      - **Advanced Patterns**: `discord-py-cogs-advanced.mdc` for advanced cog implementation
      - **Commands**: `discord-py-commands.mdc` for command implementation best practices
      - **Tasks**: `discord-py-tasks.mdc` for background tasks implementation
      - **Routing**: `discord-py-router.mdc` for command routing strategies

      ## Discord.py Testing Rules

      For testing Discord bots:

      - **Core Testing**: `dpytest-core.mdc` for basic testing with dpytest
      - **Test Configuration**: `dpytest-config.mdc` for configuring test environments
      - **Test Callbacks**: `dpytest-callbacks.mdc` for event callback testing
      - **State Management**: `dpytest-state.mdc` for managing test state
      - **Test Verification**: `dpytest-verify.mdc` for verifying bot behavior
      - **Voice Testing**: `dpytest-voice.mdc` for testing voice functionality

      ## FastMCP Development Rules

      For FastMCP tool development:

      - **Core Development**: `fastmcp.mdc` for FastMCP server development basics
      - **Tool Development**: `fastmcp-tools.mdc` for creating MCP tools
      - **Testing**: `fastmcp-testing.mdc` for testing FastMCP tools
      - **Argument Auditing**: `fastmcp_audit_args.mdc` for validating tool arguments

      ## Code Explanation Rules

      For explaining and documenting code changes:

      - **Code Modification**: `explain-code-modification.mdc` for explaining code changes
      - **Chain of Thought**: `anthropic-chain-of-thought.mdc` for structured reasoning

      ## GitHub Actions Rules

      For GitHub Actions workflows:

      - **Security**: `gh-action-security.mdc` for securing GitHub Actions workflows

examples:
  - input: |
      How do I refactor my large Python file into smaller modules?
    output: |
      I'll help you find the right guidance for refactoring your Python code into smaller modules.

      **Optimized Query for Claude:**
      "What is the recommended approach for breaking down a large Python file into smaller modules? I need specific steps for identification, extraction, and testing of components."

      **Recommended Cursor Rules:**

      1. `python-refactor.mdc` - This is the most comprehensive rule for your needs, offering a complete guide to refactoring Python code with TDD practices.

      2. `python-modularization.mdc` - Specifically focuses on breaking down monolithic Python code into smaller, more manageable components.

      3. `python-refactoring-workflow.mdc` - Provides a step-by-step workflow for refactoring tasks.

      4. `python-refactoring-planning.mdc` - Helps with planning your refactoring approach before implementation.

      5. `python-poc-development.mdc` - Useful for creating proof-of-concept implementations during refactoring.

      These rules will guide you through the entire process of breaking down your large Python file while maintaining functionality and ensuring proper test coverage.

  - input: |
      I need to test my Discord bot's voice commands
    output: |
      I'll help you find the right guidance for testing Discord bot voice commands.

      **Optimized Query for Claude:**
      "What is the recommended approach for testing Discord bot voice commands using dpytest? I need specific guidance on setting up the test environment, simulating voice channels, and verifying bot behavior."

      **Recommended Cursor Rules:**

      1. `dpytest-voice.mdc` - This is the primary rule for your needs, focusing specifically on testing Discord voice functionality with dpytest.

      2. `dpytest-core.mdc` - Provides fundamental concepts for Discord bot testing that apply to all test scenarios.

      3. `dpytest-verify.mdc` - Contains verification strategies to confirm your voice commands are working correctly.

      4. `dpytest-config.mdc` - Helps set up the proper test configuration needed for voice testing.

      5. `dpytest.mdc` - Offers general best practices for Discord bot testing that complement voice-specific tests.

      These rules will guide you through setting up a proper testing environment for voice commands, simulating voice interactions, and verifying your bot responds correctly.

  - input: |
      I need to explain the changes I made to the code
    output: |
      I'll help you find the right guidance for explaining your code changes.

      **Optimized Query for Claude:**
      "What is the recommended approach for documenting and explaining code modifications? I need a structured format for presenting the old code, explaining the reasoning behind changes, and showing the new implementation."

      **Recommended Cursor Rules:**

      1. `explain-code-modification.mdc` - This is the primary rule for your needs, providing comprehensive guidelines for explaining code modifications with clear formats and examples.

      2. `anthropic-chain-of-thought.mdc` - Offers structured reasoning techniques using XML tags that can help present your code changes logically.

      The `explain-code-modification.mdc` rule specifically recommends:
      - Referencing and documenting changes with before/after comparisons
      - Using XML tags to structure explanations
      - Providing step-by-step reasoning for complex changes
      - Verifying changes with examples

      These rules will help you create clear, comprehensive explanations of your code changes that others can easily understand.

metadata:
  priority: high
  version: 1.0
  tags:
    - recommendation
    - rule-suggestion
    - query-optimization
</rule>

## Rule Categories and Recommendations

This rule helps users navigate the large collection of cursor rules by analyzing their query and suggesting the most appropriate rules for their specific task. It also optimizes the query for Claude to improve the quality of AI responses.

### Python Development Categories

| Task Type | Primary Rule | Supporting Rules |
|-----------|--------------|------------------|
| General Refactoring | python-refactor.mdc | python-refactoring-workflow.mdc, python-tdd-basics.mdc |
| Documentation | python-documentation-standards.mdc | explain-code-modification.mdc |
| Modularization | python-modularization.mdc | python-refactoring-planning.mdc |
| Proof of Concept | python-poc-development.mdc | python-tdd-basics.mdc |
| Testing | python-tdd-basics.mdc | fastmcp-testing.mdc, pytest-loop.mdc |

### Discord.py Development Categories

| Task Type | Primary Rule | Supporting Rules |
|-----------|--------------|------------------|
| Bot Structure | discord-py-cogs.mdc | discord-py-cogs-advanced.mdc |
| Commands | discord-py-commands.mdc | discord-py-router.mdc |
| Background Tasks | discord-py-tasks.mdc | discord-py-cogs.mdc |
| Extensions | discord-py-cogs-advanced.mdc | discord.mdc |

### Testing Categories

| Task Type | Primary Rule | Supporting Rules |
|-----------|--------------|------------------|
| Discord Bot Testing | dpytest.mdc | dpytest-core.mdc, dpytest-config.mdc |
| Voice Testing | dpytest-voice.mdc | dpytest-verify.mdc |
| State Management | dpytest-state.mdc | dpytest-runner.mdc |
| Test Integration | dpytest-integration.mdc | dpytest-ext-test.mdc |
| FastMCP Testing | fastmcp-testing.mdc | fastmcp-tools.mdc |

### GitHub Actions Categories

| Task Type | Primary Rule | Supporting Rules |
|-----------|--------------|------------------|
| Workflow Security | gh-action-security.mdc | debug-gh-actions.mdc |
| FastMCP Integration | fastmcp.mdc | fastmcp-tools.mdc |

### Code Explanation Categories

| Task Type | Primary Rule | Supporting Rules |
|-----------|--------------|------------------|
| Code Changes | explain-code-modification.mdc | anthropic-chain-of-thought.mdc |
| Documentation | python-documentation-standards.mdc | explain-code-modification.mdc |

## Query Optimization Techniques

To optimize queries for Claude:

1. **Be specific**: Transform vague requests into specific questions
2. **Include context**: Mention relevant technologies and frameworks
3. **Ask for structured responses**: Request step-by-step guidance or specific formats
4. **Mention desired depth**: Indicate whether you need basic concepts or advanced techniques
5. **Request examples**: Ask for code examples when appropriate

## Rule Recommendation Logic

The recommendation system uses these factors to suggest rules:

1. **Task type**: The specific development task being undertaken
2. **Technology stack**: The primary technologies mentioned in the query
3. **Development phase**: Whether the user is planning, implementing, or explaining code
4. **Complexity level**: Whether the task requires basic or advanced guidance
5. **Content recency**: Prioritizing recently updated rules (like those from March 25th)

## Example Recommendation Patterns

```
I notice you're working on [task type] with [technology].
Based on your query, I recommend:

1. [Primary Rule] - This is most relevant because [reason]
2. [Supporting Rule 1] - This helps with [specific aspect]
3. [Supporting Rule 2] - Consider this for [specific aspect]

For optimal results, try this optimized query:
"[Optimized query for Claude]"
