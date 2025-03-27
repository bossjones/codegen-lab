---
description:
globs:
alwaysApply: false
---
# Pytest Suggest Three Fixes

Suggest Three Approaches to Fix Failing Tests

This rule provides guidance for generating three different approaches to fix failing tests.

<rule>
name: pytest-suggest-3-fixes
description: Generate three different approaches to fix failing pytest tests
filters:
  # Match test files
  - type: file_extension
    pattern: "\\.py$"
  # Match test-related content
  - type: content
    pattern: "(?i)(test|assert|pytest|unittest|mock|fixture)"
  # Match test failure messages
  - type: message
    pattern: "(?i)(test fail|failing test|fix test|test error|test not passing)"

actions:
  - type: instructions
    message: |
      # Three-Approach Test Fix Strategy

      When encountering failing tests, provide three distinct approaches to fix the issue:

      ## Analysis Phase

      1. **Understand the Test Failure**:
         - Examine the error message and traceback
         - Identify the assertion that's failing
         - Understand what the test is expecting vs. what it's getting

      2. **Analyze the Implementation**:
         - Review the code being tested
         - Identify potential issues in the implementation
         - Check for environment or setup issues

      3. **Examine Test Structure**:
         - Review test fixtures and setup
         - Check for proper test isolation
         - Verify test assumptions

      ## Solution Generation Phase

      For each failing test, generate three distinct approaches:

      ### Approach 1: Minimal Implementation Fix
      - Focus on the simplest change to make the test pass
      - Modify only the implementation code
      - Preserve existing interfaces and behavior
      - Example: "Fix the implementation to correctly handle the input"

      ### Approach 2: Test Adaptation
      - Adjust the test to match expected behavior
      - Use test fixtures or mocks to control the environment
      - Preserve core test assertions while fixing setup
      - Example: "Update the test to properly set up the test environment"

      ### Approach 3: Architectural Improvement
      - Suggest a more substantial refactoring
      - Address underlying design issues
      - Improve both test and implementation
      - Example: "Refactor the component to improve testability and fix the issue"

      ## Implementation Phase

      For each approach:

      1. **Clearly Describe the Approach**:
         - Explain the rationale
         - Highlight pros and cons
         - Indicate complexity and impact

      2. **Provide Concrete Implementation**:
         - Show exact code changes
         - Include before/after comparisons
         - Explain why the changes fix the issue

      3. **Suggest Verification Steps**:
         - How to verify the fix works
         - Additional tests to consider
         - Potential side effects to check

examples:
  - input: |
      This test is failing with AssertionError: assert None == 'expected content'. How can I fix it?

      ```python
      def test_read_cursor_rule_existing(self):
          # Create a temporary directory for cursor rules
          cursor_rules_dir = Path(self.temp_dir) / "cursor_rules"
          cursor_rules_dir.mkdir(parents=True)

          # Create a test rule file
          rule_content = "Test rule content"
          rule_path = cursor_rules_dir / "test-rule.mdc.md"
          rule_path.write_text(rule_content)

          # Call the function
          result = read_cursor_rule("test-rule")

          # Verify the result
          assert result == rule_content
      ```

      The implementation looks like:

      ```python
      def read_cursor_rule(rule_name: str) -> str | None:
          rule_path = CURSOR_RULES_DIR / f"{rule_name}.mdc.md"
          if rule_path.exists():
              return rule_path.read_text()
          return None
      ```

      Where CURSOR_RULES_DIR is defined as:

      ```python
      CURSOR_RULES_DIR = Path("hack/drafts/cursor_rules")
      ```
    output: |
      I'll provide three different approaches to fix this failing test:

      ### Approach 1: Patch the CURSOR_RULES_DIR Constant

      This approach uses monkeypatch to temporarily change the CURSOR_RULES_DIR constant during the test.

      ```python
      def test_read_cursor_rule_existing(self, monkeypatch: "MonkeyPatch") -> None:
          # Create a temporary directory for cursor rules
          cursor_rules_dir = Path(self.temp_dir) / "cursor_rules"
          cursor_rules_dir.mkdir(parents=True)

          # Create a test rule file
          rule_content = "Test rule content"
          rule_path = cursor_rules_dir / "test-rule.mdc.md"
          rule_path.write_text(rule_content)

          # Patch the CURSOR_RULES_DIR to point to our test directory
          monkeypatch.setattr("codegen_lab.prompt_library.CURSOR_RULES_DIR", cursor_rules_dir)

          # Call the function
          result = read_cursor_rule("test-rule")

          # Verify the result
          assert result == rule_content
      ```

      This approach:
      - Keeps the implementation unchanged
      - Uses pytest's monkeypatch fixture to temporarily modify the constant
      - Is clean and follows testing best practices
      - Isolates the test from the actual file system

      ### Approach 2: Modify the read_cursor_rule Function

      This approach modifies the implementation to accept an optional directory parameter:

      ```python
      def read_cursor_rule(rule_name: str, directory: Path | None = None) -> str | None:
          rule_dir = directory if directory is not None else CURSOR_RULES_DIR
          rule_path = rule_dir / f"{rule_name}.mdc.md"
          if rule_path.exists():
              return rule_path.read_text()
          return None
      ```

      And update the test:

      ```python
      def test_read_cursor_rule_existing(self) -> None:
          # Create a temporary directory for cursor rules
          cursor_rules_dir = Path(self.temp_dir) / "cursor_rules"
          cursor_rules_dir.mkdir(parents=True)

          # Create a test rule file
          rule_content = "Test rule content"
          rule_path = cursor_rules_dir / "test-rule.mdc.md"
          rule_path.write_text(rule_content)

          # Call the function with our test directory
          result = read_cursor_rule("test-rule", directory=cursor_rules_dir)

          # Verify the result
          assert result == rule_content
      ```

      This approach:
      - Makes the function more flexible
      - Improves the API for future use cases
      - Requires updating all call sites if backward compatibility is needed
      - Makes testing easier without mocking

      ### Approach 3: Use a Context Manager for Directory Change

      This approach uses a context manager to temporarily change the working directory:

      ```python
      def test_read_cursor_rule_existing(self) -> None:
          # Create a temporary directory for cursor rules
          cursor_rules_dir = Path(self.temp_dir) / "cursor_rules"
          cursor_rules_dir.mkdir(parents=True)

          # Create a test rule file
          rule_content = "Test rule content"
          rule_path = cursor_rules_dir / "test-rule.mdc.md"
          rule_path.write_text(rule_content)

          # Save the original directory
          original_dir = os.getcwd()

          try:
              # Change to the temporary directory
              os.chdir(self.temp_dir)

              # Temporarily patch the CURSOR_RULES_DIR to use a relative path
              with patch("codegen_lab.prompt_library.CURSOR_RULES_DIR", Path("cursor_rules")):
                  # Call the function
                  result = read_cursor_rule("test-rule")

                  # Verify the result
                  assert result == rule_content
          finally:
              # Restore the original directory
              os.chdir(original_dir)
      ```

      This approach:
      - Works with the existing implementation
      - Uses a context manager pattern for clean setup/teardown
      - Changes the global state (working directory) which could affect other tests
      - Is more complex but demonstrates a useful pattern for file system tests

  - input: |
      The test_calculate_total function is failing with "AssertionError: assert 15 == 16". Here's the test:

      ```python
      def test_calculate_total():
          items = [
              {"price": 10, "quantity": 1},
              {"price": 5, "quantity": 1}
          ]
          result = calculate_total(items)
          assert result == 16
      ```

      And here's the implementation:

      ```python
      def calculate_total(items):
          total = 0
          for item in items:
              total += item["price"]
          return total
      ```
    output: |
      I'll provide three different approaches to fix this failing test:

      ### Approach 1: Fix the Implementation to Consider Quantity

      The implementation is not considering the quantity of each item, which is causing the test to fail.

      ```python
      def calculate_total(items):
          total = 0
          for item in items:
              total += item["price"] * item["quantity"]
          return total
      ```

      This approach:
      - Fixes the core issue in the implementation
      - Properly calculates the total based on price and quantity
      - Maintains the existing function signature
      - Is the most straightforward solution that aligns with the test's expectations

      ### Approach 2: Update the Test to Match the Implementation

      If the implementation is correct (only summing prices without considering quantity), we could update the test:

      ```python
      def test_calculate_total():
          items = [
              {"price": 10, "quantity": 1},
              {"price": 5, "quantity": 1}
          ]
          result = calculate_total(items)
          assert result == 15  # Changed from 16 to 15
      ```

      This approach:
      - Aligns the test with the current implementation
      - Is appropriate if the function is intentionally designed to only sum prices
      - Requires verifying that ignoring quantity is the intended behavior
      - Is simpler but may not reflect the actual business requirements

      ### Approach 3: Refactor with a More Flexible Design

      Refactor to make the calculation logic more explicit and configurable:

      ```python
      def calculate_item_cost(item, include_quantity=True):
          if include_quantity:
              return item["price"] * item["quantity"]
          return item["price"]

      def calculate_total(items, include_quantity=True):
          return sum(calculate_item_cost(item, include_quantity) for item in items)
      ```

      And update the test:

      ```python
      def test_calculate_total():
          items = [
              {"price": 10, "quantity": 1},
              {"price": 5, "quantity": 1}
          ]

          # Test with quantity included (default)
          result = calculate_total(items)
          assert result == 15

          # Test with explicit quantity flag
          result = calculate_total(items, include_quantity=True)
          assert result == 15

          # Test price-only calculation
          result = calculate_total(items, include_quantity=False)
          assert result == 15

          # Test with different quantities
          items_with_quantities = [
              {"price": 10, "quantity": 1},
              {"price": 5, "quantity": 2}
          ]
          result = calculate_total(items_with_quantities)
          assert result == 20  # 10*1 + 5*2 = 20
      ```

      This approach:
      - Makes the behavior explicit through a parameter
      - Provides flexibility for different calculation needs
      - Improves testability with more granular functions
      - Adds comprehensive test cases for different scenarios
      - Requires more changes but results in a more robust solution

metadata:
  priority: high
  version: 1.0
  tags:
    - testing
    - pytest
    - debugging
    - test-fixes
</rule>
