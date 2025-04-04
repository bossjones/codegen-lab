#!/bin/sh
# Copyright (c) 2023-present Malcolm Jones
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
set -e

# Set DRY_RUN=1 for dry run mode
DRY_RUN=${DRY_RUN:-1}  # Default to dry run mode

# Function to check if required binaries are available
check_required_binaries() {
  local missing_binaries=()

  # List of required binaries
  local required_bins=("uv" "git" "gh" "awk" "python" "just")

  # Add OS-specific requirements
  if [[ "$OSTYPE" == "darwin"* ]]; then
    required_bins+=("gsed" "ggrep")
  else
    required_bins+=("sed" "grep")
  fi

  # Check each required binary
  for bin in "${required_bins[@]}"; do
    if ! command -v $bin &> /dev/null; then
      missing_binaries+=("$bin")
    fi
  done

  # Report any missing binaries
  if [ ${#missing_binaries[@]} -ne 0 ]; then
    echo "ERROR: The following required binaries are missing:"
    for bin in "${missing_binaries[@]}"; do
      echo "  - $bin"
    done
    echo "Please install them before running this script."
    exit 1
  fi

  echo "All required binaries are available."
}

# Check for required binaries
check_required_binaries

# Get the appropriate sed/grep commands for the current OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    SED_CMD="gsed"
    GREP_CMD="ggrep"
else
    SED_CMD="sed"
    GREP_CMD="grep"
fi

# Check for unprocessed changelog fragments
if [ "$(find changes/*.*.md 2>/dev/null | wc -l)" != "0" ]; then
  echo "Cannot create release if CHANGELOG fragment files exist under 'changes/'!" && exit 1
fi

echo "Defined environment variables"
env | grep -oP "^[^=]+" | sort

# Check if VERSION is provided or extract from pyproject.toml
if [ -z ${VERSION+x} ]; then
  echo "VERSION environment variable not provided, extracting from pyproject.toml"
  VERSION=$($GREP_CMD -h '^version = ".*"' pyproject.toml | $SED_CMD 's/^version = "\(.*\)"/\1/')
  if [ -z "$VERSION" ]; then
    echo "Error: Could not extract version from pyproject.toml" && exit 1
  fi
  echo "Extracted version: $VERSION"
else
  if [ -z "${VERSION}" ]; then
    echo '$VERSION environment variable is empty' && exit 1
  fi

  # Verify the version in pyproject.toml matches VERSION
  pyproject_version=$($GREP_CMD -h '^version = ".*"' pyproject.toml | $SED_CMD 's/^version = "\(.*\)"/\1/')
  if [ -z "${pyproject_version}" ]; then
    echo "Version not found in pyproject.toml!" && exit 1
  fi

  if [ "${pyproject_version}" != "${VERSION}" ]; then
    echo "Version in pyproject.toml does not match the version this release is for! [pyproject_version='${pyproject_version}'; VERSION='${VERSION}']" && exit 1
  fi
fi

# Get the current git reference
ref="$(git rev-parse HEAD)"
echo "Current git reference: ${ref}"

echo "===== BUILDING PACKAGE ====="
# Install dependencies
echo "-- Installing dependencies --"
if [ "$DRY_RUN" -eq 1 ]; then
    echo "Would execute: uv sync --frozen"
else
    uv sync --frozen
fi

echo "-- Building package --"
if [ "$DRY_RUN" -eq 1 ]; then
    echo "Would execute: uv build"
    echo "Would list contents of . and ./dist"
else
    uv build
    echo "-- Contents of . --"
    ls -ahl
    echo
    echo "-- Contents of ./dist --"
    ls -ahl dist
fi

echo "===== UPDATING VERSION IN REPOSITORY ====="
echo "-- Calculating new development version --"
if [ "$DRY_RUN" -eq 1 ]; then
    echo "Would execute: uv run python scripts/ci/increase_version_number.py \"${VERSION}\""
    new_version="${VERSION}-dev0"  # Placeholder for dry run
    echo "Placeholder new development version: ${new_version}"
else
    new_version="$(uv run python scripts/ci/increase_version_number.py "${VERSION}")"
    echo "New development version: ${new_version}"
fi

echo "-- Setting up git --"
# Retrieve the latest information about the remote repository without modifying local files
if [ "$DRY_RUN" -eq 1 ]; then
    echo "Would execute: git fetch origin"
    echo "Would execute: git checkout -f main"
else
    git fetch origin
    # Force checkout to the main branch, discarding any local changes that might exist
    git checkout -f main
fi

echo "-- Bumping to development version (${new_version}) --"
# Update version in pyproject.toml
if [ "$DRY_RUN" -eq 1 ]; then
    echo "Would execute: $SED_CMD -i \"s/^version = \".*\"/version = \"${new_version}\"/' pyproject.toml"
else
    $SED_CMD -i "s/^version = \".*\"/version = \"${new_version}\"/" pyproject.toml || (echo "Failed to update version in pyproject.toml!" && exit 1)
fi

echo "-- Pushing to repository --"
if [ "$DRY_RUN" -eq 1 ]; then
    echo "Would execute: git commit -am \"Bump to development version (${new_version})\""
    echo "Would execute: git push"
else
    git commit -am "Bump to development version (${new_version})"
    git push
fi

echo "===== CREATING GITHUB RELEASE ====="
echo "-- Creating release v${VERSION} --"
# Use GitHub CLI to create a release
if command -v gh &> /dev/null; then
    if [ "$DRY_RUN" -eq 1 ]; then
        echo "Would execute: gh release create \"v${VERSION}\" --generate-notes"
    else
        gh release create "v${VERSION}" --generate-notes
        echo "GitHub release v${VERSION} created successfully!"
    fi
else
    echo "GitHub CLI not installed. Please create release manually with:"
    echo "gh release create \"v${VERSION}\" --generate-notes"
fi

echo "===== RELEASE COMPLETED SUCCESSFULLY ====="
echo "Version ${VERSION} has been released!"
if [ "$DRY_RUN" -eq 1 ]; then
    echo "This was a DRY RUN. No changes were actually made."
else
    echo "GitHub Release: https://github.com/bossjones/codegen-lab/releases/tag/v${VERSION}"
fi
