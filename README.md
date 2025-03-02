# 🧩 LLM Codegen Lab

A comprehensive toolkit for AI-assisted code generation workflows, inspired by [Harper Reed's LLM codegen workflow](https://harper.blog/2025/02/16/my-llm-codegen-workflow-atm/).

This lab provides a collection of tools and workflows for leveraging Large Language Models (LLMs) in your development process, with a focus on:

- 🤖 **Cursor Agent** integration with cursor rule files
- 📋 **Taskfile** for context collection and LLM interactions
- 🚀 **Greenfield Development** using LLM-assisted workflows
- 🧪 **Test-Driven Development** with AI assistance
- 📦 **UV Workspace** for managing modular packages

## ✨ Features

- 📝 Generate codebases from specifications
- 🔍 Create comprehensive code reviews
- 🧩 Identify and implement missing tests
- 📊 Generate GitHub issues from codebase analysis
- 🧠 Leverage Cursor IDE with custom rule files for enhanced AI assistance
- 📦 Organize code in modular packages with UV workspace management

## 🛠️ Prerequisites

To use these tools, you'll need to install:

1. [repomix](https://github.com/replicate/repomix) - For bundling your codebase
2. [llm](https://llm.datasette.io/) - For interacting with various LLMs
3. [Cursor](https://cursor.sh/) - The AI-native code editor
4. [UV](https://github.com/astral-sh/uv) - Fast Python package installer and environment manager
5. Either [Task](https://taskfile.dev/) or [mise](https://mise.jdx.dev/) - Task runners

### 📥 Installation

```bash
# Install repomix
npm install -g repomix

# Install llm
pip install llm

# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Task (for Taskfile.yml)
# macOS
brew install go-task/tap/go-task

# Install mise (for mise.toml)
# macOS
brew install mise

# Install Cursor IDE
# Visit https://cursor.sh/ and follow instructions
```

## 🚀 Quickstart Guide

### 1️⃣ Using Cursor Agent with Custom Rules

The repository includes a collection of specialized cursor rule files in `hack/drafts/cursor_rules/` that enhance Cursor's AI capabilities:

```bash
# Clone the repository
git clone https://github.com/bossjones/codegen-lab.git
cd codegen-lab

# Setup your project by copying cursor rules to your editor
mkdir -p ~/.cursor/rules
cp hack/drafts/cursor_rules/*.mdc ~/.cursor/rules/
```

Key cursor rules include:
- `greenfield.mdc` - For implementing new projects from scratch
- `tdd.mdc` - For test-driven development workflows
- `anthropic-chain-of-thought.mdc` - For enhanced reasoning
- `code-context-gatherer.mdc` - For context collection
- `uv-workspace.mdc` - For UV workspace package management

### 2️⃣ Using UV Workspace for Package Management

The project uses UV workspace to manage multiple packages in a single repository:

```bash
# Lock dependencies for the entire workspace
make uv-workspace-lock

# Install dependencies for the workspace root
make uv-workspace-sync

# Create a new package in the workspace
make uv-workspace-init-package name=my-new-package

# Add a workspace package as a dependency
make uv-workspace-add-dep package=cursor-rules-mcp-server

# Install dependencies for a specific package
make uv-workspace-package-sync package=cursor-rules-mcp-server

# Run a command in a specific package
make uv-workspace-run package=cursor-rules-mcp-server cmd="python -m cursor_rules_mcp_server"
```

### 3️⃣ Using Taskfile for Context Collection

Generate codebase bundles and LLM prompts using Task:

```bash
# Generate a bundle of your codebase
task llm:generate_bundle

# Generate missing tests and copy to clipboard
task llm:generate_missing_tests
task llm:copy_buffer_bundle

# Format and lint your Python code
task python:format
task python:lint
```

### 4️⃣ Implementing Greenfield Projects

Follow the Greenfield development workflow:

1. **Idea Honing** (15 minutes):
   - Use an LLM to refine your idea into a detailed specification
   - Save the specification as `spec.md`

2. **Planning** (15-30 minutes):
   - Create a step-by-step implementation plan
   - Break down into small, incremental tasks
   - Save as `prompt_plan.md` and `todo.md`

3. **Execution**:
   - Use Cursor's AI capabilities with custom rules
   - Implement each step from your plan
   - Test and verify at each stage

## 📂 Project Structure

```
.
├── .cursor/                     # Active cursor rules directory
│   └── rules/                   # Production cursor rules
├── Makefile                     # Build automation
├── README.md                    # Project overview and setup instructions
├── hack/                        # Development tooling
│   └── drafts/                  # Work-in-progress resources
│       └── cursor_rules/        # Staging area for cursor rules
├── packages/                    # UV workspace packages
│   └── cursor-rules-mcp-server/ # Cursor rules MCP server package
│       ├── pyproject.toml       # Package configuration
│       └── src/                 # Package source code
│           └── cursor_rules_mcp_server/ # Package code
├── src/                         # Python source code
│   └── goob_ai/                 # Core application modules
├── tests/                       # Test suites
│   ├── integration/             # Integration tests
│   └── unittests/               # Unit tests
└── docs/                        # Project documentation
```

## 🧰 Available Task Runners

This repository provides two equivalent task runner configurations:

1. `Taskfile.yml` - For users of Task
2. `mise.toml` - For users of mise

Both provide the same functionality, just choose the one that fits your workflow.

### 📚 LLM Tasks

| Task Name | Description |
|-----------|-------------|
| `llm:generate_bundle` | Generates an `output.txt` file containing your codebase using repomix |
| `llm:clean_bundles` | Removes all generated `output.txt` files |
| `llm:generate_readme` | Generates a README.md from your codebase |
| `llm:copy_buffer_bundle` | Copies the generated bundle to your clipboard |
| `llm:generate_github_issues` | Generates GitHub issues from your codebase |
| `llm:generate_code_review` | Generates a code review of your codebase |
| `llm:generate_missing_tests` | Identifies and generates missing tests for your codebase |
| `llm:generate_issue_prompts` | Generates issue prompts from your codebase |

### 🐍 Python Tasks

| Task Name | Description |
|-----------|-------------|
| `python:format` | Formats Python code using ruff |
| `python:lint` | Lints Python code using ruff |
| `python:lint-fix` | Automatically fixes Python linting issues |
| `python:test` | Runs Python tests using pytest |

### 🔧 Utility Tasks

| Task Name | Description |
|-----------|-------------|
| `jupyter` | Starts Jupyter Lab |
| `webui` | Starts WebUI |
| `claude` | Starts Claude CLI |

### 📦 UV Workspace Tasks

| Task Name | Description |
|-----------|-------------|
| `uv-workspace-lock` | Updates the lockfile for the entire workspace |
| `uv-workspace-sync` | Installs dependencies for the workspace root |
| `uv-workspace-init-package` | Creates a new package in the workspace |
| `uv-workspace-add-dep` | Adds a workspace package as a dependency |
| `uv-workspace-package-sync` | Installs dependencies for a specific package |
| `uv-workspace-run` | Runs a command in a specific package |

## 💡 Typical Workflow

1. **Setup your environment**:
   - Configure Cursor with custom rule files
   - Initialize your project structure

2. **Generate code context**:
   - `task llm:generate_bundle` to create a codebase snapshot
   - `task llm:generate_missing_tests` to identify gaps

3. **Use Cursor with context**:
   - Copy the bundle to clipboard: `task llm:copy_buffer_bundle`
   - Use Cursor's AI capabilities with specific prompts
   - Leverage custom rule files for specialized assistance

4. **Implement and test**:
   - Write code in Cursor with AI assistance
   - Run tests: `task python:test`
   - Format code: `task python:format`

5. **Review and refine**:
   - Generate code reviews: `task llm:generate_code_review`
   - Identify issues: `task llm:generate_github_issues`
   - Iterate and improve

## 📘 Documentation

For more detailed information, check out the documentation in the `docs/` directory.

## 🔧 Customization

You can customize these task runner configurations by:

1. Modifying the ignore patterns in the `llm:generate_bundle` task
2. Changing the LLM models used in each task
3. Adding new tasks specific to your workflow

For mise, you can override tasks locally by creating a `.mise.toml` file in your project directory.

## 📝 Changelog Management

This project follows the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format and [Semantic Versioning](https://semver.org/spec/v2.0.0.html) principles for documenting changes.

### Updating the Changelog

To automatically update the changelog with the latest changes:

```bash
# Update changelog with changes from a specific branch
python scripts/update_changelog.py --branch=your-branch-name

# Finalize a new release version
python scripts/update_changelog.py --finalize --version=1.0.0
```

The script will extract conventional commit messages and categorize them according to their type:
- `feat`: Added
- `fix`: Fixed
- `refactor`, `style`, `perf`: Changed
- `chore`: Added (for important changes)
- `docs`: Documentation changes

You can customize the changelog configuration by editing the `.changelog-config.yml` file in the project root.
