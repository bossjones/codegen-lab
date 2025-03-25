#!/usr/bin/env zsh

# Script to tail Cursor logs and Claude logs, colorized with ccze
# Finds all log files modified today in the Cursor logs directory

# Path to Claude logs
CLAUDE_LOGS="$HOME/Library/Logs/Claude/mcp-server-prompt_library.log"

# Path to Cursor logs directory
CURSOR_LOGS_DIR="$HOME/Library/Application Support/Cursor Nightly/logs/"

# Create an array for log files
log_files=("$CLAUDE_LOGS")

# Find all log files modified today in the Cursor logs directory
# zsh arrays handle spaces in filenames correctly
cursor_logs=("${(@f)$(find "$CURSOR_LOGS_DIR" -type f -name "*.log" -mtime 0)}")

# Combine the arrays
all_logs=("$log_files[@]" "$cursor_logs[@]")

# Tail all logs, colorized with ccze
tail -f "${all_logs[@]}" | ccze -A
