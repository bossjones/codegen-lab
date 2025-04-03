#!/usr/bin/env python
# pyright: reportPrivateImportUsage=false

# Copyright (c) 2020 Nekokatt
# Copyright (c) 2021-present davfsa
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Generate the code reference pages.

This script generates API reference documentation pages for the codegen_lab project using mkdocstrings.
It recursively scans through Python modules and creates corresponding markdown files with API documentation.

Based on https://mkdocstrings.github.io/recipes/#generate-pages-on-the-fly

Key features:
- Generates markdown files for each Python module in codegen_lab
- Creates a navigation structure for documentation
- Handles special cases for __init__.py files
- Ignores internal and private modules
- Generates a summary file for navigation

Example:
    Running this script will generate markdown files in the 'docs/api-reference' directory:
    ```bash
    python gen_ref_pages.py
    ```

Note:
    This script assumes it's run from the project root directory and expects
    the 'codegen_lab' package in the src directory.
"""

from __future__ import annotations

import pathlib
from typing import Any, TextIO

import mkdocs_gen_files
from mkdocs_gen_files.nav import Nav  # type: ignore # Nav is actually exported

# Initialize the navigation structure
nav: Nav = mkdocs_gen_files.Nav()

# Define key paths
PACKAGE_PATH = pathlib.Path("src/codegen_lab")
DOCS_OUTPUT_PATH = pathlib.Path("docs/api-reference")

def process_module_path(path: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path, pathlib.Path, tuple[str, ...], bool]:
    """Process a module path and return relevant path information.

    Args:
        path: The path to the Python module file.

    Returns:
        A tuple containing:
        - module_path: Path relative to package root without extension
        - doc_path: Path for the markdown file
        - full_doc_path: Complete path including api-reference directory
        - parts: Tuple of path components
        - index: Boolean indicating if this is an index module
    """
    # Get path relative to the package root
    module_path = path.relative_to(PACKAGE_PATH.parent).with_suffix("")
    doc_path = module_path.with_suffix(".md")
    full_doc_path = DOCS_OUTPUT_PATH / doc_path
    parts = tuple(module_path.parts)
    index = False

    # Handle __init__.py files
    if parts[-1] == "__init__":
        index = True
        parts = parts[:-1]
        doc_path = doc_path.with_name("index.md")
        full_doc_path = full_doc_path.with_name("index.md")

    return module_path, doc_path, full_doc_path, parts, index

def write_module_page(fd: TextIO, parts: tuple[str, ...], index: bool) -> None:
    """Write the module documentation page content.

    Args:
        fd: The file descriptor to write to.
        parts: Tuple of path components forming the module name.
        index: Boolean indicating if this is an index module.
    """
    full_name = ".".join(parts)
    fd.write(
        "---\n"
        f"title: `{full_name}`\n"
        f"description: {full_name} - API reference\n"
        "---\n"
        f"# `{full_name}`\n"
        f"::: {full_name}\n"
    )

    if index:
        fd.write("    options:\n")
        fd.write("      members: false\n")

def write_summary(nav_items: Any) -> None:
    """Write the summary markdown file for navigation.

    Args:
        nav_items: Navigation items from mkdocs_gen_files.Nav.
    """
    with mkdocs_gen_files.open(DOCS_OUTPUT_PATH / "summary.md", "w") as nav_file:
        nav_file.write("# API Reference\n\n")
        for item in nav_items:
            path = pathlib.Path(item.filename).with_suffix("")

            if path.name == "index":
                path = path.parent

            full_name = ".".join(path.parts)
            nav_file.write("    " * item.level + f"* [{full_name}]({item.filename})\n")

def ensure_output_directory() -> None:
    """Ensure the output directory exists."""
    DOCS_OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

def main() -> None:
    """Main function to generate API reference documentation."""
    ensure_output_directory()

    # Process all Python files in the codegen_lab package
    for path in sorted(PACKAGE_PATH.rglob("*.py")):
        # Skip internal modules
        if "internal" in path.parts:
            continue

        # Process the module path
        module_path, doc_path, full_doc_path, parts, index = process_module_path(path)

        # Skip private modules
        if not index and parts[-1].startswith("_"):
            continue

        # Add to navigation
        nav[parts] = doc_path.as_posix()

        # Generate the module documentation page
        with mkdocs_gen_files.open(full_doc_path, "w") as fd:
            write_module_page(fd, parts, index)

        mkdocs_gen_files.set_edit_path(full_doc_path, pathlib.Path("..", path))

    # Generate the summary file
    write_summary(nav.items())

if __name__ == "__main__":
    main()
