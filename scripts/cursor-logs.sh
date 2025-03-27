#!/usr/bin/env zsh

# Increase maximum number of open files
# Check current limits
echo "Current ulimit: $(ulimit -n)"
# Try to increase to 10240 first, if that fails, try 4096
if ! ulimit -n 10240 2>/dev/null; then
    ulimit -n 4096 2>/dev/null
fi
echo "New ulimit: $(ulimit -n)"

# Script to tail Cursor logs and Claude logs, colorized with ccze
# Finds all log files modified today in the Cursor logs directories

# Path to Claude logs
CLAUDE_LOGS="$HOME/Library/Logs/Claude/mcp-server-prompt_library.log"

# Paths to Cursor logs directories
CURSOR_NIGHTLY_LOGS_DIR="$HOME/Library/Application Support/Cursor Nightly/logs/"
CURSOR_STABLE_LOGS_DIR="$HOME/Library/Application Support/Cursor/logs/"

# Create an array for log files
log_files=("$CLAUDE_LOGS")

# Find all log files modified today in both Cursor logs directories
# zsh arrays handle spaces in filenames correctly
cursor_nightly_logs=("${(@f)$(find "$CURSOR_NIGHTLY_LOGS_DIR" -type f -name "*.log" -mtime 0 2>/dev/null)}")
cursor_stable_logs=("${(@f)$(find "$CURSOR_STABLE_LOGS_DIR" -type f -name "*.log" -mtime 0 2>/dev/null)}")

# Combine all arrays
all_logs=("$log_files[@]" "$cursor_nightly_logs[@]" "$cursor_stable_logs[@]")

# Tail all logs, colorized with ccze
tail -f "${all_logs[@]}" | ccze -A
