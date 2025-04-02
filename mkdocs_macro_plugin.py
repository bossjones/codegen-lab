"""
Macro definitions for https://mkdocs-macros-plugin.readthedocs.io/

This module provides macro functions for use with the mkdocs-macros-plugin.
It enables dynamic content generation and template rendering in MkDocs pages.
"""
# pyright: reportUnusedFunction=false

import os
from collections.abc import Callable
from textwrap import dedent
from typing import Any, Dict, List, Optional

from jinja2 import Environment

SIGNATURE: str = "mkdocs_macro_plugin"


def define_env(env: Environment) -> None:
    """Define macros for the mkdocs-macros-plugin environment.

    This function serves as the entry point for registering custom macros
    with the mkdocs-macros-plugin. It receives the plugin environment and
    decorates functions to make them available as macros in MkDocs pages.

    Args:
        env: The mkdocs-macros-plugin environment object that provides access
            to the configuration and page context.
    """
    # activate trace
    chatter: Callable[..., None] = env.start_chatting(SIGNATURE)

    @env.macro
    def include_file(filename: str, start_line: int = 0, end_line: int | None = None) -> str:
        """Include a file's contents with optional line range selection.

        Include a file, optionally indicating start_line and end_line
        (start counting from 0). The path is relative to the top directory
        of the documentation project.

        Args:
            filename: The path to the file to include, relative to the project directory
            start_line: The line number to start including from (0-based index)
            end_line: The line number to end including at (0-based index, exclusive)

        Returns:
            str: The content of the file between start_line and end_line

        Example:
            ```markdown
            {{ include_file("docs/example.md", start_line=5, end_line=10) }}
            ```
        """
        chatter("Including:", filename)
        full_filename = os.path.join(env.project_dir, filename)
        with open(full_filename) as f:
            lines = f.readlines()
        line_range = lines[start_line:end_line]
        return "\n".join(line_range)

    @env.macro
    def doc_env() -> dict[str, Any]:
        """Document the environment by returning visible attributes.

        Returns a dictionary containing all visible attributes of the environment
        object (those not starting with '_' or 'register').

        Returns:
            Dict[str, Any]: A dictionary mapping attribute names to their values
                           for all visible environment attributes.

        Example:
            ```markdown
            {{ doc_env() }}
            ```
        """
        return {
            name: getattr(env, name) for name in dir(env) if not (name.startswith("_") or name.startswith("register"))
        }

    @env.macro
    def render_with_page_template(page_template: str) -> str:
        """Render a page using a template from the templates directory.

        This macro loads a template file from the templates directory and
        processes it through the MkDocs markdown pipeline, allowing for
        dynamic content generation based on templates.

        Args:
            page_template: The name of the template file (without extension)
                         to load from the templates directory.

        Returns:
            str: The rendered markdown content after template processing.

        Example:
            ```markdown
            {{ render_with_page_template("project") }}
            ```

        For more detailed example usages, see:
          - streamlit-outline-display.md
          - streamlit-dcai-image-describe.md
          - streamlit-dcai-vortex-insights

        Raises:
            FileNotFoundError: If the template file does not exist
            IOError: If there are issues reading the template file
        """
        with open(f"templates/{page_template}.jinja") as template_file:
            return env.conf.plugins.on_page_markdown(
                template_file.read(),
                page=env.page,
                config=env.conf,
                files=[],
            )


def on_post_build(env: Environment) -> None:
    """Post-build hook for mkdocs-macros-plugin.

    This function is called after the MkDocs build process completes.
    It can be used to perform cleanup tasks or post-processing operations.

    Args:
        env: The mkdocs-macros-plugin environment object that provides access
            to the configuration and page context.
    """
    # activate trace
    chatter: Callable[..., None] = env.start_chatting(SIGNATURE)
    chatter("This means `on_post_build(env)` works")
