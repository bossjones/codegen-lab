## v1.1.0 (2025-04-07)

### Feat

- introduce git commit and push rules for consistent message formatting
- add GitHub release automation script
- add release preparation script with enhanced safeguards

### Fix

- simplify PR creation command in release preparation script
- update GitHub CLI authentication check in release preparation script
- remove invalid commitizen consistency check

### Refactor

- replace grep -P with cross-platform sed command

## v1.0.0 (2025-04-04)

### BREAKING CHANGE

- Replaced commit.just with cz.just for commitizen-based commit workflow

### Feat

- Enhance conventional commits rule with detailed configuration
- Add PR Markdown Generator manual for structured PR descriptions

## v0.2.0 (2025-04-04)

### Feat

- Update Bats workflow and release script
- Add Bats test execution step to workflow
- Add verification step for BATS_LIB_PATH in Bats workflow
- Enhance Bats workflow by removing duplicate library paths
- Update Bats testing workflow and fragments check configuration
- Enhance Bats testing workflow with debugging support and library path adjustments
- Add Bats testing workflow for automated testing
- Update MkDocs configuration and enhance documentation generation
- Enhance MkDocs configuration and add changelog management
- Enhance mkdocs_macro_plugin with new macros and update configuration
- Update MkDocs configuration and enhance documentation styling
- Enhance documentation and tooling support

### Fix

- Improve Bats workflow error handling and output visibility
- Correct architecture and URL in taplo.just file
- Correct changelog directory path in pyproject.toml

### Refactor

- Update BATS_LIB_PATH in Bats workflow
- Update BATS_LIB_PATH verification step in Bats workflow
- Rename and enhance verification step for BATS_LIB_PATH in Bats workflow
- Revise documentation structure and consolidate content
