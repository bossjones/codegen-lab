---
description: Security rule for GitHub Actions to address tj-actions/changed-files vulnerability and implement security best practices
globs: .github/workflows/*.yml, .github/workflows/*.yaml
alwaysApply: false
---

# GitHub Actions Security Rule

This rule helps identify and mitigate security risks in GitHub Actions workflows, particularly focusing on the tj-actions/changed-files vulnerability and implementing security best practices.

## Background

A security incident was reported by Unit42 (Palo Alto Networks) regarding GitHub Actions artifacts and dependencies. This rule helps prevent potential security issues and implements recommended best practices.

## Rules

<rule>
name: github-actions-security
description: Enforces security best practices for GitHub Actions workflows and replaces vulnerable actions
filters:
  - type: file_extension
    pattern: "\\.ya?ml$"
  - type: directory
    pattern: "^\\.github/workflows/"

actions:
  - type: suggest
    conditions:
      - pattern: "uses:\\s*tj-actions/changed-files(@|\\s*$)"
        message: |
          ⚠️ Security Alert: tj-actions/changed-files has been identified as potentially vulnerable.

          Recommended Actions:
          1. Replace with a more secure alternative:
             - Use GitHub's built-in `github.event.before` and `github.event.after` for commit ranges
             - Use `git diff --name-only ${{ github.event.before }} ${{ github.event.after }}` for changed files
             - Consider using actions/checkout with explicit commit SHA

          Example replacement:
          ```yaml
          - uses: actions/checkout@v4
            with:
              fetch-depth: 0
          - name: Get changed files
            id: changed-files
            run: |
              echo "files=$(git diff --name-only ${{ github.event.before }} ${{ github.event.after }} | tr '\n' ' ')" >> $GITHUB_OUTPUT
          ```

  - type: suggest
    conditions:
      - pattern: "uses:\\s*[^@]+@[^v]"
        message: |
          ⚠️ Security Best Practice: Always pin actions to specific versions using SHA hashes.

          Instead of using branch names or semantic versions, use the commit SHA:
          1. Find the action's repository
          2. Navigate to the desired version tag
          3. Copy the full commit SHA
          4. Update the action reference to use the SHA

          Example:
          ```yaml
          # Instead of:
          # uses: actions/checkout@main
          # Use:
          uses: actions/checkout@8ade135a41bc03ea155e62e844d188df1ea18608  # v4.1.1
          ```

  - type: suggest
    conditions:
      - pattern: "permissions:\\s*write-all"
        message: |
          ⚠️ Security Alert: Overly permissive workflow permissions detected.

          Recommended Actions:
          1. Follow the principle of least privilege
          2. Only grant permissions that are absolutely necessary
          3. Use fine-grained token permissions

          Example:
          ```yaml
          permissions:
            contents: read
            issues: write  # Only if needed
            pull-requests: write  # Only if needed
          ```

  - type: suggest
    conditions:
      - pattern: "GITHUB_TOKEN"
        message: |
          ⚠️ Security Best Practice: Review GITHUB_TOKEN permissions

          Recommendations:
          1. Set minimum required permissions for GITHUB_TOKEN
          2. Use GitHub's actions-permissions to reduce workflow permissions
          3. Implement Pipeline-Based Access Controls (PBAC)
          4. Consider using environment protection rules for sensitive workflows

          Example:
          ```yaml
          permissions:
            contents: read
            packages: read
          ```

examples:
  - input: |
      name: CI
      on: [push]
      jobs:
        build:
          runs-on: ubuntu-latest
          steps:
            - uses: tj-actions/changed-files@main
              id: changed-files
    output: |
      name: CI
      on: [push]
      jobs:
        build:
          runs-on: ubuntu-latest
          permissions:
            contents: read
          steps:
            - uses: actions/checkout@8ade135a41bc03ea155e62e844d188df1ea18608  # v4.1.1
              with:
                fetch-depth: 0
            - name: Get changed files
              id: changed-files
              run: |
                echo "files=$(git diff --name-only ${{ github.event.before }} ${{ github.event.after }} | tr '\n' ' ')" >> $GITHUB_OUTPUT

metadata:
  priority: high
  version: 1.0
  references:
    - https://unit42.paloaltonetworks.com/github-actions-supply-chain-attack/
    - https://www.paloaltonetworks.com/blog/prisma-cloud/github-actions-worm-dependencies/
</rule>
