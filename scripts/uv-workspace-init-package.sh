#!/bin/bash
# This script initializes a new package in the UV workspace

set -euo pipefail

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <package-name>"
    exit 1
fi

name="$1"
package_dir="packages/${name}"
src_dir="${package_dir}/src/$(echo ${name} | tr '-' '_')"

# Create package directory structure
mkdir -p "${src_dir}"

# Create pyproject.toml
echo "Creating pyproject.toml for ${name}"
cat > "${package_dir}/pyproject.toml" << EOF
[project]
name = "${name}"
version = "0.1.0"
description = "${name} package"
readme = "README.md"
authors = [
    { name = "Malcolm Jones", email = "bossjones@theblacktonystark.com" }
]
requires-python = ">=3.12"
dependencies = [
    "better-exceptions>=0.3.3",
]

[build-system]
requires = ["setuptools>=61"]
build-backend = "setuptools.build_meta"

[tool.setuptools]
package-dir = {"" = "src"}
packages = ["$(echo ${name} | tr '-' '_')"]
EOF

# Create __init__.py
echo "Creating __init__.py for ${name}"
cat > "${src_dir}/__init__.py" << EOF
"""${name} package."""

__version__ = "0.1.0"
EOF

# Create README.md
echo "Creating README.md for ${name}"
cat > "${package_dir}/README.md" << EOF
# ${name}

Description of ${name} package.
EOF

echo "Package ${name} initialized successfully!"
echo "Don't forget to add workspace dependency in root pyproject.toml:"
echo "[tool.uv.sources]"
echo "${name} = { workspace = true }"
echo "Then run: make uv-workspace-lock"
