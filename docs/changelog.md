# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]

## [0.2.0] - 2025-03-02

### Added
- **Cheatsheets**: Add Taskfile cheatsheet and repomix cheatsheet
- **Cursor**: Add cheatsheet creation best practices documentation - Comprehensive guidelines for creating well-structured command cheatsheets
- **Cursor**: Add MCP server configuration for memory file path - Configure the Cursor MCP server with a memory file path
- **Cursor**: Add MCP server development guidelines and best practices - Comprehensive documentation for developing Model Context Protocol (MCP) servers in Python
- **Makefile**: Update Taskfile copy destination path - Modify the `copy-global-taskfile` target to use `~/Taskfile.yml` instead of `~/.taskfile.yml`
- **Taskfile**: Add empty line in Taskfile.yml - Minor whitespace adjustment to improve readability
- **VSCode**: Add VSCode settings and Taskfile schema integration

### Changed
- **Cursor**: Add output.txt context extraction guidelines - Enhanced documentation for working with output.txt files
- **Fastmcp**: Add comprehensive FastMCP server development examples - Expanded documentation with detailed usage examples
- **Fastmcp**: Enhance server development guidelines with examples - Detailed server type selection and implementation guidelines
- **Fastmcp**: Expand documentation with advanced MCP server examples - Comprehensive usage examples and demonstrations
- **Taskfile**: Update Taskfile schema and improve organization

## [0.1.0] - 2025-02-15

### Added
- Initial release
- Core code generation functionality
- Basic API functionality
- Command-line interface
- Basic documentation
- Documentation structure
- Initial project setup

### Fixed
- N/A

### Changed
- N/A

### Removed
- N/A

## How to Update the Changelog

1. Always add new entries at the top under the `[Unreleased]` section
2. Group changes by type: Added, Changed, Deprecated, Removed, Fixed, Security
3. When releasing a new version, rename the `[Unreleased]` section to the new version number and date
4. Create a new `[Unreleased]` section at the top
5. Use link references at the bottom of the file for version comparisons

[Unreleased]: https://github.com/bossjones/codegen-lab/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/bossjones/codegen-lab/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/bossjones/codegen-lab/releases/tag/v0.1.0
