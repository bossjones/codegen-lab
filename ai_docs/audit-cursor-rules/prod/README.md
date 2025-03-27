# Cursor Rules Visualization - Production Environment

## Current Rule Structure and Relationships

This document provides an overview of how cursor rules are triggered and their impact on LLM context. The analysis is based on the current production environment configuration.

## Rule Types Legend

| Rule Type        | Usage                                            | description Field | globs Field           | alwaysApply field |
| ---------------- | ------------------------------------------------ | ----------------- | --------------------- | ----------------- |
| Agent Selected   | Agent sees description and chooses when to apply | critical          | blank                 | false             |
| Always           | Applied to every chat and cmd-k request          | blank             | blank                 | true              |
| Auto Select      | Applied to matching existing files               | blank             | critical glob pattern | false             |
| Auto Select+desc | Better for new files                             | included          | critical glob pattern | false             |
| Manual           | User must reference in chat                      | blank             | blank                 | false             |

## Token Impact Categories

- Low impact: < 500 tokens
- Medium impact: 500-2000 tokens
- High impact: > 2000 tokens
- Very High impact: > 5000 tokens

## Current Rule Distribution

| Rule Type        | Count |
| ---------------- | ----- |
| Agent Selected   | 5     |
| Always           | 1     |
| Auto Select      | 1     |
| Auto Select+desc | 10    |
| Manual           | 2     |

## Token Usage by Rule

| Rule                                         | Type             | Token Count | Impact     |
| -------------------------------------------- | ---------------- | ----------- | ---------- |
| global-rules/emoji-communication-always.mdc  | Always           | 262         | Low        |
| documentation/markdown-auto.mdc              | Auto Select+desc | 303         | Low        |
| repomix.mdc                                  | Auto Select+desc | 4,659       | High       |
| repo_analyzer.mdc                            | Auto Select+desc | 3,774       | High       |
| uv.mdc                                       | Auto Select+desc | 1,212       | Medium     |
| tdd.mdc                                      | Auto Select+desc | 1,412       | Medium     |
| uv-workspace.mdc                             | Auto Select+desc | 3,071       | High       |
| tree.mdc                                     | Auto Select+desc | 99          | Low        |
| suggest-cursor-rule.mdc                      | Auto Select+desc | 2,442       | High       |
| project_layout.mdc                           | Auto Select+desc | 1,716       | Medium     |
| cursor_rules_location.mdc                    | Auto Select+desc | 856         | Medium     |

## Analysis and Recommendations

Based on the analysis of various query scenarios, the following recommendations are provided:

1. Consider converting high-token Auto Select+desc rules to manual invocation
   - repomix.mdc (4,659 tokens)
   - repo_analyzer.mdc (3,774 tokens)
   - uv-workspace.mdc (3,071 tokens)
   - suggest-cursor-rule.mdc (2,442 tokens)

2. Consolidate overlapping rules to reduce context bloat
   - repomix.mdc and tree.mdc have some overlapping repository structure functionality
   - uv.mdc and uv-workspace.mdc could potentially be combined

3. Keep low-impact rules as automatic
   - emoji-communication-always.mdc (262 tokens) is reasonable for an Always rule
   - tree.mdc (99 tokens) is low impact and can remain automatic

4. Review glob patterns with wide coverage
   - Several rules use "*" or "**/*" globs which activate on almost any file
   - Consider more specific glob patterns to reduce unnecessary rule activation
