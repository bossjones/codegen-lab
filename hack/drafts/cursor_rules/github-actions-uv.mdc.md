---
description: GitHub Actions with UV Package Manager Standards
globs: .github/workflows/*.yml
---
# GitHub Actions with UV Standards

Guidelines for using UV package manager in GitHub Actions workflows.

<rule>
name: github-actions-uv
description: Standards for using UV in GitHub Actions workflows
filters:
  # Match GitHub Actions workflow files
  - type: file_path
    pattern: "\\.github/workflows/.*\\.yml$"
  # Match content related to Python package installation
  - type: content
    pattern: "(pip install|python -m pip|setup\\.py|requirements\\.txt|uv )"

actions:
  - type: suggest
    message: |
      # UV Best Practices for GitHub Actions

      When working with Python in GitHub Actions workflows, follow these UV standards:

      ## 1. Installing UV

      Always use this standard pattern to install UV:

      ```yaml
      - name: Install UV
        run: |
          curl -LsSf https://astral.sh/uv/install.sh | sh
          echo "$HOME/.cargo/bin" >> $GITHUB_PATH
      ```

      ## 2. Setting Up Environment

      Create a virtual environment using UV:

      ```yaml
      - name: Create virtual environment
        run: |
          uv venv
      ```

      ## 3. Installing Dependencies

      ### Preferred: Use Makefile Targets

      ```yaml
      # For documentation dependencies
      - name: Install dependencies
        run: |
          # Set up a virtual environment
          uv venv
          # Install documentation dependencies using the Makefile target
          make docs-setup
      ```

      ### Alternative: Direct UV Commands

      If you must install packages directly (e.g., simple workflows), use `uv add` instead of `uv pip install`:

      ```yaml
      # NEVER DO THIS
      - name: Bad practice
        run: |
          uv pip install package-name

      # DO THIS INSTEAD
      - name: Good practice
        run: |
          uv add package-name
      ```

      ## 4. Running Python Code

      Always use `uv run` to execute Python code:

      ```yaml
      # NEVER DO THIS
      - name: Bad practice
        run: |
          python script.py
          pytest tests/

      # DO THIS INSTEAD
      - name: Good practice
        run: |
          uv run python script.py
          uv run pytest tests/
      ```

      ## 5. Using Existing Makefile Targets

      Prefer using existing Makefile targets when available:

      ```yaml
      # For running tests
      - name: Run tests
        run: |
          make test

      # For documentation
      - name: Build docs
        run: |
          make docs-build

      # For deployment
      - name: Deploy docs
        run: |
          make docs-deploy
      ```

examples:
  - input: |
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install mkdocs mkdocs-material

      - name: Deploy
        run: |
          mkdocs gh-deploy --force
    output: |
      This workflow should be updated to use UV instead of pip:

      ```yaml
      - name: Install UV
        run: |
          curl -LsSf https://astral.sh/uv/install.sh | sh
          echo "$HOME/.cargo/bin" >> $GITHUB_PATH

      - name: Install dependencies
        run: |
          uv venv
          make docs-setup

      - name: Deploy
        run: |
          make docs-deploy
      ```

  - input: |
      - name: Run tests
        run: |
          python -m pytest
    output: |
      This should be updated to use UV:

      ```yaml
      - name: Run tests
        run: |
          uv run pytest
      # Or preferably using the Makefile target:
      - name: Run tests
        run: |
          make test
      ```

metadata:
  priority: high
  version: 1.0
  tags:
    - github-actions
    - uv
    - package-management
    - python
    - ci-cd
</rule>

## Common GitHub Actions + UV Patterns

### Python Version Setup

```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.12'
    # NO CACHE: 'pip' PARAMETER - we use UV instead
```

### Documentation Workflow

```yaml
- name: Install UV
  run: |
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "$HOME/.cargo/bin" >> $GITHUB_PATH

- name: Install dependencies
  run: |
    uv venv
    make docs-setup

- name: Deploy documentation
  run: |
    touch .nojekyll  # Disable Jekyll for GitHub Pages
    git config --global user.name "GitHub Actions"
    git config --global user.email "actions@github.com"
    make docs-deploy
```

### Python Testing Workflow

```yaml
- name: Install UV
  run: |
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "$HOME/.cargo/bin" >> $GITHUB_PATH

- name: Install dependencies
  run: |
    uv venv
    uv sync --frozen

- name: Run tests
  run: |
    make test
```

### Dependency Caching

Using GitHub Actions caching with UV:

```yaml
- name: Cache UV data
  uses: actions/cache@v3
  with:
    path: |
      ~/.cache/uv
      ~/.cargo/bin/uv
    key: ${{ runner.os }}-uv-${{ hashFiles('**/pyproject.toml') }}
    restore-keys: |
      ${{ runner.os }}-uv-
```

### Common Pitfalls to Avoid

1. **Don't use pip with UV**: Never mix `pip install` commands with UV commands
2. **Don't use `uv pip install`**: Always use `uv add` or Makefile targets instead
3. **Don't run Python directly**: Always use `uv run python` or `make` targets
4. **Don't specify caching mechanism for pip**: When using UV, don't use pip caching
5. **Avoid `--user` flag**: UV creates and manages its own environments

Remember to update existing workflows when they are modified, and ensure all new workflows follow these standards.
