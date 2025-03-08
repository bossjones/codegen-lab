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
mcp = FastMCP("Cursor Rules Prompt Library")

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


# Resource endpoints
@mcp.resource("cursor-rules://list")
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


@mcp.resource("cursor-rule://{name}")
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


@mcp.resource("cursor-rule-raw://{name}")
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


@mcp.tool()
def save_cursor_rule(rule_name: str, rule_content: str) -> str:
    """Save a cursor rule to the cursor rules directory.

    Args:
        rule_name: The name of the cursor rule
        rule_content: The content of the cursor rule

    Returns:
        str: Success message

    """
    rule_path = CURSOR_RULES_DIR / f"{rule_name}.mdc.md"
    rule_path.write_text(rule_content)
    return f"Cursor rule saved to {rule_path}"


if __name__ == "__main__":
    mcp.run()
