import json
import os
import pathlib
import re
import subprocess

# Additional libraries for enhanced functionality
import spacy
import yaml
from jinja2 import Template
from mcp.server.fastmcp import FastMCP
from pydantic import Field


class CursorRulesGenerator:
    """Enhanced generator for Cursor rules with NLP and project analysis capabilities."""

    def __init__(self):
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

    def _load_templates(self) -> dict[str, dict]:
        """Load all template files with metadata from the template directory.
        Each template should have a YAML front matter with metadata.
        """
        templates = {}

        for template_file in self.template_dir.glob("*.mdc"):
            with open(template_file) as f:
                content = f.read()

                # Parse YAML front matter if present
                metadata = {}
                if content.startswith("---"):
                    end_idx = content.find("---", 3)
                    if end_idx != -1:
                        yaml_content = content[3:end_idx].strip()
                        try:
                            metadata = yaml.safe_load(yaml_content)
                            content = content[end_idx + 3 :].strip()
                        except yaml.YAMLError:
                            # If YAML parsing fails, assume no front matter
                            pass

                templates[template_file.stem] = {"content": content, "metadata": metadata}

        return templates

    def _analyze_project(self, project_path: str) -> dict:
        """Analyze project directory to gather context information.
        """
        context = {"file_count": 0, "technologies": [], "dependencies": [], "project_structure": {}}

        if not project_path or not os.path.exists(project_path):
            return context

        # Count files by extension
        file_extensions = {}

        for root, _, files in os.walk(project_path):
            for file in files:
                _, ext = os.path.splitext(file)
                if ext:
                    file_extensions[ext] = file_extensions.get(ext, 0) + 1
                context["file_count"] += 1

                # Check for specific config files to identify technologies
                if file == "package.json":
                    try:
                        with open(os.path.join(root, file)) as f:
                            package_data = json.load(f)
                            deps = list(package_data.get("dependencies", {}).keys())
                            dev_deps = list(package_data.get("devDependencies", {}).keys())
                            context["dependencies"].extend(deps + dev_deps)

                            # Check for React
                            if "react" in deps:
                                context["technologies"].append("react")
                            # Check for Node
                            if "express" in deps:
                                context["technologies"].append("nodejs")
                    except:
                        pass

                elif file == "requirements.txt":
                    try:
                        with open(os.path.join(root, file)) as f:
                            packages = [line.strip().split("==")[0] for line in f if line.strip()]
                            context["dependencies"].extend(packages)
                            context["technologies"].append("python")
                    except:
                        pass

                elif file == "tsconfig.json":
                    context["technologies"].append("typescript")

                elif file == "go.mod":
                    context["technologies"].append("golang")

                elif file in ["pom.xml", "build.gradle"]:
                    context["technologies"].append("java")

        # Determine dominant file types
        if file_extensions:
            context["file_extensions"] = file_extensions

            # Make technology inferences based on file extensions
            if ".tsx" in file_extensions or ".jsx" in file_extensions:
                if "react" not in context["technologies"]:
                    context["technologies"].append("react")
            if ".ts" in file_extensions:
                if "typescript" not in context["technologies"]:
                    context["technologies"].append("typescript")
            if ".py" in file_extensions:
                if "python" not in context["technologies"]:
                    context["technologies"].append("python")
            if ".go" in file_extensions:
                if "golang" not in context["technologies"]:
                    context["technologies"].append("golang")
            if ".java" in file_extensions:
                if "java" not in context["technologies"]:
                    context["technologies"].append("java")

        # Remove duplicates
        context["technologies"] = list(set(context["technologies"]))
        context["dependencies"] = list(set(context["dependencies"]))

        return context

    def _find_best_template(self, project_description: str, project_context: dict) -> tuple[str, float]:
        """Use NLP to find the best matching template based on project description and context.
        Returns template content and confidence score.
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
        for tech, keywords in self.tech_keywords.items():
            for keyword in keywords:
                if keyword in project_description.lower():
                    mentioned_techs.add(tech)

        # Also consider technologies detected from project analysis
        for tech in project_context.get("technologies", []):
            mentioned_techs.add(tech)

        # Score each template
        for template_name, template_data in self.templates.items():
            metadata = template_data.get("metadata", {})
            template_techs = set(metadata.get("technologies", []))

            # Calculate score based on technology match
            match_count = len(mentioned_techs.intersection(template_techs))
            technology_score = match_count / max(len(template_techs), 1) if template_techs else 0

            # Calculate score based on keyword relevance
            keyword_score = 0
            template_keywords = metadata.get("keywords", [])
            if template_keywords:
                matches = sum(1 for keyword in template_keywords if keyword.lower() in project_description.lower())
                keyword_score = matches / len(template_keywords)

            # Weight both scores (can be adjusted)
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

        return self.templates[best_template_name]["content"], highest_score

    def _create_default_template(self) -> str:
        """Create a basic default template when no templates are available"""
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

    def _render_template(self, template_content: str, context: dict) -> str:
        """Render the template with the provided context using Jinja2.
        """

        # Add conditional helpers (similar to Handlebars style)
        def _process_conditionals(content, context):
            # Process {{#if variable}} blocks
            pattern = r"{{#if ([^}]+)}}(.*?){{/if}}"

            def replace_if(match):
                var_name = match.group(1).strip()
                content = match.group(2)

                if context.get(var_name):
                    return content
                return ""

            # Apply all conditional replacements
            return re.sub(pattern, replace_if, content, flags=re.DOTALL)

        # Pre-process conditionals
        preprocessed = _process_conditionals(template_content, context)

        # Render with Jinja2
        template = Template(preprocessed)
        return template.render(**context)

    def _validate_rules(self, rules_content: str) -> tuple[bool, list[str]]:
        """Basic validation of Cursor rules syntax.
        Returns (is_valid, error_messages).
        """
        errors = []

        # Check for unbalanced braces
        open_braces = rules_content.count("{")
        close_braces = rules_content.count("}")

        if open_braces != close_braces:
            errors.append(f"Unbalanced braces: {open_braces} opening vs {close_braces} closing")

        # Check for basic section structure
        required_sections = ["editing", "technology", "project"]
        for section in required_sections:
            if section not in rules_content:
                errors.append(f"Missing recommended section: '{section}'")

        # Check for unclosed string literals
        lines = rules_content.split("\n")
        for i, line in enumerate(lines):
            # Skip comments
            if line.strip().startswith("//"):
                continue

            # Check for unclosed quotes
            quote_count = line.count('"')
            if quote_count % 2 != 0:
                errors.append(f"Unclosed string on line {i + 1}: {line}")

        return len(errors) == 0, errors

    def _split_into_files(self, rules_content: str) -> dict[str, str]:
        """Split the rules content into multiple files based on sections.
        Returns a dictionary mapping filenames to content.
        """
        files = {}

        # Extract main sections
        section_pattern = r"(\w+)\s*{([^{]*(?:{[^{]*(?:{[^}]*}[^{]*)*}[^{]*)*)"
        sections = re.findall(section_pattern, rules_content, re.DOTALL)

        for section_name, section_content in sections:
            filename = f"{section_name}.cursor-rules"
            content = f"{section_name} {{{section_content}}}"
            files[filename] = content

        return files

    def generate_rules(
        self, project_description: str, project_path: str | None = None, output_format: str = "single"
    ) -> str:
        """Create custom Cursor rules based on project description and context.
        """
        # Analyze project if path provided
        project_context = self._analyze_project(project_path) if project_path else {}

        # Find best matching template
        template_content, confidence = self._find_best_template(project_description, project_context)

        # Extract project name from path or use default
        project_name = "MyProject"
        if project_path:
            project_name = os.path.basename(os.path.abspath(project_path))

        # Prepare context for template rendering
        context = {
            "project_name": project_name,
            "tech_stack": project_description,
            "project_context": project_context,
            "has_typescript": "typescript" in project_context.get("technologies", []),
            "has_react": "react" in project_context.get("technologies", []),
            "has_python": "python" in project_context.get("technologies", []),
            "dependencies": project_context.get("dependencies", []),
            "file_extensions": project_context.get("file_extensions", {}),
        }

        # Render template
        generated_rules = self._render_template(template_content, context)

        # Validate rules
        is_valid, errors = self._validate_rules(generated_rules)
        if not is_valid:
            error_messages = "\n".join([f"- {error}" for error in errors])
            generated_rules = f"""// WARNING: Generated rules have validation issues:
// {error_messages}
// Please review and fix these issues.

{generated_rules}"""

        # Handle output format
        if output_format.lower() == "multiple":
            # Split into multiple files
            rule_files = self._split_into_files(generated_rules)

            # Create output directory
            output_dir = pathlib.Path(".cursor/rules")
            output_dir.mkdir(parents=True, exist_ok=True)

            # Write each file
            for filename, content in rule_files.items():
                file_path = output_dir / filename
                with open(file_path, "w") as f:
                    f.write(content)

            # Return summary
            return f"Generated {len(rule_files)} rule files in .cursor/rules/:\n" + "\n".join(
                [f"- {filename}" for filename in rule_files.keys()]
            )
        else:
            # Return single file content
            return generated_rules


# Set up FastMCP server
mcp = FastMCP("Cursor Rules Generator")


@mcp.tool()
def generate_rules(
    project_description: str = Field(description="Describe your project (tech stack, structure, etc)"),
    project_path: str = Field(description="Optional path to project directory for analysis", default=""),
    output_format: str = Field(
        description="Output format: 'single' for one file, 'multiple' for separate rule files", default="single"
    ),
) -> str:
    """Create custom Cursor rules based on project setup"""
    generator = CursorRulesGenerator()
    return generator.generate_rules(
        project_description=project_description,
        project_path=project_path if project_path else None,
        output_format=output_format,
    )


# For direct execution
if __name__ == "__main__":
    mcp.run()
