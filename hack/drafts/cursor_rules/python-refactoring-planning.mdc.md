---
description:
globs:
alwaysApply: false
---

# Python Refactoring Planning

Planning and documentation guidelines for Python refactoring projects

This rule provides guidance for planning and documenting Python code refactoring efforts.

<rule>
name: python-refactoring-planning
description: Planning and documentation guidelines for Python refactoring projects
filters:
  - type: file_extension
    pattern: "\\.py$"
  - type: content
    pattern: "(?i)(refactor|modularize|break down|split|large file)"

actions:
  - type: suggest
    message: |
      # Python Refactoring Planning Guide

      ## Initial Planning Phase

      1. **Create a Scratch Pad**
      Add a planning docstring at the top of your module:
      ```python
      """Refactoring Plan:
      - [ ] Analyze code dependencies
      - [ ] Create directory structure
      - [ ] Create empty files with docstrings
      - [ ] Write tests for module 1
      - [ ] Implement module 1 (pseudocode first)
      - [ ] Write tests for module 2
      - [ ] Implement module 2 (pseudocode first)
      - [ ] Update imports
      - [ ] Verify tests pass
      """
      ```

      2. **Create PLAN.md**
      ```markdown
      # Refactoring Plan for [module_name]

      ## Overview
      Brief description of what's being refactored and why.

      ## Goals
      - Improve maintainability
      - Separate concerns
      - [Other specific goals]

      ## XML Tag Structure
      <success_criteria>
      - All tests passing
      - No functionality loss
      - Improved code organization
      </success_criteria>

      <implementation>
      - Phase 1: Initial setup
      - Phase 2: Component extraction
      - Phase 3: Testing and validation
      </implementation>

      <dependencies>
      - Module A depends on Module B
      - Module C requires configuration from Module D
      </dependencies>

      <testing_strategy>
      - Unit tests for each component
      - Integration tests for module interactions
      - End-to-end tests for full workflows
      </testing_strategy>

      <documentation>
      - Update module docstrings
      - Add function/class documentation
      - Create usage examples
      </documentation>

      ## Architecture Changes
      - List proposed structural changes
      - Document new module organization

      ## Risk Assessment
      <risk_assessment>
      ### High Risk Areas
      - [ ] Data migration or schema changes
      - [ ] Critical business logic modifications
      - [ ] Performance-sensitive components
      - [ ] Security-related code
      - [ ] External API changes

      ### Impact Analysis
      - **Business Impact**: [Low/Medium/High]
        - Affected business processes
        - User-facing changes
        - Compliance considerations

      ### Technical Risks
      - **Complexity**: [Low/Medium/High]
        - Complex algorithms being modified
        - Intricate dependencies
        - Technical debt implications

      ### Mitigation Strategies
      - Feature flags for gradual rollout
      - Comprehensive testing plan
      - Performance benchmarking
      - Security review if needed
      </risk_assessment>

      ## Rollback Strategy
      <rollback_strategy>
      ### Pre-Deployment
      - [ ] Create backup of current codebase
      - [ ] Document current database state
      - [ ] Save configuration files
      - [ ] Record current dependencies

      ### Rollback Triggers
      - Critical bug discovery
      - Performance degradation
      - Unexpected system behavior
      - Data integrity issues
      - Security vulnerabilities

      ### Rollback Steps
      ```bash
      # 1. Stop Services
      systemctl stop application_service

      # 2. Restore Code
      git checkout <previous_stable_commit>

      # 3. Restore Database (if needed)
      pg_restore -d dbname backup_file

      # 4. Restore Configuration
      cp /backup/config.py /app/config.py

      # 5. Restart Services
      systemctl start application_service
      ```

      ### Verification Steps
      - [ ] Verify application starts
      - [ ] Run critical path tests
      - [ ] Check data integrity
      - [ ] Monitor error rates
      - [ ] Validate core functionality

      ### Communication Plan
      - Notify stakeholders of rollback
      - Document rollback reason
      - Schedule post-mortem
      - Plan next steps
      </rollback_strategy>

      ## Implementation Phases
      1. **Setup Phase**
         - Create directory structure
         - Initialize files

      2. **Migration Phase**
         - Move components to new files
         - Add proper typing and docstrings

      3. **Integration Phase**
         - Update imports
         - Test functionality

      ## Current Status
      <status>
      - [ ] Phase 1: Setup
      - [ ] Phase 2: Migration
      - [ ] Phase 3: Integration
      </status>

      ## Notes
      <notes>
      - Document dependencies
      - Note potential issues
      - Record design decisions
      </notes>
      ```

      3. **Track Progress**
      - Update PLAN.md status after each phase
      - Document challenges and solutions
      - Record architectural decisions

      ## Documentation Standards

      1. **Module Documentation**
      ```python
      """Module purpose and functionality.

      This module handles:
      1. Primary responsibility
      2. Secondary responsibility

      Dependencies:
      - Module A
      - Module B

      Examples:
          >>> from module import function
          >>> result = function()
      """
      ```

      2. **Implementation Notes**
      - Document complex algorithms
      - Explain architectural decisions
      - Note dependencies and requirements

      3. **Progress Tracking**
      - Update scratch pad checklist
      - Mark completed items
      - Add new tasks as discovered

metadata:
  priority: high
  version: 1.0
  tags:
    - python
    - refactoring
    - planning
    - documentation
