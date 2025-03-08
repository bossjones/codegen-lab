# Non-Greenfield Iterative Development Cursor Rules

This collection of cursor rules implements Harper Reed's non-greenfield iteration workflow as described in [their blog post](https://harper.blog/2025/02/16/my-llm-codegen-workflow-atm/). The rules are designed to help you automatically follow this workflow using Cursor's agent mode.

## Workflow Overview

Harper's non-greenfield iteration workflow involves:

1. **Getting context** from the existing codebase
2. **Planning per task** rather than for the entire project
3. **Implementing incrementally** with constant testing and feedback
4. **Debugging and fixing issues** as they arise

## Rules in this Collection

This collection contains the following cursor rules:

1. **[anthropic-chain-of-thought.mdc.md](anthropic-chain-of-thought.mdc.md)** - Best practices for chain of thought reasoning and XML tag usage with Anthropic models
2. **[avoid-debug-loops.mdc.md](avoid-debug-loops.mdc.md)** - When stuck in debugging loops, break the cycle by minimizing to an MVP
3. **[basedpyright.mdc.md](basedpyright.mdc.md)** - Comprehensive best practices for using pyright and BasedPyright in Python projects
4. **[bossjones-cursor-tools.mdc.md](bossjones-cursor-tools.mdc.md)** - Global Rule for cursor tools
5. **[changelog.mdc.md](changelog.mdc.md)** - Changelog Management Guidelines for Codegen Lab
6. **[cheatsheet.mdc.md](cheatsheet.mdc.md)** - Cheatsheet Creation Best Practices
7. **[chezmoi.mdc.md](chezmoi.mdc.md)** - Best practices and reference for working with Chezmoi dotfile manager
8. **[code-context-gatherer.mdc.md](code-context-gatherer.mdc.md)** - Efficiently gather code context from the codebase for LLM consumption
9. **[cursor_rules_location.mdc.md](cursor_rules_location.mdc.md)** - Cursor Rules Location
10. **[debug-gh-actions.mdc.md](debug-gh-actions.mdc.md)** - GitHub Actions Workflow Debugging Guide
11. **[dev-loop.mdc.md](dev-loop.mdc.md)** - QA every edit
12. **[docs.mdc.md](docs.mdc.md)** - Documentation Standards for Chezmoi Dotfiles
13. **[enrich-github-markdown.mdc.md](enrich-github-markdown.mdc.md)** - Automatically update README.md files with nested directory structures
14. **[fastmcp.mdc.md](fastmcp.mdc.md)** - Fast Python MCP Server Development
15. **[get_context_for_llm.mdc.md](get_context_for_llm.mdc.md)** - Get Context for LLM
16. **[github-actions-uv.mdc.md](github-actions-uv.mdc.md)** - GitHub Actions with UV Package Manager Standards
17. **[greenfield-documentation.mdc.md](greenfield-documentation.mdc.md)** - Greenfield Documentation Standards
18. **[greenfield-execution.mdc.md](greenfield-execution.mdc.md)** - Greenfield Execution Best Practices
19. **[greenfield-index.mdc.md](greenfield-index.mdc.md)** - Greenfield Development Index
20. **[greenfield.mdc.md](greenfield.mdc.md)** - Greenfield Development Workflow
21. **[incremental-task-planner.mdc.md](incremental-task-planner.mdc.md)** - Break down a development task into smaller, manageable steps for incremental implementation
22. **[iterative-debug-fix.mdc.md](iterative-debug-fix.mdc.md)** - Guidance for debugging and fixing issues that arise during iterative development
23. **[iterative-development-workflow.mdc.md](iterative-development-workflow.mdc.md)** - Structured workflow for incremental development in existing codebases
24. **[mcp_spec.mdc.md](mcp_spec.mdc.md)** - Anthropic Model Context Protocol (MCP) Specification Reference
25. **[mcpclient.mdc.md](mcpclient.mdc.md)** - Expert guidance for building and working with MCP clients
26. **[notes-llms-txt.mdc.md](notes-llms-txt.mdc.md)** - LLM-friendly markdown format for notes directories
27. **[notify.mdc.md](notify.mdc.md)** - At the end of any task
28. **[output_txt_context.mdc.md](output_txt_context.mdc.md)** - Guidelines for extracting context from output.txt files
29. **[project_layout.mdc.md](project_layout.mdc.md)** - Documentation of the Codegen Lab project structure, organization, and Greenfield development process
30. **[python_rules.mdc.md](python_rules.mdc.md)** - Comprehensive Python development rules and standards for the Codegen Lab project
31. **[repo_analyzer.mdc.md](repo_analyzer.mdc.md)** - Repository Analysis Tool
32. **[repomix.mdc.md](repomix.mdc.md)** - Repomix tool
33. **[ruff.mdc.md](ruff.mdc.md)** - Ruff linting configuration and usage guidelines
34. **[sheldon.mdc.md](sheldon.mdc.md)** - Expert guidance for Sheldon shell plugin manager configuration and debugging
35. **[tdd.mdc.md](tdd.mdc.md)** - Implement Test-Driven Development (TDD) for AI-generated code to ensure quality, reliability, and correctness
36. **[test-generator.mdc.md](test-generator.mdc.md)** - Identify missing tests and generate appropriate test cases for the codebase
37. **[tree.mdc.md](tree.mdc.md)** - Display repository structure
38. **[update-markdown-nested-lists.mdc.md](update-markdown-nested-lists.mdc.md)** - Automatically update README.md files with nested directory structures
39. **[uv-workspace.mdc.md](uv-workspace.mdc.md)** - UV Workspace Configuration
40. **[uv.mdc.md](uv.mdc.md)** - UV Package Manager and Environment Management Guidelines

## How to Use These Rules

To use these rules in your project:

1. These are draft rules that need to be moved to your `.cursor/rules/` directory for Cursor to apply them
2. Copy the `.mdc.md` files to `.cursor/rules/` in your project
3. Cursor's agent mode will automatically apply these rules based on your queries

## Sample Usage Flow

Here's how you might use these rules in a typical development session:

1. **Start with the workflow**: "Help me implement a feature using the iterative development workflow"
2. **Gather context**: "Help me understand the current authentication system"
3. **Plan your task**: "Break down the task of adding two-factor authentication"
4. **Implement incrementally**: "Help me implement the first step of the 2FA feature"
5. **Add tests**: "Generate tests for the 2FA authentication code"
6. **Debug issues**: "The 2FA verification isn't working, help me debug it"

## Installation

To install these rules in your project:

```bash
mkdir -p .cursor/rules
cp hack/drafts/cursor_rules/*.mdc.md .cursor/rules/
```

## Credits

These rules are based on Harper Reed's blog post ["My LLM codegen workflow atm"](https://harper.blog/2025/02/16/my-llm-codegen-workflow-atm/) which describes an effective iterative development workflow using LLMs.
