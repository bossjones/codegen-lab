# Cursor Rules MCP Server

A Model Context Protocol (MCP) server that helps users create custom cursor rules based on their repository structure.

## What is This?

This MCP server provides a conversational interface for:

1. Analyzing your repository structure
2. Suggesting appropriate cursor rules based on the analysis
3. Customizing and generating cursor rules tailored to your project
4. Exporting the cursor rules to your repository

## What are Cursor Rules?

Cursor rules are instructions that guide Claude when working with your code. They can help:
- Define project-specific conventions
- Enforce coding standards
- Guide development workflows
- Provide context about your codebase

## Installation

This package is part of the Codegen Lab UV workspace. You can install it with:

```bash
# Clone the repository
git clone https://github.com/bossjones/codegen-lab.git
cd codegen-lab

# Install workspace dependencies
make uv-workspace-sync

# Install this package specifically
make uv-workspace-package-sync package=cursor_rules_mcp_server
```

Alternatively, you can install it directly:

```bash
# Install using UV
uv pip install -e packages/cursor_rules_mcp_server

# Or using pip
pip install -e packages/cursor_rules_mcp_server
```

## Usage

### Starting the Server

```bash
# Run via the workspace
make uv-workspace-run package=cursor_rules_mcp_server cmd="python -m cursor_rules_mcp_server"

# Or run directly
python -m cursor_rules_mcp_server
```

### Connecting with Claude Desktop

1. Open Claude Desktop
2. Go to Settings > Developers > MCP Servers
3. Add a new MCP server with:
   - Name: Cursor Rules Generator
   - URL: http://localhost:8000
4. Select the "Create Custom Cursor Rules" prompt

### Available Tools

The server provides the following tools:

- `analyze_repository`: Analyze a repository and suggest cursor rules based on its structure
- `get_rule_templates`: Get available cursor rule templates
- `get_rule_template`: Get a specific cursor rule template
- `generate_rule`: Generate a cursor rule from a template
- `customize_rule`: Customize a cursor rule for a specific repository
- `validate_rule`: Validate a cursor rule for correctness
- `save_rule`: Save a cursor rule to the database
- `list_rules`: List all saved cursor rules
- `export_rules`: Export cursor rules to markdown files

## Development

### Project Structure

```
packages/cursor_rules_mcp_server/
├── pyproject.toml    # Package configuration
├── README.md         # This documentation
└── src/              # Source code directory
    └── cursor_rules_mcp_server/
        ├── __init__.py        # Package initialization and docstring checklist
        ├── server.py          # MCP server implementation
        ├── models.py          # Database models and schema
        ├── repository_analyzer.py  # Repository structure analysis
        └── rule_generator.py  # Rule generation and customization
```

### Extending

To add new rule templates, create them in the `hack/drafts/cursor_rules` directory and run the server. They will be automatically imported and made available to users.

## License

MIT
