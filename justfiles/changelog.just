# Initialize the changelog
[group('changelog')]
init-changelog:
    ./scripts/init-changelog.sh

# Show towncrier version and build draft changelog for main version
[group('changelog')]
changelog-draft:
    uv run towncrier --version
    uv run towncrier build --version main --draft

# Show towncrier version and build changelog for main version
[group('changelog')]
changelog:
    uv run towncrier --version
    uv run towncrier build --version v0.2.0
