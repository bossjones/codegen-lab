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
EXTERNAL_DOCS_PATH := "limbo/bindings/python"
EXTERNAL_DOCS_MODEL := "claude-3.5-sonnet"
