"""FastMCP Prompt Library Server

This server exposes cursor rules as resources and provides a prompt endpoint for creating
custom cursor rules based on user input.

Plan of Action:
1. Set up the FastMCP server with appropriate capabilities
   - [x] Initialize server with name and description
   - [x] Enable resources capability for exposing cursor rules
   - [x] Enable prompts capability for cursor rule generation

2. Expose cursor rules as resources
   - [x] Create a resource template for accessing cursor rules by name
   - [x] Implement a resource for listing all available cursor rules
   - [x] Implement a resource for accessing cursor rule content by name

3. Implement prompts for cursor rule generation
   - [x] Create a prompt for gathering repository information
   - [x] Create a prompt for generating a custom cursor rule
   - [x] Define appropriate arguments for each prompt

4. Implement utility functions
   - [x] Function to read cursor rule files from the filesystem
   - [x] Function to parse cursor rule content
   - [x] Function to generate new cursor rules based on templates and user input

5. Implement the main server logic
   - [x] Set up resource handlers
   - [x] Set up prompt handlers
   - [x] Configure server capabilities

6. Add documentation and examples
   - [x] Add comprehensive docstrings
   - [x] Include usage examples
   - [x] Document available resources and prompts

7. Implement error handling
   - [x] Handle missing cursor rules
   - [x] Validate user input
   - [x] Provide helpful error messages
"""

import glob
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict, Union

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.server import Context
from pydantic import Field

# import logging
# import logging.handlers
# from datetime import datetime

# # Configure JSON logger
# class JsonFormatter(logging.Formatter):
#     """Custom JSON formatter for logging.

#     This formatter outputs log records in JSON format with timestamp, level,
#     and message fields.
#     """

#     def format(self, record: logging.LogRecord) -> str:
#         """Format the log record as JSON.

#         Args:
#             record: The log record to format

#         Returns:
#             str: JSON formatted log string
#         """
#         log_obj = {
#             "timestamp": datetime.fromtimestamp(record.created).isoformat(),
#             "level": record.levelname,
#             "message": record.getMessage(),
#             "logger": record.name
#         }

#         if record.exc_info:
#             log_obj["exc_info"] = self.formatException(record.exc_info)

#         return json.dumps(log_obj)

# # Set up file handler with JSON formatter
# file_handler = logging.handlers.RotatingFileHandler(
#     filename="mcpserver.log",
#     maxBytes=10485760,  # 10MB
#     backupCount=5,
#     encoding="utf-8"
# )
# file_handler.setFormatter(JsonFormatter())

# # Configure root logger
# logger = logging.getLogger("prompt_library")
# logger.setLevel(logging.INFO)
# logger.addHandler(file_handler)


# Define types for cursor rule components
class CursorRuleMetadata(TypedDict, total=False):
    """Metadata for a cursor rule.

    Attributes:
        priority: The priority of the rule (high, medium, low)
        version: The version of the rule
        tags: List of tags associated with the rule

    """

    priority: str
    version: str
    tags: list[str]


class CursorRuleExample(TypedDict):
    """Example for a cursor rule.

    Attributes:
        input: The input example
        output: The expected output

    """

    input: str
    output: str


class CursorRuleFilter(TypedDict):
    """Filter for a cursor rule.

    Attributes:
        type: The type of filter (file_extension, content, etc.)
        pattern: The pattern to match

    """

    type: str
    pattern: str


class CursorRuleAction(TypedDict):
    """Action for a cursor rule.

    Attributes:
        type: The type of action (suggest, etc.)
        message: The message to display

    """

    type: str
    message: str


class CursorRule(TypedDict):
    """Complete cursor rule structure.

    Attributes:
        name: The name of the rule
        description: The description of the rule
        filters: List of filters for the rule
        actions: List of actions for the rule
        examples: List of examples for the rule
        metadata: Metadata for the rule

    """

    name: str
    description: str
    filters: list[CursorRuleFilter]
    actions: list[CursorRuleAction]
    examples: list[CursorRuleExample]
    metadata: CursorRuleMetadata


# Create server
mcp = FastMCP("prompt_library", debug=True, log_level="DEBUG")

# Define paths
CURSOR_RULES_DIR = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../hack/drafts/cursor_rules")))


def get_cursor_rule_files() -> list[Path]:
    """Get all cursor rule files from the cursor rules directory.

    Returns:
        List[Path]: List of paths to cursor rule files

    """
    return list(CURSOR_RULES_DIR.glob("*.mdc.md"))


def get_cursor_rule_names() -> list[str]:
    """Get all cursor rule names from the cursor rules directory.

    Returns:
        List[str]: List of cursor rule names (without extension)

    """
    return [file.stem.replace(".mdc", "") for file in get_cursor_rule_files()]


def read_cursor_rule(rule_name: str) -> str | None:
    """Read a cursor rule file by name.

    Args:
        rule_name: The name of the cursor rule (without extension)

    Returns:
        Optional[str]: The content of the cursor rule file, or None if not found

    """
    rule_path = CURSOR_RULES_DIR / f"{rule_name}.mdc.md"
    if rule_path.exists():
        return rule_path.read_text()
    return None


def parse_cursor_rule(content: str) -> dict[str, Any]:
    """Parse cursor rule content into a structured format.

    Args:
        content: The content of the cursor rule file

    Returns:
        Dict[str, Any]: Structured representation of the cursor rule

    """
    # Extract frontmatter
    frontmatter = {}
    frontmatter_match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
    if frontmatter_match:
        frontmatter_text = frontmatter_match.group(1)
        for line in frontmatter_text.strip().split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                frontmatter[key.strip()] = value.strip()

    # Extract title and description
    title_match = re.search(r"# (.*?)\n", content)
    title = title_match.group(1) if title_match else ""

    description = ""
    description_match = re.search(r"# .*?\n\n(.*?)\n\n", content, re.DOTALL)
    if description_match:
        description = description_match.group(1).strip()

    # Extract rule content
    rule_content = {}
    rule_match = re.search(r"<rule>(.*?)</rule>", content, re.DOTALL)
    if rule_match:
        rule_text = rule_match.group(1)

        # Extract name
        name_match = re.search(r"name: (.*?)$", rule_text, re.MULTILINE)
        if name_match:
            rule_content["name"] = name_match.group(1).strip()

        # Extract description
        desc_match = re.search(r"description: (.*?)$", rule_text, re.MULTILINE)
        if desc_match:
            rule_content["description"] = desc_match.group(1).strip()

        # Extract filters section
        filters_match = re.search(r"filters:(.*?)(?:actions:|examples:|metadata:)", rule_text, re.DOTALL)
        if filters_match:
            filters_text = filters_match.group(1).strip()
            filters = []
            for filter_match in re.finditer(r"- type: (.*?)\n\s+pattern: \"(.*?)\"", filters_text, re.DOTALL):
                filters.append({"type": filter_match.group(1).strip(), "pattern": filter_match.group(2).strip()})
            rule_content["filters"] = filters

        # Extract actions section
        actions_match = re.search(r"actions:(.*?)(?:examples:|metadata:|$)", rule_text, re.DOTALL)
        if actions_match:
            actions_text = actions_match.group(1).strip()
            actions = []
            for action_match in re.finditer(
                r"- type: (.*?)\n\s+message: \|(.*?)(?:\n\s+-|\n\nexamples|\n\nmetadata|$)", actions_text, re.DOTALL
            ):
                actions.append({"type": action_match.group(1).strip(), "message": action_match.group(2).strip()})
            rule_content["actions"] = actions

        # Extract examples section
        examples_match = re.search(r"examples:(.*?)(?:metadata:|$)", rule_text, re.DOTALL)
        if examples_match:
            examples_text = examples_match.group(1).strip()
            examples = []
            for example_match in re.finditer(r"- input: \|(.*?)\n\s+output: \"(.*?)\"", examples_text, re.DOTALL):
                examples.append({"input": example_match.group(1).strip(), "output": example_match.group(2).strip()})
            rule_content["examples"] = examples

        # Extract metadata section
        metadata_match = re.search(r"metadata:(.*?)(?:$)", rule_text, re.DOTALL)
        if metadata_match:
            metadata_text = metadata_match.group(1).strip()
            metadata = {}

            priority_match = re.search(r"priority: (.*?)$", metadata_text, re.MULTILINE)
            if priority_match:
                metadata["priority"] = priority_match.group(1).strip()

            version_match = re.search(r"version: (.*?)$", metadata_text, re.MULTILINE)
            if version_match:
                metadata["version"] = version_match.group(1).strip()

            tags_match = re.search(r"tags:(.*?)(?:\n\s+[a-z]+:|\n\n|$)", metadata_text, re.DOTALL)
            if tags_match:
                tags_text = tags_match.group(1).strip()
                tags = []
                for tag_match in re.finditer(r"- (.*?)$", tags_text, re.MULTILINE):
                    tags.append(tag_match.group(1).strip())
                metadata["tags"] = tags

            rule_content["metadata"] = metadata

    return {"frontmatter": frontmatter, "title": title, "description": description, "rule": rule_content}


def generate_cursor_rule(
    rule_name: str,
    description: str,
    file_patterns: list[str],
    content_patterns: list[str],
    action_message: str,
    examples: list[dict[str, str]],
    tags: list[str],
    priority: str = "medium",
) -> str:
    """Generate a cursor rule based on the provided parameters.

    Args:
        rule_name: The name of the rule
        description: The description of the rule
        file_patterns: List of file patterns to match
        content_patterns: List of content patterns to match
        action_message: The message to display when the rule is triggered
        examples: List of examples for the rule
        tags: List of tags for the rule
        priority: The priority of the rule (high, medium, low)

    Returns:
        str: The generated cursor rule content

    """
    # Create frontmatter
    frontmatter = f"""---
description: {description}
globs: {", ".join(file_patterns)}
alwaysApply: false
---"""

    # Create title and description
    title_section = f"# {rule_name.replace('-', ' ').title()}\n\n{description}\n"

    # Create rule section
    rule_section = f"""<rule>
name: {rule_name}
description: {description}
filters:
  # Match file patterns
  - type: file_extension
    pattern: "{"|".join(file_patterns)}"
  # Match content patterns
  - type: content
    pattern: "(?s)({"|".join(content_patterns)})"

actions:
  - type: suggest
    message: |
{action_message}

examples:
"""

    # Add examples
    for example in examples:
        # Use string concatenation instead of f-string with replace to avoid backslash issues
        input_text = example["input"].replace("\n", "\n      ")
        rule_section += f"""  - input: |
      {input_text}
    output: "{example["output"]}"

"""

    # Add metadata
    rule_section += f"""metadata:
  priority: {priority}
  version: 1.0
  tags:
"""
    for tag in tags:
        rule_section += f"    - {tag}\n"

    rule_section += "</rule>"

    # Combine all sections
    return f"{frontmatter}\n{title_section}\n{rule_section}\n"


# Dictionary mapping technology patterns to recommended cursor rules
TECHNOLOGY_PATTERNS = {
    # Python development
    r"python|django|flask|fastapi": [
        {"name": "python_rules", "description": "Comprehensive Python development rules and standards"},
        {"name": "basedpyright", "description": "Best practices for using pyright and BasedPyright in Python projects"},
        {"name": "ruff", "description": "Ruff linting configuration and usage guidelines"},
    ],
    # Testing
    r"test|pytest|unittest": [
        {"name": "tdd", "description": "Test-Driven Development for AI-generated code"},
        {"name": "test-generator", "description": "Generate appropriate test cases for the codebase"},
    ],
    # Discord bots
    r"discord|bot|chat": [
        {"name": "discord", "description": "Best practices for working with Discord.py library"},
        {"name": "dpytest", "description": "Testing Discord bots with dpytest"},
    ],
    # MCP/FastMCP
    r"mcp|model context protocol|fastmcp": [
        {"name": "fastmcp", "description": "Fast Python MCP Server Development"},
        {"name": "mcp_spec", "description": "Anthropic Model Context Protocol Specification Reference"},
        {"name": "mcpclient", "description": "Building and working with MCP clients"},
    ],
    # Greenfield development
    r"greenfield|new project|from scratch": [
        {"name": "greenfield", "description": "Greenfield Development Workflow"},
        {"name": "greenfield-execution", "description": "Greenfield Execution Best Practices"},
        {"name": "greenfield-documentation", "description": "Greenfield Documentation Standards"},
        {"name": "greenfield-index", "description": "Greenfield Development Index"},
    ],
    # GitHub Actions
    r"github actions|ci|cd|workflow|pipeline": [
        {"name": "debug-gh-actions", "description": "GitHub Actions Workflow Debugging Guide"},
        {"name": "github-actions-uv", "description": "GitHub Actions with UV Package Manager Standards"},
    ],
    # Package management
    r"package|dependency|uv|pip|venv": [
        {"name": "uv", "description": "UV Package Manager and Environment Management Guidelines"},
        {"name": "uv-workspace", "description": "UV Workspace Configuration"},
    ],
    # Documentation
    r"documentation|docs|readme|changelog": [
        {"name": "docs", "description": "Documentation Standards"},
        {"name": "changelog", "description": "Changelog Management Guidelines"},
        {
            "name": "update-markdown-nested-lists",
            "description": "Update README.md files with nested directory structures",
        },
    ],
    # Development workflows
    r"development|workflow|debug|fix": [
        {"name": "dev-loop", "description": "QA every edit"},
        {"name": "iterative-development-workflow", "description": "Structured workflow for incremental development"},
        {"name": "iterative-debug-fix", "description": "Debugging and fixing issues during iterative development"},
        {"name": "avoid-debug-loops", "description": "Break the cycle when stuck in debugging loops"},
    ],
    # Repository analysis
    r"repo|repository|analyze|codebase": [
        {"name": "repo_analyzer", "description": "Repository Analysis Tool"},
        {"name": "repomix", "description": "Repomix tool for repository analysis"},
        {"name": "code-context-gatherer", "description": "Gather code context from the codebase for LLM consumption"},
        {"name": "get_context_for_llm", "description": "Get Context for LLM"},
    ],
    # Configuration management
    r"config|dotfiles|chezmoi": [
        {"name": "chezmoi", "description": "Best practices for working with Chezmoi dotfile manager"},
        {"name": "sheldon", "description": "Sheldon shell plugin manager configuration and debugging"},
    ],
    # Project structure
    r"project structure|layout|organization": [
        {"name": "project_layout", "description": "Documentation of the project structure and organization"},
        {"name": "cursor_rules_location", "description": "Cursor Rules Location"},
    ],
    # LLM/AI integration
    r"llm|ai|claude|gpt|anthropic": [
        {"name": "anthropic-chain-of-thought", "description": "Anthropic Chain of Thought and XML Tag Best Practices"},
        {"name": "notes-llms-txt", "description": "LLM-friendly markdown format for notes directories"},
    ],
}


# Resource endpoints
@mcp.resource(
    "cursor-rules://list",
    name="list_cursor_rules",
    description="List all available cursor rules with their names and descriptions",
)
def list_cursor_rules() -> list[dict[str, str]] | dict[str, Any]:
    """List all available cursor rules.

    This resource retrieves all available cursor rules and returns them as a list
    of dictionaries containing the rule name, description, and title.

    Returns:
        Union[list[dict[str, str]], dict[str, Any]]: Either:
            - On success: List of cursor rules with the following structure:
                - "name": The rule name (without extension)
                - "description": The rule description (empty string if not found)
                - "title": The rule title (empty string if not found)
            - On error: Error object with the following structure:
                - "isError": True
                - "content": List of content objects with error message

    Examples:
        >>> rules = list_cursor_rules()
        >>> if not isinstance(rules, dict) or not rules.get("isError"):
        >>>     print(rules[0]["name"])
        >>>     'example-rule'

    """
    try:
        rules = []
        for rule_name in get_cursor_rule_names():
            content = read_cursor_rule(rule_name)
            if content:
                parsed = parse_cursor_rule(content)
                rules.append(
                    {"name": rule_name, "description": parsed.get("description", ""), "title": parsed.get("title", "")}
                )
        return rules
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": f"Error retrieving cursor rules: {e!s}"}]}


@mcp.resource(
    "cursor-rule://{name}",
    name="get_cursor_rule",
    description="Get a parsed cursor rule by name with structured content",
)
def get_cursor_rule(name: str) -> dict[str, Any]:
    """Get a cursor rule by name.

    Args:
        name: The name of the cursor rule

    Returns:
        Dict[str, Any]: The cursor rule content

    Raises:
        FileNotFoundError: If the cursor rule is not found

    """
    content = read_cursor_rule(name)
    if not content:
        raise FileNotFoundError(f"Cursor rule '{name}' not found")

    return parse_cursor_rule(content)


@mcp.resource(
    "cursor-rule-raw://{name}",
    name="get_cursor_rule_raw",
    description="Get the raw markdown content of a cursor rule by name",
)
def get_cursor_rule_raw(name: str) -> str:
    """Get the raw content of a cursor rule by name.

    Args:
        name: The name of the cursor rule

    Returns:
        str: The raw content of the cursor rule

    Raises:
        FileNotFoundError: If the cursor rule is not found

    """
    content = read_cursor_rule(name)
    if not content:
        raise FileNotFoundError(f"Cursor rule '{name}' not found")

    return content


@mcp.tool(
    name="get_static_cursor_rule",
    description="Get a static cursor rule file by name to be written to the caller's .cursor/rules directory",
)
def get_static_cursor_rule(rule_name: str) -> dict[str, str | bool | list[dict[str, str]]]:
    """Get a static cursor rule file by name.

    This tool returns the content of a specific cursor rule file so it can be
    written to the calling repository's .cursor/rules directory.

    Args:
        rule_name: The name of the cursor rule to retrieve (without .md extension)

    Returns:
        dict[str, Union[str, bool, list[dict[str, str]]]]: A dictionary containing either:
            - On success: {"rule_name": str, "content": str}
            - On error: {"isError": bool, "content": list[dict[str, str]]}

    Raises:
        No exceptions are raised; errors are returned in the result object.

    """
    # Add .md extension if not already present
    full_rule_name = rule_name if rule_name.endswith(".md") else f"{rule_name}.md"

    content = read_cursor_rule(rule_name.replace(".md", ""))
    if not content:
        # Return an error result object instead of raising an exception
        return {
            "isError": True,
            "content": [{"type": "text", "text": f"Error: Static cursor rule '{rule_name}' not found"}],
        }

    return {"rule_name": full_rule_name, "content": content}


@mcp.tool(
    name="get_static_cursor_rules",
    description="Get multiple static cursor rule files to be written to the caller's .cursor/rules directory",
)
def get_static_cursor_rules(
    rule_names: list[str] = Field(
        description="List of cursor rule names to retrieve (with or without .md extension)",
        examples=[["python-best-practices", "react-patterns"], ["error-handling"]],
        min_items=1,
    ),
) -> dict[str, list[dict[str, str | bool | list[dict[str, str]]]]]:
    """Get multiple static cursor rule files by name.

    This tool returns the content of specific cursor rule files so they can be
    written to the calling repository's .cursor/rules directory.

    Args:
        rule_names: List of cursor rule names to retrieve (with or without .md extension)

    Returns:
        dict[str, list[dict[str, Union[str, bool, list[dict[str, str]]]]]]: A dictionary containing:
            - "rules": A list of rule data objects, each with either:
                - On success: {"rule_name": str, "content": str}
                - On error: {"isError": bool, "content": list[dict[str, str]]}

    Raises:
        No exceptions are raised; errors are returned in the result objects.

    Examples:
        >>> result = get_static_cursor_rules(["python-best-practices", "react-patterns"])
        >>> print(len(result["rules"]))
        2

    """
    # Validate input
    if not rule_names:
        return {
            "rules": [{"isError": True, "content": [{"type": "text", "text": "Error: Empty rule_names list provided"}]}]
        }

    results = []

    for rule_name in rule_names:
        # Get the rule data using get_static_cursor_rule
        rule_data = get_static_cursor_rule(rule_name)

        # Add the result to our list
        results.append(rule_data)

    # Return a single JSON object with the results array
    return {"rules": results}


# Prompt endpoints
@mcp.prompt(name="repo-analysis", description="Analyze a repository to gather information for cursor rule creation")
def repo_analysis_prompt(
    repo_description: str, main_languages: str, file_patterns: str, key_features: str, ctx: Context | None = None
) -> list[dict[str, Any]]:
    """Prompt for analyzing a repository to gather information for cursor rule creation.

    Args:
        repo_description: Description of the repository and its purpose
        main_languages: Main programming languages used in the repository
        file_patterns: Common file patterns in the repository
        key_features: Key features or components of the repository
        ctx: The MCP context (optional)

    Returns:
        List[Dict[str, Any]]: List of messages for the prompt

    """
    return [
        {
            "role": "user",
            "content": {
                "type": "text",
                "text": f"""I need to analyze a repository to create a cursor rule. Here's the information:

Repository Description:
{repo_description}

Main Languages:
{main_languages}

File Patterns:
{file_patterns}

Key Features:
{key_features}

Based on this information, what types of cursor rules would be most beneficial for this repository?
What patterns should I look for in the code?
What best practices should I enforce?
""",
            },
        }
    ]


@mcp.prompt(name="generate-cursor-rule", description="Generate a custom cursor rule based on repository information")
def generate_cursor_rule_prompt(
    rule_name: str,
    description: str,
    file_patterns: str,
    content_patterns: str,
    action_message: str,
    examples: str,
    tags: str,
    priority: str = "medium",
    template_rule: str | None = None,
    ctx: Context | None = None,
) -> list[dict[str, Any]]:
    """Prompt for generating a custom cursor rule.

    Args:
        rule_name: Name of the cursor rule (kebab-case)
        description: Description of the cursor rule
        file_patterns: File patterns to match (comma-separated)
        content_patterns: Content patterns to match (comma-separated)
        action_message: Message to display when the rule is triggered
        examples: Examples in JSON format
        tags: Tags for the rule (comma-separated)
        priority: Priority of the rule (high, medium, low)
        template_rule: Optional template rule name to base the new rule on
        ctx: The MCP context (optional)

    Returns:
        List[Dict[str, Any]]: List of messages for the prompt

    """
    # Parse inputs
    file_patterns_list = [p.strip() for p in file_patterns.split(",")]
    content_patterns_list = [p.strip() for p in content_patterns.split(",")]
    tags_list = [t.strip() for t in tags.split(",")]

    try:
        examples_list = json.loads(examples)
    except json.JSONDecodeError:
        raise ValueError("Examples must be valid JSON")

    # Generate the cursor rule
    template_content = None
    if template_rule:
        template_content = read_cursor_rule(template_rule)
        if not template_content and ctx:
            ctx.warning(f"Template rule '{template_rule}' not found, generating without template")

    # Generate the cursor rule
    generated_rule = generate_cursor_rule(
        rule_name=rule_name,
        description=description,
        file_patterns=file_patterns_list,
        content_patterns=content_patterns_list,
        action_message=action_message,
        examples=examples_list,
        tags=tags_list,
        priority=priority,
    )

    return [
        {
            "role": "user",
            "content": {
                "type": "text",
                "text": f"""I've generated a cursor rule based on your specifications:

```markdown
{generated_rule}
```

This cursor rule:
1. Matches files with patterns: {", ".join(file_patterns_list)}
2. Looks for content patterns: {", ".join(content_patterns_list)}
3. Provides suggestions when triggered
4. Includes {len(examples_list)} examples
5. Has tags: {", ".join(tags_list)}
6. Priority: {priority}

You can save this to a file named `{rule_name}.mdc.md` in your cursor rules directory.
""",
            },
        }
    ]


@mcp.tool(name="save_cursor_rule", description="Save a cursor rule to the cursor rules directory in the project")
def save_cursor_rule(
    rule_name: str = Field(
        description="The name of the cursor rule file (without extension)",
        examples=["python-best-practices", "react-component-patterns", "error-handling"],
        min_length=3,
        pattern="^[a-z0-9-]+$",
    ),
    rule_content: str = Field(
        description="The complete content of the cursor rule in mdc.md format",
        examples=[
            "# Python Best Practices\n\nWhen writing Python code, follow these guidelines:\n\n1. Use type hints\n2. Write docstrings\n3. Follow PEP 8"
        ],
        min_length=10,
    ),
) -> dict[str, Any]:
    """Save a cursor rule to the cursor rules directory.

    Args:
        rule_name: The name of the cursor rule file (without extension)
        rule_content: The complete content of the cursor rule in mdc.md format

    Returns:
        dict: Dictionary containing file operation instructions

    """
    # Define the path for the cursor rules directory
    cursor_rules_dir_path = "hack/drafts/cursor_rules"
    rule_file_path = f"{cursor_rules_dir_path}/{rule_name}.mdc.md"

    # Return operations for the client to perform
    return {
        "operations": [
            {"type": "create_directory", "path": cursor_rules_dir_path, "options": {"parents": True, "exist_ok": True}},
            {"type": "write_file", "path": rule_file_path, "content": rule_content, "options": {"mode": "w"}},
        ],
        "message": f"Instructions to save cursor rule to {rule_file_path}",
    }


@mcp.tool(
    name="recommend_cursor_rules",
    description="Analyze a repository summary and recommend cursor rules to generate based on identified technologies and patterns",
)
def recommend_cursor_rules(
    repo_summary: str = Field(
        description="A summary description of the repository, including technologies, frameworks, and key features",
        examples=[
            "A Python web application using FastAPI, SQLAlchemy, and React for the frontend. Includes authentication, API endpoints, and database models.",
            "A TypeScript library for data visualization with React components. Uses webpack for bundling and Jest for testing.",
        ],
        min_length=20,
    ),
) -> list[dict[str, str | list[str]]]:
    """Recommend cursor rules to generate based on a repository summary.

    This tool analyzes a summary of a repository and suggests cursor rules
    that would be beneficial to generate based on the technologies, patterns,
    and features identified in the repository.

    Args:
        repo_summary: A summary description of the repository, including
                     technologies, frameworks, and key features

    Returns:
        list[dict[str, Union[str, list[str]]]]: A list of recommended cursor rules, each containing
                             'name', 'description', and 'reason' fields, and potentially 'dependencies'
                             as a list of strings

    """
    # Define technology/feature patterns and corresponding rule recommendations
    rule_recommendations = {
        # Web frameworks
        "fastapi": [
            {
                "name": "fastapi-best-practices",
                "description": "Best practices for FastAPI development",
                "reason": "Repository uses FastAPI framework",
            },
            {
                "name": "fastapi-security",
                "description": "Security considerations for FastAPI applications",
                "reason": "Ensure secure API development with FastAPI",
            },
            {
                "name": "fastapi-testing",
                "description": "Testing strategies for FastAPI endpoints",
                "reason": "Help with writing comprehensive tests for FastAPI endpoints",
            },
        ],
        "flask": [
            {
                "name": "flask-best-practices",
                "description": "Best practices for Flask development",
                "reason": "Repository uses Flask framework",
            },
            {
                "name": "flask-security",
                "description": "Security considerations for Flask applications",
                "reason": "Ensure secure web application development with Flask",
            },
        ],
        "django": [
            {
                "name": "django-best-practices",
                "description": "Best practices for Django development",
                "reason": "Repository uses Django framework",
            },
            {
                "name": "django-orm",
                "description": "Effective use of Django ORM",
                "reason": "Optimize database interactions in Django applications",
            },
        ],
        # Frontend frameworks
        "react": [
            {
                "name": "react-component-patterns",
                "description": "Patterns for React component development",
                "reason": "Repository uses React framework",
            },
            {
                "name": "react-hooks",
                "description": "Best practices for React hooks",
                "reason": "Optimize React hooks usage",
            },
        ],
        "vue": [
            {
                "name": "vue-component-patterns",
                "description": "Patterns for Vue component development",
                "reason": "Repository uses Vue.js framework",
            }
        ],
        # Database technologies
        "sql": [
            {
                "name": "sql-query-optimization",
                "description": "SQL query optimization techniques",
                "reason": "Repository uses SQL database queries",
            },
            {
                "name": "sql-injection-prevention",
                "description": "Preventing SQL injection vulnerabilities",
                "reason": "Ensure secure database interactions",
            },
        ],
        "mongodb": [
            {
                "name": "mongodb-best-practices",
                "description": "Best practices for MongoDB schema design and queries",
                "reason": "Repository uses MongoDB database",
            }
        ],
        # Testing frameworks
        "pytest": [
            {
                "name": "pytest-patterns",
                "description": "Effective pytest patterns and fixtures",
                "reason": "Repository uses pytest for testing",
            }
        ],
        "jest": [
            {
                "name": "jest-testing-patterns",
                "description": "Effective Jest testing patterns",
                "reason": "Repository uses Jest for testing",
            }
        ],
        # DevOps and infrastructure
        "docker": [
            {
                "name": "dockerfile-best-practices",
                "description": "Best practices for writing Dockerfiles",
                "reason": "Repository uses Docker for containerization",
            }
        ],
        "kubernetes": [
            {
                "name": "kubernetes-configuration",
                "description": "Best practices for Kubernetes configuration",
                "reason": "Repository uses Kubernetes for orchestration",
            }
        ],
        # General software patterns
        "api": [
            {
                "name": "api-security",
                "description": "Security considerations for API development",
                "reason": "Repository implements APIs",
            },
            {
                "name": "api-documentation",
                "description": "Best practices for API documentation",
                "reason": "Improve API documentation",
            },
        ],
        "authentication": [
            {
                "name": "auth-security",
                "description": "Security best practices for authentication systems",
                "reason": "Repository implements authentication",
            }
        ],
        "microservice": [
            {
                "name": "microservice-patterns",
                "description": "Design patterns for microservice architecture",
                "reason": "Repository uses microservice architecture",
            }
        ],
        # Language-specific patterns
        "python": [
            {
                "name": "python-type-hints",
                "description": "Best practices for Python type annotations",
                "reason": "Improve type safety in Python code",
            },
            {
                "name": "python-docstrings",
                "description": "Standards for Python docstring documentation",
                "reason": "Enhance code documentation in Python",
            },
        ],
        "typescript": [
            {
                "name": "typescript-patterns",
                "description": "Effective TypeScript patterns and practices",
                "reason": "Repository uses TypeScript",
            }
        ],
        "javascript": [
            {
                "name": "javascript-best-practices",
                "description": "Modern JavaScript best practices",
                "reason": "Repository uses JavaScript",
            }
        ],
        # Data science and ML
        "machine learning": [
            {
                "name": "ml-code-organization",
                "description": "Best practices for organizing machine learning code",
                "reason": "Repository contains machine learning components",
            }
        ],
        "data science": [
            {
                "name": "data-processing-patterns",
                "description": "Patterns for effective data processing pipelines",
                "reason": "Repository contains data science components",
            }
        ],
    }

    # Always recommend these general rules
    recommended_rules = [
        {
            "name": "code-documentation",
            "description": "Standards for code documentation and comments",
            "reason": "Improve overall code documentation",
        },
        {
            "name": "error-handling",
            "description": "Best practices for error handling and logging",
            "reason": "Enhance application reliability with proper error handling",
        },
    ]

    # Convert summary to lowercase for case-insensitive matching
    summary_lower = repo_summary.lower()

    # Find matches in the repository summary
    for keyword, rules in rule_recommendations.items():
        if keyword.lower() in summary_lower:
            recommended_rules.extend(rules)

    # Remove duplicates while preserving order
    seen_names = set()
    unique_recommendations = []
    for rule in recommended_rules:
        if rule["name"] not in seen_names:
            seen_names.add(rule["name"])
            unique_recommendations.append(rule)

    return unique_recommendations


@mcp.tool(
    name="prep_workspace",
    description="Prepare the workspace for cursor rules by returning natural language instructions",
)
def prep_workspace() -> dict[str, str]:
    """Prepare the workspace for cursor rules.

    This function provides natural language instructions and commands
    for cursor rules, including directory creation and file preparation steps.
    It returns instructions relative to the current working directory without
    actually creating any directories.

    Returns:
        dict[str, str]: A dictionary containing status, instructions, and commands
        with the following keys:
        - status: "success" or "error"
        - message: Instructions or error message
        - directory_exists: Boolean indicating if directory already exists
        - directory_path: Path to the cursor rules directory
        - mkdir_command: Command to create the directory
        - directory_structure: Information about the structure to create

    Raises:
        No exceptions are raised as they are caught and returned as error messages.

    """
    try:
        # Get the current working directory
        current_dir = Path.cwd()

        # Define the cursor rules directory path
        cursor_rules_dir = current_dir / "hack" / "drafts" / "cursor_rules"

        # Check if the directory exists
        dir_exists = cursor_rules_dir.exists()

        # Prepare instructions with relative path for display
        relative_path = "./hack/drafts/cursor_rules"
        mkdir_cmd = f"mkdir -p {relative_path} .cursor/rules || true"

        instructions = {
            "status": "success",
            "message": f"""
To prepare the workspace for cursor rules, the following steps are needed:

1. Create the cursor rules directory structure, this should be relative to the repo root eg ./hack/drafts/cursor_rules:
   {mkdir_cmd}

2. Ensure the .cursor/rules directory exists for deployment:
   mkdir -p .cursor/rules
   mkdir -p ./hack/drafts/cursor_rules

3. Check if Makefile exists with an update-cursor-rules task:
   The update-cursor-rules task should copy files from hack/drafts/cursor_rules to .cursor/rules. This command updates Cursor editor rules by copying rule definitions from a drafts directory into the Cursor configuration folder. It first creates a .cursor/rules directory if it doesn't exist. Then it finds all Markdown (.md) files in the hack/drafts/cursor_rules directory (excluding any README files), copies them to the .cursor/rules directory, and preserves their filenames without the .md extension. The comment notes that Cursor doesn't support generating .mdc files directly through the Composer Agent at the time this was written


4. Update .dockerignore to exclude the cursor rules drafts directory:
   Add 'hack/drafts/cursor_rules' to .dockerignore if it exists

5. Write the following mandatory cursor rule files to the client repo's cursor rules stage directory one at a time, using the get_static_cursor_rules function to retrieve each file. when saving the file ensure the file has extension .mdc.md, eg tree.mdc becomes tree.mdc.md:
   - tree.mdc: A rule for displaying repository structure
   - repo_analyzer.mdc: A rule for analyzing repository structure and locating code definitions
   - notify.mdc: A rule for notification at the end of tasks
   - repomix.mdc: A rule for repository summarization and packaging for LLM consumption
   - cursor_rules_location.mdc: A rule for locating the cursor rules directory and how to write them

6. Update the client repo's .cursor/mcp.json file to include new entries if they don't already exist:
   Ensure the .cursor/mcp.json file contains entries for prompt_library and sequentialthinking:
   ```json
   {{
     "prompt_library": {{
       "command": "uv",
       "args": [
         "run",
         "--with",
         "mcp[cli]",
         "mcp",
         "run",
         "${{PWD}}/src/codegen_lab/prompt_library.py"
       ]
     }},
     "sequentialthinking": {{
       "command": "npx",
       "args": [
         "-y",
         "@modelcontextprotocol/server-sequential-thinking"
       ]
     }}
   }}
   ```
   Note: The path in the prompt_library entry should be adjusted to use the actual project path (PWD) instead of hardcoded paths.
""",
            "directory_exists": dir_exists,
            "directory_path": relative_path,
            "mkdir_command": mkdir_cmd,
            "directory_structure": f"Directory structure to create at {relative_path}",
            "workspace_prepared": False,  # Changed to False since we're not creating directories
            "workspace_result": {
                "status": "success",
                "message": f"Instructions provided for workspace preparation at {relative_path}",
                "directory_exists": dir_exists,
                "directory_path": relative_path,
                "mkdir_command": mkdir_cmd,
            },
        }

        return instructions

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error preparing workspace instructions: {e!s}",
            "directory_exists": False,
            "directory_path": "./hack/drafts/cursor_rules",
            "mkdir_command": "mkdir -p ./hack/drafts/cursor_rules .cursor/rules || true",
            "workspace_prepared": False,
            "workspace_result": {
                "status": "error",
                "message": f"Error preparing workspace instructions: {e!s}",
                "directory_exists": False,
                "directory_path": "./hack/drafts/cursor_rules",
                "mkdir_command": "mkdir -p ./hack/drafts/cursor_rules .cursor/rules || true",
            },
        }


@mcp.tool(
    name="create_cursor_rule_files",
    description="Create empty cursor rule files and provide instructions for sequential content creation",
)
def create_cursor_rule_files(
    rule_names: list[str] = Field(
        description="A list of cursor rule names to create (without file extensions)",
        examples=["python-best-practices", "react-component-structure", "typescript-patterns"],
        min_length=1,
    ),
) -> dict[str, Any]:
    """Create empty cursor rule files in the hack/drafts/cursor_rules directory.

    Args:
        rule_names: A list of cursor rule names to create (without file extensions)

    Returns:
        dict[str, Any]: A dictionary containing file operation instructions and next steps

    """
    try:
        # Define the cursor rules directory path
        cursor_rules_dir_path = "hack/drafts/cursor_rules"

        # Prepare operations list
        operations = [
            {"type": "create_directory", "path": cursor_rules_dir_path, "options": {"parents": True, "exist_ok": True}}
        ]

        created_files = []
        for rule_name in rule_names:
            # Ensure the rule name has the correct extension
            file_name = f"{rule_name}.mdc.md" if not rule_name.endswith(".mdc.md") else rule_name

            # Create the file path
            file_path = f"{cursor_rules_dir_path}/{file_name}"

            # Add operation to create an empty file
            operations.append(
                {
                    "type": "write_file",
                    "path": file_path,
                    "content": "",  # Empty content for now
                    "options": {"mode": "w"},
                }
            )

            created_files.append(file_name)

        # Prepare touch command for display
        touch_cmd = f"touch {' '.join([cursor_rules_dir_path + '/' + f for f in created_files])}"

        # Prepare next steps
        next_steps = """
Next steps:
1. Write content to each file sequentially
2. Deploy the rules using 'make update-cursor-rules'
3. Verify the rules are correctly deployed to .cursor/rules
"""

        return {
            "success": True,
            "operations": operations,
            "created_files": created_files,
            "touch_command": touch_cmd,
            "next_steps": next_steps,
            "message": f"Instructions to create {len(created_files)} empty cursor rule files in {cursor_rules_dir_path}. {next_steps}",
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"An error occurred: {e}",
            "next_steps": "Check the error message and try again.",
        }


@mcp.tool(
    name="ensure_makefile_task",
    description="Ensure the Makefile has the update-cursor-rules task",
)
def ensure_makefile_task(
    makefile_path: str = Field(
        description="Path to the Makefile file, relative to the project root",
        examples=["Makefile", "build/Makefile"],
        default="Makefile",
    ),
) -> dict[str, Any]:
    """Ensure the Makefile has the update-cursor-rules task.

    This function checks if the Makefile exists and contains the update-cursor-rules task.
    If the task doesn't exist, it returns instructions to add it to the Makefile.
    If the Makefile doesn't exist, it returns instructions to create one with the task.

    Args:
        makefile_path: Path to the Makefile, defaults to "Makefile"

    Returns:
        dict[str, Any]: A dictionary containing operations to perform and additional information

    """
    # Handle the case where makefile_path is a Field object
    # This is a common pattern when using FastMCP with Field decorators
    if hasattr(makefile_path, "default"):
        path_str = makefile_path.default
    else:
        path_str = makefile_path

    # Check if the makefile path is valid
    if "*" in str(path_str) or "?" in str(path_str):
        return {
            "success": False,
            "error": "Invalid file path",
            "message": "Invalid file path: wildcards are not allowed",
            "next_steps": "Please provide a valid file path without wildcards.",
        }

    # The update-cursor-rules task content
    update_task_content = """
# Cursor Rules
.PHONY: update-cursor-rules
update-cursor-rules:  ## Update cursor rules from prompts/drafts/cursor_rules
	# Create .cursor/rules directory if it doesn't exist.
	# Note: at the time of writing, cursor does not support generating .mdc files via Composer Agent.s
	mkdir -p .cursor/rules || true
	# Copy files from hack/prompts/drafts/cursor_rules to .cursor/rules and change extension to .mdc
	# Exclude README.md files from being copied
	find hack/drafts/cursor_rules -type f -name "*.md" ! -name "README.md" -exec sh -c 'for file; do target=$${file%.md}; cp -a "$$file" ".cursor/rules/$$(basename "$$target")"; done' sh {} +
"""

    # Define the operations to check if Makefile exists and contains the task
    operations = [
        {"type": "check_file_exists", "path": path_str},
        {"type": "read_file", "path": path_str, "options": {"encoding": "utf-8"}},
    ]

    # Return operations with instructions for the client
    return {
        "operations": operations,
        "requires_result": True,
        "message": "Instructions to check Makefile and update if needed",
        "update_task_content": update_task_content,
        "next_steps": "After applying these operations, you'll need to check if the Makefile exists and contains the update-cursor-rules task, then update or create it accordingly.",
    }


@mcp.tool(
    name="process_makefile_result",
    description="Process the results of checking the Makefile and update it if needed",
)
def process_makefile_result(
    operation_results: dict[str, Any] = Field(description="Results from the file operations"),
    update_task_content: str = Field(description="The update-cursor-rules task content"),
) -> dict[str, Any]:
    """Process the results of checking the Makefile and update it if needed.

    Args:
        operation_results: Results from the file operations
        update_task_content: The update-cursor-rules task content

    Returns:
        dict[str, Any]: A dictionary containing operations to perform and additional information

    """
    # Check for empty operation results
    if not operation_results:
        return {
            "success": False,
            "error": "Missing operation results",
            "message": "Missing operation results",
            "next_steps": "Please ensure the file operations were executed correctly.",
        }

    # Check for malformed operation results
    if not isinstance(operation_results, dict):
        return {
            "success": False,
            "error": "Invalid operation results",
            "message": "Invalid operation results format",
            "next_steps": "Please ensure the operation results are in the correct format.",
        }

    makefile_result = operation_results.get("Makefile", {})
    if not isinstance(makefile_result, dict):
        return {
            "success": False,
            "error": "Invalid operation results",
            "message": "Invalid operation results format",
            "next_steps": "Please ensure the operation results are in the correct format.",
        }

    # Check for required fields in Makefile result
    if "exists" not in makefile_result:
        return {
            "success": False,
            "error": "Invalid operation results",
            "message": "Invalid operation results format: missing required field 'exists'",
            "next_steps": "Please ensure the operation results contain all required fields.",
        }

    # Extract results
    makefile_exists = makefile_result.get("exists", False)
    makefile_content = ""
    if makefile_exists:
        if "error" in makefile_result:
            return {
                "success": False,
                "error": makefile_result["error"],
                "message": f"Error accessing Makefile: {makefile_result['error']}",
                "next_steps": "Please check file permissions and try again.",
            }
        if "content" not in makefile_result:
            return {
                "success": False,
                "error": "Invalid operation results",
                "message": "Invalid operation results format: missing required field 'content'",
                "next_steps": "Please ensure the operation results contain all required fields.",
            }
        makefile_content = makefile_result.get("content", "")
    elif "error" in makefile_result:
        # Handle permission denied or other errors
        error = makefile_result["error"]
        return {
            "success": False,
            "error": error,
            "message": f"Error accessing Makefile: {error}",
            "next_steps": "Please check file permissions and try again.",
        }

    # Check if the update-cursor-rules task exists
    has_update_task = "update-cursor-rules" in makefile_content
    action_taken = "none"
    operations = []

    if makefile_exists:
        if not has_update_task:
            # Add the update-cursor-rules task to the Makefile
            operations.append(
                {
                    "type": "write_file",
                    "path": "Makefile",
                    "content": makefile_content + update_task_content,
                    "options": {"mode": "w"},
                }
            )
            action_taken = "updated"
            has_update_task = True  # Set to True after adding the task
    else:
        # Create a new Makefile with the update-cursor-rules task
        operations.append(
            {"type": "write_file", "path": "Makefile", "content": update_task_content, "options": {"mode": "w"}}
        )
        action_taken = "created"
        makefile_exists = True
        has_update_task = True

    # Prepare next steps and message
    if action_taken == "none":
        message = "The Makefile already contains the update-cursor-rules task."
    elif action_taken == "updated":
        message = "Instructions to add the update-cursor-rules task to the existing Makefile."
    else:
        message = "Instructions to create a new Makefile with the update-cursor-rules task."

    return {
        "operations": operations,
        "success": True,
        "has_makefile": makefile_exists,
        "has_update_task": has_update_task,
        "action_taken": action_taken,
        "message": message,
        "next_steps": "Run 'make update-cursor-rules' to deploy the cursor rules.",
    }


@mcp.tool(
    name="run_update_cursor_rules",
    description="Run the update-cursor-rules Makefile task to deploy cursor rules",
)
def run_update_cursor_rules() -> dict[str, Any]:
    """Run the update-cursor-rules Makefile task to deploy cursor rules.

    This function returns instructions to execute the update-cursor-rules Makefile task
    to deploy cursor rules from hack/drafts/cursor_rules to .cursor/rules.

    Returns:
        dict[str, Any]: A dictionary containing operations to perform and additional information

    """
    # Define the operations to check if Makefile exists and contains the task
    operations = [
        {"type": "check_file_exists", "path": "Makefile"},
        {"type": "read_file", "path": "Makefile", "options": {"encoding": "utf-8"}},
    ]

    # Return operations with instructions for the client
    return {
        "operations": operations,
        "requires_result": True,
        "message": "Instructions to check Makefile before running update-cursor-rules task",
    }


@mcp.tool(
    name="process_update_cursor_rules_result",
    description="Process the results of checking the Makefile and run the update-cursor-rules task if possible",
)
def process_update_cursor_rules_result(
    operation_results: dict[str, Any] = Field(description="Results from the file operations"),
) -> dict[str, Any]:
    """Process the results of checking the Makefile and run the update-cursor-rules task if possible.

    Args:
        operation_results: Results from the file operations

    Returns:
        dict[str, Any]: A dictionary containing operations to perform and additional information

    """
    # Extract results
    makefile_exists = operation_results.get("Makefile", {}).get("exists", False)
    makefile_content = ""
    if makefile_exists and "Makefile" in operation_results:
        makefile_content = operation_results.get("Makefile", {}).get("content", "")

    # Check if the update-cursor-rules task exists
    has_update_task = "update-cursor-rules" in makefile_content

    if not makefile_exists:
        return {
            "isError": True,
            "content": [
                {
                    "type": "text",
                    "text": "Error: Makefile not found. Please create a Makefile with the update-cursor-rules task.",
                }
            ],
            "message": "Makefile not found",
            "next_steps": "Use the ensure_makefile_task tool to create the Makefile.",
        }

    if not has_update_task:
        return {
            "isError": True,
            "content": [{"type": "text", "text": "Error: The update-cursor-rules task was not found in the Makefile."}],
            "message": "update-cursor-rules task not found",
            "next_steps": "Use the ensure_makefile_task tool to add the update-cursor-rules task to the Makefile.",
        }

    # Return operation to execute the make command
    return {
        "operations": [
            {"type": "execute_command", "command": "make update-cursor-rules", "options": {"cwd": "."}},
            {"type": "check_file_exists", "path": ".cursor/rules"},
        ],
        "requires_result": True,
        "message": "Instructions to run the update-cursor-rules task and check the results",
    }


@mcp.tool(
    name="finalize_update_cursor_rules",
    description="Process the results of running the update-cursor-rules task",
)
def finalize_update_cursor_rules(
    operation_results: dict[str, Any] = Field(description="Results from the command execution"),
) -> dict[str, Any]:
    """Process the results of running the update-cursor-rules task.

    Args:
        operation_results: Results from the command execution

    Returns:
        dict[str, Any]: A dictionary containing the results

    """
    # Check if the command was executed successfully
    command_result = operation_results.get("make update-cursor-rules", {})
    cursor_rules_dir_exists = operation_results.get(".cursor/rules", {}).get("exists", False)

    if "error" in command_result:
        return {
            "isError": True,
            "content": [
                {
                    "type": "text",
                    "text": f"Error: Failed to run the update-cursor-rules task: {command_result.get('error')}",
                }
            ],
            "message": "Failed to run the update-cursor-rules task",
            "next_steps": "Check the Makefile and try again.",
        }

    # Return success message
    return {
        "success": True,
        "cursor_rules_dir_exists": cursor_rules_dir_exists,
        "message": "Successfully deployed cursor rules.",
        "next_steps": "The cursor rules have been deployed to .cursor/rules.",
    }


@mcp.tool(
    name="update_dockerignore",
    description="Update the .dockerignore file to exclude the cursor rules drafts directory",
)
def update_dockerignore() -> dict[str, Any]:
    """Update the .dockerignore file to exclude the cursor rules drafts directory.

    This function returns instructions to check if the .dockerignore file exists and add an entry
    to exclude the cursor rules drafts directory if it doesn't already exist.

    Returns:
        dict[str, Any]: A dictionary containing operations to perform and additional information

    """
    # The entry to add to .dockerignore
    entry = "hack/drafts/cursor_rules"

    # Define the operations to check if .dockerignore exists and read its content
    operations = [
        {"type": "check_file_exists", "path": ".dockerignore"},
        {"type": "read_file", "path": ".dockerignore", "options": {"encoding": "utf-8"}},
    ]

    # Return operations with instructions for the client
    return {
        "operations": operations,
        "requires_result": True,
        "message": "Instructions to check .dockerignore file",
        "entry": entry,
    }


@mcp.tool(
    name="process_dockerignore_result",
    description="Process the results of checking the .dockerignore file and update it if needed",
)
def process_dockerignore_result(
    operation_results: dict[str, Any] = Field(description="Results from the file operations"),
    entry: str = Field(description="The entry to add to .dockerignore"),
) -> dict[str, Any]:
    """Process the results of checking the .dockerignore file and update it if needed.

    Args:
        operation_results: Results from the file operations
        entry: The entry to add to .dockerignore

    Returns:
        dict[str, Any]: A dictionary containing operations to perform and additional information

    """
    # Extract results
    dockerignore_exists = operation_results.get(".dockerignore", {}).get("exists", False)
    dockerignore_content = ""
    if dockerignore_exists and ".dockerignore" in operation_results:
        dockerignore_content = operation_results.get(".dockerignore", {}).get("content", "")

    # Check if the entry already exists
    entry_exists = entry in dockerignore_content.split("\n") if dockerignore_content else False
    action_taken = "none"
    operations = []

    if dockerignore_exists:
        if not entry_exists:
            # Ensure the file ends with a newline
            if not dockerignore_content.endswith("\n"):
                dockerignore_content += "\n"

            # Add the new entry
            updated_content = dockerignore_content + f"{entry}\n"

            operations.append(
                {"type": "write_file", "path": ".dockerignore", "content": updated_content, "options": {"mode": "w"}}
            )

            action_taken = "updated"
    else:
        # Create a new .dockerignore file with the entry
        operations.append(
            {"type": "write_file", "path": ".dockerignore", "content": f"{entry}\n", "options": {"mode": "w"}}
        )

        action_taken = "created"
        dockerignore_exists = True
        entry_exists = True

    # Prepare message
    if action_taken == "none":
        message = "The .dockerignore file already contains an entry for the cursor rules drafts directory."
    elif action_taken == "updated":
        message = (
            "Instructions to add an entry for the cursor rules drafts directory to the existing .dockerignore file."
        )
    else:
        message = "Instructions to create a new .dockerignore file with an entry for the cursor rules drafts directory."

    return {
        "operations": operations,
        "success": True,
        "has_dockerignore": dockerignore_exists,
        "entry_exists": entry_exists,
        "action_taken": action_taken,
        "message": message,
    }


@mcp.tool(
    name="cursor_rules_workflow",
    description="Execute the complete cursor rules workflow",
)
def cursor_rules_workflow(
    rule_names: list[str] = Field(
        description="A list of cursor rule names to create (without file extensions)",
        examples=["python-best-practices", "react-component-structure", "typescript-patterns"],
    ),
) -> dict[str, Any]:
    """Execute the complete cursor rules workflow.

    Args:
        rule_names: A list of cursor rule names to create (without file extensions)

    Returns:
        dict[str, Any]: A dictionary containing operations to perform and additional information

    """
    # First call prep_workspace directly
    workspace_result = prep_workspace()

    # Call create_cursor_rule_files directly
    files_result = create_cursor_rule_files(rule_names)

    # Call ensure_makefile_task directly
    makefile_result = ensure_makefile_task()

    # Call update_dockerignore directly
    dockerignore_result = update_dockerignore()

    # Prepare next steps message
    next_steps = """
Workflow completed successfully. Next steps:

1. Write content to each cursor rule file sequentially:
   - Edit each file to add the cursor rule content
   - Save each file after editing

2. Deploy the cursor rules:
   - Run 'make update-cursor-rules' to deploy the cursor rules to .cursor/rules
   - Verify the rules are correctly deployed

3. Test the cursor rules:
   - Open a file that should trigger a cursor rule
   - Verify that the cursor rule is applied correctly
"""

    return {
        "success": True,
        "message": f"Instructions to execute the cursor rules workflow for {len(rule_names)} rule(s): {', '.join(rule_names)}",
        "next_steps": next_steps,
        "workspace_result": workspace_result,
        "files_result": files_result,
        "makefile_result": makefile_result,
        "dockerignore_result": dockerignore_result,
        "created_files": files_result.get("created_files", []),
    }


@mcp.tool(
    name="process_cursor_rules_workflow_result",
    description="Process the results of executing the cursor rules workflow",
)
def process_cursor_rules_workflow_result(
    operation_results: dict[str, Any] = Field(description="Results from the workflow operations"),
) -> dict[str, Any]:
    """Process the results of executing the cursor rules workflow.

    Args:
        operation_results: Results from the workflow operations

    Returns:
        dict[str, Any]: A dictionary containing the workflow results and next steps

    """
    # Extract results from each operation
    workspace_result = operation_results.get("workspace_result", {})
    files_result = operation_results.get("files_result", {})
    makefile_result = operation_results.get("makefile_result", {})
    dockerignore_result = operation_results.get("dockerignore_result", {})

    # Check if all operations were successful
    all_successful = (
        workspace_result.get("success", False)
        and files_result.get("success", False)
        and makefile_result.get("success", False)
        and dockerignore_result.get("success", False)
    )

    # Get the list of created files
    created_files = files_result.get("created_files", [])

    # Prepare next steps
    next_steps = """
Workflow completed successfully. Next steps:

1. Write content to each cursor rule file sequentially:
   - Edit each file to add the cursor rule content
   - Save each file after editing

2. Deploy the cursor rules:
   - Run 'make update-cursor-rules' to deploy the cursor rules to .cursor/rules
   - Verify the rules are correctly deployed

3. Test the cursor rules:
   - Open a file that should trigger a cursor rule
   - Verify that the cursor rule is applied correctly
"""

    return {
        "success": all_successful,
        "workspace_result": workspace_result,
        "files_result": files_result,
        "makefile_result": makefile_result,
        "dockerignore_result": dockerignore_result,
        "created_files": created_files,
        "message": f"Cursor rules workflow completed successfully. Created {len(created_files)} empty cursor rule files.",
        "next_steps": next_steps,
    }


@mcp.tool(
    name="plan_and_execute_prompt_library_workflow",
    description="Execute a structured workflow for generating custom cursor rules based on repository analysis",
)
def plan_and_execute_prompt_library_workflow(
    repo_description: str = Field(description="Brief description of the repository's purpose and functionality"),
    main_languages: str = Field(description="Main programming languages used in the repository (comma-separated)"),
    file_patterns: str = Field(description="Common file patterns/extensions in the repository (comma-separated)"),
    key_features: str = Field(description="Key features or functionality of the repository (comma-separated)"),
    client_repo_root: str = Field(description="Absolute path to the client's repository root directory", default=""),
    phase: int = Field(description="Current phase of the workflow (1-5)", default=1),
    workflow_state: dict[str, Any] = Field(
        description="Current state of the workflow for continuing execution", default=None
    ),
) -> dict[str, Any]:
    """Execute a structured workflow for generating custom cursor rules based on repository analysis.

    This tool facilitates a structured, phase-based workflow for analyzing a repository and
    generating custom cursor rules tailored to its specific technologies and patterns.

    The workflow consists of five phases:
    1. Repository Analysis: Analyze the repository to identify technologies, patterns, and features
    2. Rule Identification: Recommend cursor rules based on the analysis
    3. Workspace Preparation: Set up the necessary directory structure
    4. Rule Creation: Generate the content for each cursor rule
    5. Deployment and Testing: Deploy the cursor rules and verify functionality

    Args:
        repo_description: Brief description of the repository's purpose and functionality
        main_languages: Main programming languages used in the repository (comma-separated)
        file_patterns: Common file patterns/extensions in the repository (comma-separated)
        key_features: Key features or functionality of the repository (comma-separated)
        client_repo_root: Absolute path to the client's repository root directory
        phase: Current phase of the workflow (1-5)
        workflow_state: Current state of the workflow for continuing execution

    Returns:
        dict[str, Any]: Status of the workflow, next steps, and any generated content

    """
    # Initialize workflow_state if it's None or not a dictionary
    actual_workflow_state = {} if workflow_state is None or not isinstance(workflow_state, dict) else workflow_state

    # If no workflow_state is provided, initialize it with the input parameters
    if not actual_workflow_state:
        # Initialize repository information
        actual_workflow_state = {
            "repository_info": {
                "description": repo_description,
                "main_languages": main_languages.split(","),
                "file_patterns": file_patterns.split(","),
                "key_features": key_features.split(","),
                "repo_root": client_repo_root,
            },
            "recommended_rules": [],
            "created_rules": [],
            "deployed_rules": [],
            "workspace_prepared": True,  # Mark workspace as prepared
            "workspace_result": prep_workspace(),  # Store workspace preparation result
        }

    # Execute the current phase
    if phase == 1:
        # Phase 1: Repository Analysis
        return execute_phase_1(actual_workflow_state)
    elif phase == 2:
        # Phase 2: Rule Identification
        return execute_phase_2(actual_workflow_state)
    elif phase == 3:
        # Phase 3: Workspace Preparation
        return execute_phase_3(actual_workflow_state)
    elif phase == 4:
        # Phase 4: Rule Creation
        return execute_phase_4(actual_workflow_state)
    elif phase == 5:
        # Phase 5: Deployment and Testing
        return execute_phase_5(actual_workflow_state)
    else:
        return {"status": "error", "message": f"Invalid phase: {phase}. Valid phases are 1-5."}


def execute_phase_1(workflow_state: dict[str, Any]) -> dict[str, Any]:
    """Execute Phase 1: Repository Analysis.

    Args:
        workflow_state: Current state of the workflow for continuing execution

    Returns:
        dict[str, Any]: Updated workflow state and next steps

    """
    # Initialize workflow_state as an empty dict if it's None or not a dictionary
    if workflow_state is None or not isinstance(workflow_state, dict):
        workflow_state = {}

    # First, ensure workspace is prepared before any analysis
    if not workflow_state.get("workspace_prepared", False):
        # Prepare the workspace
        workspace_result = prep_workspace()
        workflow_state["workspace_prepared"] = True
        workflow_state["workspace_result"] = workspace_result

        # If workspace preparation failed, return error
        if workspace_result.get("status") == "error":
            return {
                "status": "error",
                "message": f"Error preparing workspace: {workspace_result.get('message')}",
                "workflow_state": workflow_state,
            }

    # If Phase 1 is already complete, return the state and suggest moving to Phase 2
    if workflow_state.get("phase_1_complete", False):
        return {
            "status": "already_complete",
            "message": "Phase 1 (Repository Analysis) is already complete. Proceed to Phase 2.",
            "workflow_state": workflow_state,
            "next_phase": 2,
        }

    # Extract repository information
    repo_info = workflow_state.get("repository_info", {})

    # Perform repository analysis using repo_analysis_prompt
    try:
        # Call the repo_analysis_prompt function to get recommendations
        analysis_results = repo_analysis_prompt(
            repo_description=repo_info.get("description", ""),
            main_languages=repo_info.get("main_languages", ""),
            file_patterns=repo_info.get("file_patterns", ""),
            key_features=repo_info.get("key_features", ""),
        )

        # Process and structure the analysis results
        structured_analysis = {
            "repository_type": analysis_results[0]["content"][0]["text"],
            "common_patterns": analysis_results[1]["content"][0]["text"],
            "recommended_rules": [],
            "analysis_summary": analysis_results[3]["content"][0]["text"] if len(analysis_results) > 3 else "",
        }

        # Extract recommended rules from the analysis
        if len(analysis_results) > 2:
            rule_suggestions = analysis_results[2]["content"][0]["text"].split("\n")
            for rule in rule_suggestions:
                if rule.strip():
                    structured_analysis["recommended_rules"].append(rule.strip())

        # Update the workflow state
        workflow_state["analysis_results"] = structured_analysis
        workflow_state["phase_1_complete"] = True

        # Create a checklist for phase 1 completion
        checklist = [
            {"item": "Workspace prepared", "complete": True},
            {"item": "Repository information gathered", "complete": True},
            {"item": "Repository structure analyzed", "complete": True},
            {"item": "Common patterns identified", "complete": len(structured_analysis["common_patterns"]) > 0},
            {"item": "Primary purpose determined", "complete": len(structured_analysis["repository_type"]) > 0},
            {"item": "Recommended rules identified", "complete": len(structured_analysis["recommended_rules"]) > 0},
        ]

        return {
            "status": "complete",
            "message": "Phase 1 (Repository Analysis) completed successfully.",
            "checklist": checklist,
            "analysis_results": structured_analysis,
            "workflow_state": workflow_state,
            "next_phase": 2,
            "next_steps": "Proceed to Phase 2: Rule Identification to select and prioritize cursor rules.",
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error during repository analysis: {e!s}",
            "workflow_state": workflow_state,
        }


def execute_phase_2(workflow_state: dict[str, Any]) -> dict[str, Any]:
    """Execute Phase 2: Rule Identification.

    Args:
        workflow_state: Current state of the workflow

    Returns:
        dict[str, Any]: Updated workflow state and next steps

    """
    # If Phase 2 is already complete, return the state and suggest moving to Phase 3
    if workflow_state.get("phase_2_complete", False):
        return {
            "status": "already_complete",
            "message": "Phase 2 (Rule Identification) is already complete. Proceed to Phase 3.",
            "workflow_state": workflow_state,
            "next_phase": 3,
        }

    # Check if Phase 1 is complete
    if not workflow_state.get("phase_1_complete", False):
        return {
            "status": "prerequisite_not_met",
            "message": "Phase 1 (Repository Analysis) must be completed before proceeding to Phase 2.",
            "workflow_state": workflow_state,
            "next_phase": 1,
        }

    # Extract analysis results from Phase 1
    analysis_results = workflow_state.get("analysis_results", {})
    repo_info = workflow_state.get("repository_info", {})

    # Create a repository summary for recommendation
    repo_summary = f"""
Repository Description: {repo_info.get("description", "")}
Main Languages: {repo_info.get("main_languages", "")}
File Patterns: {repo_info.get("file_patterns", "")}
Key Features: {repo_info.get("key_features", "")}
Repository Type: {analysis_results.get("repository_type", "")}
Common Patterns: {analysis_results.get("common_patterns", "")}
"""

    try:
        # Call the recommend_cursor_rules function to get rule recommendations
        recommended_rules = recommend_cursor_rules(repo_summary)

        # Group and categorize rules
        categorized_rules = {}
        for rule in recommended_rules:
            category = rule.get("category", "General")
            if category not in categorized_rules:
                categorized_rules[category] = []
            categorized_rules[category].append(rule)

        # Prioritize rules based on value and relevance
        prioritized_rules = []
        for rule in recommended_rules:
            # Add priority field if not present
            if "priority" not in rule:
                # Set default priority based on category
                category = rule.get("category", "General")
                if category in ["Formatting", "Style"]:
                    priority = "medium"
                elif category in ["Testing", "Documentation"]:
                    priority = "high"
                else:
                    priority = "medium"
                rule["priority"] = priority

            # Add to prioritized list
            prioritized_rules.append(rule)

        # Sort rules by priority
        prioritized_rules.sort(key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x.get("priority", "medium"), 1))

        # Filter out redundant or low-value rules
        filtered_rules = []
        rule_names_seen = set()
        for rule in prioritized_rules:
            rule_name = rule.get("name", "")
            # Skip rules we've already seen or with empty names
            if not rule_name or rule_name in rule_names_seen:
                continue
            rule_names_seen.add(rule_name)
            filtered_rules.append(rule)

        # Identify dependencies between rules
        # Simple dependency identification based on categories
        for rule in filtered_rules:
            dependencies = []
            rule_category = rule.get("category", "")
            rule_name = rule.get("name", "")

            # Documentation rules might depend on style rules
            if rule_category == "Documentation":
                for other_rule in filtered_rules:
                    if other_rule.get("category", "") == "Style" and other_rule.get("name", "") != rule_name:
                        dependencies.append(other_rule.get("name", ""))

            # Add the dependencies to the rule
            rule["dependencies"] = dependencies  # type: ignore

        # Update the workflow state
        workflow_state["recommended_rules"] = filtered_rules
        workflow_state["categorized_rules"] = categorized_rules
        workflow_state["selected_rules"] = filtered_rules  # Default to selecting all filtered rules
        workflow_state["phase_2_complete"] = True

        # Create a checklist for phase 2 completion
        checklist = [
            {"item": "Generated potential cursor rules", "complete": len(recommended_rules) > 0},
            {"item": "Prioritized rules by impact and relevance", "complete": len(prioritized_rules) > 0},
            {"item": "Filtered out redundant rules", "complete": len(filtered_rules) < len(recommended_rules)},
            {"item": "Grouped rules into categories", "complete": len(categorized_rules) > 0},
            {
                "item": "Identified dependencies between rules",
                "complete": any(len(rule.get("dependencies", [])) > 0 for rule in filtered_rules),
            },
        ]

        return {
            "status": "complete",
            "message": "Phase 2 (Rule Identification) completed successfully.",
            "checklist": checklist,
            "recommended_rules": filtered_rules,
            "categorized_rules": categorized_rules,
            "total_rules": len(filtered_rules),
            "workflow_state": workflow_state,
            "next_phase": 3,
            "next_steps": "Proceed to Phase 3: Workspace Preparation to set up your environment for cursor rule creation.",
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error during rule identification: {e!s}",
            "workflow_state": workflow_state,
        }


def execute_phase_3(workflow_state: dict[str, Any]) -> dict[str, Any]:
    """Execute Phase 3: Workspace Preparation.

    Args:
        workflow_state: Current state of the workflow

    Returns:
        dict[str, Any]: Updated workflow state and next steps

    """
    # If Phase 3 is already complete, return the state and suggest moving to Phase 4
    if workflow_state.get("phase_3_complete", False):
        return {
            "status": "already_complete",
            "message": "Phase 3 (Workspace Preparation) is already complete. Proceed to Phase 4.",
            "workflow_state": workflow_state,
            "next_phase": 4,
        }

    # Check if Phase 2 is complete
    if not workflow_state.get("phase_2_complete", False):
        return {
            "status": "prerequisite_not_met",
            "message": "Phase 2 (Rule Identification) must be completed before proceeding to Phase 3.",
            "workflow_state": workflow_state,
            "next_phase": 2,
        }

    # Extract rule information from Phase 2
    selected_rules = workflow_state.get("selected_rules", [])

    # Get rule names from the selected rules
    rule_names = [rule.get("name", f"rule_{i}") for i, rule in enumerate(selected_rules)]

    # Ensure rule names are valid and unique
    valid_rule_names = []
    seen_names = set()
    for name in rule_names:
        # Create a valid filename from the rule name
        valid_name = name.lower().replace(" ", "_").replace("-", "_")

        # Ensure uniqueness by adding a suffix if needed
        if valid_name in seen_names:
            suffix = 1
            while f"{valid_name}_{suffix}" in seen_names:
                suffix += 1
            valid_name = f"{valid_name}_{suffix}"

        seen_names.add(valid_name)
        valid_rule_names.append(valid_name)

    try:
        # Get the workspace result from the initial preparation
        workspace_result = workflow_state.get("workspace_result", {})
        if not workspace_result:
            return {
                "status": "error",
                "message": "Workspace preparation result not found in workflow state.",
                "workflow_state": workflow_state,
            }

        # Step 2: Ensure the Makefile has the update-cursor-rules task
        makefile_result = ensure_makefile_task()

        # Step 3: Update .dockerignore to exclude drafts directory
        dockerignore_result = update_dockerignore()

        # Step 4: Create empty files for each planned cursor rule
        files_result = create_cursor_rule_files(valid_rule_names)

        # Check if any of the operations failed
        if makefile_result.get("status") == "error":
            return {
                "status": "error",
                "message": f"Error ensuring Makefile task: {makefile_result.get('message')}",
                "workflow_state": workflow_state,
            }

        if dockerignore_result.get("status") == "error":
            return {
                "status": "error",
                "message": f"Error updating .dockerignore: {dockerignore_result.get('message')}",
                "workflow_state": workflow_state,
            }

        if files_result.get("status") == "error":
            return {
                "status": "error",
                "message": f"Error creating cursor rule files: {files_result.get('message')}",
                "workflow_state": workflow_state,
            }

        # Update the workflow state
        workflow_state["phase_3_complete"] = True
        workflow_state["rule_file_names"] = valid_rule_names
        workflow_state["workspace_prepared"] = True

        # Map rule metadata to file names
        rule_file_mapping = {}
        for i, rule_name in enumerate(valid_rule_names):
            if i < len(selected_rules):
                rule_file_mapping[rule_name] = selected_rules[i]

        workflow_state["rule_file_mapping"] = rule_file_mapping

        # Create a checklist for phase 3 completion
        checklist = [
            {
                "item": "Created cursor rules directory structure",
                "complete": True,  # Already completed in initial preparation
            },
            {
                "item": "Ensured Makefile has update-cursor-rules task",
                "complete": makefile_result.get("status") == "success",
            },
            {"item": "Updated .dockerignore", "complete": dockerignore_result.get("status") == "success"},
            {"item": "Prepared empty files for cursor rules", "complete": files_result.get("status") == "success"},
        ]

        return {
            "status": "complete",
            "message": "Phase 3 (Workspace Preparation) completed successfully.",
            "checklist": checklist,
            "rule_files": valid_rule_names,
            "directory_structure": workspace_result.get("directory_structure", ""),
            "workflow_state": workflow_state,
            "next_phase": 4,
            "next_steps": "Proceed to Phase 4: Rule Creation to implement each cursor rule.",
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error during workspace preparation: {e!s}",
            "workflow_state": workflow_state,
        }


def execute_phase_4(workflow_state: dict[str, Any]) -> dict[str, Any]:
    """Execute Phase 4: Rule Creation.

    Args:
        workflow_state: Current state of the workflow

    Returns:
        dict[str, Any]: Updated workflow state and next steps

    """
    # If Phase 4 is already complete, return the state and suggest moving to Phase 5
    if workflow_state.get("phase_4_complete", False):
        return {
            "status": "already_complete",
            "message": "Phase 4 (Rule Creation) is already complete. Proceed to Phase 5.",
            "workflow_state": workflow_state,
            "next_phase": 5,
        }

    # Check if Phase 3 is complete
    if not workflow_state.get("phase_3_complete", False):
        return {
            "status": "prerequisite_not_met",
            "message": "Phase 3 (Workspace Preparation) must be completed before proceeding to Phase 4.",
            "workflow_state": workflow_state,
            "next_phase": 3,
        }

    # Extract rule information from previous phases
    rule_file_names = workflow_state.get("rule_file_names", [])
    rule_file_mapping = workflow_state.get("rule_file_mapping", {})

    if not rule_file_names:
        return {
            "status": "error",
            "message": "No rule files found. Please complete Phase 3 properly.",
            "workflow_state": workflow_state,
            "next_phase": 3,
        }

    try:
        # Track created rules and any errors
        created_rules = []
        creation_errors = []

        # Process each rule file
        for rule_name in rule_file_names:
            try:
                # Get rule metadata from mapping
                rule_metadata = rule_file_mapping.get(rule_name, {})

                # Extract or generate rule components
                rule_description = rule_metadata.get("description", f"Rule for {rule_name}")

                # Determine file patterns to match
                file_patterns = rule_metadata.get("file_patterns", [])
                if not file_patterns and "category" in rule_metadata:
                    # Generate default patterns based on category
                    category = rule_metadata.get("category", "")
                    if category == "Python":
                        file_patterns = ["*.py"]
                    elif category == "JavaScript":
                        file_patterns = ["*.js", "*.jsx", "*.ts", "*.tsx"]
                    elif category == "Documentation":
                        file_patterns = ["*.md", "README*", "CONTRIBUTING*"]
                    else:
                        file_patterns = ["*"]

                # Convert file patterns to string if needed
                if isinstance(file_patterns, list):
                    file_patterns_str = ", ".join(file_patterns)
                else:
                    file_patterns_str = str(file_patterns)

                # Determine content patterns to match
                content_patterns = rule_metadata.get("content_patterns", [])
                if not content_patterns and "category" in rule_metadata:
                    # Generate default patterns based on category
                    category = rule_metadata.get("category", "")
                    if category == "Python":
                        content_patterns = ["def ", "class ", "import "]
                    elif category == "JavaScript":
                        content_patterns = ["function", "const", "import"]
                    elif category == "Documentation":
                        content_patterns = ["#", "##", "```"]
                    else:
                        content_patterns = []

                # Convert content patterns to string if needed
                if isinstance(content_patterns, list):
                    content_patterns_str = ", ".join(content_patterns)
                else:
                    content_patterns_str = str(content_patterns)

                # Create action message
                action_message = rule_metadata.get("action_message", f"Guidance for {rule_name}")

                # Create examples
                examples_str = rule_metadata.get("examples", "")
                if not examples_str:
                    # Generate a simple example
                    examples_str = """
                    # Example input
                    Sample input for the rule

                    # Example output
                    Expected output or behavior
                    """

                # Determine tags
                tags = rule_metadata.get("tags", [])
                if not tags and "category" in rule_metadata:
                    tags = [rule_metadata.get("category", "").lower()]

                # Convert tags to string if needed
                if isinstance(tags, list):
                    tags_str = ", ".join(tags)
                else:
                    tags_str = str(tags)

                # Determine priority
                priority = rule_metadata.get("priority", "medium")

                # Generate the cursor rule content
                rule_content = generate_cursor_rule(
                    rule_name=rule_name,
                    description=rule_description,
                    file_patterns=file_patterns_str,
                    content_patterns=content_patterns_str,
                    action_message=action_message,
                    examples=[{"input": "Example input", "output": "Example output"}],
                    tags=tags if isinstance(tags, list) else tags_str.split(","),
                    priority=priority,
                )

                # Save the rule to the cursor rules directory
                save_result = save_cursor_rule(rule_name=f"{rule_name}.mdc", rule_content=rule_content)

                if "error" in save_result:
                    creation_errors.append(
                        {"rule_name": rule_name, "error": save_result.get("error", "Unknown error saving rule")}
                    )
                else:
                    created_rules.append(
                        {"rule_name": rule_name, "file_path": save_result.get("file_path", ""), "status": "created"}
                    )

            except Exception as e:
                creation_errors.append({"rule_name": rule_name, "error": str(e)})

        # Update the workflow state
        workflow_state["created_rules"] = created_rules
        workflow_state["creation_errors"] = creation_errors
        workflow_state["phase_4_complete"] = len(created_rules) > 0

        # Create a checklist for phase 4 completion
        checklist = [
            {"item": "Defined rule names and descriptions", "complete": True},
            {"item": "Specified file patterns to match", "complete": True},
            {"item": "Defined content patterns to match", "complete": True},
            {"item": "Crafted action messages with guidance", "complete": True},
            {"item": "Created example input/output pairs", "complete": True},
            {"item": "Added appropriate tags and metadata", "complete": True},
            {"item": "Saved rules to cursor rules directory", "complete": len(created_rules) > 0},
        ]

        # Determine status based on results
        if len(created_rules) == 0:
            status = "error"
            message = "Failed to create any cursor rules."
        elif len(creation_errors) > 0:
            status = "partial"
            message = f"Created {len(created_rules)} cursor rules with {len(creation_errors)} errors."
        else:
            status = "complete"
            message = f"Phase 4 (Rule Creation) completed successfully. Created {len(created_rules)} cursor rules."

        return {
            "status": status,
            "message": message,
            "checklist": checklist,
            "created_rules": created_rules,
            "creation_errors": creation_errors,
            "total_created": len(created_rules),
            "total_errors": len(creation_errors),
            "workflow_state": workflow_state,
            "next_phase": 5,
            "next_steps": "Proceed to Phase 5: Deployment and Testing to deploy and test your cursor rules.",
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error during rule creation: {e!s}",
            "workflow_state": workflow_state,
        }


def execute_phase_5(workflow_state: dict[str, Any]) -> dict[str, Any]:
    """Execute Phase 5: Deployment and Testing.

    Args:
        workflow_state: Current state of the workflow

    Returns:
        dict[str, Any]: Updated workflow state and next steps

    """
    # If Phase 5 is already complete, return the state
    if workflow_state.get("phase_5_complete", False):
        return {
            "status": "already_complete",
            "message": "Phase 5 (Deployment and Testing) is already complete. The workflow is finished.",
            "workflow_state": workflow_state,
            "next_phase": None,
        }

    # Check if Phase 4 is complete
    if not workflow_state.get("phase_4_complete", False):
        return {
            "status": "prerequisite_not_met",
            "message": "Phase 4 (Rule Creation) must be completed before proceeding to Phase 5.",
            "workflow_state": workflow_state,
            "next_phase": 4,
        }

    # Extract rule information from previous phases
    created_rules = workflow_state.get("created_rules", [])

    if not created_rules:
        return {
            "status": "error",
            "message": "No rules have been created. Please complete Phase 4 properly.",
            "workflow_state": workflow_state,
            "next_phase": 4,
        }

    try:
        # Step 1: Deploy rules using the update-cursor-rules task
        deployment_result = run_update_cursor_rules()

        # Check if deployment was successful
        if deployment_result.get("status") == "error":
            return {
                "status": "error",
                "message": f"Error deploying cursor rules: {deployment_result.get('message')}",
                "workflow_state": workflow_state,
            }

        # Track deployed rules
        deployed_rules = []
        for rule in created_rules:
            deployed_rules.append({"rule_name": rule.get("rule_name", ""), "status": "deployed"})

        # Update the workflow state
        workflow_state["deployed_rules"] = deployed_rules
        workflow_state["phase_5_complete"] = True

        # Create a checklist for phase 5 completion
        checklist = [
            {"item": "Saved rules to cursor rules directory", "complete": len(created_rules) > 0},
            {
                "item": "Deployed rules using update-cursor-rules task",
                "complete": deployment_result.get("status") == "success",
            },
            {"item": "Rules ready for testing", "complete": True},
        ]

        # Generate testing instructions
        testing_instructions = """
## Testing Your Cursor Rules

To test your newly deployed cursor rules:

1. Open a file that should trigger one of your rules
2. Check if the rule is applied correctly by:
   - Looking for rule suggestions in the Cursor UI
   - Verifying that the rule's action message appears
   - Testing any interactive features of the rule

3. For each rule, verify:
   - The rule triggers on the correct file types
   - The content matching works as expected
   - The guidance provided is helpful and accurate

4. If you need to make adjustments:
   - Edit the rule files in the cursor rules drafts directory
   - Run `make update-cursor-rules` to deploy the changes
   - Test again to verify the changes

5. Common issues to check:
   - File pattern matching not working as expected
   - Content pattern too broad or too narrow
   - Action message unclear or not helpful
   - Examples not representative of real use cases
"""

        return {
            "status": "complete",
            "message": "Phase 5 (Deployment and Testing) completed successfully. All cursor rules have been deployed.",
            "checklist": checklist,
            "deployed_rules": deployed_rules,
            "total_deployed": len(deployed_rules),
            "workflow_state": workflow_state,
            "next_phase": None,
            "next_steps": "The workflow is complete. Your cursor rules have been deployed and are ready for testing.",
            "testing_instructions": testing_instructions,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error during deployment and testing: {e!s}",
            "workflow_state": workflow_state,
        }


if __name__ == "__main__":
    mcp.run()
