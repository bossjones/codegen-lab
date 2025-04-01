# https://just.systems/man/en/

# REQUIRES

docker := require("docker")
find := require("find")
rm := require("rm")
uv := require("uv")

# SETTINGS

# Load a .env file, if present.
set dotenv-load := true

set shell := ["zsh", "-cu"]


# VARIABLES

PACKAGE := "codegen_lab"
REPOSITORY := "codegen-lab"
SOURCES := "src"
TESTS := "tests"
CURRENT_DIR := "$(pwd)"
BASE64_CMD := if "{{os()}}" == "macos" { "base64 -w 0 -i cert.pem -o ca.pem" } else { "base64 -w 0 -i cert.pem > ca.pem" }
GREP_CMD := if "{{os()}}" =~ "macos" { "ggrep" } else { "grep" }
SED_CMD := if "{{os()}}" =~ "macos" { "gsed" } else { "sed" }
PYTHON := "uv run python"
UV_RUN := "uv run"
LANGGRAPH_REPLACEMENT := if "{{os()}}" =~ "macos" { `ggrep -h 'langgraph-sdk>=.*",' pyproject.toml | gsed 's/^[[:space:]]*"//; s/",$//'` } else { `grep -h 'langgraph-sdk>=.*",' pyproject.toml | sed 's/^[[:space:]]*"//; s/",$//'` }
EXTERNAL_DOCS_PATH := "limbo/bindings/python"
EXTERNAL_DOCS_MODEL := "claude-3.5-sonnet"


# DEFAULTS

# display help information
default:
	@just --list



# bump package
[group('commit')]
commit-bump:
	uv run cz bump

# commit package
[group('commit')]
commit-files:
	uv run cz commit

# get commit info
[group('commit')]
commit-info:
	uv run cz info



# run check tasks
[group('check')]
check: check-code check-type check-format check-security check-coverage

# check code quality
[group('check')]
check-code:
	uv run ruff check {{SOURCES}} {{TESTS}}

# check code coverage
[group('check')]
check-coverage numprocesses="auto" cov_fail_under="30":
	uv run pytest --numprocesses={{numprocesses}} --cov={{SOURCES}} --cov-fail-under={{cov_fail_under}} {{TESTS}}

# check code format
[group('check')]
check-format:
	uv run ruff format --check {{SOURCES}} {{TESTS}}

# check code security
[group('check')]
check-security:
	uv run bandit --recursive --configfile=pyproject.toml {{SOURCES}}

# check unit tests
[group('check')]
check-test numprocesses="auto":
	uv run pytest --numprocesses={{numprocesses}} {{TESTS}}

# check code typing
[group('check')]
check-type:
	uv run mypy {{SOURCES}} {{TESTS}}


# run clean tasks
[group('clean')]
clean: clean-build clean-cache clean-constraints clean-coverage clean-docs clean-environment clean-mlruns clean-mypy clean-outputs clean-pytest clean-python clean-requirements clean-ruff

# clean build folders
[group('clean')]
clean-build:
	rm -rf dist/
	rm -rf build/

# clean cache folder
[group('clean')]
clean-cache:
	rm -rf .cache/

# clean constraints file
[group('clean')]
clean-constraints:
	rm -rf constraints.txt

# clean coverage files
[group('clean')]
clean-coverage:
	rm -rf .coverage*

# clean docs folder
[group('clean')]
clean-docs:
	rm -rf docs/

# clean environment file
[group('clean')]
clean-environment:
	rm -f python_env.yaml

# clean mlruns folder
[group('clean')]
clean-mlruns:
	rm -rf mlruns/*

# clean mypy folders
[group('clean')]
clean-mypy:
	rm -rf .mypy_cache/

# clean outputs folder
[group('clean')]
clean-outputs:
	rm -rf outputs/*

# clean pytest cache
[group('clean')]
clean-pytest:
	rm -rf .pytest_cache/

# clean python caches
[group('clean')]
clean-python:
	find . -type f -name '*.py[co]' -delete
	find . -type d -name __pycache__ -exec rm -r {} \+

# clean requirements file
[group('clean')]
clean-requirements:
	rm -f requirements.txt

# clean ruff cache
[group('clean')]
clean-ruff:
	rm -rf .ruff_cache/

# clean venv folder
[confirm]
[group('clean')]
clean-venv:
	rm -rf .venv/


# run format tasks
[group('format')]
format: format-import format-source

# format code import
[group('format')]
format-import:
	uv run ruff check --select=I --fix {{SOURCES}} {{TESTS}}

# format code source
[group('format')]
format-source:
	uv run ruff format {{SOURCES}} {{TESTS}}


# run package tasks
[group('package')]
package: package-build

# build package constraints
[group('package')]
package-constraints constraints="constraints.txt":
	uv pip compile pyproject.toml --generate-hashes --output-file={{constraints}}

# build python package
[group('package')]
package-build constraints="constraints.txt": clean-build package-constraints
	uv build --build-constraint={{constraints}} --require-hashes --wheel


# run install tasks
[group('install')]
install: install-project install-hooks

# install git hooks
[group('install')]
install-hooks:
	uv run pre-commit install --hook-type=pre-push
	uv run pre-commit install --hook-type=commit-msg

# install the project
[group('install')]
install-project:
	uv sync --all-groups

# run doc tasks
[group('doc')]
doc: doc-build

# build documentation
[group('doc')]
doc-build format="google" output="gh-docs": clean-docs
    uv run pdoc --docformat={{format}} --output-directory={{output}} {{SOURCES}}/{{PACKAGE}}

# serve documentation
[group('doc')]
doc-serve format="google" port="8088":
    uv run pdoc --docformat={{format}} --port={{port}} {{SOURCES}}/{{PACKAGE}}
