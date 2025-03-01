# Contributing to Codegen Lab

Thank you for your interest in contributing to Codegen Lab! This document provides guidelines and instructions for contributors.

## Code of Conduct

Please read and follow our [Code of Conduct](https://github.com/bossjones/codegen-lab/blob/main/CODE_OF_CONDUCT.md) before contributing.

## How to Contribute

There are many ways to contribute to Codegen Lab:

1. **Reporting Bugs**: Report bugs by opening an issue on the [GitHub repository](https://github.com/bossjones/codegen-lab/issues).
2. **Suggesting Enhancements**: Suggest new features or improvements by opening an issue.
3. **Pull Requests**: Submit pull requests with bug fixes, improvements, or new features.
4. **Documentation**: Help improve documentation or fix typos.
5. **Answering Questions**: Help answer questions in issues or discussions.

## Development Setup

1. Fork the repository on GitHub.
2. Clone your fork to your local machine:

   ```bash
   git clone https://github.com/YOUR_USERNAME/codegen-lab.git
   cd codegen-lab
   ```

3. Create a new branch for your changes:

   ```bash
   git checkout -b feature/your-feature-name
   ```

4. Set up the development environment:

   ```bash
   uv venv --python 3.12.0
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv sync --frozen --dev
   ```

5. Make your changes and commit them with a clear, descriptive commit message.

## Pull Request Process

1. Ensure your code follows the project's style guidelines.
2. Update documentation if necessary.
3. Add tests for your changes.
4. Make sure all tests pass:

   ```bash
   uv run pytest tests/
   ```

5. Push your changes to your fork:

   ```bash
   git push origin feature/your-feature-name
   ```

6. Submit a pull request to the main repository.
7. The maintainers will review your pull request and provide feedback.

## Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/) for Python code.
- Add type hints to functions and methods.
- Write clear, descriptive docstrings following [PEP 257](https://peps.python.org/pep-0257/).
- Use meaningful variable and function names.

## Testing

- Write tests for all new features and bug fixes.
- Use pytest for testing.
- Aim for high test coverage.

## Documentation

- Update documentation for any changes to the API or behavior.
- Use clear, concise language.
- Provide examples for API usage.

## License

By contributing to Codegen Lab, you agree that your contributions will be licensed under the project's license.
