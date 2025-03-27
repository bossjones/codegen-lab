---
description:
globs:
alwaysApply: false
---

# Python TDD Basics

 Core Test-Driven Development (TDD) workflow and testing practices for Python projects

This rule provides guidance for Test-Driven Development (TDD) in Python projects, focusing on core testing practices and workflow.

<rule>
name: python-tdd-basics
description: Core TDD workflow and testing practices for Python projects
filters:
  - type: file_extension
    pattern: "\\.py$"

actions:
  - type: suggest
    message: |
      # Python TDD Best Practices

      ## Core TDD Cycle
      1. Write a failing test first
      2. Write minimal code to make the test pass
      3. Refactor while keeping tests green
      4. Repeat

      ## TDD Verification Loop

      Always verify your tests and code in an iterative loop:

      ```bash
      # 1. Format code first
      uv run ruff format .

      # 2. Run the specific test to verify it fails (for new tests)
      # or passes (after implementation/fix)
      uv run pytest tests/path/to/test_file.py::TestClass::test_method -v

      # 3. If test fails with errors other than assertion failures (e.g., import or syntax errors),
      # fix those structural issues first

      # 4. After implementation, run the test again to verify it passes
      uv run pytest tests/path/to/test_file.py::TestClass::test_method -v

      # 5. Run related tests to verify no regressions
      uv run pytest tests/path/to/test_file.py -v

      # 6. Fix any linting/type checking issues
      uv run ruff check . --fix --show-fixes
      uv run mypy

      # 7. Run tests again to ensure fixes didn't break anything
      uv run pytest tests/path/to/test_file.py -v
      ```

      ### Best Practices for Test Verification

      1. **Verify Tests First**: When creating a new test file, verify it loads correctly before adding tests:
         ```bash
         # Verify the test file loads without errors
         uv run pytest tests/path/to/new_test_file.py -v
         ```

      2. **Iterative Testing**: Test each specific change immediately after making it:
         ```bash
         # Run only the specific test you're working on
         uv run pytest tests/path/to/test_file.py::TestClass::test_method -vxs
         ```

      3. **Test with Debugging**: For failing tests, use debugging flags:
         ```bash
         # Run with debug on failures and verbose output
         uv run pytest tests/path/to/test_file.py::TestClass::test_method -vxs --pdb
         ```

      4. **Focus on Relevant Tests**: Use the `-k` flag to run only relevant tests:
         ```bash
         # Run all tests related to a specific feature
         uv run pytest -k "feature_name" -v
         ```

      5. **Check Test Coverage**: Verify your tests cover the code:
         ```bash
         # Run with coverage report
         uv run pytest --cov=src/path/to/module tests/path/to/test_file.py
         ```

      ## Test Structure Template
      ```python
      """Unit tests for component functionality.

      This test suite verifies the behavior of the component
      in isolation from other system components.
      """
      from typing import TYPE_CHECKING

      import pytest

      if TYPE_CHECKING:
          from _pytest.capture import CaptureFixture
          from _pytest.fixtures import FixtureRequest
          from _pytest.logging import LogCaptureFixture
          from _pytest.monkeypatch import MonkeyPatch
          from pytest_mock.plugin import MockerFixture

      @pytest.fixture
      def component_fixture():
          """Create an isolated component instance for testing."""
          return ComponentUnderTest()

      def test_component_behavior(
          component_fixture: ComponentUnderTest,
          mocker: MockerFixture,
          caplog: LogCaptureFixture,
      ) -> None:
          """Test specific component behavior.

          Args:
              component_fixture: The component under test
              mocker: Pytest mock fixture
              caplog: Fixture to capture log output

          This test verifies that the component behaves correctly
          under specific conditions.
          """
          # Given
          input_data = {"test": "data"}

          # When
          result = component_fixture.process(input_data)

          # Then
          assert result == expected_output
      ```

      ## Test Organization Strategies for Large Codebases

      When working with large codebases, proper test organization is crucial for maintainability and clarity. Follow these guidelines:

      ### Directory Structure

      ```
      tests/
      ├── __init__.py
      ├── conftest.py                 # Global fixtures and configuration
      ├── unit/                       # Unit tests directory
      │   ├── __init__.py
      │   ├── models/                 # Tests for models
      │   │   ├── __init__.py
      │   │   ├── conftest.py        # Model-specific fixtures
      │   │   └── test_*.py
      │   ├── services/              # Tests for services
      │   │   ├── __init__.py
      │   │   ├── conftest.py        # Service-specific fixtures
      │   │   └── test_*.py
      │   └── utils/                 # Tests for utilities
      │       ├── __init__.py
      │       ├── conftest.py        # Utility-specific fixtures
      │       └── test_*.py
      ├── integration/               # Integration tests
      │   ├── __init__.py
      │   ├── conftest.py           # Integration test fixtures
      │   └── test_*.py
      ├── e2e/                      # End-to-end tests
      │   ├── __init__.py
      │   ├── conftest.py          # E2E test fixtures
      │   └── test_*.py
      └── performance/              # Performance tests
          ├── __init__.py
          ├── conftest.py          # Performance test fixtures
          └── test_*.py
      ```

      ### Test Categories and Naming

      1. **Unit Tests**
         ```python
         # tests/unit/models/test_user.py
         from typing import TYPE_CHECKING

         import pytest
         from your_package.models import User

         if TYPE_CHECKING:
             from _pytest.fixtures import FixtureRequest
             from pytest_mock.plugin import MockerFixture

         class TestUser:
             """Test suite for User model functionality."""

             @pytest.fixture
             def user_fixture(self) -> User:
                 """Create a test user instance."""
                 return User(id=1, name="Test User")

             def test_user_creation(self, user_fixture: User) -> None:
                 """Test user instance creation and attributes."""
                 assert user_fixture.id == 1
                 assert user_fixture.name == "Test User"
         ```

      2. **Integration Tests**
         ```python
         # tests/integration/test_user_service.py
         from typing import TYPE_CHECKING

         import pytest
         from your_package.services import UserService
         from your_package.models import User

         if TYPE_CHECKING:
             from _pytest.fixtures import FixtureRequest
             from pytest_mock.plugin import MockerFixture

         class TestUserServiceIntegration:
             """Integration tests for UserService."""

             @pytest.fixture
             async def service_fixture(self) -> UserService:
                 """Create a service instance with real dependencies."""
                 service = UserService()
                 await service.initialize()
                 yield service
                 await service.cleanup()

             async def test_user_creation_flow(
                 self,
                 service_fixture: UserService,
                 mocker: MockerFixture
             ) -> None:
                 """Test complete user creation flow with real dependencies."""
                 result = await service_fixture.create_user("Test User")
                 assert isinstance(result, User)
         ```

      ### Fixture Organization

      1. **Global Fixtures** (`tests/conftest.py`):
         ```python
         """Global test fixtures and configuration."""
         from typing import TYPE_CHECKING, Generator

         import pytest
         from your_package.config import Config
         from your_package.db import Database

         if TYPE_CHECKING:
             from _pytest.fixtures import FixtureRequest
             from pytest_mock.plugin import MockerFixture

         @pytest.fixture(scope="session")
         def config() -> Config:
             """Provide test configuration."""
             return Config(environment="test")

         @pytest.fixture(scope="function")
         def db(config: Config) -> Generator[Database, None, None]:
             """Provide test database instance."""
             db = Database(config)
             db.initialize()
             yield db
             db.cleanup()
         ```

      2. **Module-Specific Fixtures** (`tests/unit/models/conftest.py`):
         ```python
         """Model-specific test fixtures."""
         from typing import TYPE_CHECKING, Dict, Any

         import pytest
         from your_package.models import User

         if TYPE_CHECKING:
             from _pytest.fixtures import FixtureRequest

         @pytest.fixture
         def user_data() -> Dict[str, Any]:
             """Provide test user data."""
             return {"id": 1, "name": "Test User"}

         @pytest.fixture
         def user(user_data: Dict[str, Any]) -> User:
             """Provide test user instance."""
             return User(**user_data)
         ```

      ### Test Collection Organization

      1. **Test Classes for Related Tests**:
         ```python
         class TestUserCreation:
             """Tests for user creation functionality."""

         class TestUserValidation:
             """Tests for user validation functionality."""

         class TestUserPermissions:
             """Tests for user permissions functionality."""
         ```

      2. **Test Groups Using Markers**:
         ```python
         @pytest.mark.slow
         def test_expensive_operation() -> None:
             """Test that might take longer to execute."""

         @pytest.mark.integration
         def test_with_database() -> None:
             """Test requiring database integration."""

         @pytest.mark.parametrize("user_id,expected", [
             (1, "active"),
             (2, "inactive"),
         ])
         def test_user_status(user_id: int, expected: str) -> None:
             """Test user status for different user IDs."""
         ```

      ### Configuration Management

      1. **pytest.ini Configuration**:
         ```ini
         [pytest]
         testpaths = tests
         python_files = test_*.py
         python_classes = Test*
         python_functions = test_*
         markers =
             slow: marks tests as slow
             integration: marks tests as integration tests
         ```

      2. **Environment-Specific Configuration** (`tests/config/test_config.yaml`):
         ```yaml
         test:
           database:
             url: sqlite:///:memory:
           logging:
             level: DEBUG
         ```

      ### Best Practices

      1. **Test Isolation**:
         ```python
         @pytest.fixture(autouse=True)
         def setup_test_isolation(self) -> None:
             """Ensure each test runs in isolation."""
             # Reset any global state
             # Clear caches
             # Reset singletons
         ```

      2. **Resource Cleanup**:
         ```python
         @pytest.fixture
         def resource_fixture(self) -> Generator[Resource, None, None]:
             """Provide and cleanup test resource."""
             resource = Resource()
             yield resource
             resource.cleanup()  # Always cleanup after test
         ```

      3. **Test Data Management**:
         ```python
         from typing import Dict, Any

         class TestData:
             """Central management of test data."""

             @staticmethod
             def get_test_user_data() -> Dict[str, Any]:
                 """Get consistent test user data."""
                 return {
                     "id": 1,
                     "name": "Test User",
                     "email": "test@example.com"
                 }

             @staticmethod
             def get_test_product_data() -> Dict[str, Any]:
                 """Get consistent test product data."""
                 return {
                     "id": 1,
                     "name": "Test Product",
                     "price": 9.99
                 }
         ```

      ## Test Naming Conventions

      Follow these naming conventions for clear and maintainable tests:

      ### Test File Names
      ```python
      # Unit tests
      test_<module_name>.py          # For testing a single module
      test_<feature_name>.py         # For testing a specific feature

      # Integration tests
      test_<service1>_<service2>_integration.py  # For testing service interactions

      # End-to-end tests
      test_<workflow_name>_e2e.py    # For testing complete workflows
      ```

      ### Test Class Names
      ```python
      class TestUserCreation:        # Group tests for user creation functionality
          """Tests for user creation functionality."""

      class TestUserAuthentication:  # Group tests for authentication
          """Tests for user authentication functionality."""

      class TestUserAPI:            # Group tests for API endpoints
          """Tests for user-related API endpoints."""
      ```

      ### Test Function Names
      ```python
      def test_should_create_user_with_valid_data() -> None:
          """Test user creation with valid input data."""

      def test_should_raise_error_when_email_invalid() -> None:
          """Test error handling for invalid email."""

      def test_should_return_none_when_user_not_found() -> None:
          """Test behavior when user is not found."""

      # For parameterized tests
      @pytest.mark.parametrize("email,is_valid", [
          ("valid@email.com", True),
          ("invalid.email", False)
      ])
      def test_should_validate_email_format(email: str, is_valid: bool) -> None:
          """Test email validation for various formats."""

      # For testing specific conditions or states
      def test_should_fail_login_after_three_attempts() -> None:
          """Test account lockout after multiple failed attempts."""

      def test_should_reset_password_with_valid_token() -> None:
          """Test password reset with valid reset token."""
      ```

      ### Naming Pattern Guidelines

      1. **Use Descriptive Prefixes**:
         - `test_should_` - Describes expected behavior
         - `test_when_` - Describes specific conditions
         - `test_given_` - Describes initial state

      2. **Include Action and Expected Result**:
         ```python
         def test_should_update_status_when_payment_confirmed() -> None:
             """Test order status update after payment confirmation."""
         ```

      3. **Specify State or Condition**:
         ```python
         def test_should_fail_when_database_unavailable() -> None:
             """Test system behavior during database outage."""
         ```

      4. **Group Related Tests**:
         ```python
         class TestOrderProcessing:
             """Tests for order processing workflow."""

             def test_should_create_order_with_valid_items(self) -> None:
                 """Test order creation with valid items."""

             def test_should_calculate_total_with_discounts(self) -> None:
                 """Test order total calculation including discounts."""

             def test_should_apply_tax_based_on_location(self) -> None:
                 """Test tax calculation based on shipping location."""
         ```

      5. **Integration Test Names**:
         ```python
         def test_should_update_inventory_after_order_confirmation() -> None:
             """Test inventory updates when order is confirmed."""

         def test_should_notify_shipping_service_after_payment() -> None:
             """Test shipping service notification after payment."""
         ```

      ## Testing Setup
      ```bash
      # Create test directory structure
      mkdir -p tests/unit tests/integration || true

      # Create test files
      touch tests/unit/test_${component}.py
      touch tests/integration/test_${component}_integration.py

      # Set up test fixtures and helpers
      touch tests/conftest.py

      # Verify test infrastructure loads correctly
      uv run pytest tests/unit/test_${component}.py -v
      ```

      ## TDD Workflow for New Features

      1. **Create Test Infrastructure First**:
         ```bash
         # Create test directory/file
         mkdir -p tests/unit/module || true
         touch tests/unit/module/test_new_feature.py

         # Create empty test file with imports and basic structure
         # Add minimal test skeleton

         # Verify test file loads without errors
         uv run pytest tests/unit/module/test_new_feature.py -v
         ```

      2. **Write First Failing Test**:
         ```python
         def test_new_feature_behavior() -> None:
             """Test that new feature behaves as expected."""
             # Write assertions for expected behavior
             assert new_feature() == expected_result
         ```

      3. **Verify Test Fails Correctly**:
         ```bash
         # Run test and confirm it fails for the expected reason
         uv run pytest tests/unit/module/test_new_feature.py::test_new_feature_behavior -v
         ```

      4. **Implement Minimal Code to Pass Test**:
         ```python
         def new_feature():
             """Implement the minimum code to pass the test."""
             return expected_result
         ```

      5. **Verify Test Passes**:
         ```bash
         # Run test and confirm it passes
         uv run pytest tests/unit/module/test_new_feature.py::test_new_feature_behavior -v
         ```

      6. **Refactor While Keeping Tests Green**:
         ```python
         def new_feature():
             """Improved implementation that still passes tests."""
             # Better implementation
             return processed_result
         ```

      7. **Verify Refactored Code Still Passes**:
         ```bash
         # Run test to confirm refactoring didn't break functionality
         uv run pytest tests/unit/module/test_new_feature.py -v
         ```

      8. **Fix Any Linting or Type Issues**:
         ```bash
         # Format code
         uv run ruff format .

         # Check and fix linting
         uv run ruff check . --fix --show-fixes

         # Check types
         uv run mypy
         ```

      9. **Final Test Verification**:
         ```bash
         # Run tests again to ensure fixes didn't break anything
         uv run pytest tests/unit/module/test_new_feature.py -v

         # Run broader test suite for possible integration issues
         uv run pytest -k "feature_name" -v
         ```

      ## Testing Best Practices
      1. Use descriptive test names that explain the behavior being tested
      2. Follow the Given-When-Then pattern for test structure
      3. One assertion per test when possible
      4. Use appropriate fixtures to reduce code duplication
      5. Mock external dependencies appropriately
      6. Include both positive and negative test cases
      7. Test edge cases and boundary conditions

      ## Common Testing Patterns
      1. **Fixture Setup**:
         ```python
         @pytest.fixture
         def mock_service(mocker: MockerFixture):
             """Create a mocked service for testing."""
             return mocker.Mock(spec=Service)
         ```

      2. **Parametrized Tests**:
         ```python
         @pytest.mark.parametrize("input,expected", [
             ("test1", "result1"),
             ("test2", "result2"),
         ])
         def test_multiple_cases(input: str, expected: str) -> None:
             """Test multiple input cases."""
             assert process(input) == expected
         ```

      3. **Exception Testing**:
         ```python
         def test_raises_error() -> None:
             """Test that appropriate errors are raised."""
             with pytest.raises(ValueError):
                 process_invalid_input()
         ```

metadata:
  priority: high
  version: 1.0
  tags:
    - python
    - testing
    - tdd
    - best-practices
