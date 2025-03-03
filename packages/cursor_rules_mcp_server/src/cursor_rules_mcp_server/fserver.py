import json
import os
import pathlib
import re
import subprocess
from typing import Any, Dict, List, Optional, Set, Tuple

import spacy
import yaml
from jinja2 import Template
from mcp.server.fastmcp import Context, FastMCP, Image
from pydantic import Field


class CursorRulesGenerator:

    """Enhanced generator for Cursor rules with NLP and project analysis capabilities.

    This class provides functionality to generate customized Cursor rules based on
    project descriptions and analysis of project structure. It uses NLP techniques
    to match project requirements with appropriate rule templates.

    Attributes:
        nlp: A spaCy NLP model for text processing
        template_dir: Directory path where rule templates are stored
        templates: Dictionary of loaded templates with their metadata
        tech_keywords: Dictionary mapping technologies to related keywords

    """

    def __init__(self) -> None:
        """Initialize the CursorRulesGenerator with NLP model and templates."""
        # Initialize NLP model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # If model isn't available, download it
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")

        # Template directory
        self.template_dir = pathlib.Path("hack/drafts/cursor_rules")
        self.template_dir.mkdir(parents=True, exist_ok=True)

        # Load templates
        self.templates = self._load_templates()

        # Define technology keywords for better matching
        self.tech_keywords = {
            "react": ["react", "jsx", "component", "hooks", "redux", "frontend"],
            "typescript": ["typescript", "ts", "static typing", "interfaces", "type-safe"],
            "python": ["python", "django", "flask", "fastapi", "pytest", "pip"],
            "nodejs": ["node", "express", "npm", "javascript", "backend", "server"],
            "golang": ["go", "golang", "gorm", "goroutine", "concurrency"],
            "java": ["java", "spring", "maven", "gradle", "jvm"],
        }

    def _load_templates(self) -> dict[str, dict[str, Any]]:
        """Load all template files with metadata from the template directory.

        Each template should have a YAML front matter with metadata. The front matter
        is expected to be enclosed between '---' markers at the beginning of the file.

        Returns:
            A dictionary mapping template names to their content and metadata.
            Format: {template_name: {'content': str, 'metadata': dict}}

        """
        templates = {}

        for template_file in self.template_dir.glob("*.mdc"):
            with open(template_file) as f:
                content = f.read()

                # Parse YAML front matter if present
                metadata = {}
                if content.startswith('---'):
                    end_idx = content.find('---', 3)
                    if end_idx != -1:
                        yaml_content = content[3:end_idx].strip()
                        try:
                            metadata = yaml.safe_load(yaml_content)
                            content = content[end_idx+3:].strip()
                        except yaml.YAMLError:
                            # If YAML parsing fails, assume no front matter
                            pass

                templates[template_file.stem] = {
                    'content': content,
                    'metadata': metadata
                }

        return templates

    def _analyze_project(self, project_path: str) -> dict[str, Any]:
        """Analyze project directory to gather context information.

        Scans the project directory to identify technologies, dependencies,
        and file structure. Detects common configuration files and makes
        inferences about the technology stack.

        Args:
            project_path: Path to the project directory to analyze

        Returns:
            A dictionary containing analysis results with keys:
            - file_count: Total number of files
            - technologies: List of detected technologies
            - dependencies: List of project dependencies
            - file_extensions: Count of files by extension
            - project_structure: Information about project structure

        """
        context = {
            'file_count': 0,
            'technologies': [],
            'dependencies': [],
            'project_structure': {}
        }

        if not project_path or not os.path.exists(project_path):
            return context

        # Count files by extension
        file_extensions = {}

        for root, _, files in os.walk(project_path):
            for file in files:
                _, ext = os.path.splitext(file)
                if ext:
                    file_extensions[ext] = file_extensions.get(ext, 0) + 1
                context['file_count'] += 1

                # Check for specific config files to identify technologies
                if file == 'package.json':
                    try:
                        with open(os.path.join(root, file)) as f:
                            package_data = json.load(f)
                            deps = list(package_data.get('dependencies', {}).keys())
                            dev_deps = list(package_data.get('devDependencies', {}).keys())
                            context['dependencies'].extend(deps + dev_deps)

                            # Check for React
                            if 'react' in deps:
                                context['technologies'].append('react')
                            # Check for Node
                            if 'express' in deps:
                                context['technologies'].append('nodejs')
                    except:
                        pass

                elif file == 'requirements.txt':
                    try:
                        with open(os.path.join(root, file)) as f:
                            packages = [line.strip().split('==')[0] for line in f if line.strip()]
                            context['dependencies'].extend(packages)
                            context['technologies'].append('python')
                    except:
                        pass

                elif file == 'tsconfig.json':
                    context['technologies'].append('typescript')

                elif file == 'go.mod':
                    context['technologies'].append('golang')

                elif file in ['pom.xml', 'build.gradle']:
                    context['technologies'].append('java')

        # Determine dominant file types
        if file_extensions:
            context['file_extensions'] = file_extensions

            # Make technology inferences based on file extensions
            if '.tsx' in file_extensions or '.jsx' in file_extensions:
                if 'react' not in context['technologies']:
                    context['technologies'].append('react')
            if '.ts' in file_extensions:
                if 'typescript' not in context['technologies']:
                    context['technologies'].append('typescript')
            if '.py' in file_extensions:
                if 'python' not in context['technologies']:
                    context['technologies'].append('python')
            if '.go' in file_extensions:
                if 'golang' not in context['technologies']:
                    context['technologies'].append('golang')
            if '.java' in file_extensions:
                if 'java' not in context['technologies']:
                    context['technologies'].append('java')

        # Remove duplicates
        context['technologies'] = list(set(context['technologies']))
        context['dependencies'] = list(set(context['dependencies']))

        return context

    def _find_best_template(self, project_description: str, project_context: dict[str, Any]) -> tuple[str, float]:
        """Use NLP to find the best matching template based on project description and context.

        Analyzes the project description and context to find the most appropriate
        template. Uses a combination of technology matching and keyword relevance
        to calculate a confidence score for each template.

        Args:
            project_description: Textual description of the project
            project_context: Dictionary containing project analysis results

        Returns:
            A tuple containing (template_content, confidence_score)
            where confidence_score is a float between 0 and 1

        """
        if not self.templates:
            # Create a default template if none exist
            return self._create_default_template(), 0.5

        # Process the project description with spaCy
        doc = self.nlp(project_description.lower())

        # Extract key technologies mentioned
        mentioned_techs = set()
        highest_score = 0
        best_template_name = None

        # Check for technology keywords in the description
        # This helps identify technologies even if they're not explicitly detected in the project
        for tech, keywords in self.tech_keywords.items():
            for keyword in keywords:
                if keyword in project_description.lower():
                    mentioned_techs.add(tech)

        # Also consider technologies detected from project analysis
        for tech in project_context.get('technologies', []):
            mentioned_techs.add(tech)

        # Score each template based on technology match and keyword relevance
        for template_name, template_data in self.templates.items():
            metadata = template_data.get('metadata', {})
            template_techs = set(metadata.get('technologies', []))

            # Calculate score based on technology match
            # Higher score when more technologies match between template and project
            match_count = len(mentioned_techs.intersection(template_techs))
            technology_score = match_count / max(len(template_techs), 1) if template_techs else 0

            # Calculate score based on keyword relevance
            # Higher score when more template keywords appear in the project description
            keyword_score = 0
            template_keywords = metadata.get('keywords', [])
            if template_keywords:
                matches = sum(1 for keyword in template_keywords if keyword.lower() in project_description.lower())
                keyword_score = matches / len(template_keywords)

            # Weight both scores - technology match is weighted more heavily (70%)
            # This weighting can be adjusted based on preference
            final_score = 0.7 * technology_score + 0.3 * keyword_score

            if final_score > highest_score:
                highest_score = final_score
                best_template_name = template_name

        # If no good match found, use first template or create default
        if not best_template_name or highest_score < 0.2:
            if self.templates:
                best_template_name = list(self.templates.keys())[0]
            else:
                return self._create_default_template(), 0.5

        return self.templates[best_template_name]['content'], highest_score

    def _create_default_template(self) -> str:
        """Create a basic default template when no templates are available.

        Generates a generic template with placeholders for project name and
        conditional sections for common technologies.

        Returns:
            A string containing the default template content

        """
        return """// Default Cursor Rules Template
// Generated for {{project_name}}

// Basic editing rules
editing {
  // Auto-format on save
  on save {
    format
  }

  // Common shortcuts
  shortcut "ctrl+alt+c" {
    insertText "// TODO: "
  }
}

// {{tech_stack}} specific rules
technology {
  {{#if has_typescript}}
  // TypeScript rules
  typescript {
    // Add types to function parameters
    hint add types
  }
  {{/if}}

  {{#if has_react}}
  // React rules
  react {
    // Suggest component optimizations
    hint optimize renders
  }
  {{/if}}
}

// Project-specific rules
project {
  // Custom rules for {{project_name}}
  // Add your specific rules here
}
"""

    def _render_template(self, template_content: str, context: dict[str, Any]) -> str:
        """Render the template with the provided context using Jinja2.

        Processes conditional blocks in the template (Handlebars-style)
        before rendering with Jinja2. Supports {{#if variable}}...{{/if}}
        syntax for conditional content.

        Args:
            template_content: The template string to render
            context: Dictionary of variables to use in rendering

        Returns:
            The rendered template as a string

        """
        # Add conditional helpers (similar to Handlebars style)
        def _process_conditionals(content: str, context: dict[str, Any]) -> str:
            """Process Handlebars-style conditional blocks in the template.

            Args:
                content: Template content with conditional blocks
                context: Context variables for evaluation

            Returns:
                Processed content with conditionals evaluated

            """
            # Process {{#if variable}} blocks
            pattern = r'{{#if ([^}]+)}}(.*?){{/if}}'

            def replace_if(match):
                var_name = match.group(1).strip()
                content = match.group(2)

                if context.get(var_name):
                    return content
                return ''

            # Apply all conditional replacements
            return re.sub(pattern, replace_if, content, flags=re.DOTALL)

        # Pre-process conditionals
        preprocessed = _process_conditionals(template_content, context)

        # Render with Jinja2
        template = Template(preprocessed)
        return template.render(**context)

    def _validate_rules(self, rules_content: str) -> tuple[bool, list[str]]:
        """Basic validation of Cursor rules syntax.

        Performs syntax checks on the generated rules:
        - Checks for balanced braces
        - Verifies presence of recommended sections
        - Detects unclosed string literals

        Args:
            rules_content: The rules content to validate

        Returns:
            A tuple (is_valid, error_messages) where:
            - is_valid: Boolean indicating if validation passed
            - error_messages: List of error messages if validation failed

        """
        errors = []

        # Check for unbalanced braces - a common syntax error in rules files
        open_braces = rules_content.count('{')
        close_braces = rules_content.count('}')

        if open_braces != close_braces:
            errors.append(f"Unbalanced braces: {open_braces} opening vs {close_braces} closing")

        # Check for basic section structure
        recommended_sections = ['editing', 'technology', 'project']
        missing_sections = []
        for section in recommended_sections:
            if section not in rules_content:
                missing_sections.append(section)

        if missing_sections:
            errors.append(f"Missing recommended sections: {', '.join(missing_sections)}")

        # Check for unclosed string literals
        lines = rules_content.split('\n')
        for i, line in enumerate(lines):
            # Skip comments
            if line.strip().startswith('//'):
                continue

            # Check for unclosed quotes
            quote_count = line.count('"')
            if quote_count % 2 != 0:
                errors.append(f"Unclosed string on line {i+1}: {line}")

        return len(errors) == 0, errors

    def _split_into_files(self, rules_content: str) -> dict[str, str]:
        """Split the rules content into multiple files based on sections.

        Extracts top-level sections from the rules content and creates
        separate files for each section.

        Args:
            rules_content: The complete rules content to split

        Returns:
            A dictionary mapping filenames to content for each section

        """
        files = {}

        # Extract main sections using regex pattern
        # This complex pattern matches nested braces to properly extract sections
        section_pattern = r'(\w+)\s*{([^{]*(?:{[^{]*(?:{[^}]*}[^{]*)*}[^{]*)*)'
        sections = re.findall(section_pattern, rules_content, re.DOTALL)

        for section_name, section_content in sections:
            filename = f"{section_name}.cursor-rules"
            content = f"{section_name} {{{section_content}}}"
            files[filename] = content

        return files

    def generate_rules(self, project_description: str, project_path: str | None = None,
                       output_format: str = "single") -> str:
        """Create custom Cursor rules based on project description and context.

        Main entry point for generating Cursor rules. Analyzes the project,
        selects an appropriate template, renders it with project context,
        validates the result, and outputs in the requested format.

        Args:
            project_description: Textual description of the project
            project_path: Optional path to project directory for analysis
            output_format: Output format - 'single' for one file or 'multiple' for separate files

        Returns:
            Generated rules content or a summary of generated files

        """
        # Step 1: Analyze project if path provided to gather context
        project_context = self._analyze_project(project_path) if project_path else {}

        # Step 2: Find best matching template based on project description and context
        template_content, confidence = self._find_best_template(project_description, project_context)

        # Step 3: Extract project name from path or use default
        project_name = "MyProject"
        if project_path:
            project_name = os.path.basename(os.path.abspath(project_path))

        # Step 4: Prepare context for template rendering with all relevant project information
        context = {
            'project_name': project_name,
            'tech_stack': project_description,
            'project_context': project_context,
            # Convenience flags for common technologies to simplify template conditionals
            'has_typescript': 'typescript' in project_context.get('technologies', []),
            'has_react': 'react' in project_context.get('technologies', []),
            'has_python': 'python' in project_context.get('technologies', []),
            'dependencies': project_context.get('dependencies', []),
            'file_extensions': project_context.get('file_extensions', {})
        }

        # Step 5: Render template with the prepared context
        generated_rules = self._render_template(template_content, context)

        # Step 6: Validate the generated rules for syntax errors
        is_valid, errors = self._validate_rules(generated_rules)
        if not is_valid:
            # If validation fails, add warning comments to the output
            error_messages = "\n".join([f"- {error}" for error in errors])
            generated_rules = f"""// WARNING: Generated rules have validation issues:
// {error_messages}
// Please review and fix these issues.

{generated_rules}"""

        # Step 7: Handle output format based on user preference
        if output_format.lower() == "multiple":
            # Split into multiple files - one per top-level section
            rule_files = self._split_into_files(generated_rules)

            # Create output directory in the standard Cursor rules location
            output_dir = pathlib.Path(".cursor/rules")
            output_dir.mkdir(parents=True, exist_ok=True)

            # Write each section to a separate file
            for filename, content in rule_files.items():
                file_path = output_dir / filename
                with open(file_path, 'w') as f:
                    f.write(content)

            # Return summary of generated files
            return f"Generated {len(rule_files)} rule files in .cursor/rules/:\n" + \
                   "\n".join([f"- {filename}" for filename in rule_files.keys()])
        else:
            # Return single file content for 'single' format
            return generated_rules


# Set up FastMCP server
mcp = FastMCP(
    name="mcp-cursor-rules",
    instructions="I can help you generate custom Cursor rules for your project. Provide a description of your project and optionally a path to analyze."
)

@mcp.tool()
def generate_rules(
    project_description: str = Field(description="Describe your project (tech stack, structure, etc)"),
    project_path: str = Field(description="Optional path to project directory for analysis", default=""),
    output_format: str = Field(description="Output format: 'single' for one file, 'multiple' for separate rule files", default="single"),
    ctx: Context = None
) -> str:
    """Create custom Cursor rules based on project setup.

    This tool generates customized Cursor rules for a project based on its description
    and optional analysis of the project directory structure. It can output rules as
    a single file or split them into multiple files by section.

    Args:
        project_description: Description of the project including technologies and structure
        project_path: Optional path to the project directory for automated analysis
        output_format: Format for output - 'single' or 'multiple'
        ctx: FastMCP context for logging

    Returns:
        Generated rules content or a summary of generated files

    """
    if ctx:
        ctx.info(f"Generating Cursor rules for project: {project_description[:50]}...")
        if project_path:
            ctx.info(f"Analyzing project directory: {project_path}")

    generator = CursorRulesGenerator()

    result = generator.generate_rules(
        project_description=project_description,
        project_path=project_path if project_path else None,
        output_format=output_format
    )

    if ctx:
        ctx.info("Rules generation complete!")

    return result

@mcp.tool()
def preview_template(template_name: str = Field(description="Name of the template to preview")) -> str:
    """Preview a specific rule template.

    Args:
        template_name: Name of the template to preview

    Returns:
        The content of the requested template

    """
    generator = CursorRulesGenerator()

    if not generator.templates:
        return "No templates found. Please create templates in the hack/drafts/cursor_rules directory."

    if template_name not in generator.templates:
        available = ", ".join(generator.templates.keys())
        return f"Template '{template_name}' not found. Available templates: {available}"

    return generator.templates[template_name]['content']

@mcp.tool()
def list_templates() -> str:
    """List all available rule templates.

    Returns:
        A formatted list of available templates with their metadata

    """
    generator = CursorRulesGenerator()

    if not generator.templates:
        return "No templates found. Please create templates in the hack/drafts/cursor_rules directory."

    result = "Available templates:\n\n"
    for name, data in generator.templates.items():
        metadata = data.get('metadata', {})
        techs = ", ".join(metadata.get('technologies', ['any']))
        keywords = ", ".join(metadata.get('keywords', []))

        result += f"- {name}\n"
        result += f"  Technologies: {techs}\n"
        if keywords:
            result += f"  Keywords: {keywords}\n"
        result += "\n"

    return result

# For direct execution
if __name__ == "__main__":
    mcp.run()
