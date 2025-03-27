---
description:
globs:
alwaysApply: false
---

# Python Refactoring Workflow Guide

Step-by-step workflow guide for Python code refactoring projects

This rule provides a step-by-step workflow for Python code refactoring.

<rule>
name: python-refactoring-workflow
description: Step-by-step workflow for Python code refactoring projects
filters:
  - type: file_extension
    pattern: "\\.py$"
  - type: content
    pattern: "(?i)(refactor|modularize|break down|split|large file)"

actions:
  - type: suggest
    message: |
      # Python Refactoring Workflow Guide

      ## Step 1: Setup Environment

      ```bash
      # Create directory structure
      mkdir -p src/package_name/submodule || true
      mkdir -p tests/unit tests/integration || true

      # Initialize files
      touch src/package_name/__init__.py
      touch src/package_name/submodule/__init__.py
      touch tests/conftest.py
      ```

      ## Step 2: Create Test Infrastructure

      ```python
      # tests/conftest.py
      """Test fixtures and configuration."""
      from typing import TYPE_CHECKING
      import pytest

      if TYPE_CHECKING:
          from _pytest.fixtures import FixtureRequest
          from pytest_mock.plugin import MockerFixture

      @pytest.fixture
      def sample_data():
          """Provide sample test data."""
          return {"test": "data"}
      ```

      ## Step 3: Extract Components

      1. **Create Component Files**
      ```bash
      touch src/package_name/submodule/models.py
      touch src/package_name/submodule/services.py
      touch tests/unit/test_models.py
      touch tests/unit/test_services.py
      ```

      2. **Add Tests First**
      ```python
      # tests/unit/test_models.py
      """Test the models module."""
      import pytest
      from package_name.submodule.models import UserModel

      def test_user_model():
          """Test UserModel initialization."""
          user = UserModel(name="test", email="test@example.com")
          assert user.name == "test"
          assert user.email == "test@example.com"
      ```

      3. **Implement Component**
      ```python
      # src/package_name/submodule/models.py
      """Data models module."""
      from typing import Optional

      class UserModel:
          """User data model."""
          def __init__(self, name: str, email: str) -> None:
              self.name = name
              self.email = email
      ```

      ## Step 4: Quality Checks

      ```bash
      # 1. Format code
      uv run ruff format .

      # 2. Run tests
      uv run pytest

      # 3. Check and fix linting
      uv run ruff check . --fix --show-fixes

      # 4. Check types
      uv run mypy

      # 5. Verify tests again
      uv run pytest
      ```

      ## Step 5: Update Dependencies

      1. **Check Imports**
      ```python
      # src/package_name/submodule/__init__.py
      """Package exports."""
      from .models import UserModel
      from .services import process_user

      __all__ = ['UserModel', 'process_user']
      ```

      2. **Update Original Module**
      ```python
      # src/package_name/main.py
      """Main module now importing from submodules."""
      from package_name.submodule import UserModel, process_user

      __all__ = ['UserModel', 'process_user']
      ```

      ## Step 6: Integration Testing

      ```python
      # tests/integration/test_workflow.py
      """Integration tests for complete workflow."""
      import pytest
      from package_name.submodule import UserModel, process_user

      def test_complete_workflow():
          """Test the entire workflow."""
          # Create user
          user = UserModel(name="test", email="test@example.com")

          # Process user
          result = process_user(user)

          # Verify result
          assert result["status"] == "success"
      ```

      ## Troubleshooting Guide

      1. **Import Issues**
      ```python
      # Add to conftest.py for import debugging
      import sys
      from pathlib import Path

      # Add src to path if needed
      src_path = Path(__file__).parent.parent / "src"
      if src_path.exists():
          sys.path.insert(0, str(src_path))
      ```

      2. **Test Failures**
      ```python
      # Add detailed assertions
      def test_with_details():
          """Test with detailed failure messages."""
          result = process_user(user)
          assert result is not None, "Result should not be None"
          assert "status" in result, f"Expected 'status' in {result}"
          assert result["status"] == "success", f"Got {result['status']}"
      ```

      3. **Type Issues**
      ```python
      # Add type ignore comments when needed
      from typing import TYPE_CHECKING

      if TYPE_CHECKING:
          from .types import CustomType  # type: ignore
      ```

      ## Best Practices

      1. **Atomic Changes**
      - Make small, focused changes
      - Test after each change
      - Commit working states

      2. **Error Handling**
      - Add proper error handling
      - Use custom exceptions
      - Log important information

      3. **Documentation**
      - Update docstrings
      - Add inline comments
      - Maintain README

metadata:
  priority: high
  version: 1.0
  tags:
    - python
    - refactoring
    - workflow
    - best-practices
</rule>
