#!/usr/bin/env bash

# Script to run Bats tests for release.sh and increase_version_number.py

set -eo pipefail

# Get the directory of this script
CURR_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Setup libraries first
echo "Setting up Bats libraries..."
# bash "${CURR_DIR}/helpers/setup_libs.bash"
bash scripts/tests/bats/helpers/setup_libs.bash

# Check if Bats is installed
if ! command -v bats &> /dev/null; then
  echo "Bats is not installed. Please install it first."
  echo "Installation instructions: https://bats-core.readthedocs.io/en/stable/installation.html"
  exit 1
fi

# Run tests
echo "Running release.sh tests..."
# bats "${CURR_DIR}/release_test.bats"
bats scripts/tests/bats/release_test.bats

echo "Running version increment tests..."
# bats "${CURR_DIR}/version_increment_test.bats"
bats scripts/tests/bats/version_increment_test.bats

echo "Running prepare-release.sh tests..."
# bats "${CURR_DIR}/prepare_release_test.bats"
bats scripts/tests/bats/prepare_release_test.bats

echo "All tests completed!"
