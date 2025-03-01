# Getting Started

This guide will help you get started with Codegen Lab.

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.10 or higher
- UV package manager
- Git

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/bossjones/codegen-lab.git
   cd codegen-lab
   ```

2. Set up a virtual environment:

   ```bash
   uv venv --python 3.12.0
   ```

3. Activate the virtual environment:

   ```bash
   # On Unix or MacOS
   source .venv/bin/activate

   # On Windows
   .venv\Scripts\activate
   ```

4. Install dependencies:

   ```bash
   uv sync --frozen
   ```

## Verification

Verify the installation by running:

```bash
python -m codegen_lab --version
```

## Next Steps

Now that you have Codegen Lab installed, you can:

1. Explore the [User Guide](user-guide/installation.md) for detailed usage instructions
2. Check the [API Reference](api-reference.md) for technical details
3. Start using Codegen Lab in your projects
