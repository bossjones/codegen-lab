SHELL := /opt/homebrew/bin/zsh

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
	@uv run pylint --output-format=colorized --disable=all --max-line-length=120 --enable=F,E --rcfile pyproject.toml src/codegen_lab tests

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
.PHONY: uv-sync-all uv-sync-dev uv-sync-group uv-check-lock uv-verify uv-verify-dry-run uv-upgrade-dry-run uv-upgrade-all uv-upgrade-package uv-reinstall-all uv-reinstall-package uv-outdated uv-clean-cache uv-export-requirements uv-export-requirements-resolution uv-workspace-lock uv-workspace-sync uv-workspace-package-sync uv-workspace-run uv-workspace-init-package uv-workspace-add-dep

uv-sync-all: ## Sync all dependencies with frozen lockfile
	@echo "🚀 Syncing all dependencies with frozen lockfile"
	@uv sync --frozen

uv-sync-dev: ## Sync only development dependencies
	@echo "🚀 Syncing development dependencies with frozen lockfile"
	@uv sync --frozen --dev

uv-sync-group: ## Sync dependencies for a specific group
	@echo "🚀 Syncing dependencies for group: $(group)"
	@uv sync --frozen --group $(group)

# UV Workspace Management Tasks
uv-workspace-lock: ## Update lockfile for the entire workspace
	@echo "🚀 Updating lockfile for the entire workspace"
	@uv lock

uv-workspace-sync: ## Install dependencies for the workspace root
	@echo "🚀 Installing dependencies for the workspace root"
	@uv sync

uv-workspace-package-sync: ## Install dependencies for a specific package (usage: make uv-workspace-package-sync package=cursor-rules-mcp-server)
	@echo "🚀 Installing dependencies for package: $(package)"
	@uv sync --package $(package)

uv-workspace-run: ## Run a command in a specific package (usage: make uv-workspace-run package=cursor-rules-mcp-server cmd="python -m cursor_rules_mcp_server")
	@echo "🚀 Running command in package: $(package)"
	@uv run --package $(package) $(cmd)

uv-workspace-add-dep: ## Add a workspace package as a dependency to the root pyproject.toml (usage: make uv-workspace-add-dep package=cursor-rules-mcp-server)
	@if [ -z "$(package)" ]; then echo "Please provide a package name with package=package-name"; exit 1; fi
	@echo "🚀 Adding $(package) as a workspace dependency"
	@if grep -q "$(package).*workspace = true" pyproject.toml; then \
		echo "$(package) is already a workspace dependency"; \
	else \
		awk '/\[tool.uv.sources\]/{found=1} found==1 && /}$$/{print "$(package) = { workspace = true }"; found=0} {print}' pyproject.toml > pyproject.toml.tmp && \
		mv pyproject.toml.tmp pyproject.toml && \
		echo "Added $(package) as a workspace dependency. Now run: make uv-workspace-lock"; \
	fi

uv-workspace-init-package: ## Initialize a new package in the workspace (usage: make uv-workspace-init-package name=new-package)
	@if [ -z "$(name)" ]; then echo "Please provide a package name with name=package-name"; exit 1; fi
	@echo "🚀 Initializing new package: $(name)"
	@./scripts/uv-workspace-init-package.sh "$(name)"

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

# Export requirements without hashes
uv-export-requirements:
	@echo "🚀 Exporting requirements.txt"
	@uv export --no-hashes --format requirements-txt -o requirements.txt

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
	# Exclude README.md files from being copied
	find hack/drafts/cursor_rules -type f -name "*.md" ! -name "README.md" -exec sh -c 'for file; do target=$${file%.md}; cp -a "$$file" ".cursor/rules/$$(basename "$$target")"; done' sh {} +



# Documentation targets
.PHONY: docs-serve docs-build docs-deploy docs-clean

# Serve documentation locally
docs-serve:
	@echo "Using shell: $$ZSH_VERSION"
	uv run python scripts/serve_docs.py --no-gh-deploy-url --kill-existing

# Build documentation without serving
docs-build:
	uv run python scripts/serve_docs.py --build-only

# Clean and build documentation
docs-clean-build:
	uv run python scripts/serve_docs.py --build-only --clean

# Deploy documentation to GitHub Pages
docs-deploy:
	uv run mkdocs gh-deploy --force

# Install documentation dependencies
docs-setup:
	uv add --dev mkdocs mkdocs-material

# Clean documentation build
docs-clean:
	rm -rf site/

# Print current shell information
.PHONY: print-shell
print-shell:
	@echo "SHELL is: $(SHELL)"
	@echo "Current shell from environment:"
	@echo $$SHELL
	@echo "Current interpreter:"
	@ps -p $$$$

# Test the shell type
.PHONY: test-shell-type
test-shell-type:
	@echo "Testing shell type:"
	@echo $0
	@echo $SHELL
	@echo "Shell features test:"
	@if [ -n "$$ZSH_VERSION" ]; then echo "Running in ZSH"; else echo "Not running in ZSH"; fi
	@if [ -n "$$BASH_VERSION" ]; then echo "Running in BASH"; else echo "Not running in BASH"; fi

# Changelog targets
.PHONY: changelog-update changelog-finalize

# Generate changelog entries from Git history
changelog-update:
	@echo "🚀 Updating changelog from Git history"
	@uv run python scripts/update_changelog.py $(if $(BRANCH),--branch=$(BRANCH)) $(if $(SINCE),--since=$(SINCE)) $(if $(UNTIL),--until=$(UNTIL)) $(if $(TYPES),--types=$(TYPES))

# Finalize a release in the changelog
changelog-finalize:
	@if [ -z "$(VERSION)" ]; then echo "Please provide a VERSION parameter, e.g., make changelog-finalize VERSION=1.0.0"; exit 1; fi
	@echo "🚀 Finalizing changelog for version $(VERSION)"
	@uv run python scripts/update_changelog.py --finalize --version=$(VERSION)

.PHONY: copy-global-taskfile
copy-global-taskfile:
	@echo "🚀 Copying global Taskfile.yml to ~/Taskfile.yml"
	@cp -av Taskfile.yml ~/Taskfile.yml

quick-fmt:
	@git ls-files '*.py' '*.ipynb' "Dockerfile" "Dockerfile.*" | xargs uv run pre-commit run --files

aider:
	uv run aider --sonnet --architect --map-tokens 2048 --cache-prompts --edit-format diff

inspect-fserver:
	@npx @modelcontextprotocol/inspector uv run python -m packages.cursor_rules_mcp_server.src.cursor_rules_mcp_server.fserver

.PHONY: relint relint-cursor-rules
relint: ## Run relint via pre-commit on specified files (usage: make relint FILES="file1 file2")
	@echo "🚀 Running relint on specified files"
	@if [ -z "$(FILES)" ]; then \
		echo "Please provide files to check with FILES=\"file1 file2\""; \
	else \
		echo $(FILES) | xargs uv run pre-commit run relint --files; \
	fi

relint-cursor-rules: ## Run relint via pre-commit on all cursor rule files tracked by git
	@echo "🚀 Running relint on cursor rule files"
	@git ls-files 'hack/drafts/cursor_rules/*.mdc.md' 'hack/drafts/cursor_rules/*.mdc' '.cursor/rules/*.mdc' | xargs uv run pre-commit run relint --files

.DEFAULT_GOAL := help

.PHONY: unittests
unittests: ## Run unittests
	uv run pytest tests/unittests/test_prompt_library.py -v -k "test_repo_analysis_prompt or test_generate_cursor_rule_prompt"


.PHONY: run-prompt-library-mcp
run-prompt-library-mcp: ## Run the prompt_library MCP server
	@echo "🚀 Starting prompt_library MCP server"
	@uv run --with 'mcp[cli]' mcp run src/codegen_lab/prompt_library.py

.PHONY: install-prompt-library-mcp
install-prompt-library-mcp: ## Install the prompt_library MCP server
	@echo "🚀 Installing prompt_library MCP server"
	@uv run --with 'mcp[cli]' mcp install src/codegen_lab/prompt_library.py

.PHONY: run-prompt-library-mcp-dev
run-prompt-library-mcp-dev: ## Run the prompt_library MCP server in development mode
	@echo "🚀 Starting prompt_library MCP server in development mode"
	@uv run --with 'mcp[cli]' mcp dev src/codegen_lab/prompt_library.py

.PHONY: run-mcp-dev
run-mcp-dev: ## Run any MCP script in development mode (usage: make run-mcp-dev script=path/to/script.py)
	@if [ -z "$(script)" ]; then \
		echo "Please provide a script path with script=path/to/script.py"; \
		exit 1; \
	fi
	@echo "🚀 Starting MCP server in development mode: $(script)"
	@uv run --with 'mcp[cli]' mcp dev $(script)

.PHONY: run-mcp-dev-with
run-mcp-dev-with: ## Run any MCP script in development mode with additional dependencies (usage: make run-mcp-dev-with script=path/to/script.py deps="pandas numpy")
	@if [ -z "$(script)" ]; then \
		echo "Please provide a script path with script=path/to/script.py"; \
		exit 1; \
	fi
	@if [ -z "$(deps)" ]; then \
		echo "Please provide dependencies with deps=\"package1 package2\""; \
		exit 1; \
	fi
	@echo "🚀 Starting MCP server in development mode with dependencies: $(script)"
	@uv run --with 'mcp[cli]' mcp dev $(script) --with $(deps)
