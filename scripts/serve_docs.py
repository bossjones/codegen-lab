#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to serve MkDocs documentation locally with enhanced functionality.

This script provides a convenient way to serve the documentation locally,
with additional features like automatic builds and hot reloading.
"""

import argparse
import os
import shutil
import subprocess
import sys
from typing import List, Optional, Union


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns:
        argparse.Namespace: The parsed command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Serve MkDocs documentation locally with enhanced functionality"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to serve documentation on"
    )
    parser.add_argument(
        "--host", type=str, default="127.0.0.1", help="Host to serve documentation on"
    )
    parser.add_argument(
        "--no-livereload", action="store_true", help="Disable live reload"
    )
    parser.add_argument(
        "--build-only", action="store_true", help="Build documentation without serving"
    )
    parser.add_argument(
        "--clean", action="store_true", help="Clean the build directory before building"
    )
    parser.add_argument(
        "--dev-addr",
        type=str,
        default="127.0.0.1:8000",
        help="IP address and port to serve documentation (default: 127.0.0.1:8000)",
    )
    parser.add_argument(
        "--no-gh-deploy-url",
        action="store_true",
        help="Disable GitHub Pages URL path for local development",
    )
    return parser.parse_args()


def run_command(cmd: List[str]) -> Union[subprocess.CompletedProcess, int]:
    """
    Run a command in a subprocess.

    Args:
        cmd: The command to run, as a list of strings.

    Returns:
        Union[subprocess.CompletedProcess, int]: The completed process object or return code.
    """
    try:
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        return e.returncode
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return 130


def ensure_directory_exists(path: str) -> None:
    """
    Ensure that a directory exists, creating it if necessary.

    Args:
        path: The path to the directory.
    """
    os.makedirs(path, exist_ok=True)


def clean_build_dir() -> None:
    """Clean the build directory by removing all files in it."""
    build_dir = os.path.join(os.getcwd(), "site")
    if os.path.exists(build_dir):
        print(f"Cleaning build directory: {build_dir}")
        shutil.rmtree(build_dir)
        os.makedirs(build_dir)
    else:
        print(f"Build directory doesn't exist, creating: {build_dir}")
        os.makedirs(build_dir)


def modify_mkdocs_config_for_local(enable_local_mode: bool) -> None:
    """
    Temporarily modify the MkDocs configuration for local development.

    Args:
        enable_local_mode (bool): Whether to enable local mode (True) or restore GitHub Pages mode (False).
    """
    config_file = os.path.join(os.getcwd(), "mkdocs.yml")

    # Create a backup if we're enabling local mode
    if enable_local_mode and not os.path.exists(f"{config_file}.bak"):
        shutil.copy2(config_file, f"{config_file}.bak")

    if enable_local_mode:
        # Read the current config
        with open(config_file, "r") as f:
            lines = f.readlines()

        # Modify the site_url for local development
        with open(config_file, "w") as f:
            for line in lines:
                if line.strip().startswith("site_url:"):
                    f.write("site_url: http://127.0.0.1:8000/\n")
                else:
                    f.write(line)
    else:
        # Restore from backup if it exists
        if os.path.exists(f"{config_file}.bak"):
            shutil.copy2(f"{config_file}.bak", config_file)
            os.remove(f"{config_file}.bak")


def main() -> int:
    """
    Main function to serve or build the documentation.

    Returns:
        int: Exit code (0 for success, non-zero for failure).
    """
    args = parse_args()

    # Make sure the scripts directory exists
    ensure_directory_exists("scripts")

    # Clean build directory if requested
    if args.clean:
        clean_build_dir()

    # Modify config for local development if requested
    if args.no_gh_deploy_url:
        modify_mkdocs_config_for_local(True)

    try:
        # Create base command with UV
        base_cmd = [sys.executable, "-m", "mkdocs"]

        if args.build_only:
            # Build the documentation
            cmd = base_cmd + ["build"]
            result = run_command(cmd)
            if isinstance(result, subprocess.CompletedProcess):
                return result.returncode
            return result
        else:
            # Serve the documentation
            cmd = base_cmd + ["serve"]

            # Add port and host arguments if provided
            cmd.extend(["--dev-addr", f"{args.dev_addr}"])

            # Add no-livereload flag if provided
            if args.no_livereload:
                cmd.append("--no-livereload")

            # Run the command
            try:
                result = run_command(cmd)
                if isinstance(result, subprocess.CompletedProcess):
                    return result.returncode
                return result
            except KeyboardInterrupt:
                print("\nStopping documentation server")
                return 0
    finally:
        # Restore original config if we modified it
        if args.no_gh_deploy_url:
            modify_mkdocs_config_for_local(False)


if __name__ == "__main__":
    sys.exit(main())
