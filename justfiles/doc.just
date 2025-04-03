# run doc tasks
[group('doc')]
doc: doc-build

# build documentation
[group('doc')]
doc-build format="google" output="gh-docs": clean-gh-docs
    uv run pdoc --docformat={{format}} --output-directory={{output}} {{SOURCES}}/{{PACKAGE}}

# serve documentation
[group('doc')]
doc-serve format="google" port="8088":
    uv run pdoc --docformat={{format}} --port={{port}} {{SOURCES}}/{{PACKAGE}}

# serve mkdocs documentation with live reload
[group('doc')]
mkdocs-serve:
    uv run mkdocs serve

# build mkdocs documentation site
[group('doc')]
mkdocs-build:
    uv run mkdocs build

# show mkdocs help
[group('doc')]
mkdocs-help:
    uv run mkdocs -h

# deploy mkdocs documentation to GitHub Pages
[group('doc')]
mkdocs-deploy-docs:
    #!/usr/bin/env zsh
    uv run mkdocs gh-deploy --force --message 'docs(mkdocs): update documentation [skip ci]'
