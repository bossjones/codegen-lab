# Cursor Rules Visualization - Staging Environment

## Current Rule Structure and Relationships

Based on the audit of the staging environment, we have identified the following distribution of rules:

- Total Rules: 76
  - Agent Selected: 1
  - Auto Select+desc: 29
  - Manual: 46

## Rule Types Legend

| Rule Type        | Usage                                            | description Field | globs Field           | alwaysApply field |
| --------------- | ------------------------------------------------ | ---------------- | -------------------- | ----------------- |
| Agent Selected   | Agent sees description and chooses when to apply | critical          | blank                 | false             |
| Always           | Applied to every chat and cmd-k request          | blank             | blank                 | true              |
| Auto Select      | Applied to matching existing files               | blank             | critical glob pattern | false             |
| Auto Select+desc | Better for new files                            | included          | critical glob pattern | false             |
| Manual           | User must reference in chat                      | blank             | blank                 | false             |

## Token Impact Categories

- Low impact: < 500 tokens
- Medium impact: 500-2000 tokens
- High impact: > 2000 tokens
- Very High impact: > 5000 tokens

## High Impact Rules Analysis

The following Auto Select+desc rules have significant token counts:

### Very High Impact (>5000 tokens)
1. fastmcp-tools.mdc.md (11,022 tokens)
2. discord-py-cogs.mdc.md (8,383 tokens)
3. python-refactor.mdc.md (8,103 tokens)
4. discord-py-cogs-advanced.mdc.md (7,655 tokens)
5. fastmcp_fixer.mdc.md (7,296 tokens)
6. fastmcp.mdc.md (6,927 tokens)
7. discord.mdc.md (6,443 tokens)
8. fastmcp_audit_args.mdc.md (5,749 tokens)

### High Impact (2000-5000 tokens)
1. python_rules.mdc.md (5,126 tokens)
2. enrich-github-markdown.mdc.md (4,772 tokens)
3. repomix.mdc.md (4,659 tokens)
4. python-tdd-basics.mdc.md (4,210 tokens)
5. basedpyright.mdc.md (3,960 tokens)
6. repo_analyzer.mdc.md (3,769 tokens)
7. fastmcp-testing.mdc.md (3,623 tokens)
8. dpytest-integration.mdc.md (3,431 tokens)
9. discord-py-commands.mdc.md (3,235 tokens)
10. uv-workspace.mdc.md (3,071 tokens)
11. ruff.mdc.md (3,026 tokens)

## Analysis and Recommendations

1. **Convert High-Impact Rules to Manual Invocation:**
   - All rules with >5000 tokens should be converted to manual invocation to reduce context bloat
   - Consider converting rules >3000 tokens to manual invocation if not frequently used

2. **Consolidate Related Rules:**
   - Discord.py related rules could be consolidated:
     - Combine `discord-py-cogs.mdc.md` and `discord-py-cogs-advanced.mdc.md`
     - Merge related Discord.py testing rules
   - FastMCP related rules could be reorganized:
     - Combine `fastmcp-tools.mdc.md` with related specific tool rules
     - Merge `fastmcp_fixer.mdc.md` and `fastmcp_audit_args.mdc.md`

3. **Keep Efficient Auto Select+desc Rules:**
   - Rules under 2000 tokens that are frequently used should remain as Auto Select+desc
   - Example: `tree.mdc.md` (99 tokens), `notify.mdc.md` (58 tokens)

4. **Optimize Rule Structure:**
   - Consider breaking down large rules into smaller, more focused components
   - Move common patterns into shared rules to reduce duplication
   - Create a hierarchical structure where base rules can be extended by more specific ones

5. **Impact on LLM Context:**
   - Current maximum potential context load: ~150,000 tokens (if all Auto Select+desc rules are triggered)
   - Recommended changes could reduce this by ~70% to ~45,000 tokens
   - This would significantly improve LLM response quality and reduce token usage

## Next Steps

1. Implement manual invocation for identified high-impact rules
2. Begin consolidation of related rule sets
3. Optimize remaining Auto Select+desc rules
4. Monitor impact on LLM performance after changes
