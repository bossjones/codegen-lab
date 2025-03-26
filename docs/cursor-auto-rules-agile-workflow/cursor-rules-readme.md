# Cursor Rules System Documentation

## Overview

The Cursor Rules system is a powerful mechanism that enables consistent AI behavior by providing structured instructions for AI assistants. Rules serve as a form of memory and guidance, ensuring that AI follows specific patterns and practices throughout a project.

## What Are Cursor Rules?

Cursor rules are specialized Markdown files with the `.mdc` extension that contain structured instructions for AI assistants. They include:

1. **Frontmatter** - YAML configuration at the top of the file that determines how and when the rule is applied
2. **Contextual information** - Explains when and why to apply the rule
3. **Critical rules** - Specific instructions the AI must follow
4. **Examples** - Valid and invalid implementations to guide the AI

## Rule Types

The system supports four distinct rule types, each with specific use cases:

| Rule Type        | Usage                                            | Description Field | Globs Field           | AlwaysApply Field | Filename Pattern    |
| ---------------- | ------------------------------------------------ | ----------------- | --------------------- | ----------------- | ------------------- |
| Agent Selected   | Agent sees description and chooses when to apply | Critical          | Blank                 | False             | *-agent.mdc         |
| Always           | Applied to every chat and cmd-k request          | Blank             | Blank                 | True              | *-always.mdc        |
| Auto Select      | Applied to matching existing files               | Blank             | Critical glob pattern | False             | *-auto.mdc          |
| Manual           | User must reference in chat                      | Blank             | Blank                 | False             | *-manual.mdc        |

### Agent Selected Rules

- Used when the AI should decide when to apply the rule based on context
- The description field must clearly indicate when the rule should be applied
- Example: A rule for generating TypeScript interfaces that the AI applies when it detects interface creation

### Always Rules

- Applied to every conversation, regardless of context
- Used for fundamental behaviors that should be consistent across all interactions
- Example: A rule for maintaining a specific communication style or error handling approach

### Auto Select Rules

- Automatically applied when working with files matching the specified glob pattern
- Perfect for language-specific conventions or file type standards
- Example: A rule that enforces TypeScript best practices when editing .ts files

### Manual Rules

- Only applied when explicitly referenced by the user with the @ symbol
- Useful for specific workflows or processes that are only needed occasionally
- Example: A rule for generating documentation that's invoked with "@documentation-generator"

## Folder Structure

Rules are organized in subdirectories under `.cursor/rules/` based on their purpose:

```
.cursor/rules/
├── core-rules/       # Rules for cursor agent behavior or rule generation
├── my-rules/         # Private rules (gitignored in shared repos)
├── global-rules/     # Rules that apply to every interaction
├── testing-rules/    # Rules for testing standards
├── tool-rules/       # Rules for specific tools (git, Linux commands)
├── ts-rules/         # TypeScript-specific rules
├── py-rules/         # Python-specific rules
├── ui-rules/         # Rules for HTML, CSS, React
└── workflows/        # Workflow implementation rules
```

This organization makes it easy to:
- Find rules related to specific domains
- Separate shared rules from private ones
- Manage rules for different programming languages

## Rule Generation

The system includes an automated rule generation capability that allows:

1. Creating new rules through natural language requests
2. Updating existing rules as needs evolve
3. Ensuring consistent rule formatting and organization

Rules can be generated directly through conversation with the AI. The process is managed by the rule-generating-agent rule, which:

- Determines the appropriate rule type based on the request
- Creates or updates the rule file with proper frontmatter
- Places the rule in the correct subfolder
- Provides a summary of the action taken

### Example Requests

To generate a rule, simply describe the desired behavior:

- "Create a typescript file commenting standard that balances thoroughness with brevity"
- "Never create JS files again, you will only create TS or JSON files!"
- "Ensure proper error handling in all TypeScript files"

## Rule Structure

Each rule file follows a consistent structure:

```
---
description: Concise description or blank
globs: Pattern to match files or blank
alwaysApply: true or false
---

# Rule Title

## Context

- When to apply this rule
- Prerequisites or conditions
- Why the rule exists

## Critical Rules

- Specific instructions for the AI
- Clear, actionable guidance
- Implementation requirements

## Examples

<example>
Valid rule application example
</example>

<example type="invalid">
Invalid rule application example
</example>
```

## Best Practices

1. **Keep rules concise** - Target under 25 lines, maximum 50 lines
2. **Include both valid and invalid examples** - Helps the AI understand boundaries
3. **Use specific descriptions** - Especially important for agent-selected rules
4. **Organize logically** - Place rules in the appropriate subfolder
5. **Use descriptive filenames** - Names should indicate purpose and rule type
6. **Avoid redundancy** - Don't repeat information across rules
7. **Update as needed** - Rules should evolve with your project
8. **Use glob patterns effectively** - Be specific about which files a rule applies to

## Private vs. Shared Rules

For team projects, consider:

- Placing team-wide rules in shared folders
- Using `.cursor/rules/my-rules/` for personal preferences
- Adding personal rule folders to `.gitignore`

## Rule Removal

As projects mature:

- Some rules become unnecessary as code conventions solidify
- The AI will naturally follow patterns in the codebase
- Remove redundant rules to reduce complexity
- Focus on rules that provide unique value
