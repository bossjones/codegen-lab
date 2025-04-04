#!/usr/bin/env bats

# Load test helper
load "helpers/test_helper"

setup() {
  setup_temp_dir
  setup_mock_commands
  cd "$TEMP_DIR"

  # Export the path to the prepare-release script
  export PREPARE_RELEASE_SCRIPT="${PROJECT_ROOT}/scripts/ci/prepare-release.sh"

  # Create mock executables for common commands
  create_mock_executable "uv" "echo 'Mock UV executed with: $@'"
  create_mock_executable "git" "echo 'Mock git executed with: $@'"
  create_mock_executable "gh" "echo 'Mock GitHub CLI executed with: $@'"
  create_mock_executable "towncrier" "echo 'Mock Towncrier executed with: $@'"

  # OS-specific mocks
  if [[ "$OSTYPE" == "darwin"* ]]; then
    create_mock_executable "gsed" "echo \"Mock gsed executed with: $@\""
  else
    create_mock_executable "sed" "echo \"Mock sed executed with: $@\""
  fi

  # Create mock pyproject.toml
  create_mock_pyproject "1.2.3"

  # Create a mock towncrier.toml file
  cat > "$TEMP_DIR/pyproject.toml" << EOF
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "codegen-lab"
version = "1.2.3"
authors = [
  { name="Malcolm Jones", email="bossjones@theblacktonystark.com" },
]
description = "A small example package"
readme = "README.md"
requires-python = ">=3.8"
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]

[project.urls]
"Homepage" = "https://github.com/bossjones/codegen-lab"
"Bug Tracker" = "https://github.com/bossjones/codegen-lab/issues"

[tool.towncrier]
package = "codegen_lab"
filename = "CHANGELOG.md"
directory = "changes"
underlines = ["", "", ""]
title_format = "## [{version}] - {project_date}"
issue_format = "[#{issue}](https://github.com/bossjones/codegen-lab/issues/{issue})"
EOF

  # Create a mock changes directory
  mkdir -p "$TEMP_DIR/changes"

  # Reset DRY_RUN and CI to default values before each test
  unset DRY_RUN
  unset CI
}

teardown() {
  cleanup_temp_dir
  restore_path
  unset VERSION
  unset DRY_RUN
  unset CI
}

# Helper function to create changelog fragments
create_changelog_fragments() {
  mkdir -p "$TEMP_DIR/changes"
  cat > "$TEMP_DIR/changes/123.feature.md" << EOF
Added awesome new feature
EOF
  cat > "$TEMP_DIR/changes/124.bugfix.md" << EOF
Fixed critical bug
EOF
}

@test "prepare-release.sh - fails when VERSION is not set" {
  unset VERSION
  run bash "$PREPARE_RELEASE_SCRIPT"
  echo "Output: $output"
  [ "$status" -eq 1 ]
  [[ "$output" == *"$VERSION environment variable is missing"* ]]
}

@test "prepare-release.sh - fails when VERSION is empty" {
  export VERSION=""
  run bash "$PREPARE_RELEASE_SCRIPT"
  echo "Output: $output"
  [ "$status" -eq 1 ]
  [[ "$output" == *"$VERSION environment variable is empty"* ]]
}

@test "prepare-release.sh - updates version in dry run mode" {
  export VERSION="2.0.0"
  export DRY_RUN=1

  run bash "$PREPARE_RELEASE_SCRIPT"
  echo "Output: $output"
  [ "$status" -eq 0 ]
  [[ "$output" == *"===== UPDATING RELEASE INFORMATION ====="* ]]
  [[ "$output" == *"Would execute: "* ]]
  [[ "$output" == *"version = \"${VERSION}\""* ]]
}

@test "prepare-release.sh - updates version in actual execution mode" {
  export VERSION="2.0.0"
  export DRY_RUN=0

  run bash "$PREPARE_RELEASE_SCRIPT"
  echo "Output: $output"
  [ "$status" -eq 0 ]
  [[ "$output" == *"===== UPDATING RELEASE INFORMATION ====="* ]]
  [[ "$output" == *"Mock "* ]]
  [[ ! "$output" == *"Would execute: "* ]]
}

@test "prepare-release.sh - updates changelog in dry run mode" {
  export VERSION="2.0.0"
  export DRY_RUN=1

  run bash "$PREPARE_RELEASE_SCRIPT"
  echo "Output: $output"
  [ "$status" -eq 0 ]
  [[ "$output" == *"===== UPDATING CHANGELOG ====="* ]]
  [[ "$output" == *"Would execute: uv sync --frozen --dev"* ]]
  [[ "$output" == *"Would execute: uv run towncrier build --yes --version ${VERSION}"* ]]
}

@test "prepare-release.sh - updates changelog in actual execution mode" {
  export VERSION="2.0.0"
  export DRY_RUN=0

  run bash "$PREPARE_RELEASE_SCRIPT"
  echo "Output: $output"
  [ "$status" -eq 0 ]
  [[ "$output" == *"===== UPDATING CHANGELOG ====="* ]]
  [[ "$output" == *"Mock UV executed with: sync --frozen --dev"* ]]
  [[ "$output" == *"Mock UV executed with: run towncrier build --yes --version ${VERSION}"* ]]
}

@test "prepare-release.sh - creates branch and commits in dry run mode" {
  export VERSION="2.0.0"
  export DRY_RUN=1

  run bash "$PREPARE_RELEASE_SCRIPT"
  echo "Output: $output"
  [ "$status" -eq 0 ]
  [[ "$output" == *"===== COMMITTING CHANGES ====="* ]]
  [[ "$output" == *"Would execute: git checkout -b \"task/prepare-release-${VERSION}\""* ]]
  [[ "$output" == *"Would execute: git commit -am \"Prepare for release of version ${VERSION}\""* ]]
}

@test "prepare-release.sh - creates branch and commits in actual execution mode" {
  export VERSION="2.0.0"
  export DRY_RUN=0

  run bash "$PREPARE_RELEASE_SCRIPT"
  echo "Output: $output"
  [ "$status" -eq 0 ]
  [[ "$output" == *"===== COMMITTING CHANGES ====="* ]]
  [[ "$output" == *"Mock git executed with: checkout -b task/prepare-release-${VERSION}"* ]]
  [[ "$output" == *"Mock git executed with: commit -am \"Prepare for release of version ${VERSION}\""* ]]
}

@test "prepare-release.sh - handles CI environment in dry run mode" {
  export VERSION="2.0.0"
  export DRY_RUN=1
  export CI=true

  run bash "$PREPARE_RELEASE_SCRIPT"
  echo "Output: $output"
  [ "$status" -eq 0 ]
  [[ "$output" == *"-- Pushing changes --"* ]]
  [[ "$output" == *"Would execute: git push origin \"task/prepare-release-${VERSION}\""* ]]
  [[ "$output" == *"Would execute: gh pr create --title \"Prepare for release of version ${VERSION}\""* ]]
}

@test "prepare-release.sh - handles CI environment in actual execution mode" {
  export VERSION="2.0.0"
  export DRY_RUN=0
  export CI=true

  run bash "$PREPARE_RELEASE_SCRIPT"
  echo "Output: $output"
  [ "$status" -eq 0 ]
  [[ "$output" == *"-- Pushing changes --"* ]]
  [[ "$output" == *"Mock git executed with: push origin task/prepare-release-${VERSION}"* ]]
  [[ "$output" == *"Mock GitHub CLI executed with: pr create"* ]]
}

@test "prepare-release.sh - handles non-CI environment" {
  export VERSION="2.0.0"
  export DRY_RUN=0
  unset CI

  run bash "$PREPARE_RELEASE_SCRIPT"
  echo "Output: $output"
  [ "$status" -eq 0 ]
  [[ "$output" == *"Changes committed to 'task/prepare-release-${VERSION}'. You can now push the changes and create a pull request"* ]]
  [[ "$output" == *"===== NEXT STEPS ====="* ]]
  [[ "$output" == *"gh release create \"v${VERSION}\" --generate-notes"* ]]
}

@test "prepare-release.sh - OS-specific sed commands" {
  export VERSION="2.0.0"

  # Different test for different OS
  if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS uses gsed
    run bash "$PREPARE_RELEASE_SCRIPT"
    echo "Output: $output"
    [ "$status" -eq 0 ]
    [[ "$output" == *"Mock gsed executed with: -i s/^version = \".*\"/version = \"2.0.0\"/ pyproject.toml"* ]]
  else
    # Linux uses sed
    run bash "$PREPARE_RELEASE_SCRIPT"
    echo "Output: $output"
    [ "$status" -eq 0 ]
    [[ "$output" == *"Mock sed executed with: -i s/^version = \".*\"/version = \"2.0.0\"/ pyproject.toml"* ]]
  fi
}
