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
mcp = FastMCP("prompt_library")

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
def list_cursor_rules() -> list[dict[str, str]]:
    """List all available cursor rules.

    Returns:
        List[Dict[str, str]]: List of cursor rules with name and description

    """
    rules = []
    for rule_name in get_cursor_rule_names():
        content = read_cursor_rule(rule_name)
        if content:
            parsed = parse_cursor_rule(content)
            rules.append(
                {"name": rule_name, "description": parsed.get("description", ""), "title": parsed.get("title", "")}
            )
    return rules


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
def save_cursor_rule(rule_name: str, rule_content: str) -> str:
    """Save a cursor rule to the cursor rules directory.

    Args:
        rule_name: The name of the cursor rule
        rule_content: The content of the cursor rule

    Returns:
        str: Success message

    """
    # Get the current working directory
    current_dir = Path.cwd()

    # Create the cursor rules directory path relative to the current directory
    local_cursor_rules_dir = current_dir / "hack" / "drafts" / "cursor_rules"

    # Create the directory if it doesn't exist
    local_cursor_rules_dir.mkdir(parents=True, exist_ok=True)

    # Save the rule to the local cursor rules directory
    rule_path = local_cursor_rules_dir / f"{rule_name}.mdc.md"
    rule_path.write_text(rule_content)

    return f"Cursor rule saved to {rule_path}"


@mcp.tool(
    name="recommend_cursor_rules",
    description="Analyze a repository summary and recommend cursor rules to generate based on identified technologies and patterns",
)
def recommend_cursor_rules(repo_summary: str) -> list[dict[str, str]]:
    """Recommend cursor rules to generate based on a repository summary.

    This tool analyzes a summary of a repository and suggests cursor rules
    that would be beneficial to generate based on the technologies, patterns,
    and features identified in the repository.

    Args:
        repo_summary: A summary description of the repository, including
                     technologies, frameworks, and key features

    Returns:
        list[dict[str, str]]: A list of recommended cursor rules, each containing
                             'name', 'description', and 'reason' fields

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

    Returns:
        dict[str, str]: A dictionary containing instructions and commands

    """
    # Get the current working directory
    current_dir = Path.cwd()

    # Define the cursor rules directory path
    cursor_rules_dir = current_dir / "hack" / "drafts" / "cursor_rules"

    # Check if the directory exists
    dir_exists = cursor_rules_dir.exists()

    # Prepare instructions
    mkdir_cmd = f"mkdir -p {cursor_rules_dir}"

    instructions = {
        "message": f"""
To prepare the workspace for cursor rules, the following steps are needed:

1. Create the cursor rules directory structure:
   {mkdir_cmd}

2. Ensure the .cursor/rules directory exists for deployment:
   mkdir -p .cursor/rules

3. Check if a Makefile exists with an update-cursor-rules task:
   The update-cursor-rules task should copy files from hack/drafts/cursor_rules to .cursor/rules

4. Update .dockerignore to exclude the cursor rules drafts directory:
   Add 'hack/drafts/cursor_rules' to .dockerignore if it exists
""",
        "directory_exists": dir_exists,
        "directory_path": str(cursor_rules_dir),
        "mkdir_command": mkdir_cmd,
    }

    return instructions


@mcp.tool(
    name="create_cursor_rule_files",
    description="Create empty cursor rule files and provide instructions for sequential content creation",
)
def create_cursor_rule_files(rule_names: list[str]) -> dict[str, Any]:
    """Create empty cursor rule files in the hack/drafts/cursor_rules directory.

    Args:
        rule_names: A list of cursor rule names to create (without file extensions)

    Returns:
        dict[str, Any]: A dictionary containing the results and next steps

    """
    try:
        # Create the cursor rules directory if it doesn't exist
        cursor_rules_dir = Path("hack/drafts/cursor_rules")
        cursor_rules_dir.mkdir(parents=True, exist_ok=True)

        created_files = []
        for rule_name in rule_names:
            # Ensure the rule name has the correct extension
            file_name = f"{rule_name}.mdc.md" if not rule_name.endswith(".mdc.md") else rule_name

            # Create the file path
            file_path = cursor_rules_dir / file_name

            # Create an empty file
            file_path.touch()

            created_files.append(file_name)

        # Check if Makefile exists and contains update-cursor-rules target
        makefile_path = Path("Makefile")
        has_makefile = makefile_path.exists()
        has_update_task = False

        if has_makefile:
            makefile_content = makefile_path.read_text()
            has_update_task = "update-cursor-rules" in makefile_content

        # Prepare touch command for display
        touch_cmd = f"touch {' '.join([str(cursor_rules_dir / f) for f in created_files])}"

        # Prepare next steps
        next_steps = """
Next steps:
1. Write content to each file sequentially
2. Deploy the rules using 'make update-cursor-rules'
3. Verify the rules are correctly deployed to .cursor/rules
"""

        return {
            "success": True,
            "created_files": created_files,
            "touch_command": touch_cmd,
            "has_makefile": has_makefile,
            "has_update_task": has_update_task,
            "next_steps": next_steps,
            "message": f"Created {len(created_files)} empty cursor rule files in {cursor_rules_dir}. {next_steps}",
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
def ensure_makefile_task() -> dict[str, Any]:
    """Ensure the Makefile has the update-cursor-rules task.

    This function checks if the Makefile exists and contains the update-cursor-rules task.
    If the task doesn't exist, it adds it to the Makefile.
    If the Makefile doesn't exist, it creates one with the task.

    Returns:
        dict[str, Any]: A dictionary containing the results and next steps

    """
    # Get the current working directory
    current_dir = Path.cwd()

    # Define the Makefile path
    makefile_path = current_dir / "Makefile"

    # Check if Makefile exists
    has_makefile = makefile_path.exists()
    has_update_task = False
    action_taken = "none"

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

    if has_makefile:
        # Read the Makefile content
        makefile_content = makefile_path.read_text()

        # Check if the update-cursor-rules task exists
        has_update_task = "update-cursor-rules" in makefile_content

        if not has_update_task:
            # Add the update-cursor-rules task to the Makefile
            with open(makefile_path, "a") as f:
                f.write(update_task_content)

            action_taken = "updated"
    else:
        # Create a new Makefile with the update-cursor-rules task
        with open(makefile_path, "w") as f:
            f.write(update_task_content)

        action_taken = "created"
        has_makefile = True
        has_update_task = True

    # Prepare next steps
    if action_taken == "none":
        message = "The Makefile already contains the update-cursor-rules task."
    elif action_taken == "updated":
        message = "Added the update-cursor-rules task to the existing Makefile."
    else:
        message = "Created a new Makefile with the update-cursor-rules task."

    return {
        "success": True,
        "has_makefile": has_makefile,
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

    This function executes the update-cursor-rules Makefile task to deploy cursor rules
    from hack/drafts/cursor_rules to .cursor/rules.

    Returns:
        dict[str, Any]: A dictionary containing the results

    """
    import subprocess

    # Get the current working directory
    current_dir = Path.cwd()

    # Define the Makefile path
    makefile_path = current_dir / "Makefile"

    # Check if Makefile exists
    has_makefile = makefile_path.exists()

    if not has_makefile:
        return {
            "success": False,
            "message": "Makefile not found. Please create a Makefile with the update-cursor-rules task.",
            "next_steps": "Use the ensure_makefile_task tool to create the Makefile.",
        }

    # Check if the update-cursor-rules task exists
    makefile_content = makefile_path.read_text()
    has_update_task = "update-cursor-rules" in makefile_content

    if not has_update_task:
        return {
            "success": False,
            "message": "The update-cursor-rules task was not found in the Makefile.",
            "next_steps": "Use the ensure_makefile_task tool to add the update-cursor-rules task to the Makefile.",
        }

    try:
        # Run the update-cursor-rules task
        result = subprocess.run(
            ["make", "update-cursor-rules"], cwd=current_dir, capture_output=True, text=True, check=True
        )

        # Check if the .cursor/rules directory exists and contains files
        cursor_rules_dir = current_dir / ".cursor" / "rules"
        deployed_rules = list(cursor_rules_dir.glob("*"))

        return {
            "success": True,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "deployed_rules": [str(rule) for rule in deployed_rules],
            "message": "Successfully deployed cursor rules.",
            "next_steps": "The cursor rules have been deployed to .cursor/rules.",
        }
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "message": f"Failed to run the update-cursor-rules task: {e}",
            "next_steps": "Check the error message and fix any issues with the Makefile.",
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"An error occurred: {e!s}",
            "next_steps": "Check the error message and try again.",
        }


@mcp.tool(
    name="update_dockerignore",
    description="Update the .dockerignore file to exclude the cursor rules drafts directory",
)
def update_dockerignore() -> dict[str, Any]:
    """Update the .dockerignore file to exclude the cursor rules drafts directory.

    This function checks if the .dockerignore file exists and adds an entry to exclude
    the cursor rules drafts directory if it doesn't already exist.

    Returns:
        dict[str, Any]: A dictionary containing the results

    """
    # Get the current working directory
    current_dir = Path.cwd()

    # Define the .dockerignore path
    dockerignore_path = current_dir / ".dockerignore"

    # The entry to add to .dockerignore
    entry = "hack/drafts/cursor_rules"

    # Check if .dockerignore exists
    has_dockerignore = dockerignore_path.exists()
    entry_exists = False
    action_taken = "none"

    if has_dockerignore:
        # Read the .dockerignore content
        dockerignore_content = dockerignore_path.read_text()

        # Check if the entry already exists
        entry_exists = entry in dockerignore_content.split("\n")

        if not entry_exists:
            # Add the entry to .dockerignore
            with open(dockerignore_path, "a") as f:
                # Add a newline if the file doesn't end with one
                if not dockerignore_content.endswith("\n"):
                    f.write("\n")

                f.write(f"{entry}\n")

            action_taken = "updated"
    else:
        # Create a new .dockerignore file with the entry
        with open(dockerignore_path, "w") as f:
            f.write(f"{entry}\n")

        action_taken = "created"
        has_dockerignore = True
        entry_exists = True

    # Prepare message
    if action_taken == "none":
        message = "The .dockerignore file already contains an entry for the cursor rules drafts directory."
    elif action_taken == "updated":
        message = "Added an entry for the cursor rules drafts directory to the existing .dockerignore file."
    else:
        message = "Created a new .dockerignore file with an entry for the cursor rules drafts directory."

    return {
        "success": True,
        "has_dockerignore": has_dockerignore,
        "entry_exists": entry_exists,
        "action_taken": action_taken,
        "message": message,
    }


@mcp.tool(
    name="cursor_rules_workflow",
    description="Execute the complete cursor rules workflow",
)
def cursor_rules_workflow(rule_names: list[str]) -> dict[str, Any]:
    """Execute the complete cursor rules workflow.

    Args:
        rule_names: A list of cursor rule names to create (without file extensions)

    Returns:
        dict[str, Any]: A dictionary containing the results and next steps

    """
    # Step 1: Prepare the workspace
    workspace_result = prep_workspace()

    # Step 2: Create empty cursor rule files
    files_result = create_cursor_rule_files(rule_names)

    # Step 3: Ensure the Makefile has the update-cursor-rules task
    makefile_result = ensure_makefile_task()

    # Step 4: Update the .dockerignore file
    dockerignore_result = update_dockerignore()

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
        "success": True,
        "workspace_result": workspace_result,
        "files_result": files_result,
        "makefile_result": makefile_result,
        "dockerignore_result": dockerignore_result,
        "created_files": files_result.get("created_files", []),
        "message": f"Cursor rules workflow completed successfully. Created {len(files_result.get('created_files', []))} empty cursor rule files.",
        "next_steps": next_steps,
    }


if __name__ == "__main__":
    mcp.run()
