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

You can view analysis results directly:
- [Production Environment Analysis (prod)](./prod/README.md) - Analysis of rules in `.cursor/rules/`
- [Staging Environment Analysis (stage)](./stage/README.md) - Analysis of rules in `hack/drafts/cursor_rules/`

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

## EXTRA | Optimization analysis

Sometimes after performing this AI workflow the LLM runs out of tokens to generate a `optimization_analysis.md` for your rules. You can open a new composer window and say something along the lines of:

```
@workflows/workflow-rule-visualization-agent-manual.mdc generate a optimization_analysis.md based on the contents of ai_docs/audit-cursor-rules/prod @prod
```

You can view the optimization analysis documents directly:
- [Production Optimization Analysis](./prod/optimization_analysis.md) - Optimization recommendations for production rules
- [Staging Optimization Analysis](./stage/optimization_analysis.md) - Optimization recommendations for staging rules

### What does the optimization analysis tell you?

The optimization analysis provides comprehensive insights into your cursor rules ecosystem and identifies opportunities for improvement:

- **Context Load Assessment**: Identifies the current token usage across different query scenarios and quantifies the impact on your LLM's context window
- **Problematic Patterns**: Highlights issues like overly broad glob patterns, automatically triggered high-token rules, and redundant functionality
- **Strategic Recommendations**: Suggests which rules to convert to manual invocation, which patterns to refine, and which rules can remain automatic
- **Visual Rule Structure**: Includes flowcharts showing the optimal rule activation patterns and their respective token impacts
- **Implementation Plan**: Outlines specific changes needed to optimize your rules, including:
  - Converting high-impact rules to manual invocation
  - Refining glob patterns for more targeted activation
  - Consolidating overlapping functionalities
  - Identifying low-impact rules that can remain automatic
- **Benefit Analysis**: Quantifies the potential improvements in token efficiency, response quality, processing speed, and user control

The analysis categorizes rules based on their token impact and provides actionable steps to significantly reduce context bloat while maintaining essential functionality.

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

## Query Analysis Files (NOTE This can change based on the makeup of your repo!!!!)

### Production Environment

Analysis files for production rules (`.cursor/rules/`):
- [Python File Query Analysis](./prod/python_file_query.md) - Analysis of rules triggered for Python files
- [Markdown File Query Analysis](./prod/markdown_file_query.md) - Analysis of rules triggered for Markdown files
- [Optimization Analysis](./prod/optimization_analysis.md) - Comprehensive optimization recommendations

### Staging Environment

Analysis files for staging rules (`hack/drafts/cursor_rules/`):
- [Python File Query Analysis](./stage/python_file_query.md) - Analysis of rules triggered for Python files
- [Test Files Query Analysis](./stage/test_files_query.md) - Analysis of rules triggered for test files
- [Shell Config Query Analysis](./stage/shell_config_query.md) - Analysis of rules triggered for shell configuration files
- [PyProject Query Analysis](./stage/pyproject_query.md) - Analysis of rules triggered for pyproject.toml files
- [GitHub Actions Query Analysis](./stage/github_actions_query.md) - Analysis of rules triggered for GitHub Actions workflows
- [Makefile Query Analysis](./stage/makefile_query.md) - Analysis of rules triggered for Makefiles
- [Optimization Analysis](./stage/optimization_analysis.md) - Comprehensive optimization recommendations

This comprehensive set of analyses helps you understand how rules are triggered in different scenarios and provides guidance for optimization.
