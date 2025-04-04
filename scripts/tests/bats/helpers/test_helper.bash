#!/usr/bin/env bash

# Set pipefail to ensure that a pipeline returns a non-zero status if any command fails
set -o pipefail

# Get the directory of this script
CURR_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PROJECT_ROOT="$( cd "$CURR_DIR/../../../../" >/dev/null 2>&1 && pwd )"

# Add the path to load helper libraries
export TEST_LIB_DIR="${CURR_DIR}/lib"
export BATS_LIB_PATH=${BATS_LIB_PATH:-"${TEST_LIB_DIR}"}


_tests_helper() {
    export BATS_LIB_PATH=${BATS_LIB_PATH:-"${TEST_LIB_DIR}"}
    echo $BATS_LIB_PATH
    bats_load_library bats-support
    bats_load_library bats-assert
    bats_load_library bats-file
    # bats_load_library bats-detik/detik.bash
}

# Load bats-support and bats-assert libraries if they exist
if [ -d "${BATS_LIB_PATH}/bats-support" ]; then
  load "${BATS_LIB_PATH}/bats-support/load"
fi

if [ -d "${BATS_LIB_PATH}/bats-assert" ]; then
  load "${BATS_LIB_PATH}/bats-assert/load"
fi

# Path to the scripts being tested
export RELEASE_SCRIPT="${PROJECT_ROOT}/scripts/ci/release.sh"
export VERSION_SCRIPT="${PROJECT_ROOT}/scripts/ci/increase_version_number.py"
export PREPARE_RELEASE_SCRIPT="${PROJECT_ROOT}/scripts/ci/prepare-release.sh"

# Create a temporary directory for test artifacts
setup_temp_dir() {
  TEMP_DIR=$(mktemp -d)
  export TEMP_DIR
}

# Clean up the temporary directory
cleanup_temp_dir() {
  if [[ -d "$TEMP_DIR" ]]; then
    rm -rf "$TEMP_DIR"
  fi
}

# Create a mock function to replace real commands
mock_command() {
  local cmd="$1"
  local response="$2"

  eval "${cmd}() { ${response}; }"
  export -f "${cmd}"
}

# Restore the original PATH
restore_path() {
  export PATH="$ORIGINAL_PATH"
}

# Save the original PATH
ORIGINAL_PATH="$PATH"

# Create a directory for mock commands
setup_mock_commands() {
  mkdir -p "$TEMP_DIR/bin"
  export PATH="$TEMP_DIR/bin:$PATH"
}

# Create a mock executable
create_mock_executable() {
  local cmd="$1"
  local response="$2"

  cat > "$TEMP_DIR/bin/$cmd" << EOF
#!/bin/bash
$response
EOF
  chmod +x "$TEMP_DIR/bin/$cmd"
}

# Mock pyproject.toml content
create_mock_pyproject() {
  local version="$1"

  cat > "$TEMP_DIR/pyproject.toml" << EOF
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "codegen-lab"
version = "$version"
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
EOF
}

# Create a mock for codegen_lab package
create_mock_codegen_lab() {
  local version="$1"

  mkdir -p "$TEMP_DIR/codegen_lab"
  cat > "$TEMP_DIR/codegen_lab/__init__.py" << EOF
__version__ = "$version"
EOF
}

# Skip OS-specific tests
skip_if_not_macos() {
  if [[ "$OSTYPE" != "darwin"* ]]; then
    skip "This test only runs on macOS"
  fi
}

skip_if_not_linux() {
  if [[ "$OSTYPE" == "darwin"* ]]; then
    skip "This test only runs on Linux"
  fi
}
