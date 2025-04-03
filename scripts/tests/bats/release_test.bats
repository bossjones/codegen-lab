#!/usr/bin/env bats

# Load test helper
load "helpers/test_helper"

setup() {
  setup_temp_dir
  setup_mock_commands
  cd "$TEMP_DIR"

  # Create mock executables for common commands
  create_mock_executable "uv" "echo 'Mock UV executed with: $@'"
  create_mock_executable "git" "echo 'Mock git executed with: $@'"
  create_mock_executable "gh" "echo 'Mock GitHub CLI executed with: $@'"
  create_mock_executable "python" "echo 'Mock Python executed with: $@'"
  create_mock_executable "twine" "echo 'Mock Twine executed with: $@'"
  create_mock_executable "just" "echo 'Mock Just executed with: $@'"

  # OS-specific mocks
  if [[ "$OSTYPE" == "darwin"* ]]; then
    create_mock_executable "gsed" "echo \"Mock gsed executed with: $@\""
    create_mock_executable "ggrep" "if [[ \"$1\" == \"-h\" && \"$2\" == '^version = \".*\"' ]]; then echo 'version = \"1.2.3\"'; else echo \"Mock ggrep executed with: $@\"; fi"
  else
    create_mock_executable "sed" "echo \"Mock sed executed with: $@\""
    create_mock_executable "grep" "if [[ \"$1\" == \"-h\" && \"$2\" == '^version = \".*\"' ]]; then echo 'version = \"1.2.3\"'; else echo \"Mock grep executed with: $@\"; fi"
  fi

  # Create mock pyproject.toml
  create_mock_pyproject "1.2.3"

  # Create an empty changes directory
  mkdir -p "changes"
}

teardown() {
  cleanup_temp_dir
  restore_path
}

# Helper function to create changelog fragments
create_changelog_fragments() {
  mkdir -p "changes"
  touch "changes/1.2.3.md"
}

@test "release.sh - check required binaries" {
  run bash "$RELEASE_SCRIPT"
  echo "Output: $output"
  [ "$status" -eq 0 ]
  [[ "$output" == *"All required binaries are available"* ]]
}

@test "release.sh - fails when changelog fragments exist" {
  create_changelog_fragments

  run bash "$RELEASE_SCRIPT"
  echo "Output: $output"
  [ "$status" -eq 1 ]
  [[ "$output" == *"Cannot create release if CHANGELOG fragment files exist"* ]]
}

@test "release.sh - extracts version from pyproject.toml when not provided" {
  run bash "$RELEASE_SCRIPT"
  echo "Output: $output"
  [ "$status" -eq 0 ]
  [[ "$output" == *"VERSION environment variable not provided, extracting from pyproject.toml"* ]]
  [[ "$output" == *"Extracted version: 1.2.3"* ]]
}

@test "release.sh - uses provided VERSION environment variable" {
  export VERSION="2.0.0"
  # Update mock pyproject to match VERSION
  create_mock_pyproject "2.0.0"

  run bash "$RELEASE_SCRIPT"
  echo "Output: $output"
  [ "$status" -eq 0 ]
  [[ ! "$output" == *"VERSION environment variable not provided"* ]]
  [[ "$output" == *"Current git reference:"* ]]
}

@test "release.sh - fails when VERSION is empty" {
  export VERSION=""

  run bash "$RELEASE_SCRIPT"
  echo "Output: $output"
  [ "$status" -eq 1 ]
  [[ "$output" == *"$VERSION environment variable is empty"* ]]
}

@test "release.sh - fails when pyproject.toml version doesn't match VERSION" {
  export VERSION="2.0.0"
  # Create pyproject.toml with a different version
  create_mock_pyproject "1.2.3"

  run bash "$RELEASE_SCRIPT"
  echo "Output: $output"
  [ "$status" -eq 1 ]
  [[ "$output" == *"Version in pyproject.toml does not match the version"* ]]
}

@test "release.sh - builds package correctly" {
  # Mock the increase_version_number.py script
  mkdir -p "scripts/ci"
  cat > "scripts/ci/increase_version_number.py" << 'EOF'
#!/usr/bin/env python
import sys
version = sys.argv[1]
# Simple version incrementer for testing
parts = version.split('.')
patch = int(parts[2]) + 1
new_version = f"{parts[0]}.{parts[1]}.{patch}.dev0"
print(new_version)
EOF
  chmod +x "scripts/ci/increase_version_number.py"

  run bash "$RELEASE_SCRIPT"
  echo "Output: $output"
  [ "$status" -eq 0 ]
  [[ "$output" == *"=== BUILDING PACKAGE ==="* ]]
  [[ "$output" == *"Mock UV executed with: sync --frozen"* ]]
  [[ "$output" == *"Mock UV executed with: build"* ]]
}

@test "release.sh - updates version in repository" {
  # Mock the increase_version_number.py script
  mkdir -p "scripts/ci"
  cat > "scripts/ci/increase_version_number.py" << 'EOF'
#!/usr/bin/env python
import sys
print("1.2.4.dev0")
EOF
  chmod +x "scripts/ci/increase_version_number.py"

  run bash "$RELEASE_SCRIPT"
  echo "Output: $output"
  [ "$status" -eq 0 ]
  [[ "$output" == *"=== UPDATING VERSION IN REPOSITORY ==="* ]]
  [[ "$output" == *"-- Calculating new development version --"* ]]
  [[ "$output" == *"-- Bumping to development version (1.2.4.dev0) --"* ]]
  [[ "$output" == *"Mock git executed with: commit -am"* ]]
  [[ "$output" == *"Mock git executed with: push"* ]]
}

@test "release.sh - creates GitHub release" {
  # Mock the increase_version_number.py script
  mkdir -p "scripts/ci"
  cat > "scripts/ci/increase_version_number.py" << 'EOF'
#!/usr/bin/env python
import sys
print("1.2.4.dev0")
EOF
  chmod +x "scripts/ci/increase_version_number.py"

  run bash "$RELEASE_SCRIPT"
  echo "Output: $output"
  [ "$status" -eq 0 ]
  [[ "$output" == *"=== CREATING GITHUB RELEASE ==="* ]]
  [[ "$output" == *"-- Creating release v1.2.3 --"* ]]
  [[ "$output" == *"Mock GitHub CLI executed with: release create"* ]]
  [[ "$output" == *"=== RELEASE COMPLETED SUCCESSFULLY ==="* ]]
}
