"""
Macro definitions for https://mkdocs-macros-plugin.readthedocs.io/

This module provides macro functions for use with the mkdocs-macros-plugin.
It enables dynamic content generation and template rendering in MkDocs pages.
"""

from textwrap import dedent
from typing import Any, Dict, List, Optional


def define_env(env: Any) -> None:
    """Define macros for the mkdocs-macros-plugin environment.

    This function serves as the entry point for registering custom macros
    with the mkdocs-macros-plugin. It receives the plugin environment and
    decorates functions to make them available as macros in MkDocs pages.

    Args:
        env: The mkdocs-macros-plugin environment object that provides access
            to the configuration and page context.
    """

    @env.macro
    def render_with_page_template(page_template: str) -> str:  # type: ignore
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
        """
        with open(f"templates/{page_template}.jinja") as template_file:
            return env.conf.plugins.on_page_markdown(
                template_file.read(),
                page=env.page,
                config=env.conf,
                files=[],
            )
