# run format tasks
[group('format')]
format: format-import format-source

# format code import
[group('format')]
format-import:
	uv run ruff check --select=I --fix {{SOURCES}} {{TESTS}}

# format code source
[group('format')]
format-source:
	uv run ruff format {{SOURCES}} {{TESTS}}

# # format markdown
# [group('format')]
# format_markdown:
#     @echo "Formatting markdown files..."
#     @echo "SOURCE: https://github.com/tmux-python/tmuxp/blob/master/Makefile"
# 	npx prettier --parser=markdown -w *.md docs/*.md docs/**/*.md CHANGES
