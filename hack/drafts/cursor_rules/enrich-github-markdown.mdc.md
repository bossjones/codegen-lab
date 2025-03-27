---
description:
globs:
alwaysApply: false
---

# Update Markdown Nested Lists 📝

Automatically update README.md files with nested directory structures

> Use the @tree.mdc rule to get accurate directory structure before updating README files.

Automatically updates README.md files with nested directory structures and hyperlinks when new files or directories are added.

## Table of Contents

- [Update Markdown Nested Lists 📝](#update-markdown-nested-lists-)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
- [Match README.md files and markdown files in any subdirectory](#match-readmemd-files-and-markdown-files-in-any-subdirectory)
- [Match when new files or directories are added](#match-when-new-files-or-directories-are-added)
- [Match file creation events](#match-file-creation-events)
  - [GitHub Markdown Best Practices](#github-markdown-best-practices)
    - [Headers and Table of Contents](#headers-and-table-of-contents)
    - [Links and References](#links-and-references)
      - [Basic Links](#basic-links)
      - [Section Links](#section-links)
      - [Custom Anchors](#custom-anchors)
    - [Lists and Nested Lists](#lists-and-nested-lists)
      - [Basic Lists](#basic-lists)
      - [Nested Lists](#nested-lists)
      - [Task Lists](#task-lists)
    - [Images and Media](#images-and-media)
    - [Formatting and Styling](#formatting-and-styling)
      - [Text Styling](#text-styling)
      - [Code Formatting](#code-formatting)
      - [Line Breaks](#line-breaks)
    - [Special Elements](#special-elements)
      - [Alerts (Note Blocks)](#alerts-note-blocks)
      - [Blockquotes](#blockquotes)
      - [Footnotes](#footnotes)
      - [Emoji](#emoji)
      - [Hiding Content](#hiding-content)
      - [Escaping Markdown](#escaping-markdown)
  - [Glossary](#glossary)

## Overview

This rule helps maintain consistent and navigable documentation across the repository by automatically updating README.md files with nested directory structures and proper links when files are added or changed.

---

<rule>
name: update-markdown-nested-lists
description: Updates README.md files with nested directory structures and hyperlinks recursively
filters:
  # Match README.md files and markdown files in any subdirectory
  - type: file_name
    pattern: "(README\\.md$|.*\\.md$)"
  # Match when new files or directories are added
  - type: file_change
    pattern: ".*"
  # Match file creation events
  - type: event
    pattern: "file_create"

actions:
  - type: suggest
    message: |
      ## When updating README.md files:

      ### 1. First Action - Get Directory Structure:
      ```bash
      # Use @tree.mdc rule to get accurate directory structure
      tree -L 5 -I "*.pyc|__pycache__|.git|.pytest_cache|.ruff_cache|.mypy_cache|.coverage|htmlcov|.venv|.env|*.egg-info|build|dist|node_modules|.DS_Store|images"
      ```

      ### 2. Structure:
      ```markdown
      # Directory Name

      ## Contents

      <!-- Directory structure will be generated based on @tree.mdc output -->
      <!-- Each README.md file found will be linked appropriately -->
      <!-- Example structure:
      - [Current Directory](./README.md)
        - [Subdirectory 1](./subdirectory1/README.md)
          - [Nested Subdirectory](./subdirectory1/nested/README.md)
        - [Subdirectory 2](./subdirectory2/README.md)
      -->
      ```

      ### 3. Guidelines:

      #### General Rules:
      - ✅ Use @tree.mdc output to ensure accuracy
      - ✅ Only create links for directories that contain README.md or .md files
      - ✅ Use relative paths for links
      - ✅ Maintain hierarchical structure from tree output
      - ✅ Include all directories with README.md files
      - ✅ Preserve existing content above and below the directory listing
      - ✅ Update both parent and child README.md files
      - ✅ Recursively update all parent README.md files up to root
      - ✅ Verify tree output matches filesystem structure before updating

      > ⚠️ **Warning:** Always verify the tree structure before making updates to avoid broken links or missing directories.

      #### Directory Linking Rules:
      - **ALWAYS** link to the README.md file inside a directory, not just the directory itself
      - Format: `[directory-name/](./directory-name/README.md)` **NOT** `[directory-name/](./directory-name)`
      - Include the trailing slash in the display text: `refactoring/` not just `refactoring`

      **Examples of correct linking:**
      ```markdown
      - [`refactoring/`](./refactoring/README.md) - Code refactoring tools
      - [`testing/`](./testing/README.md) - Test automation tools
      - [`documentation/`](./documentation/README.md) - Documentation tools
      ```

      **Examples of incorrect linking:**
      ```markdown
      # ❌ DON'T do these:
      - [`refactoring`](./refactoring) - Missing trailing slash and README.md
      - [`testing/`](./testing) - Missing README.md in link
      - [`documentation`](./documentation/README.md) - Missing trailing slash
      ```

      #### Comparison of Linking Approaches

      | Style | Example | Status | Reason |
      |-------|---------|--------|--------|
      | Correct Format | [`refactoring/`](./refactoring/README.md) | ✅ Good | Has trailing slash and links to README.md |
      | Missing Slash | [`refactoring`](./refactoring/README.md) | ❌ Bad | Missing trailing slash in display text |
      | Missing README | [`refactoring/`](./refactoring/) | ❌ Bad | Doesn't link directly to README.md |
      | Wrong Both | [`refactoring`](./refactoring) | ❌ Bad | Missing slash and doesn't link to README.md |

      #### Special Cases:

      **For directories containing draft cursor rules (e.g., prompts/drafts/cursor_rules/):**
      - List all .mdc.md files in a nested list under the parent directory
      - Include a brief description from each file's frontmatter if available
      - Example structure:
        ```markdown
        - [Cursor Rules](./cursor_rules/)
          - [Update Markdown Lists](./cursor_rules/update-markdown-nested-lists.mdc.md) - Automatically update README.md files with nested directory structures
          - [Tree](./cursor_rules/tree.mdc.md) - Display repository structure
          - [Notify](./cursor_rules/notify.mdc.md) - Send notifications on task completion
        ```

      **For directories containing multiple related .md files:**
      - Group related files under their parent directory
      - Include all .md files in the nested list structure
      - Example:
        ```markdown
        - [Guidelines](./guidelines/)
          - [Model Specific](./guidelines/model_specific/)
            - [Anthropic Guidelines](./guidelines/model_specific/anthropic.md)
            - [OpenAI Guidelines](./guidelines/model_specific/openai.md)
        ```

      ### 4. Update Process:

      #### a. When a new .md file is added:

      **Update Checklist:**
      - [ ] Identify the directory where the file was added
      - [ ] Verify tree structure is current using `@tree.mdc`
      - [ ] Update immediate parent directory README.md
      - [ ] Update all parent READMEs recursively up to root
      - [ ] Verify all links are functioning
      - [ ] Send completion notification

      1. Identify the directory it was added to
      2. Update the immediate parent directory's README.md with:
         - For regular directories: standard nested list structure
         - For cursor_rules directories: detailed list with descriptions from frontmatter
         - Example for cursor_rules README.md:
           ```markdown
           # Cursor Rules

           ## Contents

           - [Adobe Cursor Tools](./adobe-cursor-tools.mdc.md) - Adobe-specific Cursor tools and commands
           - [Anthropic Chain of Thought](./anthropic-chain-of-thought.mdc.md) - Best practices for chain of thought reasoning
           - [Brain Memories](./brain-memories-lessons-learned-scratchpad.mdc.md) - Memory system for AI development
           ```
      3. Recursively update all parent README.md files up to root:
         - Each README.md in the chain should maintain its own context and perspective
         - Example chain for a new testing prompt:
           ```markdown
           # In prompts/domains/ide/testing/README.md:
           - [New Test](./new_test.md) - Description of the specific test

           # In prompts/domains/ide/README.md:
           - [Testing](./testing/README.md) - Testing assistance
             - [New Test](./testing/new_test.md) - Description in IDE context

           # In prompts/domains/README.md:
           - [IDE Development](./ide/README.md) - IDE functionality
             - [Testing](./ide/testing/README.md) - Testing tools
               - [New Test](./ide/testing/new_test.md) - High-level description

           # In prompts/README.md:
           - [Domains](./domains/README.md) - Domain-specific prompts
             - [IDE](./domains/ide/README.md) - IDE tools
               - [Testing](./domains/ide/testing/README.md) - Testing
           ```
         - Each level should provide appropriate context and detail for its scope
         - Maintain consistent formatting and style across all levels
         - Include relevant section headers (e.g., "Contents", "Related Resources")
         - Cross-reference related sections when appropriate

         > 💡 **Tip:** Maintain a consistent depth of nesting at each level. Root README.md might show only 1-2 levels, while deeper READMEs can show more detailed structure.

         - Special handling for cursor rules across levels:
           ```markdown
           # In prompts/drafts/cursor_rules/README.md:
           - [New Rule](./new-rule.mdc.md) - Detailed technical description of the rule's functionality

           # In prompts/drafts/README.md:
           - [Cursor Rules](./cursor_rules/) - Cursor rule drafts and templates
             - [New Rule](./cursor_rules/new-rule.mdc.md) - Rule description with usage context

           # In prompts/README.md:
           - [Drafts](./drafts/README.md) - Work in progress prompts
             - [Cursor Rules](./drafts/cursor_rules/) - Cursor rule drafts
               - [New Rule](./drafts/cursor_rules/new-rule.mdc.md) - High-level purpose

           # In root README.md:
           - [Prompts](./prompts/README.md) - Core prompt library
             - [Drafts](./prompts/drafts/README.md) - Work in progress
               - [Cursor Rules](./prompts/drafts/cursor_rules/) - Rule drafts
           ```

      #### b. For each README.md update:

      **README Update Procedure:**
      - [x] Run @tree.mdc to get current structure
      - [ ] Parse tree output to identify directories
      - [ ] Check each directory for README.md and markdown files
      - [ ] Generate nested markdown list with valid links
      - [ ] Update the README.md while preserving other content
      - [ ] Continue up the directory tree until reaching root

      1. Run @tree.mdc to get current structure
      2. Parse tree output to identify directories
      3. Check each directory for README.md and markdown files
      4. Generate nested markdown list with valid links
      5. Update the README.md while preserving other content
      6. Continue up the directory tree until reaching root

      #### c. Send notification on completion

      > 🔔 **Note:** Remember to send a notification when the update is complete using the @notify.mdc rule.

      ---

## GitHub Markdown Best Practices

The following best practices are based on GitHub's official Markdown syntax documentation. Incorporating these practices will ensure consistent, readable, and accessible documentation across your repository.

### Headers and Table of Contents

- Use `#` for headers (1-6 levels): `# H1`, `## H2`, `### H3`, etc.
- GitHub automatically generates a table of contents from your headers
- Access the TOC by clicking the menu icon in the file header
- Keep headers concise and descriptive for better TOC navigation
- Use sentence case for headers (capitalize first word only)

> [!TIP]
> When using two or more headings, GitHub automatically generates a table of contents that users can access by clicking within the file header.

### Links and References

#### Basic Links
- Create inline links with `[link text](URL)`
- Use relative links for repository files: `[Contribution guidelines](docs/CONTRIBUTING.md)`
- Relative links are preferred as they work in repository clones

#### Section Links
- Link to specific sections with `[link text](#section-name)`
- Section anchors follow these rules:
  - Convert to lowercase
  - Replace spaces with hyphens
  - Remove punctuation and special characters
  - Example: `## This'll be a _Helpful_ Section!` becomes `#thisll-be-a-helpful-section`

#### Custom Anchors
- Create custom anchors with `<a name="anchor-name"></a>`
- Link to them with `[link text](#anchor-name)`
- Use unique names for custom anchors to avoid conflicts

> [!IMPORTANT]
> Custom anchors are not included in the document's table of contents.

### Lists and Nested Lists

#### Basic Lists
- Create unordered lists with `-`, `*`, or `+`
- Create ordered lists with numbers: `1.`, `2.`, etc.
- GitHub renders the correct numbers regardless of the actual numbers used

#### Nested Lists
- Indent nested items with spaces until the list marker aligns below the first character of the parent item
- In monospaced editors (like VS Code), align visually
- For nested items under numbered lists, count characters of the parent item including the number and period
- Example proper alignment:
  ```markdown
  1. First list item
     - First nested list item
       - Second nested list item
  ```

#### Task Lists
- Create task lists with `- [ ]` for incomplete items
- Use `- [x]` for completed items
- Example:
  ```markdown
  - [x] Complete task
  - [ ] Incomplete task
  ```

### Images and Media

- Insert images with `![Alt text](image-url)`
- Use relative paths for repository images
- Recommended relative paths for images:
  | Context | Relative Link |
  | --- | --- |
  | In `.md` file (same branch) | `/assets/images/logo.png` |
  | In `.md` file (other branch) | `/../main/assets/images/logo.png` |
  | In issues/PRs | `../blob/main/assets/images/logo.png?raw=true` |

### Formatting and Styling

#### Text Styling
- **Bold**: `**text**` or `__text__`
- *Italic*: `*text*` or `_text_`
- ~~Strikethrough~~: `~~text~~`
- **Bold and _nested italic_**: `**text and _nested text_**`
- ***All bold and italic***: `***text***`
- <sub>Subscript</sub>: `<sub>text</sub>`
- <sup>Superscript</sup>: `<sup>text</sup>`

#### Code Formatting
- Inline code: `` `code` ``
- Code blocks:
  ````markdown
  ```language
  code block
  ```
  ````
- Syntax highlighting by specifying language after backticks

#### Line Breaks
- For line breaks in `.md` files:
  - Add two spaces at the end of a line, OR
  - Use a backslash `\` at the end of a line, OR
  - Use an HTML break tag `<br/>`
- Blank lines create new paragraphs

### Special Elements

#### Alerts (Note Blocks)
```markdown
> [!NOTE]
> Important information that users should know.

> [!TIP]
> Helpful advice for doing things better.

> [!IMPORTANT]
> Essential information users need.

> [!WARNING]
> Urgent info needing immediate attention.

> [!CAUTION]
> Advises about risks or negative outcomes.
```

#### Blockquotes
```markdown
> This is a regular blockquote.
> It continues on this line.
```

#### Footnotes
```markdown
Here is text with a footnote[^1].

[^1]: This is the footnote content.
```

#### Emoji
- Add emoji with `:EMOJICODE:` (e.g., `:+1:` for 👍)
- Type `:` to trigger emoji autocomplete

#### Hiding Content
- Hide content using HTML comments: `<!-- Hidden content -->`

#### Escaping Markdown
- Escape Markdown characters with backslash: `\*not italic\*`

examples:
  - input: |
      # Bad: Flat structure without links or tree verification
      * Directory1
      * Directory2
      * Subdirectory1

      # Bad: Links without verifying existence
      - [NonexistentDir](./nonexistent/README.md)
      - [BrokenLink](./broken/link.md)

      # Good: Tree-verified structure with links
      # First run @tree.mdc:
      $ tree -L 2
      .
      ├── Directory1
      │   └── README.md
      └── Directory2
          └── README.md

      - [Directory1](./Directory1/README.md)
      - [Directory2](./Directory2/README.md)
    output: "Basic structure with tree verification"

  - input: |
      # New file added: prompts/domains/ide/testing/test-example.md
      # Update chain using @tree.mdc:

      1. Update prompts/domains/ide/README.md:
      ```markdown
      # IDE Domain

      ## Contents

      - [Testing](./testing/README.md)
        - [Test Example](./testing/test-example.md)
      ```

      2. Update prompts/domains/README.md:
      ```markdown
      # Domains

      ## Contents

      - [IDE](./ide/README.md)
        - [Testing](./ide/testing/README.md)
      ```

      3. Update prompts/README.md:
      ```markdown
      # Prompts

      ## Contents

      - [Domains](./domains/README.md)
        - [IDE](./domains/ide/README.md)
      ```
    output: "Recursive README updates after new file addition"

  - input: |
      # Project Title

      Project description here.

      ## Directory Structure

      <!-- Generated from @tree.mdc -->
      - [Source](./src/README.md)
        - [Components](./src/components/README.md)
          - [UI](./src/components/ui/README.md)
        - [Utils](./src/utils/README.md)
      - [Tests](./tests/README.md)
        - [Unit Tests](./tests/unit/README.md)

      ## Additional Information

      More content here.
    output: "Complete README with nested directory structure"

  - input: |
      # New cursor rule added: prompts/drafts/cursor_rules/new-rule.mdc.md
      # Update chain for cursor rules:

      1. Update prompts/drafts/README.md:
      ```markdown
      # Drafts

      ## Contents

      - [Cursor Rules](./cursor_rules/)
        - [Adobe Cursor Tools](./cursor_rules/adobe-cursor-tools.mdc.md) - Adobe-specific Cursor tools and commands
        - [Anthropic Chain of Thought](./cursor_rules/anthropic-chain-of-thought.mdc.md) - Best practices for chain of thought reasoning
        - [Brain Memories](./cursor_rules/brain-memories-lessons-learned-scratchpad.mdc.md) - Memory system for AI development
        - [Cursor Rules Location](./cursor_rules/cursor_rules_location.mdc.md) - Cursor rules file organization
        - [Documentation Standards](./cursor_rules/documentations-inline-comments-changelog-docs.mdc.md) - Documentation guidelines
        - [Git Commits](./cursor_rules/git_conventional_commits.mdc.md) - Conventional commit message standards
        - [New Rule](./cursor_rules/new-rule.mdc.md) - Description from frontmatter
      ```

      2. Update prompts/README.md to reflect the new draft rule
    output: "Special handling for cursor rule drafts directory"

metadata:
  priority: high
  version: 1.0
  tags:
    - documentation
    - markdown
    - directory-structure
    - auto-update
    - recursive-update
    - tree-integration
</rule>

## Glossary

| Term | Description |
|------|-------------|
| **README.md** | The standard documentation file in each directory that describes its contents |
| **@tree.mdc** | A cursor rule that displays the repository structure using the tree command |
| **@notify.mdc** | A cursor rule that sends notifications on task completion |
| **.mdc.md** | Extension for cursor rule files with markdown content |
| **Frontmatter** | YAML metadata at the beginning of markdown files, contained between --- markers |
| **Nested List** | A hierarchical list structure with indented sublists representing directory hierarchy |
| **Relative Path** | A file path that is relative to the current document location, usually starting with ./ |
| **Alert** | Special blockquote with predefined types (NOTE, TIP, IMPORTANT, WARNING, CAUTION) |
| **Anchor** | A target for in-page navigation links |
| **Task List** | Checkbox list created with `- [ ]` (unchecked) and `- [x]` (checked) syntax |
