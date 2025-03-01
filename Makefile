.PHONY: install
install: ## Install the virtual environment and install the pre-commit hooks
	@echo "🚀 Creating virtual environment using uv"
	@uv sync --dev
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

# UV Package Management Tasks
.PHONY: uv-sync-all uv-sync-dev uv-sync-group uv-check-lock uv-verify uv-verify-dry-run uv-upgrade-dry-run uv-upgrade-all uv-upgrade-package uv-reinstall-all uv-reinstall-package uv-outdated uv-clean-cache uv-export-requirements uv-export-requirements-resolution

uv-sync-all: ## Sync all dependencies with frozen lockfile
	@echo "🚀 Syncing all dependencies with frozen lockfile"
	@uv sync --frozen

uv-sync-dev: ## Sync only development dependencies
	@echo "🚀 Syncing development dependencies with frozen lockfile"
	@uv sync --frozen --dev

uv-sync-group: ## Sync dependencies for a specific group
	@echo "🚀 Syncing dependencies for group: $(group)"
	@uv sync --frozen --group $(group)

uv-check-lock: ## Check lockfile consistency (prevents updates)
	@echo "🚀 Checking lockfile consistency"
	@uv pip compile --check-lock pyproject.toml

uv-verify: ## Verify lockfile is up to date
	@echo "🚀 Verifying lockfile"
	@uv pip compile pyproject.toml

uv-verify-dry-run: ## Verify lockfile (dry run)
	@echo "🚀 Verifying lockfile (dry run)"
	@uv pip compile --dry-run pyproject.toml

uv-upgrade-dry-run: ## Preview potential upgrades (dry run)
	@echo "🚀 Previewing potential upgrades"
	@uv pip compile --upgrade --dry-run pyproject.toml

uv-upgrade-all: ## Upgrade all dependencies
	@echo "🚀 Upgrading all dependencies"
	@uv pip compile --upgrade pyproject.toml

uv-upgrade-package: ## Upgrade specific package (usage: make uv-upgrade-package package=ruff)
	@echo "🚀 Upgrading package: $(package)"
	@uv pip compile --upgrade-package $(package) pyproject.toml

uv-reinstall-all: ## Reinstall all packages
	@echo "🚀 Reinstalling all packages"
	@uv sync --reinstall --frozen

uv-reinstall-package: ## Reinstall specific package (usage: make uv-reinstall-package package=ruff)
	@echo "🚀 Reinstalling package: $(package)"
	@uv sync --reinstall-package $(package) --frozen

uv-outdated: ## List outdated packages
	@echo "🚀 Listing outdated packages"
	@uv pip list --outdated

uv-clean-cache: ## Clean UV cache
	@echo "🚀 Cleaning UV cache"
	@uv cache clean

uv-export-requirements: ## Export requirements without hashes
	@echo "🚀 Exporting requirements to requirements.txt"
	@uv pip export --without-hashes pyproject.toml -o requirements.txt

uv-export-requirements-resolution: ## Export with specific resolution strategy (usage: make uv-export-requirements-resolution strategy=highest)
	@echo "🚀 Exporting requirements with $(strategy) resolution strategy"
	@uv pip export --without-hashes --resolution $(strategy) pyproject.toml -o requirements.txt

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
