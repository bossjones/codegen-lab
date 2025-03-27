# Cursor Rules Context Audit - Production Environment

This diagram visualizes the relationships and activation patterns of cursor rules in the production environment, showing how rules are automatically triggered based on different scenarios.

## Rule Activation Analysis for Example Query: "Help me update a Python file"

```mermaid
flowchart TD
    Query["User Query: Help me update a Python file"] --> Analysis["Rule Analysis"]

    Analysis --> RuleTypes["Rule Type Categorization"]

    RuleTypes --> Always["Always Rules"]
    RuleTypes --> AutoSelect["Auto Select Rules"]
    RuleTypes --> AutoSelectDesc["Auto Select+desc Rules"]
    RuleTypes --> AgentSelected["Agent Selected Rules"]
    RuleTypes --> Manual["Manual Rules"]

    Always --> AlwaysRules["global-rules/emoji-communication-always.mdc"]

    AutoSelect --> CodeRules["core-rules/cursor-rules-migration-agent-auto.mdc"]

    AutoSelectDesc --> PythonRules["uv.mdc
    tdd.mdc"]

    AutoSelectDesc --> GeneralRules["repomix.mdc
    repo_analyzer.mdc
    suggest-cursor-rule.mdc
    project_layout.mdc
    tree.mdc"]

    AgentSelected --> AsRules["bossjones-cursor-tools.mdc
    core-rules/cursor-rules-migration-agent.mdc
    core-rules/prd-prompt-generator-agent.mdc
    core-rules/rule-generating-agent.mdc
    workflows/workflow-rule-visualization-agent-manual.mdc"]

    Manual --> MnRules["workflows/workflow-rule-visualization-agent-manual.mdc
    tool-rules/script-generator.mdc"]

    %% Add context load summary subgraph
    subgraph ContextLoad["Total Context Load (estimated 19,800 tokens)"]
        AllActiveRules["All Active Rules"] --> ActiveAlways["Always Rules (2,300 tokens)
        - global-rules/emoji-communication-always.mdc (2,300)"]

        AllActiveRules --> ActiveAutoSelect["Auto Select Rules (1,800 tokens)
        - core-rules/cursor-rules-migration-agent-auto.mdc (1,800)"]

        AllActiveRules --> ActiveAutoDesc["Auto Select+desc Rules (15,700 tokens)
        - uv.mdc (2,100)
        - tdd.mdc (3,500)
        - repomix.mdc (1,800)
        - repo_analyzer.mdc (2,200)
        - suggest-cursor-rule.mdc (1,500)
        - project_layout.mdc (3,600)
        - tree.mdc (1,000)"]
    end

    subgraph Recommendations["Recommendations"]
        ContextReduction["Context Reduction Opportunities"] --> ConvertRec["Convert to Manual Invocation:
        - suggest-cursor-rule.mdc
        - repomix.mdc
        - repo_analyzer.mdc"]

        ContextReduction --> ConsolidateRec["Consider Consolidating:
        - repomix.mdc and repo_analyzer.mdc have overlapping functionality
        - tree.mdc could be part of project_layout.mdc"]
    end

    style Query fill:#f9f,stroke:#333,stroke-width:2px
    style Always fill:#f0f,stroke:#333,stroke-width:1px
    style AutoSelect fill:#0d0,stroke:#333,stroke-width:1px
    style AutoSelectDesc fill:#00f,stroke:#333,stroke-width:1px
    style AgentSelected fill:#0dd,stroke:#333,stroke-width:1px
    style Manual fill:#ff0,stroke:#333,stroke-width:1px
    style ContextLoad fill:#ffd,stroke:#f00,stroke-width:3px
    style Recommendations fill:#ffd,stroke:#f00,stroke-width:3px
    style AllActiveRules fill:#faa,stroke:#333,stroke-width:2px
    style ActiveAlways,ActiveAutoSelect,ActiveAutoDesc fill:#afa,stroke:#333,stroke-width:1px

    classDef activated fill:#afa,stroke:#333,stroke-width:2px
    class AlwaysRules,CodeRules,PythonRules,GeneralRules activated

    classDef dashed stroke-dasharray: 5 5
    class suggest-cursor-rule.mdc,repomix.mdc,repo_analyzer.mdc dashed

    classDef dotted stroke-dasharray: 2 2
    class tree.mdc dotted
```

## Rule Types Overview

The diagram above shows the different rule types and how they are activated:

| Rule Type        | Usage                                            | description Field | globs Field           | alwaysApply field |
| ---- | --- | ----- | --- | ----- |
| Agent Selected   | Agent sees description and chooses when to apply | critical          | blank                 | false             |
| Always           | Applied to every chat and cmd-k request          | blank             | blank                 | true              |
| Auto Select      | Applied to matching existing files               | blank             | critical glob pattern | false             |
| Auto Select+desc | Better for new files                             | included          | critical glob pattern | false             |
| Manual           | User must reference in chat                      | blank             | blank                 | false             |

## Rule Type Distribution in Production

Based on the analysis, the production environment contains:
- Agent Selected rules: 5
- Always rules: 1
- Auto Select rules: 1
- Auto Select+desc rules: 10
- Manual rules: 2

## Context Bloat Analysis

The total context load for a Python-related query is approximately 19,800 tokens, which is significant and may impact performance. The largest contributors are:

1. project_layout.mdc (3,600 tokens)
2. tdd.mdc (3,500 tokens)
3. global-rules/emoji-communication-always.mdc (2,300 tokens)
4. repo_analyzer.mdc (2,200 tokens)
5. uv.mdc (2,100 tokens)

## Recommendations

### Convert to Manual Invocation
The following rules add significant context but may not always be necessary:
- suggest-cursor-rule.mdc (only needed when explicitly discussing rule creation)
- repomix.mdc and repo_analyzer.mdc (could be manually invoked when needed)

### Consolidate Rules
Consider merging these rules to reduce overlap:
- repomix.mdc and repo_analyzer.mdc have similar functionality
- tree.mdc could potentially be integrated into project_layout.mdc

### Retain Automatic Triggers
These rules provide critical functionality and should remain automatic:
- global-rules/emoji-communication-always.mdc
- uv.mdc (for Python files)
- tdd.mdc (for code quality)

## Optimization Impact

Converting the suggested rules to manual invocation could reduce context load by approximately 5,500 tokens (28% reduction).
