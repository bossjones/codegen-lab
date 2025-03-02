"""Main entry point for the Cursor Rules MCP Server.

This module allows running the server as a package:
    python -m cursor_rules_mcp_server
"""

import asyncio
import logging
import sys

from .server import main


def parse_args(args: list[str] | None = None) -> dict:
    """Parse command line arguments.

    Args:
        args (Optional[List[str]]): Command line arguments. Defaults to sys.argv[1:].

    Returns:
        dict: Parsed arguments.

    """
    import argparse

    parser = argparse.ArgumentParser(description="Run the Cursor Rules MCP Server")
    parser.add_argument(
        "--db-path",
        type=str,
        help="Path to the SQLite database file"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run the server on (default: 8000)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Host to bind the server to (default: localhost)"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level (default: INFO)"
    )

    return vars(parser.parse_args(args))


def main_cli() -> None:
    """Entry point for the command-line script."""
    # Parse command line arguments
    parsed_args = parse_args()

    # Configure logging
    log_level = getattr(logging, parsed_args["log_level"])
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Run the server
    try:
        # On Windows, we need to set the event loop policy
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        # Run the main function
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
    except Exception as e:
        logging.error(f"Error running server: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main_cli()
