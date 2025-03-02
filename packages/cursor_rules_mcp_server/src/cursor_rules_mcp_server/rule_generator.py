"""Rule generator for cursor rules MCP server.

This module provides functionality to generate and customize cursor rules
based on repository analysis and user input.
"""

import re
from pathlib import Path
from typing import Any

from .repository_analyzer import analyze_repository, get_rule_template


class RuleGenerator:
    """Generates and customizes cursor rules based on analysis and templates.

    This class provides methods to create, customize, and validate cursor rules
    based on repository analysis and predefined templates.

    Attributes:
        repo_path (Path): Path to the repository root directory.
        analysis_results (Optional[Dict[str, Any]]): Cached analysis results.

    """

    def __init__(self, repo_path: str | None = None):
        """Initialize the rule generator.

        Args:
            repo_path (Optional[str]): Path to the repository to analyze. If None,
                rule generation won't include repository-specific customizations.

        """
        self.repo_path = Path(repo_path).expanduser().resolve() if repo_path else None
        self.analysis_results: dict[str, Any] | None = None

    def analyze_repo(self) -> dict[str, Any]:
        """Analyze the repository and cache the results.

        Returns:
            Dict[str, Any]: Analysis results.

        Raises:
            ValueError: If no repository path was provided during initialization.

        """
        if not self.repo_path:
            raise ValueError("No repository path provided for analysis")

        if not self.analysis_results:
            self.analysis_results = analyze_repository(str(self.repo_path))

        return self.analysis_results

    def get_suggested_rules(self) -> list[dict[str, Any]]:
        """Get suggested rules based on repository analysis.

        Returns:
            List[Dict[str, Any]]: List of suggested rule metadata.

        Raises:
            ValueError: If no repository path was provided during initialization.

        """
        analysis = self.analyze_repo()
        return analysis.get("suggested_rules", [])

    def generate_rule(self, rule_name: str, customizations: dict[str, Any] | None = None) -> str:
        """Generate a cursor rule based on a template and customizations.

        Args:
            rule_name (str): Name of the rule template to use.
            customizations (Optional[Dict[str, Any]]): Custom values to override
                template defaults. May include title, description, filters, etc.

        Returns:
            str: The generated rule content.

        Raises:
            ValueError: If the rule template could not be found.

        """
        # Get repository analysis if available
        repo_analysis = self.analysis_results if self.repo_path else None

        # Get the base template
        template = get_rule_template(rule_name, repo_analysis)
        if not template:
            raise ValueError(f"Rule template '{rule_name}' not found")

        # Apply customizations if provided
        if customizations:
            for key, value in customizations.items():
                # Simple string replacement for now - can be enhanced for more complex customizations
                placeholder = "{" + key + "}"
                if placeholder in template:
                    template = template.replace(placeholder, str(value))

        return template

    def validate_rule(self, rule_content: str) -> tuple[bool, list[str]]:
        """Validate cursor rule content for correctness.

        Args:
            rule_content (str): The rule content to validate.

        Returns:
            Tuple[bool, List[str]]: A tuple containing a boolean indicating if the
                rule is valid, and a list of validation messages/errors.

        """
        errors = []

        # Check basic structure
        if not rule_content.strip():
            errors.append("Rule content is empty")
            return False, errors

        # Check required sections
        required_sections = [
            "<rule>", "</rule>",
            "name:", "description:",
            "filters:", "actions:"
        ]

        for section in required_sections:
            if section not in rule_content:
                errors.append(f"Missing required section: {section}")

        # Check for valid rule name
        name_match = re.search(r"name:\s*(.+)$", rule_content, re.MULTILINE)
        if not name_match:
            errors.append("Rule must have a valid name")
        else:
            name = name_match.group(1).strip()
            if not name or len(name) < 3:
                errors.append("Rule name must be at least 3 characters")

        # Check for valid filters
        filters_section = re.search(r"filters:(.*?)(?:actions:|examples:|metadata:)",
                                  rule_content, re.DOTALL | re.MULTILINE)
        if filters_section:
            filters_text = filters_section.group(1)
            if "type:" not in filters_text:
                errors.append("Filters must specify a type")

        # Check for valid actions
        actions_section = re.search(r"actions:(.*?)(?:examples:|metadata:|</rule>)",
                                  rule_content, re.DOTALL | re.MULTILINE)
        if actions_section:
            actions_text = actions_section.group(1)
            if "type:" not in actions_text:
                errors.append("Actions must specify a type")

        return len(errors) == 0, errors

    def generate_multiple_rules(self, rule_names: list[str]) -> dict[str, str]:
        """Generate multiple cursor rules from a list of rule names.

        Args:
            rule_names (List[str]): Names of rule templates to generate.

        Returns:
            Dict[str, str]: Mapping of rule names to generated rule content.

        """
        result = {}
        for rule_name in rule_names:
            try:
                rule_content = self.generate_rule(rule_name)
                result[rule_name] = rule_content
            except ValueError:
                # Skip rules that couldn't be generated
                continue

        return result

    def customize_rule_for_repo(self, rule_name: str) -> str:
        """Customize a rule specifically for the analyzed repository.

        Args:
            rule_name (str): Name of the rule template to customize.

        Returns:
            str: The customized rule content.

        Raises:
            ValueError: If no repository path was provided or rule template not found.

        """
        if not self.repo_path:
            raise ValueError("No repository path provided for customization")

        analysis = self.analyze_repo()

        # Create customizations based on repository analysis
        customizations = {
            "title": f"{rule_name.replace('-', ' ').title()} for {self.repo_path.name}",
        }

        # Add more specific customizations based on repository type and languages
        repo_type = analysis.get("repo_type", "generic")
        languages = analysis.get("languages", {})
        primary_language = next(iter(languages.keys())) if languages else None

        if primary_language:
            customizations["context_pattern"] = f"{primary_language.lower()}|{repo_type}"

        # Generate and return the customized rule
        return self.generate_rule(rule_name, customizations)

    def export_rules_to_files(self, rules: dict[str, str], output_dir: str) -> list[str]:
        """Export generated rules to markdown files.

        Args:
            rules (Dict[str, str]): Mapping of rule names to rule content.
            output_dir (str): Directory to save rule files.

        Returns:
            List[str]: List of paths to created rule files.

        """
        output_path = Path(output_dir).expanduser().resolve()
        output_path.mkdir(parents=True, exist_ok=True)

        created_files = []
        for rule_name, rule_content in rules.items():
            file_path = output_path / f"{rule_name}.md"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(rule_content)
            created_files.append(str(file_path))

        return created_files


def generate_rule(rule_name: str, repo_path: str | None = None,
                 customizations: dict[str, Any] | None = None) -> str:
    """Generate a cursor rule based on a template and optional customizations.

    Args:
        rule_name (str): Name of the rule template to use.
        repo_path (Optional[str]): Path to the repository for customizations.
        customizations (Optional[Dict[str, Any]]): Custom values to override defaults.

    Returns:
        str: The generated rule content.

    """
    generator = RuleGenerator(repo_path)
    return generator.generate_rule(rule_name, customizations)


def analyze_and_suggest_rules(repo_path: str) -> dict[str, Any]:
    """Analyze a repository and suggest appropriate cursor rules.

    Args:
        repo_path (str): Path to the repository to analyze.

    Returns:
        Dict[str, Any]: Analysis results with suggested rules.

    """
    generator = RuleGenerator(repo_path)
    analysis = generator.analyze_repo()
    return {
        "analysis": analysis,
        "suggested_rules": analysis.get("suggested_rules", [])
    }


def validate_rule_content(rule_content: str) -> tuple[bool, list[str]]:
    """Validate cursor rule content for correctness.

    Args:
        rule_content (str): The rule content to validate.

    Returns:
        Tuple[bool, List[str]]: A tuple containing a boolean indicating if the
            rule is valid, and a list of validation messages/errors.

    """
    generator = RuleGenerator()
    return generator.validate_rule(rule_content)
