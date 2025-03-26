---
description:
globs: .cursor/rules/**/*.mdc
alwaysApply: false
---

# MDC File Linting Rules

## Context

- Ensures all .mdc files follow the standard Cursor Rules format
- Validates structure, frontmatter, and content organization
- Helps maintain consistency across rule files
- Automatically checks files using relint
- Only applies to .mdc files within subdirectories of .cursor/rules/

## Critical Rules

- All .mdc files must be linted using the relint configuration below
- Place the relint config at `.relint.yml` in the project root
- Run relint on all .mdc files before committing changes
- Fix any errors or warnings before finalizing rule changes
- Only applies to files matching pattern `.cursor/rules/<dir>/*.mdc`

## Relint Configuration

<example>
```yaml
# .relint.yml - MDC File Validation Rules

- name: "Frontmatter Format"
  pattern: "^---\n(description:.*\nglobs:.*\nalwaysApply:.*\n)?---\n"
  hint: "MDC files must start with frontmatter containing description, globs, and alwaysApply fields"
  filePattern: "\\.cursor/rules/[^/]+/.*\\.mdc$"
  error: true

- name: "Rule Title Format"
  pattern: "^---.*?---\n\n# [A-Z].*?\n"
  hint: "MDC files must have a top-level title starting with #"
  filePattern: "\\.cursor/rules/[^/]+/.*\\.mdc$"
  error: true

- name: "Required Sections"
  pattern: "## Context.*?## Critical Rules.*?## Examples"
  hint: "MDC files must contain Context, Critical Rules, and Examples sections in order"
  filePattern: "\\.cursor/rules/[^/]+/.*\\.mdc$"
  error: true

- name: "Example Format"
  pattern: "<example>.*?</example>"
  hint: "MDC files must contain at least one example section"
  filePattern: "\\.cursor/rules/[^/]+/.*\\.mdc$"
  error: true

- name: "Invalid Example Format"
  pattern: "<example type=\"invalid\">.*?</example>"
  hint: "MDC files must contain at least one invalid example section"
  filePattern: "\\.cursor/rules/[^/]+/.*\\.mdc$"
  error: true

- name: "File Naming Convention"
  pattern: "^.*/(.*-(?:auto|agent|manual|always)\\.mdc)$"
  hint: "MDC files must end with -auto.mdc, -agent.mdc, -manual.mdc, or -always.mdc"
  filePattern: "\\.cursor/rules/[^/]+/.*\\.mdc$"
  error: true

- name: "Line Count Warning"
  pattern: "(?s).{2000,}"
  hint: "MDC files should ideally be under 50 lines, better under 25 lines"
  filePattern: "\\.cursor/rules/[^/]+/.*\\.mdc$"
  error: false
```
</example>

<example type="invalid">
```yaml
# Invalid .relint.yml configuration

- name: "Wrong Format"
  pattern: ".*"  # Too permissive
  hint: "Files must follow MDC format"
  filePattern: "*.mdc"  # Invalid glob pattern - should be \\.cursor/rules/[^/]+/.*\\.mdc$
  error: true

- name: "Missing Required Fields"
  pattern: "^---\n.*\n---\n"  # Doesn't check for required fields
  hint: "Files must have frontmatter"
  filePattern: "{*.mdc}"  # Invalid glob pattern with {} - should be \\.cursor/rules/[^/]+/.*\\.mdc$
  error: true
```
</example>
