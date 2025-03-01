# Cursor Rules for Iterative Development

## Overview

This document describes the collection of Cursor rules implemented for Harper Reed's iterative development workflow. These rules help automate and guide developers through the process of working with existing codebases in a structured, incremental manner.

## What are Cursor Rules?

Cursor rules are custom instructions for Cursor's AI assistant that help automate repetitive tasks, enforce best practices, and guide you through complex workflows. They're defined in `.mdc.md` files and are triggered based on specific patterns in your messages or the files you're working with.

## Rule Collection for Iterative Development

This collection implements Harper Reed's non-greenfield iteration workflow as described in [their blog post](https://harper.blog/2025/02/16/my-llm-codegen-workflow-atm/). The workflow is specifically designed for working with existing codebases rather than greenfield (new) projects.

### Workflow Philosophy

Harper's non-greenfield iteration workflow involves:

1. **Getting context** from the existing codebase
2. **Planning per task** rather than for the entire project
3. **Implementing incrementally** with constant testing and feedback
4. **Debugging and fixing issues** as they arise

### Rules in this Collection

This collection contains the following cursor rules:

1. **Incremental Task Planner** - Breaks down a development task into smaller, manageable steps for incremental implementation
2. **Code Context Gatherer** - Efficiently gathers code context from the codebase for LLM consumption
3. **Test Generator** - Identifies missing tests and generates appropriate test cases for the codebase
4. **Iterative Debug and Fix** - Provides guidance for debugging and fixing issues that arise during iterative development
5. **Iterative Development Workflow** - Master rule that provides a structured workflow for incremental development in existing codebases

## Detailed Rule Descriptions

### 1. Incremental Task Planner

**Purpose**: Help break down a development task into smaller, manageable steps for incremental implementation.

**When to use**: When you need to plan the implementation of a new feature or bug fix in an existing codebase.

**Activation phrases**:
- "Plan this feature"
- "Break down this task"
- "Help me implement this incrementally"
- "Steps for adding [feature]"

**What it does**:
- Analyzes the task requirements
- Identifies relevant parts of the codebase
- Breaks the task into small, logical steps
- Creates a todo checklist
- Plans for testing
- Provides implementation guidance

### 2. Code Context Gatherer

**Purpose**: Efficiently gather code context from the codebase for LLM consumption.

**When to use**: When you need to understand how a specific part of the codebase works.

**Activation phrases**:
- "Help me understand this code"
- "Gather context for [feature/component]"
- "How does [system/feature] work?"
- "Explain the existing code"

**What it does**:
- Identifies relevant components and files
- Efficiently collects context from key files
- Organizes the context in a logical structure
- Summarizes architecture and key patterns
- Highlights potential areas for modification

### 3. Test Generator

**Purpose**: Identify missing tests and generate appropriate test cases for the codebase.

**When to use**: When you need to improve test coverage for an existing component.

**Activation phrases**:
- "Generate tests for [component]"
- "We need tests for [feature]"
- "Add missing test coverage"
- "Write tests for this code"

**What it does**:
- Analyzes the code for testable components
- Determines appropriate test types (unit, integration, etc.)
- Follows the project's testing patterns
- Generates comprehensive test cases
- Includes edge cases and error conditions
- Implements tests with proper typing and documentation

### 4. Iterative Debug and Fix

**Purpose**: Provide guidance for debugging and fixing issues that arise during iterative development.

**When to use**: When you encounter a bug or an issue in your implementation.

**Activation phrases**:
- "Debug this issue"
- "Fix this error"
- "This isn't working correctly"
- "Help me troubleshoot [problem]"

**What it does**:
- Helps gather comprehensive error information
- Guides you through reproducing and isolating the issue
- Provides a systematic approach to debugging
- Assists in testing hypotheses about the root cause
- Helps design and implement targeted fixes
- Guides verification and regression testing
- Suggests preventative measures for the future

### 5. Iterative Development Workflow

**Purpose**: Provide a structured workflow for incremental development in existing codebases.

**When to use**: When you want guidance on the overall process of implementing a feature or fix.

**Activation phrases**:
- "Help me develop this feature"
- "Guide me through implementing [feature]"
- "What's the workflow for adding [feature]"
- "Non-greenfield development process"

**What it does**:
- Guides you through the three phases of iterative development:
  1. Understand and Plan
  2. Implement Incrementally
  3. Refine and Complete
- Provides structured steps for each phase
- Helps maintain focus on incremental progress
- Ensures quality through testing and refactoring

## How to Use These Rules

### Installation

To use these rules in your project:

1. Ensure you have a `.cursor/rules/` directory in your project root:
   ```bash
   mkdir -p .cursor/rules
   ```

2. Copy the rule files from the source location:
   ```bash
   cp hack/drafts/cursor_rules/*.mdc.md .cursor/rules/
   ```

### Usage Flow

Here's how you might use these rules in a typical development session:

1. **Start with the workflow**: "Help me implement a feature using the iterative development workflow"
2. **Gather context**: "Help me understand the current authentication system"
3. **Plan your task**: "Break down the task of adding two-factor authentication"
4. **Implement incrementally**: "Help me implement the first step of the 2FA feature"
5. **Add tests**: "Generate tests for the 2FA authentication code"
6. **Debug issues**: "The 2FA verification isn't working, help me debug it"

### Example Conversations

#### Example 1: Planning a New Feature

**You**: "I need to add a new payment method to our existing e-commerce system."

**Cursor Assistant**: *[Using Incremental Task Planner rule]* "I'll help you break that down into manageable steps..."

#### Example 2: Understanding Existing Code

**You**: "I need to understand how our user authentication system works."

**Cursor Assistant**: *[Using Code Context Gatherer rule]* "Let me gather the relevant code and explain how it works..."

#### Example 3: Adding Tests

**You**: "We need to add tests for our newly implemented payment service."

**Cursor Assistant**: *[Using Test Generator rule]* "I'll help you generate comprehensive tests for the payment service..."

#### Example 4: Fixing an Issue

**You**: "The payment processing is failing when users have special characters in their names."

**Cursor Assistant**: *[Using Iterative Debug and Fix rule]* "Let's debug this issue systematically..."

## Customizing the Rules

You can customize these rules by editing the `.mdc.md` files in your `.cursor/rules/` directory:

1. Modify the filters to match your specific project patterns
2. Adjust the instructions to align with your team's practices
3. Add or modify examples to better match your codebase

## Credits

These rules are based on Harper Reed's blog post ["My LLM codegen workflow atm"](https://harper.blog/2025/02/16/my-llm-codegen-workflow-atm/) which describes an effective iterative development workflow using LLMs.
