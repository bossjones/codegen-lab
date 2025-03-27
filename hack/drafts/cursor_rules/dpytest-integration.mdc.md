---
description:
globs:
alwaysApply: false
---
# dpytest Integration Guide
Guide to integrating dpytest with other testing tools and CI/CD systems

Documentation for integrating dpytest with other testing tools and CI/CD systems.

<rule>
name: dpytest_integration
description: Guide to integrating dpytest with other tools and CI/CD systems
filters:
  # Match Python files
  - type: file_extension
    pattern: "\\.py$"
  # Match test files
  - type: file_path
    pattern: "tests?/"
  # Match CI/CD and integration files
  - type: file_path
    pattern: "(\\.github/workflows/.*\\.ya?ml|\\.gitlab-ci\\.ya?ml|tox\\.ini|noxfile\\.py|pytest\\.ini|setup\\.cfg)"

actions:
  - type: suggest
    message: |
      # dpytest Integration Guide

      Guide to integrating dpytest with other testing tools and CI/CD systems.

      ## Integration with Testing Tools

      ### 1. pytest Integration

      ```python
      from typing import AsyncGenerator, Optional
      import pytest
      from discord.ext.test import runner
      from _pytest.fixtures import FixtureRequest

      @pytest.fixture(scope="session")
      def event_loop():
          """Create an instance of the default event loop for the session."""
          import asyncio
          loop = asyncio.new_event_loop()
          yield loop
          loop.close()

      @pytest.fixture(scope="function")
      async def bot_setup(request: FixtureRequest) -> AsyncGenerator[None, None]:
          """
          Set up bot testing environment.

          Args:
              request: Pytest fixture request

          Yields:
              None
          """
          # Configure dpytest
          runner.configure(
              client_config=getattr(request, "param", {}),
              runner_config={"timeout": 2.0}
          )
          yield
          await runner.cleanup()

      @pytest.mark.asyncio
      async def test_bot_command(bot_setup: None) -> None:
          """Test bot command with pytest-asyncio."""
          # Test implementation
          pass
      ```

      ### 2. Coverage.py Integration

      ```ini
      # .coveragerc
      [run]
      source = your_bot_package
      omit =
          tests/*
          */__init__.py

      [report]
      exclude_lines =
          pragma: no cover
          def __repr__
          raise NotImplementedError
      ```

      ### 3. tox Integration

      ```ini
      # tox.ini
      [tox]
      envlist = py39, py310, py311
      isolated_build = True

      [testenv]
      deps =
          pytest>=7.0
          pytest-asyncio>=0.18
          pytest-cov>=3.0
          discord.py>=2.0
          dpytest>=0.6
      commands =
          pytest {posargs:tests} --cov=your_bot_package

      [pytest]
      asyncio_mode = auto
      testpaths = tests
      python_files = test_*.py
      ```

      ### 4. nox Integration

      ```python
      # noxfile.py
      from typing import Any
      import nox
      from nox.sessions import Session

      @nox.session(python=["3.9", "3.10", "3.11"])
      def tests(session: Session) -> None:
          """
          Run test suite with nox.

          Args:
              session: Nox session
          """
          session.install("pytest", "pytest-asyncio", "pytest-cov")
          session.install("discord.py", "dpytest")
          session.run(
              "pytest",
              "--cov=your_bot_package",
              "tests/",
              *session.posargs
          )
      ```

      ## CI/CD Integration

      ### 1. GitHub Actions

      ```yaml
      # .github/workflows/test.yml
      name: Test

      on:
        push:
          branches: [ main ]
        pull_request:
          branches: [ main ]

      jobs:
        test:
          runs-on: ubuntu-latest
          strategy:
            matrix:
              python-version: ["3.9", "3.10", "3.11"]

          steps:
          - uses: actions/checkout@v3

          - name: Set up Python ${{ matrix.python-version }}
            uses: actions/setup-python@v4
            with:
              python-version: ${{ matrix.python-version }}

          - name: Install dependencies
            run: |
              python -m pip install --upgrade pip
              pip install pytest pytest-asyncio pytest-cov
              pip install discord.py dpytest
              pip install -e .

          - name: Run tests
            run: |
              pytest tests/ --cov=your_bot_package --cov-report=xml

          - name: Upload coverage
            uses: codecov/codecov-action@v3
            with:
              file: ./coverage.xml
              fail_ci_if_error: true
      ```

      ### 2. GitLab CI

      ```yaml
      # .gitlab-ci.yml
      image: python:3.11

      stages:
        - test

      variables:
        PIP_CACHE_DIR: "$CI_PROJECT_DIR/.pip-cache"

      cache:
        paths:
          - .pip-cache/

      test:
        stage: test
        script:
          - pip install pytest pytest-asyncio pytest-cov
          - pip install discord.py dpytest
          - pip install -e .
          - pytest tests/ --cov=your_bot_package --cov-report=xml
        coverage: '/TOTAL.+ ([0-9]{1,3}%)/'
        artifacts:
          reports:
            coverage_report:
              coverage_format: cobertura
              path: coverage.xml
      ```

      ### 3. CircleCI

      ```yaml
      # .circleci/config.yml
      version: 2.1

      orbs:
        python: circleci/python@2.1

      jobs:
        test:
          docker:
            - image: cimg/python:3.11
          steps:
            - checkout
            - python/install-packages:
                pkg-manager: pip
                packages:
                  - pytest
                  - pytest-asyncio
                  - pytest-cov
                  - discord.py
                  - dpytest
            - run:
                command: |
                  pytest tests/ --cov=your_bot_package

      workflows:
        main:
          jobs:
            - test
      ```

      ## Integration Patterns

      ### 1. Test Environment Setup

      ```python
      from typing import AsyncGenerator, Optional, Dict, Any
      import pytest
      from discord.ext.test import runner

      class TestEnvironment:
          """Test environment configuration."""

          def __init__(
              self,
              config: Optional[Dict[str, Any]] = None
          ) -> None:
              """
              Initialize test environment.

              Args:
                  config: Optional configuration
              """
              self.config = config or {}

          async def setup(self) -> None:
              """Set up test environment."""
              runner.configure(**self.config)

          async def cleanup(self) -> None:
              """Clean up test environment."""
              await runner.cleanup()

      @pytest.fixture
      async def test_env(
          request: FixtureRequest
      ) -> AsyncGenerator[TestEnvironment, None]:
          """
          Provide test environment.

          Args:
              request: Pytest fixture request

          Yields:
              TestEnvironment: Configured test environment
          """
          env = TestEnvironment(getattr(request, "param", {}))
          await env.setup()
          yield env
          await env.cleanup()
      ```

      ### 2. Test Data Management

      ```python
      from typing import Dict, Any, Optional
      import json
      import os

      class TestDataManager:
          """Test data management."""

          def __init__(
              self,
              data_dir: str = "tests/data"
          ) -> None:
              """
              Initialize test data manager.

              Args:
                  data_dir: Test data directory
              """
              self.data_dir = data_dir

          def load_fixture(
              self,
              name: str
          ) -> Dict[str, Any]:
              """
              Load test fixture data.

              Args:
                  name: Fixture name

              Returns:
                  Dict[str, Any]: Fixture data
              """
              path = os.path.join(self.data_dir, f"{name}.json")
              with open(path) as f:
                  return json.load(f)

          def save_fixture(
              self,
              name: str,
              data: Dict[str, Any]
          ) -> None:
              """
              Save test fixture data.

              Args:
                  name: Fixture name
                  data: Fixture data
              """
              path = os.path.join(self.data_dir, f"{name}.json")
              with open(path, "w") as f:
                  json.dump(data, f, indent=2)
      ```

      ### 3. Test Result Reporting

      ```python
      from typing import Dict, Any, List, Optional
      import json
      import os
      from datetime import datetime

      class TestReporter:
          """Test result reporting."""

          def __init__(
              self,
              report_dir: str = "test-reports"
          ) -> None:
              """
              Initialize test reporter.

              Args:
                  report_dir: Report directory
              """
              self.report_dir = report_dir
              os.makedirs(report_dir, exist_ok=True)

          def save_report(
              self,
              results: Dict[str, Any],
              name: Optional[str] = None
          ) -> None:
              """
              Save test results report.

              Args:
                  results: Test results
                  name: Optional report name
              """
              if name is None:
                  name = datetime.now().strftime("%Y%m%d_%H%M%S")

              path = os.path.join(self.report_dir, f"{name}.json")
              with open(path, "w") as f:
                  json.dump(results, f, indent=2)

          def load_report(
              self,
              name: str
          ) -> Dict[str, Any]:
              """
              Load test results report.

              Args:
                  name: Report name

              Returns:
                  Dict[str, Any]: Test results
              """
              path = os.path.join(self.report_dir, f"{name}.json")
              with open(path) as f:
                  return json.load(f)

          def compare_reports(
              self,
              report1: str,
              report2: str
          ) -> Dict[str, Any]:
              """
              Compare two test reports.

              Args:
                  report1: First report name
                  report2: Second report name

              Returns:
                  Dict[str, Any]: Comparison results
              """
              data1 = self.load_report(report1)
              data2 = self.load_report(report2)

              return {
                  "differences": self._compare_data(data1, data2),
                  "report1": report1,
                  "report2": report2
              }

          def _compare_data(
              self,
              data1: Dict[str, Any],
              data2: Dict[str, Any]
          ) -> List[str]:
              """
              Compare two data sets.

              Args:
                  data1: First data set
                  data2: Second data set

              Returns:
                  List[str]: List of differences
              """
              differences = []
              for key in set(data1) | set(data2):
                  if key not in data1:
                      differences.append(f"Missing in report1: {key}")
                  elif key not in data2:
                      differences.append(f"Missing in report2: {key}")
                  elif data1[key] != data2[key]:
                      differences.append(
                          f"Different values for {key}: "
                          f"{data1[key]} vs {data2[key]}"
                      )
              return differences
      ```

      ## Best Practices

      1. **Consistent Test Environment**
         ```python
         @pytest.fixture(scope="session")
         def test_config() -> Dict[str, Any]:
             """Provide consistent test configuration."""
             return {
                 "client_config": {
                     "intents": discord.Intents.all(),
                     "prefix": "!"
                 },
                 "runner_config": {
                     "timeout": 5.0,
                     "tick_rate": 0.1
                 }
             }

         @pytest.fixture(scope="function")
         async def test_env(
             test_config: Dict[str, Any]
         ) -> AsyncGenerator[None, None]:
             """Set up test environment."""
             runner.configure(**test_config)
             yield
             await runner.cleanup()
         ```

      2. **CI/CD Pipeline Organization**
         ```yaml
         # .github/workflows/test.yml
         name: Test Pipeline

         on:
           push:
             branches: [ main ]
           pull_request:
             branches: [ main ]

         jobs:
           lint:
             runs-on: ubuntu-latest
             steps:
               - uses: actions/checkout@v3
               - uses: actions/setup-python@v4
               - run: pip install ruff
               - run: ruff check .

           test:
             needs: lint
             runs-on: ubuntu-latest
             strategy:
               matrix:
                 python-version: ["3.9", "3.10", "3.11"]
             steps:
               - uses: actions/checkout@v3
               - uses: actions/setup-python@v4
               - run: pip install -e ".[test]"
               - run: pytest tests/

           coverage:
             needs: test
             runs-on: ubuntu-latest
             steps:
               - uses: actions/checkout@v3
               - uses: actions/setup-python@v4
               - run: |
                   pip install -e ".[test]"
                   pytest --cov=your_bot_package
                   coverage xml
               - uses: codecov/codecov-action@v3
         ```

      3. **Test Data Organization**
         ```
         tests/
         ├── data/
         │   ├── messages.json
         │   ├── users.json
         │   └── guilds.json
         ├── fixtures/
         │   ├── __init__.py
         │   ├── bot.py
         │   └── data.py
         ├── integration/
         │   └── test_bot_commands.py
         └── unit/
             └── test_utils.py
         ```

examples:
  - input: |
      How do I set up GitHub Actions for my Discord bot tests?
    output: |
      Here's how to set up GitHub Actions for testing your Discord bot:

      ```yaml
      # .github/workflows/test.yml
      name: Test Discord Bot

      on:
        push:
          branches: [ main ]
        pull_request:
          branches: [ main ]

      jobs:
        test:
          runs-on: ubuntu-latest
          strategy:
            matrix:
              python-version: ["3.9", "3.10", "3.11"]

          steps:
          - uses: actions/checkout@v3

          - name: Set up Python ${{ matrix.python-version }}
            uses: actions/setup-python@v4
            with:
              python-version: ${{ matrix.python-version }}

          - name: Install dependencies
            run: |
              python -m pip install --upgrade pip
              pip install pytest pytest-asyncio pytest-cov
              pip install discord.py dpytest
              pip install -e .

          - name: Run tests
            run: |
              pytest tests/ --cov=your_bot_package --cov-report=xml

          - name: Upload coverage
            uses: codecov/codecov-action@v3
            with:
              file: ./coverage.xml
              fail_ci_if_error: true
      ```

      This workflow:
      1. Runs on push to main and pull requests
      2. Tests against multiple Python versions
      3. Installs all necessary dependencies
      4. Runs tests with coverage reporting
      5. Uploads coverage data to Codecov

metadata:
  priority: high
  version: 1.0
  tags:
    - discord
    - testing
    - pytest
    - ci-cd
    - integration
    - dpytest
</rule>
