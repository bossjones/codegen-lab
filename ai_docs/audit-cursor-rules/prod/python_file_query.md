# Query Analysis: "Update my Python script with async functionality"

## Activated Rules

| Rule                           | Type             | Token Count | Impact     | Activation Reason                      |
| ------------------------------ | ---------------- | ----------- | ---------- | -------------------------------------- |
| emoji-communication-always.mdc | Always           | 262         | Low        | Always applied                         |
| repomix.mdc                    | Auto Select+desc | 4,659       | High       | "*" glob matches Python files          |
| repo_analyzer.mdc              | Auto Select+desc | 3,774       | High       | "*" glob matches Python files          |
| uv.mdc                         | Auto Select+desc | 1,212       | Medium     | "*.py" glob pattern                    |
| tdd.mdc                        | Auto Select+desc | 1,412       | Medium     | "**/*.py" glob pattern                 |
| tree.mdc                       | Auto Select+desc | 99          | Low        | "*" glob matches Python files          |
| suggest-cursor-rule.mdc        | Auto Select+desc | 2,442       | High       | "**/*" glob matches Python files       |
| project_layout.mdc             | Auto Select+desc | 1,716       | Medium     | "**/*.py" glob pattern                 |
| **TOTAL**                      |                  | **15,576**  | **Very High** |                                     |

## Mermaid Diagram

```mermaid
flowchart TD
    Query["User Query: Update my Python script with async functionality"] --> Analysis["Rule Analysis"]

    Analysis --> RuleTypes["Rule Type Categorization"]

    RuleTypes --> Always["Always Rules"]
    RuleTypes --> AutoSelect["Auto Select Rules"]
    RuleTypes --> AutoSelectDesc["Auto Select+desc Rules"]
    RuleTypes --> AgentSelected["Agent Selected Rules"]
    RuleTypes --> Manual["Manual Rules"]

    Always --> emoji["emoji-communication-always.mdc
    (262 tokens)"]

    AutoSelectDesc --> WildcardGlob["Rules with '*' glob"]
    AutoSelectDesc --> PythonGlob["Rules with Python globs"]

    WildcardGlob --> repomix["repomix.mdc
    (4,659 tokens)"]
    WildcardGlob --> repo_analyzer["repo_analyzer.mdc
    (3,774 tokens)"]
    WildcardGlob --> tree["tree.mdc
    (99 tokens)"]

    PythonGlob --> uv["uv.mdc
    (1,212 tokens)"]
    PythonGlob --> tdd["tdd.mdc
    (1,412 tokens)"]
    PythonGlob --> project_layout["project_layout.mdc
    (1,716 tokens)"]

    WildcardGlob & PythonGlob --> suggest_cursor_rule["suggest-cursor-rule.mdc
    (2,442 tokens)"]

    %% Add context load summary subgraph
    subgraph ContextLoad["Total Context Load (15,576 tokens)"]
        AllActiveRules["All Active Rules"] --> ActiveAlways["Always Rules (262 tokens)
        - emoji-communication-always.mdc (262)"]

        AllActiveRules --> ActiveAutoDesc["Auto Select+desc Rules (15,314 tokens)
        - repomix.mdc (4,659)
        - repo_analyzer.mdc (3,774)
        - uv.mdc (1,212)
        - tdd.mdc (1,412)
        - tree.mdc (99)
        - suggest-cursor-rule.mdc (2,442)
        - project_layout.mdc (1,716)"]
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
    class emoji,repomix,repo_analyzer,uv,tdd,tree,suggest_cursor_rule,project_layout activated
```

## Token Impact Analysis

The current rule configuration adds 15,576 tokens to the LLM context for a Python file modification query. This is an extremely high token count that significantly impacts:

1. Response quality - the large context may dilute the LLM's focus on the actual task
2. Token usage costs - adds unnecessary tokens to every interaction
3. Response speed - processing larger contexts takes more time

The Auto Select+desc rules account for 98.3% of the total token usage, with just three rules (repomix.mdc, repo_analyzer.mdc, and suggest-cursor-rule.mdc) contributing 10,875 tokens (69.8% of the total).

## Recommendations

1. Convert high-impact rules to manual invocation:
   - repomix.mdc (4,659 tokens) → @repomix
   - repo_analyzer.mdc (3,774 tokens) → @repo-analyzer
   - suggest-cursor-rule.mdc (2,442 tokens) → @suggest-cursor-rule

2. Consider more specific glob patterns:
   - Multiple rules use wildcard globs ("*" or "**/*") which activate on almost any file
   - For the Python-specific use case, tree.mdc could use a more specific glob

3. Consolidate similar functionality:
   - uv.mdc and project_layout.mdc have some overlapping Python project concepts

4. Keep low-impact rules as automatic:
   - emoji-communication-always.mdc (262 tokens) is reasonable for an Always rule
   - tree.mdc (99 tokens) is low impact and can remain automatic

These changes could reduce the automatic context load by approximately 10,875 tokens (69.8%) for Python file operations.
