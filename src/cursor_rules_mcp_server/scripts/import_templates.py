"""Script to import cursor rule templates from the hack/drafts/cursor_rules directory.

This script can be run to import existing cursor rule templates from the
hack/drafts/cursor_rules directory into the database used by the MCP server.
"""

import os
import sys
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add parent directory to path to allow importing from parent package
sys.path.insert(0, str(Path(__file__).parents[2]))

from cursor_rules_mcp_server.models import RuleTemplate
from cursor_rules_mcp_server.server import CursorRulesDatabase

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("import_templates")


def parse_template_file(file_path: Path) -> Optional[Dict[str, Any]]:
    """Parse a template file into a dictionary.

    Args:
        file_path (Path): Path to the template file.

    Returns:
        Optional[Dict[str, Any]]: Template data dictionary or None if parsing failed.
    """
    logger.info(f"Parsing template file: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract metadata from the filename
        name = file_path.stem.replace(".mdc", "")

        # Basic validation
        if not content or len(content) < 10:
            logger.warning(f"Template file is too small or empty: {file_path}")
            return None

        # Extract title from first heading if available
        title = name.replace("-", " ").title()
        lines = content.split("\n")
        for line in lines:
            if line.startswith("# "):
                title = line[2:].strip()
                break

        # Extract description from first paragraph if available
        description = "Custom cursor rule template"
        for i, line in enumerate(lines):
            if line.startswith("# "):
                for j in range(i+1, len(lines)):
                    if lines[j].strip() and not lines[j].startswith("#"):
                        description = lines[j].strip()
                        break
                break

        # Determine category based on content
        category = "General"
        if "python" in content.lower() or "py" in content.lower():
            category = "Python"
        elif "javascript" in content.lower() or "js" in content.lower():
            category = "JavaScript"
        elif "css" in content.lower() or "html" in content.lower():
            category = "Web"
        elif "code" in content.lower() and "style" in content.lower():
            category = "Code Style"
        elif "develop" in content.lower() or "workflow" in content.lower():
            category = "Workflow"

        return {
            "name": name,
            "title": title,
            "description": description,
            "content": content,
            "category": category,
            "created_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error parsing template file {file_path}: {e}")
        return None


def import_templates(templates_dir: Path, db_path: Optional[str] = None) -> List[RuleTemplate]:
    """Import templates from the templates directory.

    Args:
        templates_dir (Path): Path to the templates directory.
        db_path (Optional[str]): Path to the database file. If None, uses the default path.

    Returns:
        List[RuleTemplate]: List of imported templates.
    """
    logger.info(f"Importing templates from {templates_dir}")

    # Check if directory exists
    if not templates_dir.exists() or not templates_dir.is_dir():
        logger.error(f"Templates directory does not exist: {templates_dir}")
        return []

    # Find template files
    template_files = list(templates_dir.glob("*.md"))
    logger.info(f"Found {len(template_files)} template files")

    # Parse templates
    templates = []
    for file_path in template_files:
        template_data = parse_template_file(file_path)
        if template_data:
            template = RuleTemplate(
                id=0,  # Will be assigned by the database
                name=template_data["name"],
                title=template_data["title"],
                description=template_data["description"],
                content=template_data["content"],
                category=template_data["category"],
                created_at=template_data["created_at"]
            )
            templates.append(template)

    # Import templates to database
    if templates:
        try:
            db = CursorRulesDatabase(db_path)
            imported = []

            for template in templates:
                try:
                    template_id = db.add_rule_template(template)
                    template.id = template_id
                    imported.append(template)
                    logger.info(f"Imported template: {template.name} (ID: {template_id})")
                except sqlite3.IntegrityError:
                    logger.warning(f"Template already exists: {template.name}")
                except Exception as e:
                    logger.error(f"Error importing template {template.name}: {e}")

            return imported
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            return []

    return []


def main():
    """Main entry point for the script."""
    import argparse

    parser = argparse.ArgumentParser(description="Import cursor rule templates")
    parser.add_argument(
        "--templates-dir",
        type=str,
        default="hack/drafts/cursor_rules",
        help="Path to the templates directory"
    )
    parser.add_argument(
        "--db-path",
        type=str,
        help="Path to the database file"
    )

    args = parser.parse_args()

    # Get absolute path to templates directory
    repo_root = Path(__file__).parents[4]
    templates_dir = repo_root / args.templates_dir

    # Import templates
    templates = import_templates(templates_dir, args.db_path)

    logger.info(f"Successfully imported {len(templates)} templates")


if __name__ == "__main__":
    main()
