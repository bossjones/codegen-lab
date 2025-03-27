#!/usr/bin/env python3
"""
Script to serve MkDocs documentation with automatic port conflict resolution.

This script checks if the default port is in use, and either:
1. Kills existing MkDocs processes using that port, or
2. Uses an alternative port
"""

import argparse
import os
import shutil
import signal
import socket
import subprocess
import sys
import time
from typing import List, Optional, Union

import psutil


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns:
        argparse.Namespace: The parsed command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Serve MkDocs documentation with automatic port management"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to use for the server (default: 8000)"
    )
    parser.add_argument(
        "--kill-existing", action="store_true", help="Kill existing MkDocs processes using the port"
    )
    parser.add_argument(
        "--no-kill-existing", action="store_false", dest="kill_existing",
        help="Don't kill existing processes, use alternative port instead"
    )
    parser.add_argument(
        "--no-gh-deploy-url", action="store_false", dest="gh_deploy_url",
        help="Don't use GitHub Pages URL in configuration"
    )
    parser.add_argument(
        "--clean", action="store_true", help="Clean the build directory before building"
    )
    parser.add_argument(
        "--build-only", action="store_true", help="Only build the documentation, don't serve it"
    )
    return parser.parse_args()


def run_command(cmd: list[str]) -> subprocess.CompletedProcess | int:
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
        with open(config_file) as f:
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


def is_port_in_use(port: int) -> bool:
    """
    Check if a port is already in use.

    Args:
        port: The port number to check

    Returns:
        True if the port is in use, False otherwise
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def find_mkdocs_pid(port: int) -> list[int]:
    """
    Find process IDs of MkDocs servers running on the given port.

    Args:
        port: The port number to check

    Returns:
        List of process IDs running MkDocs on the specified port
    """
    pids = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline', [])
            if cmdline and 'mkdocs' in ' '.join(cmdline) and f'127.0.0.1:{port}' in ' '.join(cmdline):
                pids.append(proc.info['pid'])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return pids


def kill_process(pid: int) -> bool:
    """
    Kill a process by its PID.

    Args:
        pid: Process ID to kill

    Returns:
        True if successfully killed, False otherwise
    """
    try:
        os.kill(pid, signal.SIGTERM)
        # Wait to see if it actually died
        time.sleep(0.5)
        if psutil.pid_exists(pid):
            os.kill(pid, signal.SIGKILL)  # Force kill if still alive
        return True
    except OSError:
        return False


def find_available_port(start_port: int = 8000, max_port: int = 8100) -> int:
    """
    Find an available port starting from the specified port.

    Args:
        start_port: The port to start checking from
        max_port: The maximum port number to check

    Returns:
        An available port number
    """
    for port in range(start_port, max_port):
        if not is_port_in_use(port):
            return port
    raise RuntimeError(f"Could not find an available port between {start_port} and {max_port}")


def serve_docs(default_port: int = 8000,
               kill_existing: bool = False,
               gh_deploy_url: bool = False) -> int:
    """
    Serve MkDocs documentation with automatic port conflict resolution.

    Args:
        default_port: The default port to use
        kill_existing: Whether to kill existing MkDocs processes on the port
        gh_deploy_url: Whether to use GitHub Pages URL in the configuration

    Returns:
        Exit code of the MkDocs process
    """
    port = default_port

    # Check if the port is in use
    if is_port_in_use(port):
        pids = find_mkdocs_pid(port)

        if pids and kill_existing:
            print(f"Found MkDocs processes using port {port}. Terminating...")
            for pid in pids:
                if kill_process(pid):
                    print(f"Successfully terminated process {pid}")
                else:
                    print(f"Failed to terminate process {pid}")

            # Wait a moment for the port to be released
            time.sleep(1)

        # If we couldn't kill or chose not to, find another port
        if is_port_in_use(port):
            if kill_existing:
                print(f"Port {port} is still in use. Looking for another port...")
            else:
                print(f"Port {port} is in use. Looking for another port...")
            port = find_available_port(port)
            print(f"Using alternative port: {port}")

    # Prepare the command
    cmd = [sys.executable, "-m", "mkdocs", "serve", "--dev-addr", f"127.0.0.1:{port}"]

    # Set site_url based on gh_deploy_url flag
    if not gh_deploy_url:
        # Use localhost URL
        cmd.extend(["--config-file", "mkdocs.yml"])

    try:
        # Print the command we're about to run
        print(f"Running: {' '.join(cmd)}")

        # Execute mkdocs serve
        process = subprocess.Popen(cmd)

        # Wait a moment
        time.sleep(2)

        # Check if the process is still running
        if process.poll() is None:
            print(f"MkDocs server started successfully on http://127.0.0.1:{port}/")
            print("Press Ctrl+C to stop the server")
            try:
                # Wait for the user to interrupt
                process.wait()
                return process.returncode
            except KeyboardInterrupt:
                # Handle Ctrl+C gracefully
                print("\nStopping MkDocs server...")
                process.terminate()
                process.wait(timeout=5)
                return 0
        else:
            print(f"MkDocs server failed to start. Return code: {process.returncode}")
            return process.returncode
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 130  # Standard exit code for SIGINT


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
    if not args.gh_deploy_url:
        modify_mkdocs_config_for_local(True)

    try:
        if args.build_only:
            # Just build the docs
            cmd = [sys.executable, "-m", "mkdocs", "build"]
            return run_command(cmd)
        else:
            # Serve the docs
            exit_code = serve_docs(
                default_port=args.port,
                kill_existing=args.kill_existing,
                gh_deploy_url=args.gh_deploy_url
            )
            return exit_code
    finally:
        # Restore original config if we modified it
        if not args.gh_deploy_url:
            modify_mkdocs_config_for_local(False)


if __name__ == "__main__":
    sys.exit(main())
