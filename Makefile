.PHONY: install
install: ## Install the virtual environment and install the pre-commit hooks
	@echo "🚀 Creating virtual environment using uv"
	@uv sync
	@uv run pre-commit install

.PHONY: check
check: ## Run code quality tools.
	@echo "🚀 Checking lock file consistency with 'pyproject.toml'"
	@uv lock --locked
	@echo "🚀 Linting code: Running pre-commit"
	@uv run pre-commit run -a
	@echo "🚀 Static type checking: Running mypy"
	@uv run mypy
	@echo "🚀 Checking for obsolete dependencies: Running deptry"
	@uv run deptry .

.PHONY: test
test: ## Test the code with pytest
	@echo "🚀 Testing code: Running pytest"
	@uv run pytest --diff-width=60 --diff-symbols --cov-append --cov-report=term-missing --junitxml=junit/test-results.xml --cov-report=xml:cov.xml --cov-report=html:htmlcov --cov-report=annotate:cov_annotate --cov=.

.PHONY: pytest
pytest: ## Test the code with pytest
	@echo "🚀 Testing code: Running pytest"
	@uv run pytest -s --verbose --showlocals --tb=short --cov-config=pyproject.toml --cov-report=xml


.PHONY: ci
ci: ## Test the code with pytest
	@echo "🚀 Checking lock file consistency with 'pyproject.toml'"
	@uv lock --locked
	@echo "🚀 Linting code: pylint"
	@uv run pylint --output-format=colorized --disable=all --max-line-length=120 --enable=F,E --rcfile pyproject.toml src/adobe_cursor_tools tests

.PHONY: build
build: clean-build ## Build wheel file
	@echo "🚀 Creating wheel file"
	@uvx --from build pyproject-build --installer uv

.PHONY: clean-build
clean-build: ## Clean build artifacts
	@echo "🚀 Removing build artifacts"
	@uv run python -c "import shutil; import os; shutil.rmtree('dist') if os.path.exists('dist') else None"

.PHONY: publish
publish: ## Publish a release to PyPI.
	@echo "🚀 Publishing."
	@uvx twine upload --repository-url https://upload.pypi.org/legacy/ dist/*

.PHONY: build-and-publish
build-and-publish: build publish ## Build and publish.

.PHONY: docs-test
docs-test: ## Test if documentation can be built without warnings or errors
	@uv run mkdocs build -s

.PHONY: docs
docs: ## Build and serve the documentation
	@uv run mkdocs serve

.PHONY: help
help:
	@uv run python -c "import re; \
	[[print(f'\033[36m{m[0]:<20}\033[0m {m[1]}') for m in re.findall(r'^([a-zA-Z_-]+):.*?## (.*)$$', open(makefile).read(), re.M)] for makefile in ('$(MAKEFILE_LIST)').strip().split()]"

.PHONY: update-cursor-rules
update-cursor-rules:  ## Update cursor rules from prompts/drafts/cursor_rules
	# Create .cursor/rules directory if it doesn't exist.
	# Note: at the time of writing, cursor does not support generating .mdc files via Composer Agent.s
	mkdir -p .cursor/rules || true
	# Copy files from prompts/drafts/cursor_rules to .cursor/rules and change extension to .mdc
	find hack/drafts/cursor_rules -type f -name "*.md" -exec sh -c 'for file; do target=$${file%.md}; cp -a "$$file" ".cursor/rules/$$(basename "$$target")"; done' sh {} +

.DEFAULT_GOAL := help
