"""Cursor Rules MCP Server implementation.

This module implements a Model Context Protocol (MCP) server that helps users
create custom cursor rules based on their repository structure.
"""

import asyncio
import json
import logging
import sqlite3
from pathlib import Path
from typing import Any

# Import MCP server library
try:
    from mcp_api_server import Handler, MCPServer  # type: ignore
except ImportError:
    raise ImportError(
        "Failed to import mcp_api_server module. "
        "Make sure it's installed in your environment."
    )

# Import local modules
from .models import (
    DB_SCHEMA,
    Repository,
    Rule,
    RuleTemplate,
    dict_to_repository,
    dict_to_rule,
    dict_to_template,
    rule_to_dict,
)
from .repository_analyzer import get_rule_template
from .rule_generator import RuleGenerator, analyze_and_suggest_rules, generate_rule, validate_rule_content

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("cursor_rules_mcp")

# Template for the prompt displayed to users
PROMPT_TEMPLATE = """# Creating Custom Cursor Rules

This tool will help you create custom cursor rules for your repository.

## What are Cursor Rules?

Cursor rules are instructions that guide Claude when working with your code. They can help:
- Define project-specific conventions
- Enforce coding standards
- Guide development workflows
- Provide context about your codebase

## Rule Components

Each rule consists of:

1. **Name**: A unique identifier for the rule (e.g., `python-code-standards`)
2. **Description**: What the rule does and when it applies
3. **Filters**: Patterns that determine when the rule is activated
   - Message filters: Trigger on user messages containing specific patterns
   - Context filters: Trigger when specific files or code patterns are present
4. **Actions**: What happens when the rule is triggered
   - Instructions: Guidance for Claude to follow
   - Commands: Specific actions for Claude to take
5. **Examples**: Sample inputs and outputs showing how the rule works
6. **Metadata**: Additional information about the rule (priority, version, etc.)

## Creating a Rule

To create a custom rule:
1. Analyze your repository structure (use the `analyze_repository` tool)
2. Choose a rule template from the suggestions
3. Customize the rule for your specific needs
4. Save and export the rule to your cursor rules directory

Let's get started by analyzing your repository!
"""

# Tool names and descriptions for MCP server
TOOLS = {
    "analyze_repository": "Analyze a repository and suggest cursor rules based on its structure",
    "get_rule_templates": "Get available cursor rule templates",
    "get_rule_template": "Get a specific cursor rule template",
    "generate_rule": "Generate a cursor rule from a template",
    "customize_rule": "Customize a cursor rule for a specific repository",
    "validate_rule": "Validate a cursor rule for correctness",
    "save_rule": "Save a cursor rule to the database",
    "list_rules": "List all saved cursor rules",
    "export_rules": "Export cursor rules to markdown files"
}


class CursorRulesDatabase:

    """Manages SQLite database operations for cursor rules.

    This class provides methods to interact with the SQLite database,
    storing and retrieving rules, repositories, and templates.

    Attributes:
        db_path (Path): Path to the SQLite database file.
        conn (sqlite3.Connection): Connection to the SQLite database.

    """

    def __init__(self, db_path: str = None):
        """Initialize the database connection.

        Args:
            db_path (str, optional): Path to the SQLite database file.
                If None, uses a default path in the user's home directory.

        """
        if db_path is None:
            home_dir = Path.home()
            db_dir = home_dir / ".cursor_rules_mcp"
            db_dir.mkdir(exist_ok=True, parents=True)
            db_path = str(db_dir / "cursor_rules.db")

        self.db_path = Path(db_path)
        logger.info(f"Using database at {self.db_path}")

        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row

        # Initialize database tables
        self._init_database()

    def _init_database(self):
        """Create database tables if they don't exist."""
        cursor = self.conn.cursor()

        # Create tables using schema definitions
        for table_name, schema in DB_SCHEMA.items():
            logger.debug(f"Creating table: {table_name}")
            cursor.execute(schema)

        self.conn.commit()

    def get_rules(self) -> list[Rule]:
        """Get all rules from the database.

        Returns:
            List[Rule]: List of all rules.

        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM rules")
        rows = cursor.fetchall()

        rules = []
        for row in rows:
            rule_dict = dict(row)
            rules.append(dict_to_rule(rule_dict))

        return rules

    def get_rule(self, rule_id: int) -> Rule | None:
        """Get a rule by ID.

        Args:
            rule_id (int): ID of the rule to retrieve.

        Returns:
            Optional[Rule]: The rule if found, None otherwise.

        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM rules WHERE id = ?", (rule_id,))
        row = cursor.fetchone()

        if row:
            rule_dict = dict(row)
            return dict_to_rule(rule_dict)

        return None

    def add_rule(self, rule: Rule) -> int:
        """Add a new rule to the database.

        Args:
            rule (Rule): The rule to add.

        Returns:
            int: The ID of the new rule.

        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO rules
            (name, description, content, template_id, repository_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                rule.name, rule.description, rule.content,
                rule.template_id, rule.repository_id,
                rule.created_at, rule.updated_at
            )
        )
        self.conn.commit()

        return cursor.lastrowid

    def update_rule(self, rule: Rule) -> bool:
        """Update an existing rule.

        Args:
            rule (Rule): The rule to update.

        Returns:
            bool: True if the rule was updated, False otherwise.

        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE rules
            SET name = ?, description = ?, content = ?,
                template_id = ?, repository_id = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                rule.name, rule.description, rule.content,
                rule.template_id, rule.repository_id, rule.updated_at,
                rule.id
            )
        )
        self.conn.commit()

        return cursor.rowcount > 0

    def delete_rule(self, rule_id: int) -> bool:
        """Delete a rule by ID.

        Args:
            rule_id (int): ID of the rule to delete.

        Returns:
            bool: True if the rule was deleted, False otherwise.

        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM rules WHERE id = ?", (rule_id,))
        self.conn.commit()

        return cursor.rowcount > 0

    def get_rule_templates(self) -> list[RuleTemplate]:
        """Get all rule templates from the database.

        Returns:
            List[RuleTemplate]: List of all rule templates.

        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM rule_templates")
        rows = cursor.fetchall()

        templates = []
        for row in rows:
            template_dict = dict(row)
            templates.append(dict_to_template(template_dict))

        return templates

    def get_rule_template(self, template_id: int) -> RuleTemplate | None:
        """Get a rule template by ID.

        Args:
            template_id (int): ID of the template to retrieve.

        Returns:
            Optional[RuleTemplate]: The template if found, None otherwise.

        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM rule_templates WHERE id = ?", (template_id,))
        row = cursor.fetchone()

        if row:
            template_dict = dict(row)
            return dict_to_template(template_dict)

        return None

    def add_rule_template(self, template: RuleTemplate) -> int:
        """Add a new rule template to the database.

        Args:
            template (RuleTemplate): The template to add.

        Returns:
            int: The ID of the new template.

        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO rule_templates
            (name, title, description, content, category, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                template.name, template.title, template.description,
                template.content, template.category, template.created_at
            )
        )
        self.conn.commit()

        return cursor.lastrowid

    def add_repository(self, repository: Repository) -> int:
        """Add a new repository to the database.

        Args:
            repository (Repository): The repository to add.

        Returns:
            int: The ID of the new repository.

        """
        cursor = self.conn.cursor()

        # Convert dictionaries to JSON strings for storage
        languages_json = json.dumps(repository.languages)
        frameworks_json = json.dumps(repository.frameworks)
        file_stats_json = json.dumps(repository.file_stats)

        cursor.execute(
            """
            INSERT INTO repositories
            (name, path, repo_type, languages, frameworks, file_stats, analysis_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                repository.name, repository.path, repository.repo_type,
                languages_json, frameworks_json, file_stats_json,
                repository.analysis_date
            )
        )
        self.conn.commit()

        return cursor.lastrowid

    def get_repository(self, repo_id: int) -> Repository | None:
        """Get a repository by ID.

        Args:
            repo_id (int): ID of the repository to retrieve.

        Returns:
            Optional[Repository]: The repository if found, None otherwise.

        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM repositories WHERE id = ?", (repo_id,))
        row = cursor.fetchone()

        if row:
            repo_dict = dict(row)

            # Convert JSON strings back to dictionaries
            repo_dict["languages"] = json.loads(repo_dict["languages"])
            repo_dict["frameworks"] = json.loads(repo_dict["frameworks"])
            repo_dict["file_stats"] = json.loads(repo_dict["file_stats"])

            return dict_to_repository(repo_dict)

        return None

    def get_repository_by_path(self, path: str) -> Repository | None:
        """Get a repository by its path.

        Args:
            path (str): Path of the repository to retrieve.

        Returns:
            Optional[Repository]: The repository if found, None otherwise.

        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM repositories WHERE path = ?", (path,))
        row = cursor.fetchone()

        if row:
            repo_dict = dict(row)

            # Convert JSON strings back to dictionaries
            repo_dict["languages"] = json.loads(repo_dict["languages"])
            repo_dict["frameworks"] = json.loads(repo_dict["frameworks"])
            repo_dict["file_stats"] = json.loads(repo_dict["file_stats"])

            return dict_to_repository(repo_dict)

        return None

    def add_repo_analysis(self, repo_path: str, analysis_results: dict[str, Any]) -> int:
        """Add or update repository analysis results.

        Args:
            repo_path (str): Path to the repository.
            analysis_results (Dict[str, Any]): Analysis results from the analyzer.

        Returns:
            int: The ID of the repository.

        """
        # Check if repository already exists
        repo_path = str(Path(repo_path).expanduser().resolve())
        existing_repo = self.get_repository_by_path(repo_path)

        if existing_repo:
            # Update existing repository
            repo = Repository(
                id=existing_repo.id,
                name=Path(repo_path).name,
                path=repo_path,
                repo_type=analysis_results.get("repo_type", "generic"),
                languages=analysis_results.get("languages", {}),
                frameworks=analysis_results.get("frameworks", {}),
                file_stats=analysis_results.get("file_stats", {}),
                analysis_date=existing_repo.analysis_date  # Keep original analysis date
            )

            cursor = self.conn.cursor()

            # Convert dictionaries to JSON strings for storage
            languages_json = json.dumps(repo.languages)
            frameworks_json = json.dumps(repo.frameworks)
            file_stats_json = json.dumps(repo.file_stats)

            cursor.execute(
                """
                UPDATE repositories
                SET name = ?, repo_type = ?, languages = ?,
                    frameworks = ?, file_stats = ?, analysis_date = ?
                WHERE id = ?
                """,
                (
                    repo.name, repo.repo_type,
                    languages_json, frameworks_json, file_stats_json,
                    repo.analysis_date, repo.id
                )
            )
            self.conn.commit()

            return existing_repo.id
        else:
            # Create new repository
            repo = Repository(
                id=0,  # Will be assigned by the database
                name=Path(repo_path).name,
                path=repo_path,
                repo_type=analysis_results.get("repo_type", "generic"),
                languages=analysis_results.get("languages", {}),
                frameworks=analysis_results.get("frameworks", {}),
                file_stats=analysis_results.get("file_stats", {})
            )

            return self.add_repository(repo)


async def handle_list_resources(args: dict[str, Any]) -> dict[str, Any]:
    """Handler for listing available resources.

    Args:
        args (Dict[str, Any]): Arguments passed to the handler.

    Returns:
        Dict[str, Any]: Dictionary of available resources.

    """
    logger.info("Listing resources")

    return {
        "resources": [
            {
                "type": "text",
                "name": "cursor_rules_guide",
                "title": "Cursor Rules Guide",
                "description": "Guide for creating and using cursor rules"
            },
            {
                "type": "text",
                "name": "rule_templates",
                "title": "Rule Templates",
                "description": "Available templates for cursor rules"
            }
        ]
    }


async def handle_read_resource(args: dict[str, Any]) -> dict[str, Any]:
    """Handler for reading a specific resource.

    Args:
        args (Dict[str, Any]): Arguments passed to the handler.

    Returns:
        Dict[str, Any]: Resource content.

    """
    resource_name = args.get("resource")
    logger.info(f"Reading resource: {resource_name}")

    if resource_name == "cursor_rules_guide":
        return {
            "content": PROMPT_TEMPLATE
        }
    elif resource_name == "rule_templates":
        # Load rule templates from the database
        db = CursorRulesDatabase()
        templates = db.get_rule_templates()

        # Format templates for display
        template_list = "\n\n".join([
            f"## {template.title}\n\n{template.description}\n\n"
            f"- **Name**: `{template.name}`\n"
            f"- **Category**: {template.category}"
            for template in templates
        ])

        if not template_list:
            template_list = "No rule templates available. Use the analyze_repository tool to get suggestions."

        return {
            "content": f"# Rule Templates\n\n{template_list}"
        }

    return {
        "error": f"Resource not found: {resource_name}"
    }


async def handle_list_prompts(args: dict[str, Any]) -> dict[str, Any]:
    """Handler for listing available prompts.

    Args:
        args (Dict[str, Any]): Arguments passed to the handler.

    Returns:
        Dict[str, Any]: Dictionary of available prompts.

    """
    logger.info("Listing prompts")

    return {
        "prompts": [
            {
                "id": "cursor_rules_creation",
                "title": "Create Custom Cursor Rules",
                "description": "Create custom cursor rules based on your repository"
            }
        ]
    }


async def handle_get_prompt(args: dict[str, Any]) -> dict[str, Any]:
    """Handler for retrieving a specific prompt.

    Args:
        args (Dict[str, Any]): Arguments passed to the handler.

    Returns:
        Dict[str, Any]: Prompt content.

    """
    prompt_id = args.get("id")
    logger.info(f"Getting prompt: {prompt_id}")

    if prompt_id == "cursor_rules_creation":
        return {
            "prompt": {
                "content": PROMPT_TEMPLATE,
                "tools": list(TOOLS.keys())
            }
        }

    return {
        "error": f"Prompt not found: {prompt_id}"
    }


async def handle_execute_tool(args: dict[str, Any]) -> dict[str, Any]:
    """Handler for executing tools.

    Args:
        args (Dict[str, Any]): Arguments passed to the handler.

    Returns:
        Dict[str, Any]: Tool execution result.

    """
    tool_name = args.get("tool")
    tool_args = args.get("args", {})

    logger.info(f"Executing tool: {tool_name} with args: {tool_args}")

    if tool_name == "analyze_repository":
        return await execute_analyze_repository(tool_args)
    elif tool_name == "get_rule_templates":
        return await execute_get_rule_templates(tool_args)
    elif tool_name == "get_rule_template":
        return await execute_get_rule_template(tool_args)
    elif tool_name == "generate_rule":
        return await execute_generate_rule(tool_args)
    elif tool_name == "customize_rule":
        return await execute_customize_rule(tool_args)
    elif tool_name == "validate_rule":
        return await execute_validate_rule(tool_args)
    elif tool_name == "save_rule":
        return await execute_save_rule(tool_args)
    elif tool_name == "list_rules":
        return await execute_list_rules(tool_args)
    elif tool_name == "export_rules":
        return await execute_export_rules(tool_args)

    return {
        "error": f"Unknown tool: {tool_name}"
    }


async def execute_analyze_repository(args: dict[str, Any]) -> dict[str, Any]:
    """Execute the analyze_repository tool.

    Args:
        args (Dict[str, Any]): Tool arguments.

    Returns:
        Dict[str, Any]: Tool execution result.

    """
    # Validate required args
    repo_path = args.get("repo_path")
    if not repo_path:
        return {"error": "Missing required argument: repo_path"}

    try:
        # Analyze the repository
        analysis_results = analyze_and_suggest_rules(repo_path)

        # Store analysis in the database
        db = CursorRulesDatabase()
        repo_id = db.add_repo_analysis(repo_path, analysis_results["analysis"])

        # Return analysis results
        return {
            "repository": {
                "id": repo_id,
                "name": Path(repo_path).name,
                "path": repo_path,
                "type": analysis_results["analysis"]["repo_type"],
                "languages": analysis_results["analysis"]["languages"],
                "frameworks": analysis_results["analysis"]["frameworks"]
            },
            "suggested_rules": analysis_results["suggested_rules"],
            "file_count": analysis_results["analysis"]["file_stats"]["file_count"]
        }
    except Exception as e:
        logger.error(f"Error analyzing repository: {e}", exc_info=True)
        return {"error": f"Failed to analyze repository: {e!s}"}


async def execute_get_rule_templates(args: dict[str, Any]) -> dict[str, Any]:
    """Execute the get_rule_templates tool.

    Args:
        args (Dict[str, Any]): Tool arguments.

    Returns:
        Dict[str, Any]: Tool execution result.

    """
    # Get rule templates from built-in ones
    templates = [
        {
            "name": "incremental-development-workflow",
            "title": "Incremental Development Workflow",
            "description": "Implements Harper Reed's non-greenfield iterative development workflow"
        },
        {
            "name": "python-code-standards",
            "title": "Python Code Standards",
            "description": "Enforces PEP 8 standards and Python best practices"
        },
        {
            "name": "web-development-workflow",
            "title": "Web Development Workflow",
            "description": "Guides web development tasks and enforces best practices"
        }
    ]

    # Try to get templates from the database as well
    try:
        db = CursorRulesDatabase()
        db_templates = db.get_rule_templates()

        for template in db_templates:
            templates.append({
                "id": template.id,
                "name": template.name,
                "title": template.title,
                "description": template.description,
                "category": template.category
            })
    except Exception as e:
        logger.warning(f"Error fetching templates from database: {e}")

    return {
        "templates": templates
    }


async def execute_get_rule_template(args: dict[str, Any]) -> dict[str, Any]:
    """Execute the get_rule_template tool.

    Args:
        args (Dict[str, Any]): Tool arguments.

    Returns:
        Dict[str, Any]: Tool execution result.

    """
    # Validate required args
    template_name = args.get("name")
    if not template_name:
        return {"error": "Missing required argument: name"}

    try:
        # Get template content
        template_content = get_rule_template(template_name)

        if not template_content:
            return {"error": f"Template not found: {template_name}"}

        return {
            "template": {
                "name": template_name,
                "content": template_content
            }
        }
    except Exception as e:
        logger.error(f"Error getting rule template: {e}", exc_info=True)
        return {"error": f"Failed to get rule template: {e!s}"}


async def execute_generate_rule(args: dict[str, Any]) -> dict[str, Any]:
    """Execute the generate_rule tool.

    Args:
        args (Dict[str, Any]): Tool arguments.

    Returns:
        Dict[str, Any]: Tool execution result.

    """
    # Validate required args
    template_name = args.get("template_name")
    if not template_name:
        return {"error": "Missing required argument: template_name"}

    # Optional args
    repo_path = args.get("repo_path")
    customizations = args.get("customizations", {})

    try:
        # Generate rule from template
        rule_content = generate_rule(template_name, repo_path, customizations)

        return {
            "rule": {
                "template_name": template_name,
                "content": rule_content
            }
        }
    except Exception as e:
        logger.error(f"Error generating rule: {e}", exc_info=True)
        return {"error": f"Failed to generate rule: {e!s}"}


async def execute_customize_rule(args: dict[str, Any]) -> dict[str, Any]:
    """Execute the customize_rule tool.

    Args:
        args (Dict[str, Any]): Tool arguments.

    Returns:
        Dict[str, Any]: Tool execution result.

    """
    # Validate required args
    template_name = args.get("template_name")
    repo_path = args.get("repo_path")
    if not template_name:
        return {"error": "Missing required argument: template_name"}
    if not repo_path:
        return {"error": "Missing required argument: repo_path"}

    try:
        # Create rule generator and customize
        generator = RuleGenerator(repo_path)
        rule_content = generator.customize_rule_for_repo(template_name)

        return {
            "rule": {
                "template_name": template_name,
                "content": rule_content
            }
        }
    except Exception as e:
        logger.error(f"Error customizing rule: {e}", exc_info=True)
        return {"error": f"Failed to customize rule: {e!s}"}


async def execute_validate_rule(args: dict[str, Any]) -> dict[str, Any]:
    """Execute the validate_rule tool.

    Args:
        args (Dict[str, Any]): Tool arguments.

    Returns:
        Dict[str, Any]: Tool execution result.

    """
    # Validate required args
    rule_content = args.get("content")
    if not rule_content:
        return {"error": "Missing required argument: content"}

    try:
        # Validate rule content
        is_valid, errors = validate_rule_content(rule_content)

        return {
            "valid": is_valid,
            "errors": errors
        }
    except Exception as e:
        logger.error(f"Error validating rule: {e}", exc_info=True)
        return {"error": f"Failed to validate rule: {e!s}"}


async def execute_save_rule(args: dict[str, Any]) -> dict[str, Any]:
    """Execute the save_rule tool.

    Args:
        args (Dict[str, Any]): Tool arguments.

    Returns:
        Dict[str, Any]: Tool execution result.

    """
    # Validate required args
    name = args.get("name")
    description = args.get("description")
    content = args.get("content")
    if not name:
        return {"error": "Missing required argument: name"}
    if not description:
        return {"error": "Missing required argument: description"}
    if not content:
        return {"error": "Missing required argument: content"}

    # Optional args
    template_id = args.get("template_id")
    repository_id = args.get("repository_id")

    try:
        # Validate rule content
        is_valid, errors = validate_rule_content(content)
        if not is_valid:
            return {
                "error": f"Invalid rule content: {', '.join(errors)}"
            }

        # Create rule object
        rule = Rule(
            id=0,  # Will be assigned by the database
            name=name,
            description=description,
            content=content,
            template_id=template_id,
            repository_id=repository_id
        )

        # Save rule to database
        db = CursorRulesDatabase()
        rule_id = db.add_rule(rule)

        return {
            "rule": {
                "id": rule_id,
                "name": name,
                "description": description
            }
        }
    except Exception as e:
        logger.error(f"Error saving rule: {e}", exc_info=True)
        return {"error": f"Failed to save rule: {e!s}"}


async def execute_list_rules(args: dict[str, Any]) -> dict[str, Any]:
    """Execute the list_rules tool.

    Args:
        args (Dict[str, Any]): Tool arguments.

    Returns:
        Dict[str, Any]: Tool execution result.

    """
    try:
        # Get rules from database
        db = CursorRulesDatabase()
        rules = db.get_rules()

        return {
            "rules": [rule_to_dict(rule) for rule in rules]
        }
    except Exception as e:
        logger.error(f"Error listing rules: {e}", exc_info=True)
        return {"error": f"Failed to list rules: {e!s}"}


async def execute_export_rules(args: dict[str, Any]) -> dict[str, Any]:
    """Execute the export_rules tool.

    Args:
        args (Dict[str, Any]): Tool arguments.

    Returns:
        Dict[str, Any]: Tool execution result.

    """
    # Validate required args
    output_dir = args.get("output_dir")
    if not output_dir:
        return {"error": "Missing required argument: output_dir"}

    # Optional args
    rule_ids = args.get("rule_ids", [])

    try:
        # Get rules from database
        db = CursorRulesDatabase()
        rules = db.get_rules()

        # Filter by rule_ids if provided
        if rule_ids:
            rules = [rule for rule in rules if rule.id in rule_ids]

        # Prepare rules for export
        rule_dict = {rule.name: rule.content for rule in rules}

        # Export rules to files
        generator = RuleGenerator()
        created_files = generator.export_rules_to_files(rule_dict, output_dir)

        return {
            "exported_files": created_files,
            "count": len(created_files)
        }
    except Exception as e:
        logger.error(f"Error exporting rules: {e}", exc_info=True)
        return {"error": f"Failed to export rules: {e!s}"}


def validate_required_args(args: dict[str, Any], required_args: list[str]) -> dict[str, Any] | None:
    """Validate that all required arguments are present.

    Args:
        args (Dict[str, Any]): Arguments to validate.
        required_args (List[str]): List of required argument names.

    Returns:
        Optional[Dict[str, Any]]: Error dictionary if validation fails, None otherwise.

    """
    missing_args = [arg for arg in required_args if arg not in args]
    if missing_args:
        return {"error": f"Missing required arguments: {', '.join(missing_args)}"}
    return None


def format_resource_content(content: str) -> dict[str, Any]:
    """Format content for a resource.

    Args:
        content (str): The content to format.

    Returns:
        Dict[str, Any]: Formatted resource.

    """
    return {"content": content}


async def main():
    """Initialize and run the MCP server."""
    logger.info("Starting Cursor Rules MCP Server")

    # Create server instance
    server = MCPServer()

    # Register handlers
    server.register_handler("list_resources", handle_list_resources)
    server.register_handler("read_resource", handle_read_resource)
    server.register_handler("list_prompts", handle_list_prompts)
    server.register_handler("get_prompt", handle_get_prompt)
    server.register_handler("execute_tool", handle_execute_tool)

    # Run server using standard input/output transport
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
