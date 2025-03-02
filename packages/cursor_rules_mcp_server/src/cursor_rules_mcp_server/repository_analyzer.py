"""Repository structure analyzer for cursor rules MCP server.

This module provides functionality to analyze a repository structure
and suggest cursor rules based on the repository's contents.
"""

import json
import os
from pathlib import Path
from typing import Any


class RepositoryAnalyzer:
    """Analyzes repository structure to suggest cursor rules.

    This class provides methods to scan a repository, detect frameworks,
    languages, file patterns, and suggest cursor rules based on the analysis.

    Attributes:
        repo_path (Path): Path to the repository root directory.
        ignored_dirs (Set[str]): Set of directory names to ignore during scanning.

    """

    def __init__(self, repo_path: str):
        """Initialize the repository analyzer.

        Args:
            repo_path (str): Path to the repository to analyze.

        """
        self.repo_path = Path(repo_path).expanduser().resolve()
        self.ignored_dirs = {
            ".git", ".github", ".vscode", ".idea", "node_modules",
            "venv", ".venv", "__pycache__", ".pytest_cache"
        }

    def analyze(self) -> dict[str, Any]:
        """Perform a full analysis of the repository.

        Returns:
            Dict[str, Any]: A dictionary containing analysis results including:
                - repo_type: The type of repository (web, library, CLI, etc.)
                - languages: Dictionary of languages with file counts
                - frameworks: Detected frameworks/libraries
                - suggested_rules: List of suggested cursor rules

        """
        file_stats = self._collect_file_stats()
        languages = self._detect_languages(file_stats)
        frameworks = self._detect_frameworks(file_stats)
        repo_type = self._determine_repo_type(languages, frameworks, file_stats)

        return {
            "repo_type": repo_type,
            "languages": languages,
            "frameworks": frameworks,
            "file_stats": file_stats,
            "suggested_rules": self._suggest_rules(repo_type, languages, frameworks, file_stats)
        }

    def _collect_file_stats(self) -> dict[str, Any]:
        """Collect file statistics from the repository.

        Returns:
            Dict[str, Any]: Statistics about the repository files.

        """
        result = {
            "file_count": 0,
            "file_types": {},
            "dir_structure": {},
            "special_files": {},
        }

        # Look for special files at the root level
        for special_file in ["package.json", "requirements.txt", "pyproject.toml",
                             "Cargo.toml", "go.mod", "Gemfile", "build.gradle",
                             "pom.xml", "Dockerfile", "docker-compose.yml"]:
            if (self.repo_path / special_file).exists():
                with open(self.repo_path / special_file, encoding='utf-8') as f:
                    try:
                        if special_file == "package.json":
                            data = json.load(f)
                            result["special_files"]["package.json"] = {
                                "name": data.get("name", ""),
                                "dependencies": list(data.get("dependencies", {}).keys()),
                                "devDependencies": list(data.get("devDependencies", {}).keys())
                            }
                        else:
                            result["special_files"][special_file] = True
                    except json.JSONDecodeError:
                        result["special_files"][special_file] = True

        # Collect file statistics
        for root, dirs, files in os.walk(self.repo_path):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if d not in self.ignored_dirs]

            # Get relative path from repository root
            rel_path = os.path.relpath(root, self.repo_path)
            if rel_path == ".":
                rel_path = ""

            # Count files and extensions
            for file in files:
                result["file_count"] += 1
                _, ext = os.path.splitext(file)
                if ext:
                    ext = ext.lower()
                    result["file_types"][ext] = result["file_types"].get(ext, 0) + 1

                # Record directory structure
                path_parts = rel_path.split(os.sep) if rel_path else []
                current_level = result["dir_structure"]
                for part in path_parts:
                    if part not in current_level:
                        current_level[part] = {}
                    current_level = current_level[part]

        return result

    def _detect_languages(self, file_stats: dict[str, Any]) -> dict[str, int]:
        """Detect programming languages used in the repository.

        Args:
            file_stats (Dict[str, Any]): Statistics about repository files.

        Returns:
            Dict[str, int]: Dictionary mapping language names to file counts.

        """
        file_types = file_stats.get("file_types", {})
        languages = {}

        # Map extensions to languages
        extension_to_language = {
            ".py": "Python",
            ".js": "JavaScript",
            ".jsx": "JavaScript",
            ".ts": "TypeScript",
            ".tsx": "TypeScript",
            ".java": "Java",
            ".go": "Go",
            ".rb": "Ruby",
            ".php": "PHP",
            ".rs": "Rust",
            ".c": "C",
            ".cpp": "C++",
            ".h": "C/C++",
            ".hpp": "C++",
            ".cs": "C#",
            ".swift": "Swift",
            ".kt": "Kotlin",
            ".scala": "Scala",
            ".clj": "Clojure",
            ".ex": "Elixir",
            ".exs": "Elixir",
            ".hs": "Haskell",
            ".html": "HTML",
            ".css": "CSS",
            ".scss": "SCSS",
            ".sass": "SASS",
            ".less": "Less",
            ".sh": "Shell",
            ".bat": "Batch",
            ".ps1": "PowerShell",
            ".r": "R",
            ".m": "Objective-C/MATLAB",
            ".mm": "Objective-C++",
            ".sql": "SQL",
            ".md": "Markdown",
            ".rst": "reStructuredText",
            ".json": "JSON",
            ".yml": "YAML",
            ".yaml": "YAML",
            ".toml": "TOML",
            ".xml": "XML",
            ".graphql": "GraphQL",
            ".dart": "Dart",
            ".lua": "Lua",
            ".pl": "Perl",
        }

        for ext, count in file_types.items():
            lang = extension_to_language.get(ext)
            if lang:
                languages[lang] = languages.get(lang, 0) + count

        return dict(sorted(languages.items(), key=lambda x: x[1], reverse=True))

    def _detect_frameworks(self, file_stats: dict[str, Any]) -> dict[str, list[str]]:
        """Detect frameworks and libraries used in the repository.

        Args:
            file_stats (Dict[str, Any]): Statistics about repository files.

        Returns:
            Dict[str, List[str]]: Dictionary mapping language to list of frameworks.

        """
        frameworks = {}
        special_files = file_stats.get("special_files", {})

        # JavaScript/TypeScript frameworks
        if "package.json" in special_files:
            js_frameworks = []
            pkg_data = special_files["package.json"]

            # Check for common frameworks in dependencies
            all_deps = set(pkg_data.get("dependencies", [])) | set(pkg_data.get("devDependencies", []))

            framework_indicators = {
                "react": "React",
                "vue": "Vue.js",
                "angular": "Angular",
                "next": "Next.js",
                "nuxt": "Nuxt.js",
                "svelte": "Svelte",
                "express": "Express.js",
                "koa": "Koa",
                "nest": "NestJS",
                "electron": "Electron",
            }

            for dep in all_deps:
                for indicator, framework_name in framework_indicators.items():
                    if indicator in dep.lower():
                        js_frameworks.append(framework_name)
                        break

            if js_frameworks:
                if "TypeScript" in file_stats.get("languages", {}):
                    frameworks["TypeScript"] = js_frameworks
                else:
                    frameworks["JavaScript"] = js_frameworks

        # Python frameworks
        if "requirements.txt" in special_files or "pyproject.toml" in special_files:
            # TODO: Parse requirements.txt or pyproject.toml to detect frameworks
            # For now, check directory structure for common patterns

            py_frameworks = []
            dir_structure = file_stats.get("dir_structure", {})

            if "django" in str(dir_structure).lower():
                py_frameworks.append("Django")
            if "flask" in str(dir_structure).lower():
                py_frameworks.append("Flask")
            if "fastapi" in str(dir_structure).lower():
                py_frameworks.append("FastAPI")

            if py_frameworks:
                frameworks["Python"] = py_frameworks

        return frameworks

    def _determine_repo_type(
        self,
        languages: dict[str, int],
        frameworks: dict[str, list[str]],
        file_stats: dict[str, Any]
    ) -> str:
        """Determine the repository type based on analysis.

        Args:
            languages (Dict[str, int]): Detected languages with file counts.
            frameworks (Dict[str, List[str]]): Detected frameworks by language.
            file_stats (Dict[str, Any]): Statistics about repository files.

        Returns:
            str: Repository type (web, library, CLI, etc.).

        """
        # Default to 'generic' if we can't determine
        repo_type = "generic"

        special_files = file_stats.get("special_files", {})

        # Check for web applications
        web_frameworks = []
        for lang_frameworks in frameworks.values():
            web_frameworks.extend([
                f for f in lang_frameworks
                if f in ["React", "Vue.js", "Angular", "Next.js", "Nuxt.js", "Django", "Flask", "FastAPI"]
            ])

        if web_frameworks or (languages.get("HTML", 0) > 5):
            repo_type = "web"

        # Check for libraries
        if "pyproject.toml" in special_files or "package.json" in special_files:
            # Look for specific patterns that indicate a library
            if "src" in file_stats.get("dir_structure", {}) and "tests" in file_stats.get("dir_structure", {}):
                repo_type = "library"

        # Check for CLI applications
        if os.path.exists(self.repo_path / "bin") or os.path.exists(self.repo_path / "cli"):
            repo_type = "cli"

        # Check for mobile applications
        if os.path.exists(self.repo_path / "android") or os.path.exists(self.repo_path / "ios"):
            repo_type = "mobile"

        return repo_type

    def _suggest_rules(
        self,
        repo_type: str,
        languages: dict[str, int],
        frameworks: dict[str, list[str]],
        file_stats: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Suggest cursor rules based on repository analysis.

        Args:
            repo_type (str): Type of repository (web, library, CLI, etc.).
            languages (Dict[str, int]): Detected languages with file counts.
            frameworks (Dict[str, List[str]]): Detected frameworks by language.
            file_stats (Dict[str, Any]): Statistics about repository files.

        Returns:
            List[Dict[str, Any]]: List of suggested cursor rules.

        """
        suggested_rules = []

        # Basic rules based on repository type
        if repo_type == "web":
            suggested_rules.append({
                "name": "web-development-workflow",
                "description": "Guides web development tasks and enforces best practices",
                "priority": "high"
            })

        if repo_type == "library":
            suggested_rules.append({
                "name": "library-development-workflow",
                "description": "Enforces library development patterns and documentation",
                "priority": "high"
            })

        # Language-specific rules
        primary_language = next(iter(languages.keys())) if languages else None

        if primary_language == "Python":
            suggested_rules.append({
                "name": "python-code-standards",
                "description": "Enforces PEP 8 standards and Python best practices",
                "priority": "medium"
            })

            if "tests" in file_stats.get("dir_structure", {}):
                suggested_rules.append({
                    "name": "python-testing-practices",
                    "description": "Enforces test coverage and testing patterns",
                    "priority": "medium"
                })

        if primary_language in ("JavaScript", "TypeScript"):
            suggested_rules.append({
                "name": "js-code-standards",
                "description": "Enforces JavaScript/TypeScript best practices",
                "priority": "medium"
            })

            # Framework-specific rules
            js_frameworks = frameworks.get("JavaScript", []) + frameworks.get("TypeScript", [])
            if "React" in js_frameworks:
                suggested_rules.append({
                    "name": "react-patterns",
                    "description": "Enforces React component patterns and best practices",
                    "priority": "medium"
                })
            elif "Vue.js" in js_frameworks:
                suggested_rules.append({
                    "name": "vue-patterns",
                    "description": "Enforces Vue.js component patterns and best practices",
                    "priority": "medium"
                })

        # Documentation rules
        if os.path.exists(self.repo_path / "docs") or len(list(self.repo_path.glob("**/*.md"))) > 5:
            suggested_rules.append({
                "name": "documentation-workflow",
                "description": "Guides documentation tasks and enforces documentation standards",
                "priority": "medium"
            })

        # Add a generic rule for any repository
        suggested_rules.append({
            "name": "incremental-development-workflow",
            "description": "Implements Harper Reed's non-greenfield iterative development workflow",
            "priority": "high"
        })

        return suggested_rules

    def get_rule_template(self, rule_name: str) -> str | None:
        """Get the content for a rule template by name.

        Args:
            rule_name (str): The name of the rule template.

        Returns:
            Optional[str]: The rule template content or None if not found.

        """
        # Base template for cursor rules
        base_template = """# {title}

{description}

<rule>
name: {name}
description: {description}
filters:
  - type: message
    pattern: "{message_pattern}"
  - type: context
    pattern: "{context_pattern}"

actions:
  - type: instructions
    message: |
      {instructions}

examples:
  - input: |
      {example_input}
    output: |
      {example_output}

metadata:
  priority: {priority}
  version: 1.0
</rule>
"""

        # Define templates for different rule types
        templates = {
            "incremental-development-workflow": {
                "title": "Incremental Development Workflow",
                "description": "This rule implements Harper Reed's non-greenfield iterative development workflow.",
                "message_pattern": "(?i)(change|update|add feature|implement|iterate|incrementally)",
                "context_pattern": "existing code|update functionality|maintenance|iteration",
                "instructions": """# Incremental Development Workflow

When implementing changes in an existing codebase:

1. **Understand the Current Context**
   - Analyze relevant parts of the existing codebase
   - Identify patterns and conventions in use
   - Locate the specific components that need changes

2. **Break Down the Changes**
   - Divide the implementation into small, incremental steps
   - Prioritize changes that can be independently tested
   - Create a step-by-step implementation plan

3. **Implement with Constant Testing**
   - Make one small change at a time
   - Test each change thoroughly before proceeding
   - Update tests to match new functionality

4. **Document Changes Thoroughly**
   - Explain what changed and why
   - Update existing documentation
   - Add inline comments for complex logic

5. **Handle Integration Carefully**
   - Ensure changes integrate well with existing code
   - Maintain consistency with the codebase
   - Consider backward compatibility

Always prefer smaller, more focused changes over large rewrites.""",
                "example_input": "I need to add a new feature to display user profiles in our application.",
                "example_output": """I'll help you implement the user profile display feature incrementally.

First, let's understand the current context by examining how user data is currently handled in the application.

Based on the codebase analysis, I recommend breaking down this implementation into these incremental steps:

1. **Analyze Current User Data Model**
   - Existing user data is stored in the database with basic information
   - We'll need to identify what additional profile data is needed

2. **Update Data Models**
   - Add the necessary fields to the user model
   - Update database migrations
   - Add validation for new fields

3. **Implement API Endpoint**
   - Create a new endpoint to fetch profile data
   - Add proper authentication checks
   - Write tests for the endpoint

4. **Create Frontend Components**
   - Implement profile view component
   - Add routing to the profile page
   - Style according to existing design patterns

5. **Connect Frontend to API**
   - Add data fetching logic
   - Implement loading and error states
   - Write tests for the integration

Let's start with step 1 - analyzing the current user data model...""",
                "priority": "high"
            },
            "python-code-standards": {
                "title": "Python Code Standards",
                "description": "This rule enforces PEP 8 standards and Python best practices.",
                "message_pattern": "(?i)(python|code review|code style|formatting|lint)",
                "context_pattern": "python|def|class|import|pep8",
                "instructions": """# Python Code Standards Guidelines

When writing or reviewing Python code, ensure it follows these standards:

1. **PEP 8 Compliance**
   - Use 4 spaces for indentation (not tabs)
   - Maximum line length of 79 characters
   - Use appropriate naming conventions:
     - `lower_case_with_underscores` for functions, methods, variables
     - `CapitalizedWords` for classes
     - `UPPER_CASE_WITH_UNDERSCORES` for constants
   - Two blank lines before top-level function and class definitions
   - One blank line before method definitions

2. **Type Annotations**
   - Add type hints to all function parameters and return values
   - Use appropriate types from the `typing` module
   - Consider using `Optional` for nullable values

3. **Documentation**
   - Add docstrings to all modules, classes, and functions
   - Follow PEP 257 docstring conventions
   - Include Args, Returns, and Raises sections in function docstrings

4. **Code Organization**
   - Organize imports in standard order: standard library, third-party, local
   - Use absolute imports rather than relative when possible
   - Keep functions and methods focused on a single responsibility

5. **Error Handling**
   - Use specific exception types rather than bare `except:`
   - Handle exceptions at the appropriate level
   - Provide meaningful error messages""",
                "example_input": "Could you review this Python function for me?",
                "example_output": """I'll review your Python function according to PEP 8 and Python best practices.

Here are my observations:

1. **Type Annotations**
   - Missing type hints for parameters and return value
   - Should specify return type as `Optional[Dict[str, Any]]`

2. **Docstring**
   - Missing docstring explaining the function's purpose
   - Should include Args, Returns, and Raises sections

3. **Error Handling**
   - Using bare `except:` which catches all exceptions
   - Should catch specific exceptions like `requests.RequestException`

4. **Variable Naming**
   - Variable `res` is too abbreviated, use descriptive name like `response`
   - Constants should be UPPER_CASE

5. **Code Structure**
   - Function is doing too many things at once
   - Consider breaking it into smaller, more focused functions

Here's a revised version with these issues addressed:

```python
def fetch_user_data(user_id: int) -> Optional[Dict[str, Any]]:
    \"\"\"Fetch user data from the API.

    Args:
        user_id: The ID of the user to fetch data for

    Returns:
        Dictionary containing user data if successful, None otherwise

    Raises:
        ValueError: If user_id is negative
    \"\"\"
    if user_id < 0:
        raise ValueError("User ID cannot be negative")

    try:
        response = requests.get(f"{API_BASE_URL}/users/{user_id}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch user data: {e}")
        return None
```

This revised version follows Python best practices with proper type hints, improved naming, better error handling, and clearer documentation.""",
                "priority": "medium"
            },
            "web-development-workflow": {
                "title": "Web Development Workflow",
                "description": "This rule guides web development tasks and enforces best practices.",
                "message_pattern": "(?i)(web|frontend|ui|component|page|route|api)",
                "context_pattern": "html|css|js|frontend|component|api",
                "instructions": """# Web Development Best Practices

When working on web development tasks:

1. **Component Structure**
   - Follow the single responsibility principle
   - Create reusable components for repeated UI elements
   - Maintain a clear component hierarchy

2. **API Integration**
   - Separate API calls from UI components
   - Implement proper error handling and loading states
   - Use consistent data fetching patterns

3. **Styling Approach**
   - Follow the project's CSS methodology (CSS Modules, styled-components, etc.)
   - Maintain a consistent naming convention
   - Ensure responsive design for all screen sizes

4. **Performance Considerations**
   - Optimize images and assets
   - Implement lazy loading for offscreen content
   - Minimize bundle size and network requests

5. **Accessibility**
   - Include proper ARIA attributes
   - Ensure keyboard navigation works correctly
   - Maintain sufficient color contrast
   - Add alt text to images

6. **Testing**
   - Write unit tests for components and utilities
   - Add integration tests for critical user flows
   - Test across different browsers and devices""",
                "example_input": "I need to create a new user dashboard page.",
                "example_output": """I'll help you create a new user dashboard page following web development best practices.

Let's approach this systematically:

1. **Component Planning**
   - Create a main `Dashboard` container component
   - Break it down into logical sub-components:
     - `UserSummary` - displays user info and quick stats
     - `ActivityFeed` - shows recent user activities
     - `MetricsDisplay` - visualizes key metrics with charts
     - `QuickActions` - provides common action buttons

2. **Data Architecture**
   - Create a data fetching service layer in `services/dashboard.js`
   - Implement proper loading states and error handling
   - Cache dashboard data where appropriate

3. **Responsive Design**
   - Design mobile-first, then enhance for larger screens
   - Use flexbox/grid for responsive layouts
   - Define consistent breakpoints

4. **Accessibility**
   - Ensure proper heading hierarchy (h1 → h6)
   - Add ARIA labels to interactive elements
   - Ensure keyboard navigation works between dashboard sections
   - Maintain 4.5:1 color contrast ratio minimum

5. **Performance**
   - Lazy load dashboard sections that aren't immediately visible
   - Implement pagination for the activity feed
   - Optimize image assets

Let's start by creating the main Dashboard component structure:

```jsx
import React, { useState, useEffect } from 'react';
import { UserSummary } from './UserSummary';
import { ActivityFeed } from './ActivityFeed';
import { MetricsDisplay } from './MetricsDisplay';
import { QuickActions } from './QuickActions';
import { fetchDashboardData } from '../services/dashboard';
import './Dashboard.css';

const Dashboard = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dashboardData, setDashboardData] = useState(null);

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setIsLoading(true);
        const data = await fetchDashboardData();
        setDashboardData(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    loadDashboardData();
  }, []);

  if (isLoading) return <div className="dashboard-loading" aria-live="polite">Loading dashboard...</div>;
  if (error) return <div className="dashboard-error" aria-live="assertive">Error: {error}</div>;

  return (
    <main className="dashboard" aria-label="User Dashboard">
      <h1>Your Dashboard</h1>
      <div className="dashboard-grid">
        <UserSummary userData={dashboardData.user} />
        <QuickActions actions={dashboardData.availableActions} />
        <MetricsDisplay metrics={dashboardData.metrics} />
        <ActivityFeed activities={dashboardData.recentActivities} />
      </div>
    </main>
  );
};

export default Dashboard;
```

Would you like me to continue with any specific component, or would you prefer to focus on a particular aspect of the dashboard?""",
                "priority": "high"
            }
        }

        if rule_name in templates:
            template_data = templates[rule_name]
            return base_template.format(**template_data)

        return None


def analyze_repository(repo_path: str) -> dict[str, Any]:
    """Analyze a repository and return detailed information.

    Args:
        repo_path (str): Path to the repository to analyze.

    Returns:
        Dict[str, Any]: Analysis results.

    """
    analyzer = RepositoryAnalyzer(repo_path)
    return analyzer.analyze()


def get_rule_template(rule_name: str, repo_analysis: dict[str, Any] | None = None) -> str | None:
    """Get a cursor rule template by name.

    Args:
        rule_name (str): Name of the rule template.
        repo_analysis (Optional[Dict[str, Any]]): Repository analysis results
            for customizing the template.

    Returns:
        Optional[str]: The rule template content or None if not found.

    """
    # For now, just delegate to the analyzer method
    analyzer = RepositoryAnalyzer("")  # Empty path since we're just using the template method
    return analyzer.get_rule_template(rule_name)
