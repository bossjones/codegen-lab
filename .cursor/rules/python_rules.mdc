---
description: Python development rules and standards
globs: ["**/*.py"]
---
# Python Development Standards

Rules for Python development in the Codegen Lab project, including type hints, docstrings, and testing standards.

<rule>
name: python_development_standards
description: Standards for Python code development including typing, docstrings, and testing
filters:
  # Match Python files
  - type: file_extension
    pattern: "\\.py$"
  # Match Python code
  - type: content
    pattern: "def |class "

actions:
  - type: suggest
    message: |
      # Python Development Standards

      This project follows strict Python development standards:

      ## Type Annotations

      All Python code must include comprehensive type hints:

      ```python
      def process_data(input_data: list[str], max_items: int = 10) -> dict[str, Any]:
          """Process the input data and return results."""
          # Implementation
      ```

      ## Docstrings

      Follow PEP 257 for docstrings:

      ```python
      def calculate_total(items: list[Item]) -> float:
          """Calculate the total value of all items.

          Args:
              items: List of Item objects to process

          Returns:
              The total calculated value

          Raises:
              ValueError: If any item has a negative value
          """
          # Implementation
      ```

      ## Testing

      All code must have corresponding pytest tests:

      ```python
      def test_calculate_total() -> None:
          """Test that calculate_total correctly sums item values."""
          items = [Item(value=10.0), Item(value=20.0)]
          result = calculate_total(items)
          assert result == 30.0
      ```

      ## Code Organization

      - Follow PEP 8 style guidelines
      - Use consistent import ordering (standard library, third-party, local)
      - Organize code into logical modules
      - Keep functions and methods focused on a single responsibility

      ## Package Structure

      For workspace packages, follow the src layout:

      ```
      package-name/
      ├── pyproject.toml
      ├── src/
      │   └── package_name/
      │       ├── __init__.py
      │       └── module.py
      └── tests/
          └── test_module.py
      ```

      ## Integration with UV Workspace

      This project uses UV workspace for package management.

      @uv-workspace.mdc

examples:
  - input: |
      # Bad: No type hints or proper docstrings
      def process_data(data, limit=100):
          # Process the data
          return {"result": processed}

      # Good: Complete type hints and docstrings
      def process_data(data: list[dict[str, Any]], limit: int = 100) -> dict[str, Any]:
          """Process the input data and return results.

          Args:
              data: List of data dictionaries to process
              limit: Maximum number of items to process

          Returns:
              Dictionary containing processed results

          Raises:
              ValueError: If data is empty or contains invalid entries
          """
          # Process the data
          return {"result": processed}
    output: "Properly formatted Python function with type hints and docstrings"

  - input: |
      # Bad: Test without type hints or docstrings
      def test_process_data():
          data = [{"key": "value"}]
          result = process_data(data)
          assert "result" in result

      # Good: Test with type hints and docstrings
      def test_process_data() -> None:
          """Test that process_data correctly handles valid input data."""
          data = [{"key": "value"}]
          result = process_data(data)
          assert "result" in result
          assert isinstance(result["result"], list)
    output: "Properly formatted test function with type hints and docstrings"

metadata:
  priority: high
  version: 1.0
  tags:
    - python
    - type-hints
    - docstrings
    - testing
</rule>

<rule>
name: python_imports_organization
description: Standards for organizing imports in Python files
filters:
  # Match Python files
  - type: file_extension
    pattern: "\\.py$"
  # Match import statements
  - type: content
    pattern: "import |from "

actions:
  - type: suggest
    message: |
      # Python Import Organization

      Organize imports in this order:

      1. **Standard library imports**
      2. **Third-party library imports**
      3. **Local application imports**

      Each group should be separated by a blank line.

      ## Example:

      ```python
      # Standard library imports
      import os
      import sys
      from typing import Any, Dict, List, Optional, Union

      # Third-party imports
      import numpy as np
      import pandas as pd
      from pydantic import BaseModel

      # Local application imports
      from myapp.models import User
      from myapp.utils import format_data
      ```

      ## Type Checking Imports

      For imports only needed for type checking:

      ```python
      from typing import TYPE_CHECKING

      if TYPE_CHECKING:
          from _pytest.capture import CaptureFixture
          from _pytest.fixtures import FixtureRequest
          from _pytest.logging import LogCaptureFixture
          from _pytest.monkeypatch import MonkeyPatch
          from pytest_mock.plugin import MockerFixture
      ```

examples:
  - input: |
      # Bad: Mixed import order
      import pandas as pd
      import os
      from myapp.utils import helper
      import sys
      from typing import List, Dict

      # Good: Organized imports
      import os
      import sys
      from typing import Dict, List

      import pandas as pd

      from myapp.utils import helper
    output: "Properly organized imports following the standard convention"

metadata:
  priority: medium
  version: 1.0
  tags:
    - python
    - imports
    - organization
</rule>
