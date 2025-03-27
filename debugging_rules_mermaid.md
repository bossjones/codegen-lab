# Cursor Rules Relationship Diagram

This diagram visualizes the relationships between different cursor rules in the codebase.
It shows how rules are categorized and which types of rules exist in each category.

```mermaid
flowchart TD
    Query["User query analyzing cursor rules"]
    Query --> RuleTypes["Rule Types"]



    %% Styling
    style Query fill:#f9f,stroke:#333,stroke-width:2px
    style RuleTypes fill:#dfd,stroke:#333,stroke-width:2px
    style Always fill:#f0f,stroke:#333,stroke-width:1px
    style AgentSelected fill:#0dd,stroke:#333,stroke-width:1px
    style AutoSelect fill:#0d0,stroke:#333,stroke-width:1px
    style AutoSelectdesc fill:#00f,stroke:#333,stroke-width:1px
    style Manual fill:#ff0,stroke:#333,stroke-width:1px
```

## Legend

- **Always Rules (Magenta)**: Always applied regardless of context
- **Agent Selected Rules (Cyan)**: Chosen by the AI based on context
- **Auto Select Rules (Green)**: Automatically selected based on file globs
- **Auto Select+desc Rules (Blue)**: Automatically selected with descriptions
- **Manual Rules (Yellow)**: Manually specified rules

# Rule Visualization for Query: "update our mermaid documentation"

```mermaid
flowchart TD
    Query["User Query: update our mermaid documentation"] --> Analysis["Rule Analysis"]

    Analysis --> RuleTypes["Rule Type Categorization"]

    RuleTypes --> Always["Always Rules"]
    RuleTypes --> AgentSelected["Agent Selected Rules"]
    RuleTypes --> AutoSelect["Auto Select Rules"]
    RuleTypes --> AutoSelectDesc["Auto Select+desc Rules"]
    RuleTypes --> Manual["Manual Rules"]

    Always --> AlwaysRules["global-rules/emoji-communication-always.mdc"]

    AgentSelected --> AgentSelectedRules["bossjones-cursor-tools.mdc
    core-rules/cursor-rules-migration-agent.mdc
    core-rules/prd-prompt-generator-agent.mdc
    core-rules/rule-generating-agent.mdc
    workflows/workflow-rule-visualization-agent-manual.mdc"]

    AutoSelect --> AutoSelectRules["core-rules/cursor-rule-syntax.mdc"]

    AutoSelectDesc --> AutoSelectDescRules["documentation/markdown-auto.mdc
    project_layout.mdc
    cursor_rules_location.mdc
    repomix.mdc
    repo_analyzer.mdc
    notify.mdc
    tree.mdc"]

    Manual --> ManualRules["workflows/workflow-migration-agent.mdc
    tool-rules/visualization-tool-rules.mdc"]

    style Query fill:#f9f,stroke:#333,stroke-width:2px
    style Always fill:#f0f,stroke:#333,stroke-width:1px
    style AgentSelected fill:#0dd,stroke:#333,stroke-width:1px
    style AutoSelect fill:#0d0,stroke:#333,stroke-width:1px
    style AutoSelectDesc fill:#00f,stroke:#333,stroke-width:1px
    style Manual fill:#ff0,stroke:#333,stroke-width:1px

    classDef activated fill:#afa,stroke:#333,stroke-width:2px
    class AlwaysRules,AgentSelectedRules,AutoSelectDescRules activated
```

## Rule Types

| Rule Type        | Usage                                            | description Field | globs Field           | alwaysApply field |
| ---- | --- | ----- | --- | ----- |
| Agent Selected   | Agent sees description and chooses when to apply | critical          | blank                 | false             |
| Always           | Applied to every chat and cmd-k request          | blank             | blank                 | true              |
| Auto Select      | Applied to matching existing files               | blank             | critical glob pattern | false             |
| Auto Select+desc | Better for new files                             | included          | critical glob pattern | false             |
| Manual           | User must reference in chat                      | blank             | blank                 | false             |

## Color Legend

- ![#f9f](https://via.placeholder.com/15/f9f/000000?text=+) User Query
- ![#f0f](https://via.placeholder.com/15/f0f/000000?text=+) Always Rules
- ![#0dd](https://via.placeholder.com/15/0dd/000000?text=+) Agent Selected Rules
- ![#0d0](https://via.placeholder.com/15/0d0/000000?text=+) Auto Select Rules
- ![#00f](https://via.placeholder.com/15/00f/000000?text=+) Auto Select+desc Rules
- ![#ff0](https://via.placeholder.com/15/ff0/000000?text=+) Manual Rules

## Rule Application Analysis

For the query "update our mermaid documentation":

- **Always Rules**: The `global-rules/emoji-communication-always.mdc` rule is applied to every query
- **Agent Selected Rules**: The workflow-rule-visualization-agent-manual.mdc rule is particularly relevant for this query about mermaid documentation
- **Auto Select+desc Rules**: The documentation/markdown-auto.mdc, project_layout.mdc, and cursor_rules_location.mdc rules apply due to working with Markdown files and cursor rules
- **Manual Rules**: While not automatically applied, the visualization-tool-rules.mdc may be relevant if manually referenced

## Understanding Rule Activation

The diagram shows how this query activates different rule types:
1. Always rules are automatically applied regardless of query context
2. Agent Selected rules like workflow-rule-visualization-agent-manual.mdc are chosen by the AI because they're specifically relevant to mermaid diagrams and cursor rule visualization
3. Auto Select+desc rules related to Markdown and documentation are applied since we're working with mermaid documentation
4. Manual rules require explicit reference and are not automatically applied

Note: Rules are identified based on the make audit-cursor-rules-prod-desc command output.

# Rule Visualization for Query: "update my changelog.md"

```mermaid
flowchart TD
    Query["User Query: update my changelog.md"] --> Analysis["Rule Analysis"]

    Analysis --> RuleTypes["Rule Types"]

    RuleTypes --> Always["Always Rules"]
    RuleTypes --> AgentSelected["Agent Selected Rules"]
    RuleTypes --> AutoSelect["Auto Select Rules"]
    RuleTypes --> AutoSelectDesc["Auto Select+desc Rules"]

    subgraph GlobalRules["Global Rules"]
        G1["emoji-communication-always.mdc"]
        G2["notify.mdc"]
    end

    subgraph FileSpecificRules["File-Specific Rules"]
        F1["changelog-update.mdc"]
        F2["markdown-auto.mdc"]
    end

    subgraph ContextRules["Context-Specific Rules"]
        C1["documentation-standards.mdc"]
    end

    Always --> GlobalRules
    AgentSelected --> FileSpecificRules
    AutoSelect --> ContextRules

    style Query fill:#f9f,stroke:#333,stroke-width:2px
    style Always fill:#f0f,stroke:#333,stroke-width:1px
    style AgentSelected fill:#0dd,stroke:#333,stroke-width:1px
    style AutoSelect fill:#0d0,stroke:#333,stroke-width:1px
    style AutoSelectDesc fill:#00f,stroke:#333,stroke-width:1px

    classDef note fill:#fff,stroke:#333,stroke-width:1px;
    class Note note;

    Note["Rules are identified based on the make audit-cursor-rules-prod-desc command output.
    The diagram shows which rules would be activated by this query."]
    Query -.-> Note
```

## Color Legend

- ![#f9f](https://via.placeholder.com/15/f9f/000000?text=+) User Query
- ![#f0f](https://via.placeholder.com/15/f0f/000000?text=+) Always Rules
- ![#0dd](https://via.placeholder.com/15/0dd/000000?text=+) Agent Selected Rules
- ![#0d0](https://via.placeholder.com/15/0d0/000000?text=+) Auto Select Rules
- ![#00f](https://via.placeholder.com/15/00f/000000?text=+) Auto Select+desc Rules

## Rule Application Analysis

- **Always Rules**: Applied to every query regardless of content
- **Agent Selected Rules**: Manually selected based on query content and file types
- **Auto Select Rules**: Automatically selected based on file extensions or content mentioned in query
- **Auto Select+desc Rules**: Automatically selected with detailed descriptions

## Understanding Rule Flow

The diagram shows how your query triggers different categories of rules, starting with the core query analysis and flowing through to specific rule types. Rules are grouped by their application method and displayed in subgraphs for better organization.

---

# Rule Visualization for Query: "add a docstring to hello.py"

```mermaid
flowchart TD
    Query["User Query: add a docstring to hello.py"] --> Analysis["Rule Analysis"]

    Analysis --> RuleTypes["Rule Types"]

    RuleTypes --> Always["Always Rules"]
    RuleTypes --> AgentSelected["Agent Selected Rules"]
    RuleTypes --> AutoSelect["Auto Select Rules"]
    RuleTypes --> AutoSelectDesc["Auto Select+desc Rules"]

    subgraph GlobalRules["Global Rules"]
        G1["emoji-communication-always.mdc"]
        G2["notify.mdc"]
    end

    subgraph PythonRules["Python-Specific Rules"]
        P1["python-documentation-standards.mdc"]
        P2["python-refactor.mdc"]
        P3["python-tdd-basics.mdc"]
    end

    subgraph DocRules["Documentation Rules"]
        D1["docstring-format.mdc"]
        D2["type-hints.mdc"]
    end

    Always --> GlobalRules
    AgentSelected --> PythonRules
    AutoSelect --> DocRules

    PythonRules -- depends on --> DocRules

    style Query fill:#f9f,stroke:#333,stroke-width:2px
    style Always fill:#f0f,stroke:#333,stroke-width:1px
    style AgentSelected fill:#0dd,stroke:#333,stroke-width:1px
    style AutoSelect fill:#0d0,stroke:#333,stroke-width:1px
    style AutoSelectDesc fill:#00f,stroke:#333,stroke-width:1px

    classDef note fill:#fff,stroke:#333,stroke-width:1px;
    class Note note;

    Note["Python file extension (.py) triggers specific Python-related rules.
    Docstring keyword activates documentation standards rules."]
    Query -.-> Note
```

## Color Legend

- ![#f9f](https://via.placeholder.com/15/f9f/000000?text=+) User Query
- ![#f0f](https://via.placeholder.com/15/f0f/000000?text=+) Always Rules
- ![#0dd](https://via.placeholder.com/15/0dd/000000?text=+) Agent Selected Rules
- ![#0d0](https://via.placeholder.com/15/0d0/000000?text=+) Auto Select Rules
- ![#00f](https://via.placeholder.com/15/00f/000000?text=+) Auto Select+desc Rules

## Rule Application Analysis

- **Always Rules**: Applied to every query regardless of content
- **Python-Specific Rules**: Selected due to the .py file extension
- **Documentation Rules**: Selected due to "docstring" keyword in query

## Understanding Rule Dependencies

The diagram shows how Python rules depend on documentation rules, creating a hierarchical relationship between rule categories. This demonstrates how rules can build upon each other to provide comprehensive guidance.

---

# Rule Visualization for Query: "Check if my .github/workflows/ci.yml file is valid"

```mermaid
flowchart TD
    Query["User Query: Check if my .github/workflows/ci.yml file is valid"] --> Analysis["Rule Analysis"]

    Analysis --> RuleTypes["Rule Types"]

    RuleTypes --> Always["Always Rules"]
    RuleTypes --> AgentSelected["Agent Selected Rules"]
    RuleTypes --> AutoSelect["Auto Select Rules"]
    RuleTypes --> AutoSelectDesc["Auto Select+desc Rules"]

    subgraph GlobalRules["Global Rules"]
        G1["emoji-communication-always.mdc"]
        G2["notify.mdc"]
    end

    subgraph GitHubRules["GitHub Actions Rules"]
        GH1["gh-action-security.mdc"]
        GH2["yaml-validator.mdc"]
        GH3["debug-gh-actions.mdc"]
    end

    subgraph CIRules["CI/CD Rules"]
        CI1["ci-best-practices.mdc"]
        CI2["workflow-validation.mdc"]
    end

    subgraph SecurityRules["Security Rules"]
        S1["security-analysis.mdc"]
        S2["secrets-scanning.mdc"]
    end

    Always --> GlobalRules
    AgentSelected --> GitHubRules
    AutoSelect --> CIRules

    GitHubRules -- includes --> SecurityRules
    CIRules -- leverages --> GitHubRules

    style Query fill:#f9f,stroke:#333,stroke-width:2px
    style Always fill:#f0f,stroke:#333,stroke-width:1px
    style AgentSelected fill:#0dd,stroke:#333,stroke-width:1px
    style AutoSelect fill:#0d0,stroke:#333,stroke-width:1px
    style AutoSelectDesc fill:#00f,stroke:#333,stroke-width:1px

    classDef note fill:#fff,stroke:#333,stroke-width:1px;
    class Note note;

    Note["GitHub Actions workflows path triggers specific GitHub Actions rules.
    Validation request activates CI/CD validation rules and security scanning."]
    Query -.-> Note
```

## Color Legend

- ![#f9f](https://via.placeholder.com/15/f9f/000000?text=+) User Query
- ![#f0f](https://via.placeholder.com/15/f0f/000000?text=+) Always Rules
- ![#0dd](https://via.placeholder.com/15/0dd/000000?text=+) Agent Selected Rules
- ![#0d0](https://via.placeholder.com/15/0d0/000000?text=+) Auto Select Rules
- ![#00f](https://via.placeholder.com/15/00f/000000?text=+) Auto Select+desc Rules

## Rule Application Analysis

- **Always Rules**: Applied to every query regardless of content
- **GitHub Actions Rules**: Selected due to the .github/workflows path and .yml extension
- **CI/CD Rules**: Selected due to "ci.yml" in the path and "valid" keyword
- **Security Rules**: Included via relationship to GitHub Actions rules

## Complex Rule Relationships

This diagram demonstrates a more complex set of rule relationships where:
1. GitHub Actions rules incorporate security scanning rules
2. CI/CD validation rules leverage GitHub Actions rules
3. Multiple rule categories interact to provide comprehensive validation
