#!/bin/sh
# cz-release.sh - Creates a GitHub release for the current version using Commitizen
#
# DESCRIPTION:
#   This script automates the GitHub release creation process by:
#   - Verifying GitHub CLI installation and authentication
#   - Determining the current version from Commitizen
#   - Checking tag existence locally and remotely
#   - Pushing tag if needed
#   - Creating a GitHub release with auto-generated release notes
#
# REQUIREMENTS:
#   - gh (GitHub CLI)
#   - uv (Python package manager)
#   - commitizen (cz)
#   - git
#
# USAGE:
#   ./scripts/ci/cz-release.sh
#
# NOTE:
#   This script is typically run after cz-prepare-release.sh and the release PR
#   has been merged to create the official GitHub release.
#
# EXIT CODES:
#   0 - Success
#   1 - Various error conditions (see error messages)
#     - GitHub CLI not found
#     - GitHub CLI not authenticated
#     - Version determination failed
#     - Release creation failed
#     - Git tag operations failed

set -e

echo "===== GITHUB RELEASE CREATION ====="

# Check for GitHub CLI
if ! command -v gh >/dev/null; then
    echo "❌ GitHub CLI (gh) not found"
    exit 1
fi

# Verify authentication
if ! gh auth status -h github.com 2>/dev/null; then
    echo "❌ GitHub CLI not authenticated"
    exit 1
fi

echo "-- Determining current version --"
VERSION=$(uv run cz version -p | tr -d '\n')
if [ -z "${VERSION}" ]; then
    echo "❌ Failed to determine current version"
    exit 1
fi
echo "✅ Current version: ${VERSION}"

# Check if tag exists locally
echo "-- Checking tag status --"
if ! git rev-parse "v${VERSION}" >/dev/null 2>&1; then
    echo "❌ Tag v${VERSION} does not exist locally"
    exit 1
fi

# Check if tag exists on remote
if ! git ls-remote --exit-code --tags origin "refs/tags/v${VERSION}" >/dev/null 2>&1; then
    echo "-- Pushing tag v${VERSION} to remote --"
    if ! git push origin "v${VERSION}"; then
        echo "❌ Failed to push tag v${VERSION} to remote"
        exit 1
    fi
    echo "✅ Successfully pushed tag v${VERSION} to remote"
fi

echo "-- Creating release v${VERSION} --"
if ! gh release create "v${VERSION}" --generate-notes; then
    echo "❌ Release creation failed"
    exit 1
fi

echo "🎉 Successfully created release v${VERSION}"
