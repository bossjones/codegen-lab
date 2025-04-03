#!/usr/bin/env python3

"""GitHub Action script that automatically renames towncrier changelog files in pull requests.

This script is designed to work as part of a GitHub Action workflow to manage changelog entries
using towncrier. It performs the following tasks:

1. Checks if the event is a pull request (no-op for other events)
2. Reads the towncrier configuration from pyproject.toml
3. Identifies changelog files in the PR that match the configured towncrier types
4. Renames these files to include the PR number in their filename

For example, if a PR #123 adds a file 'changes/feature.rst', it will be renamed to
'changes/123.feature.rst'.

The script uses:
- GitHub API (through PyGithub) to access PR information
- towncrier configuration from pyproject.toml
- Regular expressions to match and rename files

Environment Variables:
    GITHUB_EVENT_NAME: The name of the GitHub event that triggered the action
    GITHUB_EVENT_PATH: Path to the event payload JSON file
    GITHUB_TOKEN: GitHub token for API access

Authors: The MNE-Python contributors.
License: BSD-3-Clause
Copyright the MNE-Python contributors.
"""

# Adapted from action-towncrier-changelog
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from tomllib import loads
from typing import Optional

from github import Github
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings for the rename_towncrier script.

    Attributes:
        GITHUB_TOKEN: GitHub token for API access
        GITHUB_EVENT_NAME: The name of the GitHub event that triggered the action
        GITHUB_EVENT_PATH: Path to the event payload JSON file
    """
    GITHUB_TOKEN: SecretStr
    GITHUB_EVENT_NAME: str = "pull_request"
    GITHUB_EVENT_PATH: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"
    )

# Load settings
settings = Settings()

event_name = settings.GITHUB_EVENT_NAME
if not event_name.startswith("pull_request"):
    print(f"No-op for {event_name}")
    sys.exit(0)

if settings.GITHUB_EVENT_PATH:
    with open(settings.GITHUB_EVENT_PATH, encoding="utf-8") as fin:
        event = json.load(fin)
    pr_num = event["number"]
    basereponame = event["pull_request"]["base"]["repo"]["full_name"]
    real = True
else:  # local testing
    pr_num = 1  # example PR number
    basereponame = "bossjones/codegen-lab"
    real = False

g = Github(settings.GITHUB_TOKEN.get_secret_value())
baserepo = g.get_repo(basereponame)

# Grab config from upstream's default branch
toml_cfg = loads(Path("pyproject.toml").read_text("utf-8"))

config = toml_cfg["tool"]["towncrier"]
pr = baserepo.get_pull(pr_num)
modified_files = [f.filename for f in pr.get_files()]

# Get types from config
types = [ent["directory"] for ent in toml_cfg["tool"]["towncrier"]["type"]]
type_pipe = "|".join(types)

# Get directory from config
directory = toml_cfg["tool"]["towncrier"]["directory"]
assert directory.endswith("/"), directory

# Updated regex pattern to match both .rst and .md files since your config supports markdown
file_re = re.compile(rf"^{directory}({type_pipe})\.(rst|md)$")
found_stubs = [f for f in modified_files if file_re.match(f)]
for stub in found_stubs:
    fro = stub
    # Preserve the original file extension
    ext = Path(fro).suffix
    to = file_re.sub(rf"{directory}{pr_num}.\1{ext}", fro)
    print(f"Renaming {fro} to {to}")
    if real:
        subprocess.check_call(["mv", fro, to])
