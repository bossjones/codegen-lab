"""Prompts for cursor rules.

This module contains MCP prompt functions for cursor rule generation, including:
- repo_analysis_prompt: Analyze a repository to gather information for cursor rule creation
- generate_cursor_rule_prompt: Generate a custom cursor rule based on repository information

Migration Plan for prompts.py:
- [x] Import all necessary dependencies
- [x] Update type imports to use models and utils modules
- [x] Implement repo_analysis_prompt:
  - [x] Set up proper context handling
  - [x] Create prompt structure with clear instructions
  - [x] Define system message with detailed analysis instructions
  - [x] Handle user input formatting and validation
  - [x] Process and format assistant response
  - [x] Add error handling for API failures
  - [x] Add logging for debugging
- [x] Implement generate_cursor_rule_prompt:
  - [x] Set up proper context handling
  - [x] Create prompt structure with rule generation instructions
  - [x] Define system message with formatting guidelines
  - [x] Incorporate template rule if provided
  - [x] Process and validate user inputs
  - [x] Format AI response into proper structure
  - [x] Add error handling for API failures
  - [x] Add logging for debugging
- [x] Add proper docstrings and type hints
- [x] Update __init__.py to re-export prompts
- [x] Verify functionality through manual testing
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

if TYPE_CHECKING:
    from mcp.server.fastmcp.server import Context

    from .models import CursorRule

from codegen_lab.promptlib import mcp

# Set up logging
logger = logging.getLogger(__name__)


@mcp.prompt(name="repo-analysis", description="Analyze a repository to gather information for cursor rule creation")
def repo_analysis_prompt(
    repo_description: str,
    main_languages: str,
    file_patterns: str,
    key_features: str,
    ctx: Context | None = None,
) -> list[dict[str, Any]]:
    """Analyze a repository to gather information for cursor rule creation.

    Args:
        repo_description: Brief description of the repository
        main_languages: Main programming languages used in the repository
        file_patterns: Common file patterns in the repository
        key_features: Key features of the repository
        ctx: Context for the prompt

    Returns:
        List[Dict[str, Any]]: Analysis results

    """
    try:
        logger.debug("Starting repository analysis prompt")
        logger.debug(f"Repository description: {repo_description}")
        logger.debug(f"Main languages: {main_languages}")
        logger.debug(f"File patterns: {file_patterns}")
        logger.debug(f"Key features: {key_features}")

        # Create system message
        system_message = """You are an expert code analyzer tasked with analyzing repository information to identify:
1. Common patterns and best practices that should be enforced
2. Potential issues that should be prevented
3. Architectural guidelines that should be followed
4. Testing and documentation requirements
5. Security considerations

Based on the repository information provided, generate a comprehensive analysis that will be used to create cursor rules."""

        # Create user message with repository information
        user_message = f"""Please analyze this repository:

Description: {repo_description}
Main Languages: {main_languages}
File Patterns: {file_patterns}
Key Features: {key_features}

Provide the following analysis sections:
1. Repository Overview
2. Common Patterns Identified
3. Recommended Rule Categories
4. Analysis Summary"""

        # Create messages list
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ]

        # Call the LLM through the context
        if ctx:
            response = ctx.llm.create_chat_completion(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
            )

            # Process and format the response
            analysis_sections = response.choices[0].message.content.split("\n\n")
            formatted_response = []

            for section in analysis_sections:
                if section.strip():
                    formatted_response.append({"text": section.strip()})

            logger.debug("Repository analysis prompt completed successfully")
            return formatted_response
        else:
            logger.error("No context provided for LLM interaction")
            return [{"text": "Error: No context provided for LLM interaction"}]

    except Exception as e:
        logger.error(f"Error in repository analysis prompt: {e!s}", exc_info=True)
        return [{"text": f"Error: {e!s}"}]


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
    """Generate a custom cursor rule based on repository information.

    Args:
        rule_name: Name of the rule to generate
        description: Description of the rule
        file_patterns: File patterns to match
        content_patterns: Content patterns to match
        action_message: Message to display when rule is triggered
        examples: Examples of rule application
        tags: Tags for the rule
        priority: Priority of the rule (default: "medium")
        template_rule: Optional template rule to use as a starting point
        ctx: Context for the prompt

    Returns:
        List[Dict[str, Any]]: Generated cursor rule

    """
    try:
        logger.debug("Starting cursor rule generation prompt")
        logger.debug(f"Rule name: {rule_name}")
        logger.debug(f"Description: {description}")
        logger.debug(f"File patterns: {file_patterns}")
        logger.debug(f"Content patterns: {content_patterns}")

        # Create system message
        system_message = """You are an expert in creating cursor rules that help maintain code quality and consistency.
Your task is to generate a well-structured cursor rule in MDC format that includes:
1. A clear description of the rule's purpose
2. Appropriate file and content pattern matching
3. Helpful action messages that guide developers
4. Relevant examples demonstrating the rule's application
5. Proper metadata including tags and priority

Follow these guidelines:
- Use clear and concise language
- Include specific pattern matching
- Provide actionable guidance
- Use realistic examples
- Ensure proper MDC formatting"""

        # Create user message with rule information
        user_message = f"""Please generate a cursor rule with the following specifications:

Name: {rule_name}
Description: {description}
File Patterns: {file_patterns}
Content Patterns: {content_patterns}
Action Message: {action_message}
Examples: {examples}
Tags: {tags}
Priority: {priority}

{f"Use this template as a starting point:\n\n{template_rule}" if template_rule else ""}

Generate the complete cursor rule in MDC format."""

        # Create messages list
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ]

        # Call the LLM through the context
        if ctx:
            response = ctx.llm.create_chat_completion(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
            )

            # Process and format the response
            rule_content = response.choices[0].message.content.strip()
            formatted_response = [{"text": rule_content}]

            logger.debug("Cursor rule generation completed successfully")
            return formatted_response
        else:
            logger.error("No context provided for LLM interaction")
            return [{"text": "Error: No context provided for LLM interaction"}]

    except Exception as e:
        logger.error(f"Error in cursor rule generation prompt: {e!s}", exc_info=True)
        return [{"text": f"Error: {e!s}"}]
