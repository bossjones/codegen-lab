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

# Function to check if required binaries are available
check_required_binaries() {
  local missing_binaries=()

  # List of required binaries
  local required_bins=("uv" "git" "gh" "awk" "python" "twine", "just")

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
uv sync --frozen

echo "-- Building package --"
uv build
echo "-- Contents of . --"
ls -ahl
echo
echo "-- Contents of ./dist --"
ls -ahl dist

echo "===== UPDATING VERSION IN REPOSITORY ====="
echo "-- Calculating new development version --"
new_version="$(uv run python scripts/ci/increase_version_number.py "${VERSION}")"

echo "-- Setting up git --"
git fetch origin
git checkout -f main

echo "-- Bumping to development version (${new_version}) --"
# Update version in pyproject.toml
$SED_CMD -i "s/^version = \".*\"/version = \"${new_version}\"/" pyproject.toml || (echo "Failed to update version in pyproject.toml!" && exit 1)

echo "-- Pushing to repository --"
git commit -am "Bump to development version (${new_version})"
git push

echo "===== CREATING GITHUB RELEASE ====="
echo "-- Creating release v${VERSION} --"
# Use GitHub CLI to create a release
if command -v gh &> /dev/null; then
    gh release create "v${VERSION}" --generate-notes
    echo "GitHub release v${VERSION} created successfully!"
else
    echo "GitHub CLI not installed. Please create release manually with:"
    echo "gh release create \"v${VERSION}\" --generate-notes"
fi

# Uncomment the following section if you want to publish to PyPI
# echo "===== PUBLISHING TO PYPI ====="
# if [ -z ${UV_PUBLISH_USERNAME+x} ]; then echo '$UV_PUBLISH_USERNAME environment variable is missing' && exit 1; fi
# if [ -z "${UV_PUBLISH_USERNAME}" ]; then echo '$UV_PUBLISH_USERNAME environment variable is empty' && exit 1; fi
# if [ -z ${UV_PUBLISH_PASSWORD+x} ]; then echo '$UV_PUBLISH_PASSWORD environment variable is missing' && exit 1; fi
# if [ -z "${UV_PUBLISH_PASSWORD}" ]; then echo '$UV_PUBLISH_PASSWORD environment variable is empty' && exit 1; fi
#
# echo "-- Publishing to PyPI --"
# uv run twine upload -u "${UV_PUBLISH_USERNAME}" -p "${UV_PUBLISH_PASSWORD}" dist/*

echo "===== RELEASE COMPLETED SUCCESSFULLY ====="
echo "Version ${VERSION} has been released!"
echo "GitHub Release: https://github.com/bossjones/codegen-lab/releases/tag/v${VERSION}"
