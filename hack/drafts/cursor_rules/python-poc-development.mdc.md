---
description:
globs:
alwaysApply: false
---

# Python POC Development Guide

Guidelines and best practices for developing Python proof-of-concept implementations during refactoring

This rule provides guidance for creating proof of concept implementations during Python refactoring.

<rule>
name: python-poc-development
description: Proof of concept development strategies for Python refactoring projects
filters:
  - type: file_extension
    pattern: "\\.py$"
  - type: content
    pattern: "(?i)(poc|proof of concept|prototype)"

actions:
  - type: suggest
    message: |
      # Python POC Development Guide

      ## POC Development Strategy

      1. **Initial POC Setup**
      ```python
      """POC Implementation Plan:
      - [ ] Identify core functionality
      - [ ] Create minimal structure
      - [ ] Implement basic functionality
      - [ ] Verify behavior matches original
      - [ ] Add validation tests
      """
      ```

      2. **Minimal Working Version**
      ```python
      # Original implementation
      def process_data(input_data):
          # Complex processing logic
          return result

      # POC implementation
      def process_data(input_data):
          # Forward to original implementation initially
          from original_module import process_data as original_process
          return original_process(input_data)
      ```

      3. **Equivalence Testing**
      ```python
      def test_refactored_matches_original():
          """Verify refactored implementation matches original."""
          from original_module import process_data as original
          from new_module import process_data as refactored

          test_data = {"sample": "data"}
          assert refactored(test_data) == original(test_data)
      ```

      ## Incremental Development

      1. **Start with Interface**
      ```python
      from typing import Protocol, Dict, Any

      class DataProcessor(Protocol):
          """Define the interface for data processing."""
          def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
              """Process input data."""
              ...

      class POCProcessor:
          """POC implementation of data processor."""
          def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
              """Forward to original implementation."""
              from original import process
              return process(data)
      ```

      2. **Add Validation**
      ```python
      def validate_poc_behavior():
          """Validate POC against original implementation."""
          original = OriginalProcessor()
          poc = POCProcessor()

          test_cases = [
              {"simple": "data"},
              {"complex": {"nested": "data"}},
          ]

          for case in test_cases:
              assert poc.process(case) == original.process(case)
      ```

      3. **Gradual Replacement**
      ```python
      class POCProcessor:
          """Gradually replace original implementation."""
          def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
              """Process with new implementation, fallback to original."""
              try:
                  return self._new_process(data)
              except NotImplementedError:
                  from original import process
                  return process(data)

          def _new_process(self, data: Dict[str, Any]) -> Dict[str, Any]:
              """New implementation to gradually fill in."""
              raise NotImplementedError
      ```

      ## Maintaining Compatibility

      1. **Version Check**
      ```python
      import warnings
      from packaging import version

      def check_compatibility():
          """Check version compatibility."""
          if version.parse(current_version) < version.parse("2.0"):
              warnings.warn("Using compatibility layer")
              return True
          return False
      ```

      2. **Feature Flags**
      ```python
      class FeatureFlags:
          """Control POC features."""
          def __init__(self):
              self.use_new_processor = False
              self.strict_validation = False

      flags = FeatureFlags()

      def process_with_flags(data: Dict[str, Any]) -> Dict[str, Any]:
          """Use feature flags to control behavior."""
          if flags.use_new_processor:
              return new_process(data)
          return original_process(data)
      ```

      3. **Logging and Monitoring**
      ```python
      import logging

      logger = logging.getLogger(__name__)

      def monitored_process(data: Dict[str, Any]) -> Dict[str, Any]:
          """Monitor POC behavior."""
          logger.info("Processing data with POC")
          try:
              result = poc_process(data)
              logger.info("POC processing successful")
              return result
          except Exception as e:
              logger.error("POC failed, falling back to original")
              return original_process(data)
      ```

      ## Best Practices

      1. **Minimal Implementation**
      - Start with the smallest working version
      - Forward to original implementation initially
      - Add new functionality gradually

      2. **Validation**
      - Test against original implementation
      - Use comprehensive test cases
      - Monitor behavior in production

      3. **Rollback Plan**
      - Maintain original implementation
      - Use feature flags for control
      - Log all operations for debugging

      4. **Documentation**
      - Document POC limitations
      - Track known differences
      - Plan for full implementation

metadata:
  priority: high
  version: 1.0
  tags:
    - python
    - poc
    - prototyping
    - refactoring
</rule>
