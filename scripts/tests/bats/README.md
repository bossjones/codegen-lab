# Bats Tests for Release Workflow

This directory contains [Bats](https://github.com/bats-core/bats-core) tests for the release workflow scripts in the project.

## Overview

The tests validate the functionality of:
- `scripts/ci/release.sh`: The main release script
- `scripts/ci/increase_version_number.py`: A helper script to calculate the next development version
- `scripts/ci/prepare-release.sh`: A script to prepare the repository for a new release

## Prerequisites

To run these tests, you need to install Bats:

### macOS

```bash
brew install bats-core
```

### Linux

```bash
sudo apt-get install bats
# or
git clone https://github.com/bats-core/bats-core.git
cd bats-core
./install.sh /usr/local
```

## Running Tests

You can run all tests with:

```bash
./scripts/tests/bats/run_tests.sh
```

Or run individual test files with:

```bash
bats scripts/tests/bats/release_test.bats
bats scripts/tests/bats/version_increment_test.bats
bats scripts/tests/bats/prepare_release_test.bats
```

## Test Structure

### Helper Libraries

The tests use two helper libraries:
- **bats-support**: Basic test support functions
- **bats-assert**: Additional assertion functions

These libraries will be automatically downloaded when you run the tests for the first time.

### Test Files

- `release_test.bats`: Tests for release.sh functionality
- `version_increment_test.bats`: Tests for increase_version_number.py functionality
- `prepare_release_test.bats`: Tests for prepare-release.sh functionality

### Helper Files

- `helpers/test_helper.bash`: Common test helper functions
- `helpers/setup_libs.bash`: Script to set up the required libraries
- `run_tests.sh`: Convenient script to run all tests

## Creating New Tests

To add a new test:

1. Create a new test file with the `.bats` extension
2. Load the test helper: `load "helpers/test_helper"`
3. Write tests using Bats `@test` syntax:

```bash
@test "test description" {
  # Test code
  run command_to_test
  [ "$status" -eq 0 ]
  [[ "$output" == *"expected output"* ]]
}
```

## Documentation

For more information on Bats testing, see:
- [Bats Documentation](https://bats-core.readthedocs.io/)
- [bats-core on GitHub](https://github.com/bats-core/bats-core)
- [bats-assert on GitHub](https://github.com/bats-core/bats-assert)
- [bats-support on GitHub](https://github.com/bats-core/bats-support)
