# Validation tasks

# Validate pyproject.toml file
[group('validate')]
validate-pyproject:
    @git ls-files 'pyproject.toml' | xargs uv run pre-commit run --files

# Run pre-commit hooks on all files
[group('validate')]
pre-commit:
    @uv run pre-commit run -a --show-diff-on-failure
