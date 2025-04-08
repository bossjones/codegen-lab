import "common.just"
import "variables.just"

# run release tasks
[group('release')]
release: release-create

# run pre-release tasks
[group('release')]
pre-release: pre-release-create

# create a GitHub release with version from pyproject.toml
[group('release')]
pre-release-create:
    ./scripts/ci/cz-prepare-release.sh

# create a GitHub release with version from pyproject.toml
[group('release')]
release-create:
    ./scripts/ci/cz-release.sh

# list all GitHub releases
[group('release')]
release-list:
    uv run gh release list

# delete a GitHub release with version from pyproject.toml
[group('release')]
release-delete:
    #!/usr/bin/env zsh
    VERSION=$({{GREP_CMD}} -h '^    version = ".*"' pyproject.toml | {{SED_CMD}} 's/^    version = "\(.*\)"/\1/')
    if [ -z "$VERSION" ]; then
        echo "Error: Could not extract version from pyproject.toml"
        exit 1
    fi
    uv run gh release delete "v$VERSION" --cleanup-tag

# dry run of deleting a GitHub release (echoes the command instead of executing it)
[group('release')]
release-delete-dry-run:
    #!/usr/bin/env zsh
    VERSION=$({{GREP_CMD}} -h '^    version = ".*"' pyproject.toml | {{SED_CMD}} 's/^    version = "\(.*\)"/\1/')
    if [ -z "$VERSION" ]; then
        echo "Error: Could not extract version from pyproject.toml"
        exit 1
    fi
    echo "Would run: gh release delete \"v$VERSION\" --cleanup-tag"

# reset (delete and recreate) a GitHub release with version from pyproject.toml. Use this task to completely reset a release if something went wrong during the initial creation.
[group('release')]
release-reset: release-delete release-create
