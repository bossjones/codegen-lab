---
description:
globs:
alwaysApply: false
---

# Python Documentation Standards

Documentation patterns and standards for Python projects

This rule provides comprehensive guidance for Python code documentation.

<rule>
name: python-documentation-standards
description: Documentation patterns and standards for Python projects
filters:
  - type: file_extension
    pattern: "\\.py$"

actions:
  - type: suggest
    message: |
      # Python Documentation Standards Guide

      ## Module Documentation

      1. **Module Docstring**
      ```python
      """Module name and purpose.

      This module provides functionality for:
      1. Primary purpose
      2. Secondary purpose

      Typical usage example:
          >>> from module import function
          >>> result = function()

      Attributes:
          CONSTANT_NAME: Description of module-level constant

      Dependencies:
          - Required package A
          - Required package B
      """
      ```

      2. **Class Documentation**
      ```python
      class UserManager:
          """Manages user operations and state.

          This class handles user creation, validation, and state management.
          It provides a clean interface for user operations.

          Attributes:
              default_role: Default role for new users
              max_users: Maximum number of users allowed

          Example:
              >>> manager = UserManager()
              >>> user = manager.create_user("test@example.com")
          """

          def __init__(self, max_users: int = 100) -> None:
              """Initialize the UserManager.

              Args:
                  max_users: Maximum number of users allowed.
                      Defaults to 100.

              Raises:
                  ValueError: If max_users is less than 1.
              """
              if max_users < 1:
                  raise ValueError("max_users must be positive")
              self.max_users = max_users
      ```

      3. **Function Documentation**
      ```python
      def process_user_data(
          user_id: str,
          data: Dict[str, Any],
          *,
          validate: bool = True,
      ) -> Dict[str, Any]:
          """Process user data and return results.

          This function validates and processes user data,
          applying business rules and returning results.

          Args:
              user_id: Unique identifier for the user
              data: Dictionary containing user data
              validate: Whether to validate data before processing.
                  Defaults to True.

          Returns:
              Dictionary containing processed results with keys:
              - status: Processing status
              - errors: List of errors if any
              - result: Processed data if successful

          Raises:
              ValueError: If user_id is empty or data is invalid
              UserNotFoundError: If user_id doesn't exist

          Example:
              >>> data = {"name": "Test User"}
              >>> result = process_user_data("123", data)
              >>> print(result["status"])
              'success'
          """
          if not user_id:
              raise ValueError("user_id cannot be empty")
      ```

      ## Type Annotations

      1. **Basic Types**
      ```python
      from typing import Dict, List, Optional, Union, Any

      def get_user(user_id: str) -> Optional[Dict[str, Any]]:
          """Get user by ID."""
          pass

      def update_users(users: List[Dict[str, Any]]) -> None:
          """Update multiple users."""
          pass
      ```

      2. **Complex Types**
      ```python
      from typing import TypeVar, Generic, Protocol

      T = TypeVar('T')

      class DataProcessor(Protocol):
          """Protocol for data processors."""
          def process(self, data: T) -> T:
              """Process data of type T."""
              ...

      class UserProcessor(Generic[T]):
          """Generic user data processor."""
          def process(self, data: T) -> T:
              """Process user data."""
              return data
      ```

      3. **Type Aliases**
      ```python
      from typing import Dict, List, Union, TypeAlias

      JSON: TypeAlias = Union[Dict[str, 'JSON'], List['JSON'], str, int, float, bool, None]
      UserData: TypeAlias = Dict[str, Union[str, int, List[str]]]

      def process_json(data: JSON) -> JSON:
          """Process JSON data."""
          return data
      ```

      ## Documentation Best Practices

      1. **Docstring Format**
      - Use reStructuredText format
      - Include all sections (Args, Returns, Raises, Example)
      - Keep examples concise and clear
      - Document all parameters and return types

      2. **Code Comments**
      ```python
      # Constants
      MAX_RETRIES = 3  # Maximum number of retry attempts

      # Complex algorithms
      def complex_algorithm():
          # Step 1: Initialize data structure
          data = []

          # Step 2: Process in chunks
          for chunk in chunks:
              # Skip empty chunks
              if not chunk:
                  continue

              # Apply transformation
              result = transform(chunk)
              data.append(result)
      ```

      3. **README Structure**
      ```markdown
      # Project Name

      Brief description of the project.

      ## Installation

      ```bash
      pip install package-name
      ```

      ## Usage

      Basic usage example:

      ```python
      from package import function
      result = function()
      ```

      ## API Reference

      ### `function(param: str) -> dict`

      Detailed function documentation.

      ## Development

      Setup development environment:

      ```bash
      # Install dependencies
      pip install -e ".[dev]"
      ```
      ```

      4. **Type Checking Comments**
      ```python
      # For runtime vs type checking imports
      from typing import TYPE_CHECKING

      if TYPE_CHECKING:
          from _pytest.fixtures import FixtureRequest
          from pytest_mock.plugin import MockerFixture

      # For complex type ignores
      def complex_function():
          result = external_library()  # type: ignore[no-any-return]
          return result

      # For forward references
      class Tree:
          def get_parent(self) -> "Tree":  # Forward reference
              return self.parent
      ```

metadata:
  priority: high
  version: 1.0
  tags:
    - python
    - documentation
    - type-hints
    - best-practices
</rule>
