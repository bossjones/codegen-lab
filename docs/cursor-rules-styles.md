# Cursor Rules: Style Guide and Migration

This document outlines the two styles of cursor rules (v1 and v2) and provides guidance for migrating between them.

## V1 Style (Legacy Format)

The original cursor rule format uses XML-style tags and a more complex structure:

```mdc
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
```

### Characteristics

- Uses `<rule>` XML tags to wrap rule content
- Requires `name` and `description` fields inside `<rule>` tag
- Uses nested `filters` and `actions` structure
- Allows quoted glob patterns and brace expansions
- Files use `.mdc.md` extension
- No strict organization structure for rule files

## V2 Style (Current Format)

The new cursor rule format uses a cleaner, pure Markdown structure with standardized sections:

```mdc
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
```

### Characteristics

- Uses pure Markdown structure without XML tags
- Has standardized sections: Context, Critical Rules, Examples
- Requires both valid and invalid examples
- Uses unquoted glob patterns with proper spacing
- Files use `.mdc` extension only
- Follows specific naming pattern: `rule-name-{type}.mdc`
- Strict organizational folder structure under `.cursor/rules/`

## Rule Types

V2 introduces four distinct rule types, each with specific naming and frontmatter requirements:

1. **Agent Selected** (`-agent.mdc`)
   - AI decides when to apply based on description
   - Description field is critical
   - Blank globs
   - `alwaysApply: false`

2. **Always** (`-always.mdc`)
   - Applied to every chat and cmd-k request
   - Blank description
   - Blank globs
   - `alwaysApply: true`

3. **Auto Select** (`-auto.mdc`)
   - Applied to matching files based on glob pattern
   - Blank description
   - Critical glob pattern
   - `alwaysApply: false`

4. **Manual** (`-manual.mdc`)
   - User must explicitly reference in chat
   - Blank description
   - Blank globs
   - `alwaysApply: false`

## Directory Structure

V2 enforces a strict organizational structure under `.cursor/rules/`:

```
.cursor/rules/
├── core-rules/       # Rules for cursor agent behavior
├── my-rules/         # Private rules (gitignored)
├── global-rules/     # Always applied rules
├── testing-rules/    # Testing standards
├── tool-rules/       # Tool-specific rules
├── ts-rules/         # TypeScript-specific rules
├── py-rules/         # Python-specific rules
├── ui-rules/         # UI/UX related rules
└── workflows/        # Workflow implementation rules
```

## Migration Process

To migrate from v1 to v2 format:

1. **Move Files**
   - From: `hack/drafts/cursor_rules/*.mdc.md`
   - To: `.cursor/rules/{appropriate-subdirectory}/`

2. **Update File Names**
   - Remove `.md` extension
   - Add appropriate type suffix: `-{auto|agent|manual|always}.mdc`

3. **Fix Frontmatter**
   - Remove quotes from glob patterns
   - Add spaces after commas in glob lists
   - Set appropriate `alwaysApply` value based on rule type
   - Clear or set description based on rule type

4. **Convert Content**
   - Remove `<rule>` tags and nested structure
   - Add required sections: Context, Critical Rules, Examples
   - Include both valid and invalid examples
   - Keep content concise (under 50 lines preferred)

5. **Verify Migration**
   - Check file location and name
   - Validate frontmatter format
   - Ensure all required sections are present
   - Test rule functionality

## Best Practices

1. **Keep Rules Concise**
   - Target under 25 lines
   - Maximum 50 lines
   - Split large rules into smaller, focused rules

2. **Use Clear Examples**
   - Always include both valid and invalid examples
   - Make examples realistic and practical
   - Use proper code formatting

3. **Maintain Organization**
   - Place rules in appropriate subdirectories
   - Use descriptive filenames
   - Follow naming conventions strictly

4. **Update Documentation**
   - Document rule purpose in Context section
   - Keep Critical Rules clear and actionable
   - Update examples when rules change
