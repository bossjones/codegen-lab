#!/usr/bin/env python
"""
Changelog Update Tool.

Automatically generates and updates changelog entries based on Git commit history
and conventional commits format. It compares commits between branches, parses
commit messages, and updates the changelog accordingly.
"""

import argparse
import datetime
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, TypedDict, Union, cast

import yaml


class CommitMapping(TypedDict):
    """Type definition for commit type to changelog section mapping."""

    section: str
    prefix: str


class ChangelogConfig(TypedDict, total=False):
    """Type definition for changelog configuration."""

    version_prefix: str
    repo_url: str
    commit_types: dict[str, str]
    exclude_types: list[str]
    changelog_path: str


# Default configuration
DEFAULT_CONFIG: ChangelogConfig = {
    "version_prefix": "v",
    "repo_url": "https://github.com/bossjones/codegen-lab",
    "commit_types": {
        "feat": "Added",
        "fix": "Fixed",
        "perf": "Changed",
        "docs": "Changed",
        "style": "Changed",
        "refactor": "Changed",
        "build": "Changed",
        "ci": "Changed",
        "chore": "Added",
        "test": None,  # Will be excluded by default
        "deprecate": "Deprecated",
        "remove": "Removed",
        "security": "Security",
    },
    "exclude_types": ["test", "ci"],
    "changelog_path": "docs/changelog.md",
}

# Regex for parsing conventional commits
COMMIT_PATTERN = re.compile(
    r"^(?P<type>[a-z]+)(?:\((?P<scope>[a-z0-9/-]+)\))?: (?P<subject>.+)$", re.IGNORECASE
)
BREAKING_PATTERN = re.compile(r"BREAKING CHANGE:", re.IGNORECASE)

# Regex for parsing the changelog
VERSION_PATTERN = re.compile(
    r"## \[(?P<version>[^\]]+)\](?: - (?P<date>\d{4}-\d{2}-\d{2}))?"
)
LINK_PATTERN = re.compile(r"\[(?P<version>[^\]]+)\]: (?P<url>.+)$")
SECTION_PATTERN = re.compile(r"### (?P<section>Added|Changed|Deprecated|Removed|Fixed|Security)")
ENTRY_PATTERN = re.compile(r"- (?P<entry>.+)$")


def load_config(config_path: str | None = None) -> ChangelogConfig:
    """
    Load configuration from file or use defaults.

    Args:
        config_path: Path to configuration file. If None, look for .changelog-config.yml.

    Returns:
        Dictionary of configuration settings.
    """
    config = DEFAULT_CONFIG.copy()

    if config_path is None:
        config_path = ".changelog-config.yml"

    config_file = Path(config_path)
    if config_file.exists():
        with open(config_file, encoding="utf-8") as f:
            user_config = yaml.safe_load(f)
            if user_config and isinstance(user_config, dict):
                # Update only the keys that are provided
                for key, value in user_config.items():
                    if key in config:
                        config[key] = value

    return config


def run_git_command(command: list[str]) -> str:
    """
    Run a git command and return its output.

    Args:
        command: Git command as a list of strings.

    Returns:
        Command output as string.

    Raises:
        RuntimeError: If the command fails.
    """
    try:
        result = subprocess.run(
            ["git"] + command,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Git command failed: {e.stderr}") from e


def get_commits(
    branch: str | None = None,
    since: str | None = None,
    until: str | None = None,
) -> list[str]:
    """
    Get list of commit messages between main and specified branch.

    Args:
        branch: Feature branch to compare with main. If None, use current branch.
        since: Optional start date for commit range.
        until: Optional end date for commit range.

    Returns:
        List of commit messages.
    """
    if branch is None:
        # Get current branch
        branch = run_git_command(["rev-parse", "--abbrev-ref", "HEAD"])

    # Build the git command
    cmd = ["log", "--format=%s %b", "--no-merges"]

    # Add date range if specified
    if since:
        cmd.extend(["--since", since])
    if until:
        cmd.extend(["--until", until])

    # Get commits that are in branch but not in main
    cmd.extend(["main.." + branch])

    try:
        commits = run_git_command(cmd)
        if not commits:
            return []
        return commits.split("\n")
    except RuntimeError as e:
        print(f"Error getting commits: {e}", file=sys.stderr)
        return []


def parse_commit(
    commit: str, config: ChangelogConfig
) -> tuple[str, str, bool] | None:
    """
    Parse a commit message according to conventional commits format.

    Args:
        commit: Commit message.
        config: Configuration dictionary.

    Returns:
        Tuple of (section, entry, is_breaking) or None if commit should be skipped.
    """
    # Split the commit message by lines
    lines = commit.strip().split("\n")
    header = lines[0]
    body = "\n".join(lines[1:]) if len(lines) > 1 else ""

    # Parse the commit header
    match = COMMIT_PATTERN.match(header)
    if not match:
        return None

    commit_type = match.group("type").lower()
    scope = match.group("scope")
    subject = match.group("subject")

    # Check if this commit type should be excluded
    if commit_type in config.get("exclude_types", []):
        return None

    # Determine the changelog section
    section = config["commit_types"].get(commit_type)
    if section is None:
        return None

    # Check for breaking changes
    is_breaking = bool(BREAKING_PATTERN.search(body))

    # Format the entry with better categorization and readability
    # Extract the first meaningful part of the subject to use as a component name
    component = None
    if scope:
        # Use scope as the component
        component = scope.title()
    elif ":" in subject:
        # If there's a colon in the subject, use text before it as component
        component_candidate = subject.split(":", 1)[0].strip()
        if len(component_candidate) < 30:  # Avoid using very long text as component
            component = component_candidate.title()

    # Format the entry with the component as bold prefix if available
    if component:
        entry = f"**{component}**: {subject}"
    else:
        entry = subject

    if is_breaking:
        entry = f"{entry} [BREAKING]"

    return section, entry, is_breaking


def read_changelog(changelog_path: str) -> list[str]:
    """
    Read the changelog file.

    Args:
        changelog_path: Path to changelog file.

    Returns:
        List of lines in the changelog.
    """
    try:
        with open(changelog_path, encoding="utf-8") as f:
            return f.read().splitlines()
    except FileNotFoundError:
        print(f"Warning: Changelog file not found at {changelog_path}", file=sys.stderr)
        return []


def parse_changelog(
    lines: list[str],
) -> tuple[list[str], dict[str, list[str]], dict[str, str]]:
    """
    Parse the changelog into header, sections, and links.

    Args:
        lines: Lines of the changelog.

    Returns:
        Tuple of (header_lines, sections, links).
    """
    header_lines: list[str] = []
    sections: dict[str, list[str]] = {}
    links: dict[str, str] = {}

    # State tracking
    current_version: str | None = None
    current_section: str | None = None
    in_unreleased = False
    past_header = False

    for line in lines:
        # Check for version headers
        version_match = VERSION_PATTERN.match(line)
        if version_match:
            version = version_match.group("version")
            current_version = version
            current_section = None
            past_header = True

            if version == "Unreleased":
                in_unreleased = True
            continue

        # Check for section headers
        section_match = SECTION_PATTERN.match(line)
        if section_match and in_unreleased:
            current_section = section_match.group("section")
            if current_section not in sections:
                sections[current_section] = []
            continue

        # Check for links
        link_match = LINK_PATTERN.match(line)
        if link_match:
            links[link_match.group("version")] = link_match.group("url")
            continue

        # Process content based on current state
        if not past_header:
            header_lines.append(line)
        elif in_unreleased and current_section and ENTRY_PATTERN.match(line):
            sections[current_section].append(line)

    return header_lines, sections, links


def update_changelog_content(
    changelog_path: str,
    new_entries: dict[str, list[str]],
    config: ChangelogConfig,
    finalize: bool = False,
    new_version: str | None = None,
) -> None:
    """
    Update the changelog with new entries.

    Args:
        changelog_path: Path to the changelog file.
        new_entries: Dictionary of sections and their new entries.
        config: Configuration dictionary.
        finalize: Whether to finalize a release.
        new_version: Version number for the release.

    Returns:
        None
    """
    lines = read_changelog(changelog_path)
    header_lines, sections, links = parse_changelog(lines)

    # Create a copy of the whole original file for reference
    original_content = lines.copy()

    # Identify which sections already exist in the current Unreleased block
    # to preserve their order and content
    unreleased_section_order = []
    in_unreleased = False
    current_section = None

    for line in original_content:
        if VERSION_PATTERN.match(line) and "[Unreleased]" in line:
            in_unreleased = True
            continue
        elif VERSION_PATTERN.match(line) and in_unreleased:
            # We've reached the next version section, so we're done
            in_unreleased = False
            break

        section_match = SECTION_PATTERN.match(line) if in_unreleased else None
        if section_match:
            current_section = section_match.group("section")
            if current_section not in unreleased_section_order:
                unreleased_section_order.append(current_section)

    # If no unreleased sections were found, use a standard order
    if not unreleased_section_order:
        unreleased_section_order = ["Added", "Changed", "Deprecated", "Removed", "Fixed", "Security"]

    # Combine existing entries with new ones and deduplicate
    for section, entries in new_entries.items():
        if section not in sections:
            sections[section] = []

        # Get existing entries
        existing_entries = set(sections[section])

        # Add new entries, avoiding duplicates
        for entry in entries:
            if entry not in existing_entries:
                sections[section].append(entry)

    # Generate new changelog content
    new_content = header_lines.copy()

    # For finalization, convert Unreleased to version
    if finalize and new_version:
        today = datetime.date.today().isoformat()

        # Update the links dictionary
        repo_url = config["repo_url"]
        version_prefix = config["version_prefix"]

        # Add new version link
        prev_version = None
        for version in sorted(links.keys(), reverse=True):
            if version != "Unreleased":
                prev_version = version
                break

        if prev_version:
            # Update the Unreleased link
            links["Unreleased"] = f"{repo_url}/compare/{version_prefix}{new_version}...HEAD"
            # Add new version link
            links[new_version] = f"{repo_url}/compare/{version_prefix}{prev_version}...{version_prefix}{new_version}"
        else:
            # First version
            links["Unreleased"] = f"{repo_url}/compare/{version_prefix}{new_version}...HEAD"
            links[new_version] = f"{repo_url}/releases/tag/{version_prefix}{new_version}"

        # Add Unreleased section
        new_content.append("")
        new_content.append("## [Unreleased]")

        # Add new version section
        new_content.append("")
        new_content.append(f"## [{new_version}] - {today}")
    else:
        # Just use the Unreleased section
        new_content.append("")
        new_content.append("## [Unreleased]")

    # Add sections and entries in the same order as they were in the original file
    for section_name in unreleased_section_order:
        if sections.get(section_name):
            new_content.append("")
            new_content.append(f"### {section_name}")

            # Sort entries for consistency but preserve any formatting
            # (e.g., if entries start with **Component**:)
            sorted_entries = sorted(sections[section_name], key=lambda x: x.lower())
            for entry in sorted_entries:
                new_content.append(entry)

    # Add link references
    new_content.append("")

    # Add a blank line after the sections and before the links
    new_content.append("")

    # Extract and preserve any content after the Unreleased section
    # (excluding the first version section to avoid duplication)
    preserve_content = []
    in_unreleased = False
    past_unreleased = False
    past_first_version = False

    for line in original_content:
        if VERSION_PATTERN.match(line) and "[Unreleased]" in line:
            in_unreleased = True
        elif VERSION_PATTERN.match(line) and in_unreleased:
            # First version section after Unreleased
            in_unreleased = False
            past_unreleased = True

            # If we're finalizing, we add a new version section instead
            if not finalize:
                preserve_content.append(line)
        elif past_unreleased:
            preserve_content.append(line)

    # If we're not finalizing, add all the preserved content
    if not finalize and preserve_content:
        new_content.extend(preserve_content)
    else:
        # If we are finalizing, we need to add back the other version sections and links
        past_first_version = False
        past_first_version_section = False
        for line in original_content:
            # Skip until we find the first version
            if VERSION_PATTERN.match(line) and "[Unreleased]" not in line and not past_first_version:
                past_first_version = True
                # Skip the first version section as we already added it
                if finalize:
                    continue

            # Once we're past the first version, start collecting again
            if past_first_version:
                # Skip all content in the first version section
                if not past_first_version_section and SECTION_PATTERN.match(line):
                    past_first_version_section = True
                    if finalize:
                        continue

                # When we hit the next version, reset the section flag
                if VERSION_PATTERN.match(line) and past_first_version_section:
                    new_content.append("")  # Add a blank line before the next version
                    new_content.append(line)
                    past_first_version_section = False
                elif not (finalize and not past_first_version_section):
                    # Only add the line if we're not skipping the first version section
                    new_content.append(line)

    # Add links at the end
    link_lines = []
    for version, url in sorted(links.items(), key=lambda x: x[0] if x[0] != "Unreleased" else ""):
        if version == "Unreleased":
            link_lines.insert(0, f"[{version}]: {url}")
        else:
            link_lines.append(f"[{version}]: {url}")

    new_content.extend(link_lines)

    # Write the updated changelog
    with open(changelog_path, "w", encoding="utf-8") as f:
        f.write("\n".join(new_content))


def main() -> None:
    """
    Main function to run the changelog update tool.
    """
    parser = argparse.ArgumentParser(description="Update changelog from Git history")
    parser.add_argument(
        "--branch",
        help="Branch to compare with main (default: current branch)",
    )
    parser.add_argument(
        "--since", help="Get commits since date (e.g., '2023-01-01')"
    )
    parser.add_argument(
        "--until", help="Get commits until date (e.g., '2023-12-31')"
    )
    parser.add_argument(
        "--types",
        help="Comma-separated list of commit types to include (e.g., 'feat,fix')",
    )
    parser.add_argument(
        "--config", help="Path to configuration file"
    )
    parser.add_argument(
        "--finalize",
        action="store_true",
        help="Finalize a release (rename Unreleased to version)",
    )
    parser.add_argument(
        "--version",
        help="Version number for the release (required with --finalize)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show changes without modifying the changelog",
    )

    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)

    # Check if a finalization was requested without a version
    if args.finalize and not args.version:
        parser.error("--version is required when using --finalize")

    # Override excluded types if specific types were requested
    if args.types:
        requested_types = args.types.split(",")
        # Filter commit_types to only include requested types
        filtered_types = {}
        for commit_type, section in config["commit_types"].items():
            if commit_type in requested_types:
                filtered_types[commit_type] = section
        config["commit_types"] = filtered_types
        # Clear exclude_types since we're explicitly including
        config["exclude_types"] = []

    # Get commits
    commits = get_commits(args.branch, args.since, args.until)

    if not commits:
        print("No new commits found to update the changelog.")
        return

    # Parse commits and group by section
    new_entries: dict[str, list[str]] = {}
    has_breaking_changes = False

    for commit in commits:
        parsed = parse_commit(commit, config)
        if parsed:
            section, entry, is_breaking = parsed
            if is_breaking:
                has_breaking_changes = True

            if section not in new_entries:
                new_entries[section] = []

            new_entries[section].append(f"- {entry}")

    if not new_entries:
        print("No relevant changes found to update the changelog.")
        return

    # Print summary
    print(f"Found {sum(len(entries) for entries in new_entries.values())} new changelog entries:")
    for section, entries in new_entries.items():
        print(f"\n### {section}")
        for entry in entries:
            print(entry)

    # Suggest version bump if finalizing
    if args.finalize and has_breaking_changes:
        print("\nNOTE: Breaking changes detected - consider a MAJOR version bump.")

    # Update the changelog
    if not args.dry_run:
        update_changelog_content(
            config["changelog_path"],
            new_entries,
            config,
            args.finalize,
            args.version,
        )
        print(f"\nChangelog updated at {config['changelog_path']}")
    else:
        print("\nDry run - no changes were made to the changelog.")


if __name__ == "__main__":
    main()
