# 🔍 Cursor Rules Visualization Agent

This document explains how to use the Workflow Rule Visualization Agent, a powerful tool for analyzing and optimizing Cursor Rules in your development environment.

## What It Does

The Visualization Agent analyzes how Cursor Rules interact with your LLM prompts by:
- Identifying which rules are automatically triggered in different scenarios 🔄
- Measuring the token consumption of each rule and their impact on context windows 📊
- Creating visual representations of rule relationships and activation patterns 🖼️
- Recommending optimizations to reduce context bloat and improve efficiency 🚀

> **From the agent definition**: "This agent specializes in analyzing and visualizing when and how Cursor Rules get automatically invoked, tracking the total context they add to LLM prompts, and identifying overlapping or redundant rules."

## Why This Matters

LLM performance depends heavily on efficient context usage. Each Cursor Rule adds tokens to your prompts, which can:
- Consume valuable context window space
- Increase token usage (affecting cost and performance)
- Create redundancies or conflicts between rules
- Lead to suboptimal rule activation patterns

## How to Use It

1. Invoke the agent using the manual reference pattern:
   ```
   @workflows/workflow-rule-visualization-agent-manual.mdc update the mermaid docs for prod
   ```

2. The agent will execute the appropriate analysis command:
   ```bash
   make audit-cursor-rules-prod-desc  # for production environment
   ```
   or
   ```bash
   make audit-cursor-rules-stage-desc  # for staging environment
   ```

3. The agent calculates token usage for each rule using the [token_counter.py](../../scripts/token_counter.py) script:
   ```bash
   uv run python scripts/token_counter.py -f .cursor/rules/path/to/rule.mdc
   ```

4. Analysis results are processed to:
   - Calculate token consumption for each rule
   - Generate Mermaid diagrams showing rule relationships
   - Identify frequently triggered rules
   - Provide optimization recommendations

## Output and Analysis

The visualization agent produces:

- **Mermaid Diagrams**: Visual representations of rule relationships and activation flows
- **Token Analysis**: Quantitative assessment of each rule's impact on context windows
- **Optimization Recommendations**: Actionable suggestions for improving rule efficiency

> **From the agent definition**: "Generate Mermaid diagrams showing rule activation patterns" and "Provide specific recommendations for rules to convert to manual invocation, rules to consolidate or remove due to overlap."

## Where Results Are Saved

Results are organized in dedicated directories:
```
ai_docs/audit-cursor-rules/prod/   # for production environment (aka .cursor/rules dir)
```
or
```
ai_docs/audit-cursor-rules/stage/  # for staging environment (aka hack/drafts/cursor_rules)
```

## Example Workflow

Here's what happens during a typical analysis:

1. **Rule Analysis**
   - The agent executes the appropriate audit command
   - All rules are analyzed for activation patterns and token usage using [token_counter.py](../../scripts/token_counter.py)

2. **Visualization**
   - Mermaid diagrams are generated showing rule interconnections
   - Token counts are integrated into the visualization

3. **Impact Assessment**
   - Rules are categorized based on their context impact
   - Redundancies and optimization opportunities are identified

4. **Recommendations**
   - The agent suggests specific improvements for your rule set
   - Recommendations distinguish between manual vs. automatic rule invocation

> **From the agent definition**: "Identify rules that should be converted to manual invocation or removed" and "Categorize rules by token usage: Low impact (< 500 tokens), Medium impact (500-2000 tokens), High impact (> 2000 tokens)."

## Token Impact Categories

Understanding token impact categories is essential for optimization:

| Impact Level | Token Range | Recommendation |
|--------------|-------------|----------------|
| Low          | < 500       | Generally safe for automatic invocation |
| Medium       | 500-2000    | Consider usage frequency and necessity |
| High         | > 2000      | Strong candidates for manual invocation |

Remember: Optimizing your cursor rules improves the efficiency and effectiveness of your LLM interactions! ✨

## Need More Help?

If you need additional assistance:
1. Explore the scripts in the [scripts folder](../../scripts/)
2. Review the [Makefile](../../Makefile/) tasks for rule auditing
3. Examine sample outputs in the [ai_docs/audit-cursor-rules](../audit-cursor-rules/) directory

For technical details about token counting, see [token_counter.py](../../scripts/token_counter.py).
