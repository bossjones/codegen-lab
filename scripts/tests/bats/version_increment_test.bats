#!/usr/bin/env bats

# Load test helper
load "helpers/test_helper"

setup() {
  setup_temp_dir
  cd "$TEMP_DIR"

  # Mock the codegen_lab package
  mkdir -p "codegen_lab"
  echo "__version__ = \"1.2.3\"" > "codegen_lab/__init__.py"

  # Add the current directory to PYTHONPATH
  export PYTHONPATH="$TEMP_DIR:$PYTHONPATH"
}

teardown() {
  cleanup_temp_dir
}

@test "increase_version_number.py - increments patch version for release version" {
  # Test with a standard release version (no prerelease component)
  run python "$VERSION_SCRIPT" "1.2.3"
  echo "Output: $output"
  [ "$status" -eq 0 ]
  [[ "$output" == "1.2.4.dev0" ]]
}

@test "increase_version_number.py - increments prerelease number for dev version" {
  # Test with a development version
  run python "$VERSION_SCRIPT" "1.2.3.dev0"
  echo "Output: $output"
  [ "$status" -eq 0 ]
  [[ "$output" == "1.2.3.dev1" ]]
}

@test "increase_version_number.py - increments prerelease number for beta version" {
  # Test with a beta version
  run python "$VERSION_SCRIPT" "1.2.3.beta2"
  echo "Output: $output"
  [ "$status" -eq 0 ]
  [[ "$output" == "1.2.3.beta3" ]]
}

@test "increase_version_number.py - handles major version increments" {
  # Test with a higher major version
  run python "$VERSION_SCRIPT" "2.0.0"
  echo "Output: $output"
  [ "$status" -eq 0 ]
  [[ "$output" == "2.0.1.dev0" ]]
}

@test "increase_version_number.py - validates version format" {
  # Test with an invalid version format
  run python "$VERSION_SCRIPT" "invalid-version"
  echo "Output: $output"
  [ "$status" -ne 0 ]
  [[ "$output" == *"Invalid version"* ]]
}

@test "increase_version_number.py - maintains correct version structure" {
  # Test version structure is maintained
  run python "$VERSION_SCRIPT" "10.20.30"
  echo "Output: $output"
  [ "$status" -eq 0 ]
  [[ "$output" == "10.20.31.dev0" ]]
}
