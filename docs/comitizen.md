# Commitizen Configuration Guide

This document explains the Commitizen configuration options used in our project's `pyproject.toml` file.

## Configuration Options

### `name = "cz_conventional_commits"`
- **Purpose**: Specifies which Commitizen plugin to use for creating conventional commits
- **Description**: The `cz_conventional_commits` plugin implements the [Conventional Commits](https://www.conventionalcommits.org/) specification
- **Impact**: Enforces a standardized commit message format that makes commit history more readable and enables automated versioning

### `tag_format = "v$version"`
- **Purpose**: Defines the format for version tags
- **Description**: When Commitizen creates a new version, it will create a git tag using this format
- **Example**: For version 1.2.3, it will create a tag named `v1.2.3`
- **Variables**:
  - `$version`: The version number (e.g., 1.2.3)
  - `$major`: Major version number
  - `$minor`: Minor version number
  - `$patch`: Patch version number

### `version_scheme = "pep440"`
- **Purpose**: Declares the versioning scheme to follow
- **Description**: Uses [PEP 440](https://peps.python.org/pep-0440/) versioning scheme, which is the standard version identification scheme for Python packages
- **Impact**: Ensures version numbers are compliant with Python packaging standards
- **Examples of valid versions**:
  - `1.2.3`
  - `2.0.0a1` (alpha release)
  - `1.3.0b2` (beta release)
  - `1.4.0rc1` (release candidate)

### `version_provider = "pep621"`
- **Purpose**: Specifies where Commitizen should look for and update the version number
- **Description**: Uses the PEP 621 standard, which means the version is defined in `pyproject.toml` under the `[project]` section
- **Impact**: Ensures version management is compliant with modern Python packaging standards

### `changelog_start_rev = "v1.0.0"`
- **Purpose**: Indicates the starting point for changelog generation
- **Description**: When generating changelogs, Commitizen will only include commits after this version tag
- **Use case**: Useful for starting fresh changelog generation from a specific version, ignoring older history

### `update_changelog_on_bump = true`
- **Purpose**: Controls automatic changelog updates during version bumps
- **Description**: When set to `true`, Commitizen will automatically update the changelog file when running version bump commands
- **Impact**: Maintains an up-to-date changelog without manual intervention
- **Generated content**:
  - Groups changes by type (feat, fix, etc.)
  - Includes commit messages and references
  - Organizes by version number

## Usage Examples

### Bumping Versions
```bash
# Automatically determine and bump version based on commits
cz bump

# Bump to a specific version
cz bump --version 1.2.3
```

### Creating Commits
```bash
# Interactive commit creation
cz commit

# Direct commit with message
cz commit -m "feat: add new feature"
```

### Generating Changelog
```bash
# Generate or update changelog
cz changelog
```

## Best Practices

1. **Commit Messages**: Follow the Conventional Commits format:
   ```
   type(scope): description

   [optional body]

   [optional footer(s)]
   ```

2. **Version Bumping**: Let Commitizen determine the version bump based on commit types:
   - `feat`: Minor version bump
   - `fix`: Patch version bump
   - `BREAKING CHANGE`: Major version bump

3. **Changelog Management**:
   - Keep changelogs up to date using `cz changelog`
   - Review generated changelogs for accuracy
   - Commit changelog updates along with version bumps

## Additional Resources

- [Commitizen Documentation](https://commitizen-tools.github.io/commitizen/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [PEP 440 -- Version Identification and Dependency Specification](https://peps.python.org/pep-0440/)
- [PEP 621 -- Storing project metadata in pyproject.toml](https://peps.python.org/pep-0621/)
