# Query Analysis: "Update my message_handler.py file"

## Activated Rules

| Rule                           | Type             | Token Count | Impact     | Activation Reason |
| ----------------------------- | ---------------- | ----------- | ---------- | ---------------- |
| python_rules.mdc.md           | Auto Select+desc | 5,126       | Very High  | *.py glob match |
| discord.mdc.md                | Auto Select+desc | 6,443       | Very High  | *.py glob match |
| discord-py-cogs.mdc.md        | Auto Select+desc | 8,383       | Very High  | *.py glob match |
| discord-py-commands.mdc.md    | Auto Select+desc | 3,235       | High       | *.py glob match |
| ruff.mdc.md                   | Auto Select+desc | 3,026       | High       | *.py glob match |
| basedpyright.mdc.md          | Auto Select+desc | 3,960       | High       | *.py glob match |
| **TOTAL**                     |                  | **30,173**  | **Critical** | |

## Mermaid Diagram

```mermaid
flowchart TD
    Query["User Query: Update message_handler.py"] --> Analysis["Rule Analysis"]

    Analysis --> RuleTypes["Rule Type Categorization"]

    RuleTypes --> AutoSelectDesc["Auto Select+desc Rules"]

    AutoSelectDesc --> PythonRules["python_rules.mdc.md
    (5,126 tokens)"]

    AutoSelectDesc --> DiscordRules["discord.mdc.md
    (6,443 tokens)"]

    AutoSelectDesc --> DiscordCogs["discord-py-cogs.mdc.md
    (8,383 tokens)"]

    AutoSelectDesc --> DiscordCommands["discord-py-commands.mdc.md
    (3,235 tokens)"]

    AutoSelectDesc --> LinterRules["ruff.mdc.md
    (3,026 tokens)
    basedpyright.mdc.md
    (3,960 tokens)"]

    %% Add context load summary subgraph
    subgraph ContextLoad["Total Context Load (30,173 tokens)"]
        AllActiveRules["All Active Rules"] --> ActivePython["Python Core Rules (5,126 tokens)
        - python_rules.mdc.md"]

        AllActiveRules --> ActiveDiscord["Discord.py Rules (18,061 tokens)
        - discord.mdc.md
        - discord-py-cogs.mdc.md
        - discord-py-commands.mdc.md"]

        AllActiveRules --> ActiveLinters["Linter Rules (6,986 tokens)
        - ruff.mdc.md
        - basedpyright.mdc.md"]
    end

    style Query fill:#f9f,stroke:#333,stroke-width:2px
    style AutoSelectDesc fill:#00f,stroke:#333,stroke-width:1px
    style ContextLoad fill:#ffd,stroke:#f00,stroke-width:3px
    style AllActiveRules fill:#faa,stroke:#333,stroke-width:2px
    style ActivePython,ActiveDiscord,ActiveLinters fill:#afa,stroke:#333,stroke-width:1px

    classDef activated fill:#afa,stroke:#333,stroke-width:2px
    class PythonRules,DiscordRules,DiscordCogs,DiscordCommands,LinterRules activated
```

## Token Impact Analysis

The current rule configuration adds 30,173 tokens to the LLM context for a simple Python file update query. This is an extremely high amount of context that will significantly impact the quality of responses and increase token usage costs.

The token usage breaks down into three main categories:
1. Discord.py Related Rules: 18,061 tokens (59.9%)
2. Linter Rules: 6,986 tokens (23.2%)
3. Python Core Rules: 5,126 tokens (17.0%)

## Recommendations

1. **Immediate Actions:**
   - Convert `discord-py-cogs.mdc.md` (8,383 tokens) to manual invocation (@discord-py-cogs)
   - Convert `discord.mdc.md` (6,443 tokens) to manual invocation (@discord)
   - Convert `python_rules.mdc.md` (5,126 tokens) to manual invocation (@python-rules)

2. **Rule Consolidation:**
   - Merge Discord.py related rules into a single, more focused rule
   - Combine linter rules (`ruff.mdc.md` and `basedpyright.mdc.md`) into a unified Python linting guide

3. **Optimization Strategy:**
   - Create a lightweight Python base rule (<2000 tokens) for common patterns
   - Move specialized Discord.py functionality to manual rules
   - Keep linter rules as Auto Select+desc but optimize their content

These changes could reduce the automatic context load by approximately 20,000 tokens (66%), bringing it down to around 10,000 tokens for Python file operations.
