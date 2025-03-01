# LLM Codegen Workflow

This repository contains task runner configurations for LLM-related code generation tasks, inspired by [Harper Reed's LLM codegen workflow](https://harper.blog/2025/02/16/my-llm-codegen-workflow-atm/).

## Prerequisites

To use these task runners, you'll need to install:

1. [repomix](https://github.com/replicate/repomix) - For bundling your codebase
2. [llm](https://llm.datasette.io/) - For interacting with various LLMs
3. Either [Task](https://taskfile.dev/) or [mise](https://mise.jdx.dev/) - Task runners

### Installation

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
```

## Available Task Runners

This repository provides two equivalent task runner configurations:

1. `Taskfile.yml` - For users of Task
2. `mise.toml` - For users of mise

Both provide the same functionality, just choose the one that fits your workflow.

## LLM Tasks

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

## Python Tasks

| Task Name | Description |
|-----------|-------------|
| `python:format` | Formats Python code using ruff |
| `python:lint` | Lints Python code using ruff |
| `python:lint-fix` | Automatically fixes Python linting issues |
| `python:test` | Runs Python tests using pytest |

## Utility Tasks

| Task Name | Description |
|-----------|-------------|
| `jupyter` | Starts Jupyter Lab |
| `webui` | Starts WebUI |
| `claude` | Starts Claude CLI |

## Usage

### Using Task

```bash
# Generate a bundle of your codebase
task llm:generate_bundle

# Generate a README
task llm:generate_readme

# Generate missing tests
task llm:generate_missing_tests

# Run Python tests
task python:test
```

### Using mise

```bash
# Generate a bundle of your codebase
mise run llm:generate_bundle

# Generate a README
mise run llm:generate_readme

# Generate missing tests
mise run llm:generate_missing_tests

# Run Python tests
mise run python:test
```

## LLM Codegen Workflow

The typical workflow as described in the blog post:

1. Set up your repository with boilerplate code and tools
2. Generate a bundle of your codebase: `task llm:generate_bundle` or `mise run llm:generate_bundle`
3. Generate missing tests or other artifacts: `task llm:generate_missing_tests` or `mise run llm:generate_missing_tests`
4. Copy the bundle to your clipboard for use with Claude or other LLMs: `task llm:copy_buffer_bundle` or `mise run llm:copy_buffer_bundle`
5. Paste the bundle into your LLM along with specific prompts (from the generated markdown files)
6. Implement the generated code in your IDE
7. Run tests and verify: `task python:test` or `mise run python:test`
8. Repeat as needed

## Customization

You can customize these task runner configurations by:

1. Modifying the ignore patterns in the `llm:generate_bundle` task
2. Changing the LLM models used in each task
3. Adding new tasks specific to your workflow

For mise, you can override tasks locally by creating a `.mise.toml` file in your project directory.
