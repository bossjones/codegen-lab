#!/bin/sh
# cz-release.sh - Creates a GitHub release for the current version using Commitizen
#
# DESCRIPTION:
#   This script automates the GitHub release creation process by:
#   - Verifying GitHub CLI installation and authentication
#   - Determining the current version from Commitizen
#   - Creating a GitHub release with auto-generated release notes
#
# REQUIREMENTS:
#   - gh (GitHub CLI)
#   - uv (Python package manager)
#   - commitizen (cz)
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

set -e

echo "===== GITHUB RELEASE CREATION ====="

# Check for GitHub CLI
if ! command -v gh >/dev/null; then
    echo "❌ GitHub CLI (gh) not found"
    exit 1
fi

# Verify authentication
if ! gh auth status 2>/dev/null; then
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

echo "-- Creating release v${VERSION} --"
gh release create "v${VERSION}" --generate-notes || {
    echo "❌ Release creation failed"
    exit 1
}

echo "🎉 Successfully created release v${VERSION}"
