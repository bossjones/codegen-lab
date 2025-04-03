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

# Get the appropriate sed command for the current OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    SED_CMD="gsed"
else
    SED_CMD="sed"
fi

echo "Defined environment variables"
env | grep -oP "^[^=]+" | sort

# Check if VERSION is provided
if [ -z ${VERSION+x} ]; then echo '$VERSION environment variable is missing' && exit 1; fi
if [ -z "${VERSION}" ]; then echo '$VERSION environment variable is empty' && exit 1; fi

echo "===== UPDATING RELEASE INFORMATION ====="
echo "-- Bumping repository version to ${VERSION} --"

# Update version in pyproject.toml
$SED_CMD -i "s/^version = \".*\"/version = \"${VERSION}\"/" pyproject.toml || (echo "Failed to update version in pyproject.toml!" && exit 1)

echo "===== UPDATING CHANGELOG ====="
echo "-- Installing dependencies --"
# Installing with towncrier group to ensure it's available
uv sync --frozen --dev

echo "-- Running towncrier --"
# Build the changelog from news fragments
uv run towncrier build --yes --version ${VERSION}

echo "===== COMMITTING CHANGES ====="
echo "-- Checkout branch task/prepare-release-${VERSION} --"
git checkout -b "task/prepare-release-${VERSION}"

echo "-- Committing changes --"
git commit -am "Prepare for release of version ${VERSION}"

if [ "${CI}" ]; then
    echo "-- Pushing changes --"
    git push origin "task/prepare-release-${VERSION}"

    echo "-- Creating pull request --"
    # Use GitHub CLI to create PR if installed
    if command -v gh &> /dev/null; then
        gh pr create --title "Prepare for release of version ${VERSION}" \
                     --body "This PR prepares the repository for release of version ${VERSION}." \
                     --base main \
                     --head "task/prepare-release-${VERSION}"
    else
        echo "GitHub CLI not installed. Please create PR manually."
    fi
else
    echo "Changes committed to 'task/prepare-release-${VERSION}'. You can now push the changes and create a pull request"
fi

echo "===== NEXT STEPS ====="
echo "After the PR is merged, create a release with:"
echo "gh release create \"v${VERSION}\" --generate-notes"
echo "or use: just release-create"
