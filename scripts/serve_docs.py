#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to serve MkDocs documentation locally with enhanced functionality.

This script provides a convenient way to serve the documentation locally,
with additional features like automatic builds and hot reloading.
"""

import argparse
import os
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
    import shutil

    build_dir = os.path.join(os.getcwd(), "site")
    if os.path.exists(build_dir):
        print(f"Cleaning build directory: {build_dir}")
        shutil.rmtree(build_dir)
        os.makedirs(build_dir)
    else:
        print(f"Build directory doesn't exist, creating: {build_dir}")
        os.makedirs(build_dir)


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
        cmd.extend(["--dev-addr", f"{args.host}:{args.port}"])

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


if __name__ == "__main__":
    sys.exit(main())
