#!/bin/sh
# cz-prepare-release.sh - Automates the release preparation process using Commitizen
#
# DESCRIPTION:
#   This script automates the process of preparing a new release by:
#   - Checking for uncommitted changes
#   - Determining the next version based on conventional commits
#   - Creating a release branch
#   - Bumping version numbers
#   - Running pre-commit hooks
#   - Creating a pull request
#
# REQUIREMENTS:
#   - uv (Python package manager)
#   - commitizen (cz)
#   - pre-commit
#   - gh (GitHub CLI, optional but recommended for PR creation)
#
# USAGE:
#   ./scripts/ci/cz-prepare-release.sh
#
# ENVIRONMENT VARIABLES:
#   PRERELEASE_PHASE - Optional. Set to 'alpha', 'beta', or 'rc' for prerelease versions
#   CI              - Optional. If set, indicates running in CI environment
#
# EXAMPLES:
#   # Standard release
#   ./scripts/ci/cz-prepare-release.sh
#
#   # Beta release
#   PRERELEASE_PHASE=beta ./scripts/ci/cz-prepare-release.sh
#
# EXIT CODES:
#   0 - Success
#   1 - Various error conditions (see error messages)

set -e

echo "===== ENVIRONMENT PRE-CHECKS ====="
# Verify clean working directory
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Stashing uncommitted changes..."
    git stash push --include-untracked --message "Stash for release preparation"
fi

echo "===== CURRENT VERSION CHECK ====="
CURRENT_VERSION=$(uv run cz version -p)
if [ -z "${CURRENT_VERSION}" ]; then
    echo "❌ Failed to determine current version"
    exit 1
fi
echo "✅ Current version: ${CURRENT_VERSION}"


echo "===== VERSION DETERMINATION ====="
echo "-- Running Commitizen dry-run --"
VERSION=$(uv run cz bump --dry-run 2>&1 | sed -n 's/bump: version .* → \(.*\)/\1/p')
CZ_EXIT_CODE=$?
if [ $CZ_EXIT_CODE -ne 0 ]; then
    echo "❌ Commitizen dry-run failed with exit code $CZ_EXIT_CODE"
    echo "Possible causes:"
    echo "1. No conventional commits since last release"
    echo "2. Version file inconsistencies"
    echo "3. Invalid commit message format"
    exit 1
fi
if [ -z "${VERSION}" ]; then
    echo "❌ Failed to determine new version from Commitizen"
    exit 1
fi
echo "✅ New version determined: ${VERSION} (from ${CURRENT_VERSION})"

# echo "===== VERSION CONSISTENCY CHECK ====="
# uv run cz check --consistency || {
#     echo "❌ Version inconsistency detected between files"
#     echo "Verify version declarations in:"
#     grep 'version_files' pyproject.toml || echo "Check Commitizen config"
#     exit 1
# }

echo "===== BRANCH MANAGEMENT ====="
RELEASE_BRANCH="task/prepare-release-${VERSION}"
if git show-ref --verify --quiet "refs/heads/${RELEASE_BRANCH}"; then
    echo "❌ Release branch ${RELEASE_BRANCH} already exists"
    echo "Resolve conflicts or delete existing branch before proceeding"
    exit 1
fi

echo "-- Creating branch ${RELEASE_BRANCH} --"
git checkout -b "${RELEASE_BRANCH}"


echo "===== VERSION BUMP EXECUTION ====="
PRERELEASE_ARG=""
if [ -n "${PRERELEASE_PHASE}" ]; then
    case "${PRERELEASE_PHASE}" in
        alpha|beta|rc)
            PRERELEASE_ARG="--prerelease ${PRERELEASE_PHASE}"
            echo "🚧 Prerelease phase: ${PRERELEASE_PHASE}"
            ;;
        *)
            echo "❌ Invalid prerelease phase: ${PRERELEASE_PHASE}"
            echo "Valid options: alpha, beta, rc"
            exit 1
            ;;
    esac
fi

uv run cz bump ${PRERELEASE_ARG} || {
    echo "❌ Version bump failed"
    echo "Possible reasons:"
    echo "- No version-changing commits since last release"
    echo "- Conflicts in version files"
    exit 1
}

echo "===== RUNNING PRE-COMMIT HOOKS ====="
uv run pre-commit run -a --show-diff-on-failure || {
    echo "❌ Pre-commit checks failed - resolve formatting issues and retry"
    echo "Some fixes may have been applied automatically - check git diff"
    exit 1
}

echo "===== CHANGE VERIFICATION ====="
# Verify changes after pre-commit fixes
if [ -z "$(git diff --name-only)" ]; then
    echo "❌ No files changed after version bump and pre-commit"
    echo "Check Commitizen configuration and commit history"
    exit 1
fi

echo "===== COMMIT SAFEGUARDS ====="
git add .
if ! git diff --cached --quiet; then
    echo "-- Committing version changes --"
    git commit -m "chore: bump version from ${CURRENT_VERSION} to ${VERSION}"
else
    echo "❌ No changes to commit after version bump and pre-commit"
    exit 1
fi


echo "===== REMOTE SYNC CHECK ====="
if [ "${CI}" ]; then
    echo "-- Verifying branch existence on remote --"
    if ! git ls-remote --exit-code origin "${RELEASE_BRANCH}"; then
        echo "⬆️  Pushing new branch to remote"
        git push origin "${RELEASE_BRANCH}"
    else
        echo "✅ Remote branch already exists"
    fi
fi

echo "===== PR CREATION SAFEGUARDS ====="
if command -v gh >/dev/null; then
    echo "-- Checking GitHub CLI authentication --"
    if ! gh auth status 2>/dev/null; then
        echo "❌ GitHub CLI not authenticated"
        exit 1
    fi

    echo "-- Creating pull request --"
    PR_TITLE="Prepare for release of ${CURRENT_VERSION} to ${VERSION}"
    PR_BODY="Release preparation triggered by @$(git config user.name).\n\nOnce merged, create a GitHub release for \`${VERSION}\` to publish."

    gh pr create \
        --title "${PR_TITLE}" \
        --body "${PR_BODY}" \
        --assignee "@me" \
        --label "release" \
        --fill \
        --base main \
        --head "${RELEASE_BRANCH}" || {
            echo "❌ PR creation failed"
            echo "Check GitHub CLI configuration and permissions"
            exit 1
        }
else
    echo "⚠️  GitHub CLI not found. Create PR manually:"
    echo "   https://github.com/bossjones/codegen-lab/compare/${RELEASE_BRANCH}?expand=1"
fi

echo "🎉 Release preparation complete with enhanced safeguards!"
