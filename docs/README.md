# Codegen Lab Documentation

This directory contains the documentation for the Codegen Lab project. The documentation is built using [MkDocs](https://www.mkdocs.org/) with the [Material theme](https://squidfunk.github.io/mkdocs-material/).

## Local Development

To work on the documentation locally:

1. Make sure you have the required dependencies installed:

   ```bash
   uv add --dev mkdocs mkdocs-material
   ```

2. Serve the documentation locally:

   ```bash
   uv run mkdocs serve
   ```

   This will start a local server at http://127.0.0.1:8000/ where you can preview the documentation.

3. Edit the files in the `docs/` directory and see the changes in real-time.

## Documentation Structure

- `mkdocs.yml` - Configuration file for MkDocs
- `docs/` - Documentation content
  - `index.md` - Home page
  - `getting-started.md` - Getting started guide
  - `user-guide/` - User guide
    - `installation.md` - Installation instructions
    - `configuration.md` - Configuration guide
  - `api-reference.md` - API reference
  - `contributing.md` - Contributing guidelines
  - `changelog.md` - Changelog

## Building the Documentation

To build the documentation without serving it:

```bash
uv run mkdocs build
```

This will generate the static site in the `site/` directory.

## Deploying to GitHub Pages

The documentation is automatically deployed to GitHub Pages when changes are pushed to the `main` branch. The deployment is handled by the GitHub Actions workflow defined in `.github/workflows/deploy-docs.yml`.

Alternatively, you can manually deploy the documentation by running:

```bash
uv run mkdocs gh-deploy
```

This will build the site and push it to the `gh-pages` branch of the repository.

## Writing Style Guide

- Use clear, concise language
- Provide examples where appropriate
- Use proper Markdown formatting
- Use headings to structure content
- Add appropriate links to other documentation pages
- Use admonitions for notes, warnings, etc.
