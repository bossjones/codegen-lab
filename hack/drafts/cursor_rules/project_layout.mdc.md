---
description:
globs:
alwaysApply: false
---
# Codegen Lab Project Layout

 Documentation of the Codegen Lab project structure, organization, and Greenfield development process

Rules for understanding and navigating the Codegen Lab project structure.

<rule>
name: project_layout_guide
description: Guide to the Codegen Lab project structure and organization
filters:
  # Match any file in the project
  - type: file_extension
    pattern: ".*"
  # Match project initialization events
  - type: event
    pattern: "file_create"

actions:
  - type: suggest
    message: |
      # Codegen Lab Project Structure

      This repository implements the Greenfield development methodology for AI-augmented software development, following Harper Reed's approach.

      ## Core Features

      - **Greenfield Development Workflow:** Structured process for LLM-assisted development
      - **Documentation Standards:** Guidelines for maintaining spec.md, prompt_plan.md, and todo.md
      - **Execution Best Practices:** Standards for implementing code with LLM assistance
      - **Python Best Practices:** Type hints, comprehensive docstrings, and thorough testing
      - **Cursor Rules Management:** System for organizing and implementing AI behavior rules
      - **UV Workspace Management:** Package organization using UV workspace structure

      ## Directory Structure

      ```
      .
      ├── .cursor/                     # Active cursor rules directory
      │   └── rules/                   # Production cursor rules
      ├── Makefile                     # Build automation
      ├── README.md                    # Project overview and setup instructions
      ├── hack/                        # Development tooling
      │   └── drafts/                  # Work-in-progress resources
      │       └── cursor_rules/        # Staging area for cursor rules
      ├── packages/                    # UV workspace packages
      │   └── cursor-rules-mcp-server/ # Cursor rules MCP server package
      │       ├── pyproject.toml       # Package configuration
      │       └── src/                 # Package source code
      │           └── cursor_rules_mcp_server/ # Package code
      ├── src/                         # Python source code
      │   └── codegen_lab/                 # Core application modules
      ├── tests/                       # Test suites
      │   ├── integration/             # Integration tests
      │   └── unittests/               # Unit tests
      └── docs/                        # Project documentation
      ```

      ## Primary Components

      ### Source Code (`src/`)
      Core Python application code following best practices for type hints, docstrings, and modular organization.

      ### Workspace Packages (`packages/`)
      Modular packages organized in a UV workspace structure, allowing for independent versioning, development, and reuse.

      @uv-workspace.mdc

      ### Tests (`tests/`)
      Comprehensive test suite using pytest for both unit and integration tests, with full type annotations and documentation.

      @python_rules.mdc

      ### Cursor Rules
      Cursor rule definitions that implement the Greenfield development workflow and related standards:
      - `hack/drafts/cursor_rules/`: Development/staging area for cursor rules
      - `.cursor/rules/`: Production cursor rules (deployed via Makefile)

      ## Development Workflow

      ### Greenfield Development
      1. **Idea Honing** - Create spec.md
      2. **Planning** - Create prompt_plan.md and todo.md
      3. **Execution** - Implement plan with testing

      ### Cursor Rules Development
      - Develop and refine cursor rules in `hack/drafts/cursor_rules/`
      - Test rules with actual development tasks
      - Run `make update-cursor-rules` to deploy to `.cursor/rules/`
      - Verify rules are working as expected in production

      ### Workspace Management
      - Create new packages: `make uv-workspace-init-package name=<package-name>`
      - Add dependencies: `make uv-workspace-add-dep package=<package-name>`
      - Update lockfile: `make uv-workspace-lock`
      - Install dependencies: `make uv-workspace-sync`

examples:
  - input: |
      # I'm new to the project, where should I put my Python code?
    output: |
      For core application code, use the `src/codegen_lab/` directory.

      For modular packages that might be reused or published separately, create a new package in the `packages/` directory using:
      ```bash
      make uv-workspace-init-package name=my-new-package
      ```

      This will set up the proper structure with pyproject.toml and src layout.

  - input: |
      # How do I add a new cursor rule?
    output: |
      1. Create a new .mdc.md file in `hack/drafts/cursor_rules/`
      2. Follow the MDC format with frontmatter, rule definition, examples, and metadata
      3. Test the rule in your development workflow
      4. When ready, run `make update-cursor-rules` to deploy to `.cursor/rules/`

metadata:
  priority: high
  version: 1.0
  tags:
    - project-structure
    - organization
    - development-workflow
</rule>

<rule>
name: project_standards
description: Standards for code quality and organization in the Codegen Lab project
filters:
  # Match any file in the project
  - type: file_extension
    pattern: ".*"
  # Match project initialization events
  - type: event
    pattern: "file_create"

actions:
  - type: suggest
    message: |
      # Codegen Lab Project Standards

      ## Python Standards

      - **Code Style**: Follow PEP 8
      - **Type Hints**: Required for all functions and classes
      - **Docstrings**: PEP 257 format required
      - **Max Line Length**: 88 characters
      - **Testing**: pytest with type annotations

      ## Cursor Rules Standards

      - **Format**: MDC (Markdown Configuration)
      - **Required Sections**: frontmatter, rule definition, examples, metadata
      - **Development**: Create in `hack/drafts/cursor_rules/`
      - **Deployment**: Use `make update-cursor-rules` to deploy

      ## Workspace Package Standards

      - **Format**: src layout with pyproject.toml
      - **Required Sections**: name, version, dependencies, development dependencies
      - **Management**: UV workspace commands via Makefile
      - **Dependency Resolution**: Central requirements.lock
      - **Version Control**: Individual package versioning

      ## Validation Requirements

      - All Python code must have type hints
      - Each function and class must have PEP 257 docstrings
      - All code must have corresponding tests
      - Tests must have type annotations
      - Each major directory must have a README.md
      - Cursor rules must follow proper MDC format
      - Workspace packages must follow src layout

examples:
  - input: |
      # What are the requirements for Python code in this project?
    output: |
      Python code in this project must:
      1. Follow PEP 8 style guidelines
      2. Include comprehensive type hints for all functions and classes
      3. Have PEP 257 docstrings for all functions and classes
      4. Be accompanied by pytest tests with type annotations
      5. Follow the src layout for packages

  - input: |
      # How should I structure a new package?
    output: |
      New packages should follow the src layout:
      ```
      package-name/
      ├── pyproject.toml
      ├── src/
      │   └── package_name/
      │       ├── __init__.py
      │       └── module.py
      └── tests/
          └── test_module.py
      ```

      Use `make uv-workspace-init-package name=my-package` to create this structure automatically.

metadata:
  priority: high
  version: 1.0
  tags:
    - standards
    - code-quality
    - organization
</rule>
