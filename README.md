# 🧩 LLM Codegen Lab

A comprehensive toolkit for AI-assisted code generation workflows, inspired by [Harper Reed's LLM codegen workflow](https://harper.blog/2025/02/16/my-llm-codegen-workflow-atm/).

This lab provides a collection of tools and workflows for leveraging Large Language Models (LLMs) in your development process, with a focus on:

- 🤖 **Cursor Agent** integration with cursor rule files
- 📋 **Taskfile** for context collection and LLM interactions
- 🚀 **Greenfield Development** using LLM-assisted workflows
- 🧪 **Test-Driven Development** with AI assistance

## ✨ Features

- 📝 Generate codebases from specifications
- 🔍 Create comprehensive code reviews
- 🧩 Identify and implement missing tests
- 📊 Generate GitHub issues from codebase analysis
- 🧠 Leverage Cursor IDE with custom rule files for enhanced AI assistance

## 🛠️ Prerequisites

To use these tools, you'll need to install:

1. [repomix](https://github.com/replicate/repomix) - For bundling your codebase
2. [llm](https://llm.datasette.io/) - For interacting with various LLMs
3. [Cursor](https://cursor.sh/) - The AI-native code editor
4. Either [Task](https://taskfile.dev/) or [mise](https://mise.jdx.dev/) - Task runners

### 📥 Installation

```bash
# Install repomix
npm install -g repomix

# Install llm
pip install llm

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

### 2️⃣ Using Taskfile for Context Collection

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

### 3️⃣ Implementing Greenfield Projects

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
