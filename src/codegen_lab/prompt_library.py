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
import logging
import logging.handlers
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict, Union

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.server import Context
from pydantic import Field

# Disable all logging handlers
logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.getLogger("mcp").handlers = []
logging.getLogger("mcp").propagate = False  # Prevent propagation to root logger


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
    name="instruct_repo_analysis",
    description="Run a repository analysis to gather information for cursor rule creation",
)
def instruct_repo_analysis() -> dict[str, Any]:
    """Run a repository analysis to gather information for cursor rule creation."""
    payload = {}
    payload["content"] = []
    payload["content"].append(
        {
            "type": "text",
            "text": {
                "status": "success",
                "message": "Repository Analysis Instructions:1. Invoke the Cursor rule for repository analysis:   Using the repo_analyzer.mdc rule located at ./.cursor/rules/repo_analyzer.mdc to perform a comprehensive code base analysis.2. Utilize the sequential thinking MCP server:   The sequentialthinking MCP server will be used to generate a detailed, structured report of the entire codebase.3. Generate and save a comprehensive report:   The analysis will be written to disk as ai_report.md for future reference and parameter population.4. Structure requirements for the report:   The markdown report should be structured to support extraction of the following parameters at minimum:   - Main languages used in the repository   - Frameworks and packages utilized   - Development packages and dependencies   - Testing frameworks and methodologies   - Other relevant code organization information5. Command to execute:   Run the repo_analyzer.mdc rule with the sequentialthinking processor to generate the comprehensive report6. Output validation:   Verify that ai_report.md has been created with proper markdown structure that facilitates parameter extraction7. Next steps:   Once generated, the ai_report.md file will be used as a source for populating project configuration parameters and documentation.",
                "repository_analysis": True,
                "analysis_rule": "./.cursor/rules/repo_analyzer.mdc",
                "processing_method": "sequentialthinking",
                "output_file": "ai_report.md",
                "required_parameters": ["main_languages", "frameworks", "packages", "dev_packages", "testing"],
                "analysis_status": {
                    "status": "pending",
                    "message": "Ready to execute repository analysis using Cursor rules and sequential thinking processor",
                    "rule_exists": True,
                    "rule_path": "./.cursor/rules/repo_analyzer.mdc",
                    "output_destination": "ai_report.md",
                },
            },
        }
    )
    payload["isError"] = False

    return payload


@mcp.tool(
    name="instruct_custom_repo_rules_generation",
    description="Run a cursor rules generation process based on repository analysis",
)
def instruct_custom_repo_rules_generation(
    # repo_summary: str = Field(
    #     description="A summary description of the repository, including technologies, frameworks, and key features",
    #     examples=["A Python web application using FastAPI, SQLAlchemy, and React for the frontend. Includes authentication, API endpoints, and database models."],
    #     min_length=20,
    # ),
    report_path: str = Field(
        description="Path to the AI report file, relative to the project root",
        examples=["ai_report.md", "docs/ai_report.md"],
        default="ai_report.md",
    ),
) -> dict[str, Any]:
    """Run a cursor rules generation process based on repository analysis.

    This function first checks for the existence of an AI report file,
    then uses its content to generate cursor rules for the repository.

    Args:
        report_path: Path to the AI report file, defaults to "ai_report.md"

    Returns:
        dict[str, Any]: A dictionary containing operations and instructions

    """
    # Define a complete sequence of operations for the cursor rules generation workflow
    operations = [
        # Step 1: Ensure the AI report exists and read its content
        {"type": "invoke_tool", "name": "ensure_ai_report", "args": {"report_path": report_path}},
        # Step 2: Generate recommended cursor rules based on the report content
        {"type": "invoke_tool", "name": "recommend_cursor_rules", "args": {"repo_summary": "{result}"}},
        # Step 3: Prepare the workspace for cursor rules
        {"type": "invoke_tool", "name": "prep_workspace", "args": {}},
        # Step 4: Check existing cursor rules
        {
            "type": "invoke_tool",
            "name": "list_directory",
            "args": {"path": "./hack/drafts/cursor_rules/", "options": "-la"},
        },
        # Step 5: Create the cursor rule files
        {
            "type": "invoke_tool",
            "name": "create_cursor_rule_files",
            "args": {"rule_names": "{result.recommended_rules}"},
        },
        # Step 6: Ensure the Makefile has the update-cursor-rules task
        {"type": "invoke_tool", "name": "ensure_makefile_task", "args": {"makefile_path": "Makefile"}},
        # Step 7: Update the .dockerignore file to exclude the cursor rules drafts directory
        {"type": "invoke_tool", "name": "update_dockerignore", "args": {}},
    ]

    # Create the response dictionary with all required fields
    response = {
        "operations": operations,
        "requires_result": True,
        "message": "Instructions to generate cursor rules based on AI report",
        "workflow_steps": [
            "1. Read and validate the AI report from the specified path",
            "2. Extract repository information and generate recommended rules",
            "3. Prepare the workspace for cursor rules creation",
            "4. Create the rule files in the drafts directory",
            "5. Ensure the Makefile contains the update-cursor-rules task",
            "6. Update .dockerignore to exclude the drafts directory",
            "7. Generate rule content based on repository analysis",
            "8. Deploy the rules using make update-cursor-rules",
        ],
        "output_directory": "hack/drafts/cursor_rules",
        "rule_format": {
            "filename": "{rule-name}.mdc.md",
            "frontmatter": {
                "description": "Brief description of the rule's purpose",
                "globs": "File patterns the rule applies to (e.g., *.py)",
                "alwaysApply": "Boolean value (typically false)",
            },
            "rule_structure": {
                "name": "rule-name",
                "description": "Detailed description of the rule",
                "filters": "Conditions for when the rule applies",
                "actions": "Suggestions or requirements provided by the rule",
                "examples": "Example inputs and outputs",
                "metadata": "Priority, version, and tags",
            },
        },
        "rule_example_template": {
            "frontmatter": "---\ndescription: Brief description of the rule\nglobs: *.py  # File patterns to match\nalwaysApply: false  # Whether to always apply the rule\n---",
            "title_and_introduction": "# Rule Title\nBrief description of what the rule covers.",
            "rule_definition": '<rule>\nname: rule_name\ndescription: Concise description of the rule\nfilters:\n  # Match specific file types\n  - type: file_extension\n    pattern: "\\\\.py$"\n  # Match specific paths\n  - type: file_path\n    pattern: "tests?/"\n  # Match specific content\n  - type: content\n    pattern: "(?i)(relevant|terms|to|match)"\nactions:\n  - type: suggest\n    message: |\n      # Main Heading\n      Explanation of the rule and its purpose.\n      ## Subheading\n      Detailed guidance with code examples:\n      ```python\n      # Example code\n      def example_function():\n          return "example"\n      ```\n      ## Another Subheading\n      More detailed information and best practices.\nexamples:\n  - input: |\n      # User query example\n      I want to do X with Y\n    output: |\n      Here\'s how to do X with Y:\n      \n      ```python\n      # Solution code\n      ```\nmetadata:\n  priority: high\n  version: 1.0\n  tags:\n    - relevant\n    - tags\n    - here\n</rule>',
        },
        "key_components_explanation": {
            "frontmatter": "YAML metadata at the top",
            "title_and_introduction": "Markdown heading and description",
            "rule_definition": "Enclosed in <rule> tags with basic properties, filters, actions, examples, and metadata",
        },
        "deployment_commands": {
            "prepare_files": "touch hack/drafts/cursor_rules/{rule-name}.mdc.md",
            "audit_files": "head -10 hack/drafts/cursor_rules/{rule-name}.mdc.md | cat",
            "deploy_to_production": "make update-cursor-rules",
        },
        "processing_tools": {
            "rule_recommendation": "recommend_cursor_rules",
            "complex_reasoning": "sequentialthinking",
            "file_management": "create_cursor_rule_files",
            "makefile_integration": "ensure_makefile_task",
            "docker_integration": "update_dockerignore",
            "ai_report_validation": "ensure_ai_report",
            "deploy_rules": "run_update_cursor_rules",
        },
        "final_steps": [
            {
                "name": "save_cursor_rule",
                "description": "For each rule, save the generated content to the appropriate file",
            },
            {"name": "run_update_cursor_rules", "description": "Run the Makefile task to deploy rules to production"},
        ],
        # Add the content field that the test is expecting with all required fields
        "content": [
            {
                "type": "text",
                "text": {
                    "status": "success",
                    "message": "Cursor Rules Generation Instructions",
                    "cursor_rules_generation": True,
                    "analysis_method": "repository_summary",
                    "operations": operations,
                    "workflow_steps": [
                        "1. Read and validate the AI report from the specified path",
                        "2. Extract repository information and generate recommended rules",
                        "3. Prepare the workspace for cursor rules creation",
                        "4. Create the rule files in the drafts directory",
                        "5. Ensure the Makefile contains the update-cursor-rules task",
                        "6. Update .dockerignore to exclude the drafts directory",
                        "7. Generate rule content based on repository analysis",
                        "8. Deploy the rules using make update-cursor-rules",
                    ],
                    "output_directory": "hack/drafts/cursor_rules",
                },
            }
        ],
    }

    return response


@mcp.tool(
    name="get_static_cursor_rule",
    description="Get a static cursor rule file by name to be written to the caller's .cursor/rules directory",
)
def get_static_cursor_rule(
    rule_name: str = Field(
        description="Name of the cursor rule to retrieve (with or without .md extension)",
        examples=["python-best-practices", "react-patterns", "error-handling"],
        min_length=1,
    ),
) -> dict[str, str | bool | list[dict[str, str]]]:
    """Get a static cursor rule file by name.

    This tool returns the content of a specific cursor rule file so it can be
    written to the calling repository's .cursor/rules directory.

    Args:
        rule_name: Name of the cursor rule to retrieve (with or without .md extension).
            Must be at least 1 character long.

    Returns:
        dict[str, Union[str, bool, list[dict[str, str]]]]: A dictionary containing either:
            - On success: {"rule_name": str, "content": str}
            - On error: {"isError": bool, "content": list[dict[str, str]]}

    Raises:
        No exceptions are raised; errors are returned in the result object.

    """
    # Add .md extension if not already present
    full_rule_name = rule_name if rule_name.endswith("mdc.md") else f"{rule_name}.mdc.md"
    # logger.debug(f"full_rule_name: {full_rule_name}")

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
        min_length=1,
    ),
    ignore_missing: bool = Field(
        description="If True, missing rules will be skipped instead of returning errors",
        default=False,
    ),
) -> dict[str, list[dict[str, str | bool | list[dict[str, str]]]]]:
    """Get multiple static cursor rule files by name.

    This tool returns the content of specific cursor rule files so they can be
    written to the calling repository's .cursor/rules directory.

    Args:
        rule_names: List of cursor rule names to retrieve (with or without .md extension)
        ignore_missing: If True, missing rules will be skipped instead of returning errors

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
        >>> # With ignore_missing=True
        >>> result = get_static_cursor_rules(["existing-rule", "non-existent-rule"], ignore_missing=True)
        >>> # Only includes the existing rule

    """
    # Validate input
    if not rule_names:
        return {
            "rules": [{"isError": True, "content": [{"type": "text", "text": "Error: Empty rule_names list provided"}]}]
        }

    results = []
    valid_rule_count = 0

    for rule_name in rule_names:
        # Basic validation of rule name format
        if not rule_name or not isinstance(rule_name, str):
            error_result = {
                "isError": True,
                "content": [{"type": "text", "text": f"Error: Invalid rule name format: {rule_name}"}],
            }
            results.append(error_result)
            continue

        # Get the rule data using get_static_cursor_rule
        rule_data = get_static_cursor_rule(rule_name)

        # logger.debug(f"rule_data: {rule_data}")

        # Check if the rule was found
        if rule_data.get("isError") and ignore_missing:
            # Skip adding this rule to results if ignore_missing is True
            continue

        # Add the result to our list
        results.append(rule_data)
        if not rule_data.get("isError"):
            valid_rule_count += 1

    # If all rules were missing and ignore_missing is True, provide a helpful message
    if ignore_missing and len(results) == 0:
        return {
            "rules": [
                {
                    "isError": True,
                    "content": [
                        {
                            "type": "text",
                            "text": f"Error: None of the requested rules ({', '.join(rule_names)}) were found",
                        }
                    ],
                }
            ]
        }

    # Return a single JSON object with the results array and metadata
    return {"rules": results, "valid_rule_count": valid_rule_count}


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
            '---\ndescription: Rule description\nglobs: *.py\nalwaysApply: false\n---\n# Python Best Practices\n\nWhen writing Python code, follow these guidelines:\n\n<rule>\nname: python-best-practices\ndescription: Best practices for Python development\nfilters:\n  - type: file_extension\n    pattern: "\\.py$"\nactions:\n  - type: suggest\n    message: |\n      Follow these guidelines:\n      1. Use type hints\n      2. Write docstrings\n      3. Follow PEP 8\n</rule>'
        ],
        min_length=10,
    ),
    overwrite: bool = Field(
        description="Whether to overwrite the file if it already exists",
        default=True,
    ),
) -> dict[str, list[dict[str, str | dict[str, bool | str]]] | str]:
    r"""Save a cursor rule to the cursor rules directory.

    This tool writes a cursor rule to the designated draft directory for cursor rules in the project.
    It performs comprehensive validation of the rule name and content before creating the necessary directory
    structure and writing the file. The function returns a dictionary with file operation
    instructions for the client to execute.

    The cursor rule format should follow this structure:
    1. Optional YAML frontmatter with metadata inside triple-dash delimiters (---)
       - description: Brief description of the rule's purpose
       - globs: File patterns the rule applies to (e.g., *.py)
       - alwaysApply: Boolean value (typically false)
    2. A markdown title and introduction
    3. A <rule>...</rule> block containing:
       - name: The rule identifier (should match the filename)
       - description: Brief explanation of the rule
       - filters: Conditions for when the rule applies
       - actions: Guidance provided when the rule matches
       - examples: Sample inputs and outputs
       - metadata: Priority, version, and tags

    Args:
        rule_name: The name of the cursor rule file (without extension).
                   Must be lowercase with hyphens (no spaces) and at least 3 characters.
        rule_content: The complete content of the cursor rule in mdc.md format.
                      Should contain valid markdown and be at least 10 characters long.
        overwrite: Whether to overwrite the file if it already exists.
                   Defaults to True.

    Returns:
        dict[str, list[dict[str, str | dict[str, bool | str]]] | str]: Dictionary containing:
            - On success: {
                "operations": [
                    {"type": "create_directory", "path": str, "options": {"parents": bool, "exist_ok": bool}},
                    {"type": "write_file", "path": str, "content": str, "options": {"mode": str, "encoding": str}}
                ],
                "message": str,
                "rule_structure": dict,
                "validation_results": dict
              }
            - On error: {
                "isError": True,
                "content": [{"type": "text", "text": str}]
              }

    Examples:
        >>> result = save_cursor_rule("python-best-practices",
        ...   "---\\ndescription: Python guidelines\\nglobs: *.py\\nalwaysApply: false\\n---\\n# Python Best Practices\\n...")
        >>> print("operations" in result)
        True

        >>> # Example with invalid rule name
        >>> result = save_cursor_rule("Invalid Name", "Some content")
        >>> print(result.get("isError"))
        True

    """
    # Additional validation beyond Field decorators
    if not rule_name:
        return {"isError": True, "content": [{"type": "text", "text": "Error: Rule name cannot be empty"}]}

    if not rule_content:
        return {"isError": True, "content": [{"type": "text", "text": "Error: Rule content cannot be empty"}]}

    # Initialize validation results
    validation_results = {
        "basic_structure": True,
        "has_frontmatter": False,
        "has_rule_block": False,
        "rule_name_match": False,
        "has_filters": False,
        "has_actions": False,
        "has_examples": False,
        "has_metadata": False,
        "warnings": [],
        "errors": [],
    }

    # Check for essential structure: the rule block
    if "<rule>" not in rule_content or "</rule>" not in rule_content:
        validation_results["basic_structure"] = False
        validation_results["has_rule_block"] = False
        error_message = "Error: Rule content must include a <rule>...</rule> block"
        validation_results["errors"].append(error_message)
        return {"isError": True, "content": [{"type": "text", "text": error_message}]}
    else:
        validation_results["has_rule_block"] = True

    # Check for frontmatter (optional but recommended)
    import re

    frontmatter_pattern = r"^---\s*\n(.*?)\n---\s*\n"
    frontmatter_match = re.search(frontmatter_pattern, rule_content, re.DOTALL)
    validation_results["has_frontmatter"] = bool(frontmatter_match)

    if validation_results["has_frontmatter"]:
        frontmatter_content = frontmatter_match.group(1)
        # Check for required frontmatter fields
        validation_results["has_description"] = "description:" in frontmatter_content
        validation_results["has_globs"] = "globs:" in frontmatter_content
        validation_results["has_always_apply"] = "alwaysApply:" in frontmatter_content

        # Add warnings for missing frontmatter fields
        if not validation_results["has_description"]:
            validation_results["warnings"].append("Warning: Frontmatter is missing 'description' field")
        if not validation_results["has_globs"]:
            validation_results["warnings"].append("Warning: Frontmatter is missing 'globs' field")
        if not validation_results["has_always_apply"]:
            validation_results["warnings"].append("Warning: Frontmatter is missing 'alwaysApply' field")

        # Check for quoted glob patterns (not recommended)
        glob_pattern = r"globs:\s*\"(.*?)\""
        if re.search(glob_pattern, frontmatter_content):
            validation_results["warnings"].append("Warning: Glob patterns should not be quoted in frontmatter")
    else:
        validation_results["warnings"].append("Warning: Rule is missing YAML frontmatter (recommended but optional)")

    # Check for markdown heading (optional if frontmatter exists)
    has_heading = bool(re.search(r"^# ", rule_content, re.MULTILINE))
    if not has_heading and not validation_results["has_frontmatter"]:
        validation_results["warnings"].append("Warning: Rule has neither frontmatter nor a markdown heading")

    # Extract rule block for deeper validation
    try:
        rule_block_start = rule_content.find("<rule>")
        rule_block_end = rule_content.find("</rule>") + len("</rule>")
        rule_block = rule_content[rule_block_start:rule_block_end]

        # Check rule name in rule block
        rule_name_pattern = r"name:\s*([a-z0-9-]+)"
        rule_name_match = re.search(rule_name_pattern, rule_block)

        if rule_name_match:
            rule_name_in_block = rule_name_match.group(1)
            validation_results["rule_name_match"] = rule_name_in_block == rule_name
            if not validation_results["rule_name_match"]:
                validation_results["warnings"].append(
                    f"Warning: Rule name in file ({rule_name}) doesn't match name in rule block ({rule_name_in_block})"
                )
        else:
            validation_results["warnings"].append("Warning: Could not find rule name in rule block")

        # Check for required rule components
        validation_results["has_filters"] = "filters:" in rule_block
        validation_results["has_actions"] = "actions:" in rule_block
        validation_results["has_examples"] = "examples:" in rule_block
        validation_results["has_metadata"] = "metadata:" in rule_block

        # Add warnings for missing components
        if not validation_results["has_filters"]:
            validation_results["warnings"].append("Warning: Rule is missing filters section")
        if not validation_results["has_actions"]:
            validation_results["warnings"].append("Warning: Rule is missing actions section")

        # Check for action types
        if "type: suggest" in rule_block:
            validation_results["has_suggest_action"] = True
        if "type: reject" in rule_block:
            validation_results["has_reject_action"] = True

        # Check for filter types
        filter_types = {
            "file_extension": "type: file_extension" in rule_block,
            "file_path": "type: file_path" in rule_block,
            "content": "type: content" in rule_block,
            "event": "type: event" in rule_block,
        }
        validation_results["filter_types"] = filter_types

    except Exception as e:
        validation_results["warnings"].append(f"Warning: Could not fully validate rule structure: {e!s}")

    try:
        # Normalize path with consideration for cross-platform compatibility
        import os

        cursor_rules_dir_path = os.path.normpath("hack/drafts/cursor_rules")
        rule_file_path = os.path.normpath(f"{cursor_rules_dir_path}/{rule_name}.mdc.md")

        # File existence operations
        check_file_existence = {"type": "custom_operation", "operation": "check_file_exists", "path": rule_file_path}

        # Determine write operation mode based on file existence and overwrite flag
        write_mode = "w"  # Default mode

        # If we don't want to overwrite and the file exists, return an error
        file_existence_check = {
            "type": "conditional_operation",
            "condition": {
                "operation": "file_exists",
                "path": rule_file_path,
                "and": {"operation": "not", "value": overwrite},
            },
            "if_true": {
                "type": "error",
                "message": f"Error: File {rule_file_path} already exists and overwrite is set to False",
            },
        }

        # Return operations for the client to perform
        return {
            "operations": [
                # Check file existence first (conditional operation)
                file_existence_check,
                # Create directory
                {
                    "type": "create_directory",
                    "path": cursor_rules_dir_path,
                    "options": {"parents": True, "exist_ok": True},
                },
                # Write file with encoding specified
                {
                    "type": "write_file",
                    "path": rule_file_path,
                    "content": rule_content,
                    "options": {"mode": write_mode, "encoding": "utf-8"},
                },
            ],
            "message": f"Instructions to save cursor rule to {rule_file_path}",
            "rule_structure": {
                "filename": f"{rule_name}.mdc.md",
                "path": rule_file_path,
                "format": "Markdown with embedded rule specification",
                "components": {
                    "frontmatter": {
                        "description": "Brief description of the rule's purpose",
                        "globs": "File patterns the rule applies to (e.g., *.py)",
                        "alwaysApply": "Boolean value (typically false)",
                    },
                    "introduction": "Markdown heading and description",
                    "rule_block": {
                        "name": "Rule identifier (should match filename)",
                        "description": "Brief explanation of the rule",
                        "filters": "Conditions for when the rule applies",
                        "actions": "Guidance provided when the rule matches",
                        "examples": "Sample inputs and outputs",
                        "metadata": "Priority, version, and tags",
                    },
                },
            },
            "validation_results": validation_results,
            "next_steps": [
                "Write content to each file sequentially",
                "Run `make update-cursor-rules` to deploy it to the .cursor/rules directory",
                "Verify the rule appears in your Cursor editor",
            ],
            "deployment_path": ".cursor/rules/",
        }
    except Exception as e:
        # Handle any unexpected errors
        return {"isError": True, "content": [{"type": "text", "text": f"Error saving cursor rule: {e!s}"}]}


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
) -> list[dict[str, str | list[str]]] | dict[str, bool | list[dict[str, str]]]:
    """Analyze a repository summary and recommend cursor rules to generate.

    This tool analyzes a summary of a repository and suggests cursor rules
    that would be beneficial to generate based on the technologies, patterns,
    and features identified in the repository. It matches keywords in the summary
    against a predefined set of technology patterns and returns corresponding
    rule recommendations.

    Args:
        repo_summary: A summary description of the repository, including
                      technologies, frameworks, and key features. Should be at
                      least 20 characters and contain meaningful information.

    Returns:
        Union[list[dict[str, Union[str, list[str]]]], dict[str, Union[bool, list[dict[str, str]]]]]:
            - On success: A list of recommended cursor rules, each containing:
                - 'name': The name of the rule (string)
                - 'description': A description of the rule (string)
                - 'reason': Why this rule is recommended for the repository (string)
                - 'dependencies': (optional) List of other rules this depends on (list[str])
            - On error: An error object with the structure:
                - {'isError': True, 'content': [{'type': 'text', 'text': 'Error message'}]}

    Examples:
        >>> # Example with Python and React
        >>> result = recommend_cursor_rules("A Python web app with React frontend")
        >>> print(len(result) > 2)  # Should have Python and React related rules
        True

        >>> # Example with error handling
        >>> try:
        ...     result = recommend_cursor_rules("")
        ... except Exception as e:
        ...     print("Error handled")
        ... else:
        ...     print("isError" in result)
        True

    """
    # Validate input beyond Field decorator
    if not repo_summary:
        return {"isError": True, "content": [{"type": "text", "text": "Error: Repository summary cannot be empty"}]}

    if len(repo_summary) < 20:
        return {
            "isError": True,
            "content": [
                {
                    "type": "text",
                    "text": f"Error: Repository summary too short ({len(repo_summary)} chars). Please provide at least 20 characters.",
                }
            ],
        }

    try:
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

        # Track matched keywords for better explanation
        matched_keywords = []

        # Find matches in the repository summary
        for keyword, rules in rule_recommendations.items():
            if keyword.lower() in summary_lower:
                recommended_rules.extend(rules)
                matched_keywords.append(keyword)

        # If no technology-specific matches were found, provide a helpful message
        if not matched_keywords and len(recommended_rules) <= 2:  # Only the default recommendations
            return {
                "isError": False,
                "content": [
                    {
                        "type": "text",
                        "text": "No specific technologies were identified in the repository summary. Consider providing more details about the technologies, frameworks, and features used in the repository.",
                    }
                ],
                "default_recommendations": recommended_rules,
            }

        # Remove duplicates while preserving order
        seen_names = set()
        unique_recommendations = []
        for rule in recommended_rules:
            if rule["name"] not in seen_names:
                seen_names.add(rule["name"])
                unique_recommendations.append(rule)

        return unique_recommendations

    except Exception as e:
        # Handle any unexpected errors
        return {"isError": True, "content": [{"type": "text", "text": f"Error analyzing repository summary: {e!s}"}]}


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

5. Write the following mandatory cursor rule files to the client repo's cursor rules stage directory one at a time, using the get_static_cursor_rules function to retrieve each file. when saving the file ensure the file has extension .mdc.md, eg tree.mdc becomes tree.mdc.md. use these as rule_names arguments to the get_static_cursor_rules function:
   - tree: A rule for displaying repository structure
   - repo_analyzer: A rule for analyzing repository structure and locating code definitions
   - notify: A rule for notification at the end of tasks
   - repomix: A rule for repository summarization and packaging for LLM consumption
   - cursor_rules_location: A rule for locating the cursor rules directory and how to write them

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
    name="ensure_ai_report",
    description="Check for the existence of an AI report file and ensure its content aligns with requirements",
)
def ensure_ai_report(
    report_path: str = Field(
        description="Path to the AI report file, relative to the project root",
        examples=[
            "./ai_report.md",
            "./docs/ai_report.md",
            "./reports/ai_report.md",
        ],
        default="./ai_report.md",
    ),
) -> dict[str, Any]:
    """Check for the existence of an AI report file and ensure its content aligns with requirements.

    This function verifies if the specified AI report file exists and contains all required sections.
    If the file doesn't exist or is missing required sections, it provides instructions for remediation.

    Args:
        report_path: Path to the AI report file, defaults to "ai_report.md"

    Returns:
        dict[str, Any]: A dictionary containing status, operations, and guidance

    """
    # Define the operations to check if the report file exists and read its content
    operations = [
        {"type": "check_file_exists", "path": report_path},
        {"type": "read_file", "path": report_path, "options": {"encoding": "utf-8"}},
    ]

    # Return payload with operations and additional information
    payload = {
        "operations": operations,
        "requires_result": True,
        "message": f"Instructions to check AI report file at {report_path}",
        "expected_sections": [
            "Project Overview",
            "Repository Structure",
            "Technology Stack",
            "Application Structure",
            "Deployment",
            "Development Tools",
            "Conclusion",
        ],
    }

    return payload


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
