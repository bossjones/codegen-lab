# Codegen Lab

This is the documentation for the Codegen Lab project.

## Overview

Codegen Lab is a project focused on code generation and AI-assisted development tools. This documentation will guide you through the installation, configuration, and usage of Codegen Lab.

## Features

- **Model Context Protocol (MCP) Server**: FastAPI-based server implementation for efficient AI model interactions
- **Multi-Model AI Integration**: Seamless integration with Anthropic and OpenAI models for diverse AI capabilities
- **Repository Analysis Tools**: Utilities for analyzing codebases and extracting relevant context for AI processing
- **Discord Bot Integration**: Built-in Discord bot functionality for automated interactions and notifications
- **Cursor Rules**: Custom workflow automations for iterative development in existing codebases
- **UV Workspace**: Efficient management of multiple packages within a single repository using UV package manager
- **Development Tools**: Comprehensive suite including Makefile automation, pre-commit hooks, and CI/CD workflows

## Quick Start

```bash
# Clone the repository
git clone https://github.com/bossjones/codegen-lab.git
cd codegen-lab

# Install dependencies
uv sync --frozen
```

## Documentation Structure

- **Getting Started**: Basic introduction and setup
- **User Guide**: Detailed usage instructions
  - **Installation**: Step-by-step installation guide
  - **Configuration**: Detailed configuration options
- **Development Tools**: Tools and workflows for effective development
  - **Cursor Rules**: Workflow automations for iterative development
  - **UV Workspace**: Package management within a monorepo structure
- **API Reference**: Technical reference for APIs
- **Contributing**: Guidelines for contributors
- **Changelog**: Project version history and updates

## Local Development

To work on the documentation locally:

1. Install documentation dependencies:

   ```bash
   uv add --dev mkdocs mkdocs-material
   ```

2. Serve the documentation locally:

   ```bash
   uv run mkdocs serve
   ```

   This will start a local server at http://127.0.0.1:8000/ where you can preview the documentation.

## Writing Style Guide

When contributing to the documentation:

- Use clear, concise language
- Provide examples where appropriate
- Use proper Markdown formatting
- Use headings to structure content
- Add appropriate links to other documentation pages
- Use admonitions for notes, warnings, etc.

## Building and Deployment

The documentation is automatically deployed to GitHub Pages when changes are pushed to the `main` branch. For manual deployment, you can run:

```bash
uv run mkdocs build   # Build static site
uv run mkdocs gh-deploy   # Deploy to GitHub Pages
```
