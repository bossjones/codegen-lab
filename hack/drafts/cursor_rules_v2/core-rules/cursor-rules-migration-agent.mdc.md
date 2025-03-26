---
description: Apply this rule when migrating or updating older cursor rule patterns to the new robust organizational format
globs:
alwaysApply: false
---
# Cursor Rules Migration Guide

## Context

- When migrating older cursor rules to the new organizational format
- When updating or refactoring existing cursor rules
- When consolidating cursor rules across projects

## Critical Rules

- Place all rules under appropriate organizational folders in `.cursor/rules/`:
  - core-rules: Agent behavior/rule generation
  - global-rules: Always applied rules
  - testing-rules: Testing standards
  - tool-rules: Tool-specific rules
  - language-specific: {lang}-rules (e.g. ts-rules, py-rules)
  - ui-rules: UI/UX related rules

- Rename files to follow pattern: `rule-name-{auto|agent|manual|always}.mdc`

- Convert frontmatter based on rule type:
  - Manual: blank description/globs, alwaysApply: false
  - Auto: blank description, valid globs, alwaysApply: false
  - Always: blank description/globs, alwaysApply: true
  - Agent: detailed description, blank globs, alwaysApply: false

- Remove quoted glob patterns: `"*.py"` → `*.py`
- Remove brace expansions: `{*.ts,*.js}` → `*.ts, *.js`
- Keep rule content concise (under 50 lines preferred)
- Include both valid and invalid examples
- Add clear context section explaining rule purpose
- Use 2-space indentation in example blocks

## Examples

<example>
# Old Format
---
description: TypeScript Standards
globs: "*.ts,*.tsx"
alwaysApply: false
---
<rule>
name: typescript_standards
description: TypeScript coding standards
filters:
  - type: file_extension
    pattern: "\\.tsx?$"
actions:
  - type: suggest
    message: "Follow TypeScript standards..."
</rule>

# New Format (.cursor/rules/ts-rules/typescript-standards-auto.mdc)
---
description:
globs: *.ts, *.tsx
alwaysApply: false
---
# TypeScript Standards

## Context
- Enforces TypeScript best practices
- Applies to all TypeScript/TSX files
- Ensures consistent code quality

## Critical Rules
- Use strict type checking
- Prefer interfaces over type aliases
- Enforce explicit return types

## Examples
<example>
// Valid TypeScript usage...
</example>

<example type="invalid">
// Invalid TypeScript usage...
</example>
</example>

<example type="invalid">
# Bad Format (Don't Do This)
---
description: "Quoted description"
globs: "{*.ts,*.tsx}"
alwaysApply: "false"
---
<rule>
  # Missing context section
  # No examples
  # Over-complicated structure
  filters:
    - many: complex
      nested: filters
    - that: are
      not: needed
</rule>
</example>
