# Query Analysis: "Update my README.md with installation instructions"

## Activated Rules

| Rule                           | Type             | Token Count | Impact     | Activation Reason                      |
| ------------------------------ | ---------------- | ----------- | ---------- | -------------------------------------- |
| emoji-communication-always.mdc | Always           | 262         | Low        | Always applied                         |
| repomix.mdc                    | Auto Select+desc | 4,659       | High       | "*" glob matches Markdown files        |
| repo_analyzer.mdc              | Auto Select+desc | 3,774       | High       | "*" glob matches Markdown files        |
| tree.mdc                       | Auto Select+desc | 99          | Low        | "*" glob matches Markdown files        |
| suggest-cursor-rule.mdc        | Auto Select+desc | 2,442       | High       | "**/*" glob matches Markdown files     |
| project_layout.mdc             | Auto Select+desc | 1,716       | Medium     | "**/*.md" glob pattern                 |
| documentation/markdown-auto.mdc| Auto Select+desc | 303         | Low        | "**/*.md" glob pattern                 |
| **TOTAL**                      |                  | **13,255**  | **Very High** |                                     |

## Mermaid Diagram

```mermaid
flowchart TD
    Query["User Query: Update my README.md with installation instructions"] --> Analysis["Rule Analysis"]

    Analysis --> RuleTypes["Rule Type Categorization"]

    RuleTypes --> Always["Always Rules"]
    RuleTypes --> AutoSelect["Auto Select Rules"]
    RuleTypes --> AutoSelectDesc["Auto Select+desc Rules"]
    RuleTypes --> AgentSelected["Agent Selected Rules"]
    RuleTypes --> Manual["Manual Rules"]

    Always --> emoji["emoji-communication-always.mdc
    (262 tokens)"]

    AutoSelectDesc --> WildcardGlob["Rules with '*' glob"]
    AutoSelectDesc --> MarkdownGlob["Rules with Markdown globs"]

    WildcardGlob --> repomix["repomix.mdc
    (4,659 tokens)"]
    WildcardGlob --> repo_analyzer["repo_analyzer.mdc
    (3,774 tokens)"]
    WildcardGlob --> tree["tree.mdc
    (99 tokens)"]

    MarkdownGlob --> project_layout["project_layout.mdc
    (1,716 tokens)"]
    MarkdownGlob --> markdown_auto["documentation/markdown-auto.mdc
    (303 tokens)"]

    WildcardGlob & MarkdownGlob --> suggest_cursor_rule["suggest-cursor-rule.mdc
    (2,442 tokens)"]

    %% Add context load summary subgraph
    subgraph ContextLoad["Total Context Load (13,255 tokens)"]
        AllActiveRules["All Active Rules"] --> ActiveAlways["Always Rules (262 tokens)
        - emoji-communication-always.mdc (262)"]

        AllActiveRules --> ActiveAutoDesc["Auto Select+desc Rules (12,993 tokens)
        - repomix.mdc (4,659)
        - repo_analyzer.mdc (3,774)
        - tree.mdc (99)
        - suggest-cursor-rule.mdc (2,442)
        - project_layout.mdc (1,716)
        - markdown-auto.mdc (303)"]
    end

    style Query fill:#f9f,stroke:#333,stroke-width:2px
    style Always fill:#f0f,stroke:#333,stroke-width:1px
    style AutoSelect fill:#0d0,stroke:#333,stroke-width:1px
    style AutoSelectDesc fill:#00f,stroke:#333,stroke-width:1px
    style AgentSelected fill:#0dd,stroke:#333,stroke-width:1px
    style Manual fill:#ff0,stroke:#333,stroke-width:1px
    style ContextLoad fill:#ffd,stroke:#f00,stroke-width:3px
    style AllActiveRules fill:#faa,stroke:#333,stroke-width:2px
    style ActiveAlways,ActiveAutoDesc fill:#afa,stroke:#333,stroke-width:1px

    %% Highlight rules for potential conversion to manual
    style repomix stroke:#f00,stroke-width:2px,stroke-dasharray: 5 5
    style repo_analyzer stroke:#f00,stroke-width:2px,stroke-dasharray: 5 5
    style suggest_cursor_rule stroke:#f00,stroke-width:2px,stroke-dasharray: 5 5

    classDef activated fill:#afa,stroke:#333,stroke-width:2px
    class emoji,repomix,repo_analyzer,tree,suggest_cursor_rule,project_layout,markdown_auto activated
```

## Token Impact Analysis

The current rule configuration adds 13,255 tokens to the LLM context for a Markdown file update query. This is a very high token count that significantly impacts:

1. Response quality - excessive context can dilute the LLM's focus on the actual task
2. Token usage costs - adds unnecessary tokens to every interaction involving Markdown files
3. Response speed - processing larger contexts takes more time

The Auto Select+desc rules account for 98% of the total token usage, with just three rules (repomix.mdc, repo_analyzer.mdc, and suggest-cursor-rule.mdc) contributing 10,875 tokens (82% of the total).

A notable observation is that markdown-auto.mdc, which is specifically designed for Markdown files, only contributes 303 tokens (2.3% of the total), while generic rules with wildcard globs contribute the vast majority of tokens.

## Recommendations

1. Convert high-impact rules to manual invocation:
   - repomix.mdc (4,659 tokens) → @repomix
   - repo_analyzer.mdc (3,774 tokens) → @repo-analyzer
   - suggest-cursor-rule.mdc (2,442 tokens) → @suggest-cursor-rule

2. Consider more specific glob patterns:
   - Multiple rules use wildcard globs ("*" or "**/*") which activate on almost any file
   - For Markdown files, tree.mdc could use a more specific glob if repository structure is needed

3. Keep low-impact rules as automatic:
   - emoji-communication-always.mdc (262 tokens) is reasonable for an Always rule
   - markdown-auto.mdc (303 tokens) is the most relevant rule for Markdown files and is low impact
   - tree.mdc (99 tokens) is low impact and can remain automatic

4. Consider restructuring project_layout.mdc:
   - At 1,716 tokens, it's a significant contributor to context bloat
   - Consider splitting into smaller, more focused rules or making it manual invocation

These changes could reduce the automatic context load by approximately 10,875 tokens (82%) for Markdown file operations, while keeping the most relevant rules (markdown-auto.mdc) active by default.
