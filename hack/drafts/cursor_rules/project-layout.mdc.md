---
description: Documentation of the Inspiration Library project structure, organization, and prompt engineering resources
globs: ["**/*.md", "**/*.py", "**/*.mdc"]
---

# Inspiration Library Project Layout

@context {
    "type": "documentation",
    "purpose": "project_structure",
    "format_version": "1.0.0",
    "supported_content_types": [
        "prompts",
        "documentation",
        "examples",
        "implementations"
    ],
    "language": "python",
    "python_version": ">=3.8",
    "supported_models": [
        "claude",
        "gpt",
        "gemini"
    ],
    "recommended_tools": [
        "ruff",
        "mypy",
        "pytest",
        "black",
        "isort"
    ]
}

@structure {
    "primary_components": [
        "prompts",
        "documentation",
        "tests",
        "utils"
    ],
    "key_directories": {
        "prompts": {
            "description": "AI prompt engineering resources",
            "subdirectories": {
                "components": "Reusable prompt components",
                "docs": "Prompt documentation",
                "domains": "Domain-specific prompts",
                "drafts": "Work-in-progress prompts",
                "examples": "Example prompts and use cases",
                "templates": "Template prompts",
                "tests": "Prompt testing resources",
                "utils": "Utility prompts and helpers"
            }
        },
        "docs": "Project documentation",
        "tests": "Test suites and resources",
        "utils": "Utility functions and helpers"
    }
}

# Project Overview

## Introduction

This repository serves as Adobe's central hub for AI-augmented software development, providing a comprehensive library of prompts, workflows, and best practices for leveraging Large Language Models (LLMs) in the development process. The focus is on enhancing developer productivity and creativity through AI collaboration.

Core Features

- **Curated Prompt Collections:** Carefully crafted prompts for different LLMs and use cases
- **AI Workflows:** Step-by-step guides for common development tasks
- **Best Practices:** Guidelines for effective AI collaboration
- **Role-Based Guidance:** Specialized prompts for different development roles
- **Tool Integration:** Optimized workflows for popular AI-powered development tools
- **Domain-Specific Resources:** Targeted prompts for web, backend, mobile, ML, and SRE development

## Directory Structure

```
.
├── CONTRIBUTING.md           # Contribution guidelines
├── README.md                # Project overview and setup instructions
├── docs                     # Project documentation
├── general_guidance.md      # General development guidelines
└── prompts                  # AI prompt engineering resources
    ├── README.md           # Prompts overview
    ├── components          # Reusable prompt components
    │   ├── README.md
    │   ├── functions      # Function-specific prompts
    │   ├── system         # System-level prompts
    │   └── templates      # Template prompts
    ├── docs               # Prompt documentation
    │   ├── README.md
    │   ├── best_practices # Best practices for prompt engineering
    │   ├── guidelines     # General prompt guidelines
    │   └── patterns       # Common prompt patterns
    ├── domains            # Domain-specific prompts
    │   ├── README.md
    │   ├── backend       # Backend development prompts
    │   ├── desktop       # Desktop app development prompts
    │   ├── ide           # IDE-specific prompts
    │   ├── ml            # Machine learning prompts
    │   ├── mobile        # Mobile development prompts
    │   ├── sre           # SRE and DevOps prompts
    │   └── web           # Web development prompts
    ├── drafts            # Draft prompts and WIP
    ├── examples          # Example prompts and use cases
    ├── tests             # Prompt testing resources
    └── utils             # Utility prompts and helpers
```

## Component Overview

@components {
    "description": "Key components and their responsibilities",
    "organization": "Modular structure for maintainability and scalability"
}

### Prompts Directory

<component name="prompts">
    <description>
        Central repository for AI prompt engineering resources, containing reusable components,
        documentation, and domain-specific implementations.
    </description>
    <structure>
        - components/: Core reusable prompt components
        - docs/: Comprehensive prompt documentation
        - domains/: Domain-specific prompt implementations
        - drafts/: Work-in-progress prompts
        - examples/: Example use cases and implementations
        - tests/: Prompt testing and validation
        - utils/: Utility functions and helpers
    </structure>
</component>

### Documentation

<component name="docs">
    <description>
        Project documentation including development phases, architecture decisions,
        and implementation guidelines.
    </description>
    <structure>
        - phases/: Development phase documentation
        - README.md: Documentation overview
    </structure>
</component>

## Best Practices

@best_practices {
    "organization": {
        "documentation": [
            "Keep READMEs up to date in each directory",
            "Use clear, descriptive file names",
            "Follow consistent documentation format",
            "Include examples where appropriate"
        ],
        "prompts": [
            "Organize prompts by domain",
            "Maintain reusable components",
            "Document prompt patterns",
            "Include test cases",
            "Version control prompt iterations",
            "Add context and purpose for each prompt"
        ],
        "code": [
            "Follow Python type hinting",
            "Include comprehensive docstrings",
            "Write unit tests",
            "Use consistent code style"
        ]
    }
}

## Implementation Guidelines

@implementation_rules {
    "prompts": {
        "structure": {
            "format": "MDC (Markdown Configuration)",
            "required_sections": [
                "frontmatter",
                "context",
                "content"
            ],
            "annotations": "Use proper @annotations"
        },
        "documentation": {
            "style": "Clear and concise",
            "examples": "Include practical examples",
            "metadata": "Proper frontmatter"
        }
    }
}

## Validation Rules

@validation {
    "requirements": [
        "All prompts must follow MDC format with proper frontmatter",
        "Each prompt must have clear context and purpose",
        "All prompt components must include usage examples",
        "Domain-specific prompts must include success criteria",
        "Each major directory must have a README.md",
        "All Python tooling must have type hints and docstrings",
        "Tests required for prompt effectiveness validation"
    ],
    "prompt_quality": {
        "clarity": "Clear, unambiguous instructions",
        "completeness": "All necessary context included",
        "modularity": "Reusable components properly separated",
        "versioning": "Track prompt iterations and improvements"
    },
    "tools": {
        "linting": {
            "ruff": "Primary linter for Python tooling",
            "mypy": "Static type checking with strict mode"
        },
        "testing": {
            "pytest": "Test framework for Python components",
            "prompt_validation": "Systematic testing of prompt effectiveness"
        }
    }
}

## Development Workflow

@workflow {
    "guidelines": {
        "prompt_development": {
            "stages": [
                "Draft in prompts/drafts",
                "Peer review and testing",
                "Documentation updates",
                "Move to appropriate domain directory"
            ],
            "iteration": "Track prompt versions and improvements",
            "testing": "Validate with multiple AI models"
        },
        "version_control": {
            "branching": "Feature branches from main",
            "commits": "Clear, descriptive commit messages",
            "pull_requests": "Required for all changes"
        },
        "documentation": {
            "updates": "Required with prompt changes",
            "reviews": "Part of PR process",
            "examples": "Include real-world usage examples"
        }
    }
}

## Project Standards

@standards {
    "prompt_engineering": {
        "format": {
            "style": "MDC (Markdown Configuration)",
            "required_sections": [
                "frontmatter",
                "context",
                "examples",
                "validation"
            ]
        },
        "documentation": {
            "style": "Clear and concise",
            "structure": "Hierarchical organization",
            "examples": "Include practical applications"
        }
    },
    "code_quality": {
        "python": {
            "style_guide": "PEP 8",
            "type_hints": "Required",
            "docstrings": "Google style",
            "max_line_length": 88
        }
    },
    "testing": {
        "prompt_coverage": {
            "minimum_scenarios": 3,
            "validation_criteria": [
                "Clarity of output",
                "Consistency across models",
                "Error handling",
                "Edge cases"
            ]
        },
        "code_coverage": {
            "minimum": "80%",
            "target": "90%"
        }
    }
}

## XML Tag Guidelines

@anthropic_xml_guidelines {
    "purpose": "Enhance prompt documentation with XML tags for better model comprehension",
    "tag_types": {
        "context": {
            "tag": "<context>",
            "usage": "Provide context about the prompt or feature",
            "example": "<context>This prompt helps generate unit tests</context>"
        },
        "implementation": {
            "tag": "<implementation>",
            "usage": "Describe implementation details",
            "example": "<implementation>Uses specific formatting for test generation</implementation>"
        },
        "examples": {
            "tag": "<examples>",
            "usage": "Provide usage examples",
            "example": "<examples>Example prompt with expected output</examples>"
        },
        "thinking": {
            "tag": "<thinking>",
            "usage": "Show step-by-step reasoning process",
            "example": "<thinking>1. Analyze requirements\n2. Generate structure\n3. Add implementation details</thinking>"
        },
        "validation": {
            "tag": "<validation>",
            "usage": "Specify validation criteria",
            "example": "<validation>Test prompt with different models and scenarios</validation>"
        }
    },
    "best_practices": [
        "Use XML tags for critical information that models should focus on",
        "Keep tags focused and concise",
        "Use consistent tag naming",
        "Include validation criteria within tags",
        "Document prompt iterations and improvements"
    ]
}

## Cursor Rules Configuration

@cursor_rules {
    "types": {
        "global": {
            "location": "Cursor Settings > General > Rules for AI",
            "scope": "All projects",
            "purpose": "Define universal AI behavior preferences"
        },
        "project": {
            "location": ".cursor/rules/*.mdc",
            "scope": "Project-specific",
            "purpose": "Granular control over AI behavior in different parts of your project"
        },
        "legacy": {
            "location": ".cursorrules",
            "scope": "Project root",
            "status": "Deprecated",
            "migration": "Migrate to .cursor/rules/ for better organization"
        }
    },
    "features": {
        "semantic_descriptions": "Each rule can include when it should be applied",
        "pattern_matching": "Use glob patterns for file/folder targeting",
        "auto_attachment": "Rules automatically included for matching files",
        "folder_specific": "Different rules for different project areas"
    }
}

### Rule Organization

<implementation>

@version "1.0.0"
@last_updated "2024-02-11"

```
</implementation>

@rule_examples {
    "python_rules": {
        "file": ".cursor/rules/python.mdc",
        "content": """
---
description: Python development rules and standards
globs: ["**/*.py"]
---

@context {
    "type": "development_rules",
    "language": "python",
    "version": ">=3.8"
}

@standards {
    "style": "PEP 8",
    "typing": "Required for all functions",
    "docstrings": "Google style required",
    "testing": "pytest with type annotations"
}
"""
    },
    "prompt_rules": {
        "file": ".cursor/rules/prompts/claude.mdc",
        "content": """
---
description: Claude-specific prompt engineering guidelines
globs: ["prompts/**/*.mdc"]
---

@context {
    "type": "prompt_rules",
    "model": "claude",
    "version": "3.5"
}

@requirements {
    "format": "MDC with XML tags",
    "sections": ["context", "implementation", "validation"],
    "tags": ["thinking", "examples", "validation"]
}
"""
    }
}

@migration_guide {
    "steps": [
        "Create .cursor/rules/ directory in project root",
        "Organize rules by domain/language/purpose",
        "Use .mdc extension for rule files",
        "Include proper frontmatter and globs",
        "Migrate content from .cursorrules if exists"
    ],
    "benefits": [
        "Better organization and maintainability",
        "Granular control over different project areas",
        "Automatic rule application based on file patterns",
        "Improved separation of concerns",
        "Better support for multi-language projects"
    ]
}
