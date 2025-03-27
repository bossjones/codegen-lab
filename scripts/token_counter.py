#!/usr/bin/env python3
from pathlib import Path
from typing import List, Optional

import tiktoken
import typer

MODEL_ENCODINGS = {
    "gpt-4o": "o200k_base",
    "gpt-4": "cl100k_base",
    "gpt-3.5": "cl100k_base",
    "codex": "p50k_base",
    "davinci": "r50k_base",
    "claude-3.5": "cl100k_base",
    "claude-3": "cl100k_base",
}

app = typer.Typer(help="Token counter for AI model context windows")

def count_tokens(text: str, model: str) -> int:
    """Count tokens using model-specific encoding"""
    try:
        encoding_name = MODEL_ENCODINGS.get(model, model)
        encoding = tiktoken.get_encoding(encoding_name)
    except KeyError:
        typer.echo(f"Warning: Using default cl100k_base encoding for unknown model {model}", err=True)
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))

@app.command()
def main(
    text: str | None = typer.Option(None, "--text", "-t", help="Input text to analyze"),
    files: list[Path] = typer.Option([], "--files", "-f", help="Paths to text files"),
    model: str = typer.Option("claude-3.5", "--model", "-m", help="Model name or encoding"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Output only the token count"),
):
    """
    Calculate total tokens across multiple files/text for AI model context
    """
    total_tokens = 0
    total_chars = 0

    # Process text input
    if text:
        total_tokens += count_tokens(text, model)
        total_chars += len(text)

    # Process files
    for file_path in files:
        try:
            content = file_path.read_text(encoding="utf-8")
            total_tokens += count_tokens(content, model)
            total_chars += len(content)
        except FileNotFoundError:
            typer.echo(f"Error: File not found - {file_path}", err=True)
            raise typer.Exit(code=1)
        except UnicodeDecodeError:
            typer.echo(f"Error: Could not decode {file_path} as UTF-8", err=True)
            raise typer.Exit(code=1)

    if not text and not files:
        typer.echo("Error: Must provide either --text or --files", err=True)
        raise typer.Exit(code=1)

    if quiet:
        typer.echo(total_tokens)
    else:
        typer.echo(f"\nModel: {model}")
        typer.echo(f"Files processed: {len(files)}")
        typer.echo(f"Total characters: {total_chars}")
        typer.echo(f"Total tokens: {total_tokens}")
        if total_tokens > 0:
            typer.echo(f"Avg characters per token: {total_chars/total_tokens:.2f}")

if __name__ == "__main__":
    app()
