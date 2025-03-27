---
description:
globs:
alwaysApply: false
---

# Python Modularization Guide

Code organization patterns and best practices for Python projects

This rule provides guidance for organizing Python code into well-structured modules and packages.

<rule>
name: python-modularization
description: Code organization patterns and best practices for Python projects
filters:
  - type: file_extension
    pattern: "\\.py$"

actions:
  - type: suggest
    message: |
      # Python Code Organization Guide

      ## Directory Structure
      ```
      src/package_name/
      ├── __init__.py
      ├── submodule/
      │   ├── __init__.py
      │   ├── models.py       # Data models and types
      │   ├── utils.py        # Utility functions
      │   ├── services.py     # Business logic
      │   └── resources.py    # API endpoints/resources
      └── main_module.py      # Original entry point
      ```

      ## Module Organization

      1. **Models Module (models.py)**
      ```python
      """Data models and type definitions.

      This module contains all data structures and type definitions
      used throughout the package.
      """
      from typing import Dict, List, Optional

      class UserModel:
          """User data model."""
          def __init__(self, name: str, email: str) -> None:
              self.name = name
              self.email = email
      ```

      2. **Services Module (services.py)**
      ```python
      """Business logic and core functionality.

      This module contains the main business logic and
      processing functions.
      """
      from typing import Dict, Any
      from .models import UserModel

      def process_user(user: UserModel) -> Dict[str, Any]:
          """Process user data."""
          return {"status": "processed"}
      ```

      3. **Utils Module (utils.py)**
      ```python
      """Utility functions and helpers.

      This module contains reusable utility functions.
      """
      from typing import Any, Optional

      def validate_input(data: Any) -> Optional[str]:
          """Validate input data."""
          return None  # Return error message if invalid
      ```

      ## Import Management

      1. **Import Organization**
      ```python
      # Standard library imports
      from typing import Dict, List
      import json

      # Third-party imports
      import pytest
      import requests

      # Local imports
      from .models import UserModel
      from .services import process_user
      ```

      2. **Import in __init__.py**
      ```python
      """Package exports and version information."""
      from .models import UserModel
      from .services import process_user

      __all__ = ['UserModel', 'process_user']
      __version__ = '0.1.0'
      ```

      3. **Type Checking Imports**
      ```python
      from typing import TYPE_CHECKING

      if TYPE_CHECKING:
          from .custom_types import CustomType
      ```

      ## Best Practices

      1. **Module Independence**
      - Keep modules focused on single responsibility
      - Minimize dependencies between modules
      - Use interfaces to define module boundaries

      2. **Circular Dependencies**
      - Avoid circular imports
      - Use dependency injection
      - Consider moving shared code to utils

      3. **Package Structure**
      - Use src/ directory layout
      - Keep tests outside src/
      - Include type hints and docstrings

      4. **Re-export Pattern**
      - Export public API in __init__.py
      - Use __all__ to control exports
      - Maintain backward compatibility

metadata:
  priority: high
  version: 1.0
  tags:
    - python
    - modularization
    - code-organization
    - best-practices
