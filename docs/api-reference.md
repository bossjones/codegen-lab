# API Reference

This page provides detailed documentation for the Codegen Lab API.

## Core API

### `codegen_lab.generate`

Main function for generating code based on a prompt.

```python
from codegen_lab import generate

code = generate(
    prompt="Create a Python function to calculate the Fibonacci sequence",
    model="gpt-4",
    temperature=0.7,
    max_tokens=1024
)

print(code)
```

#### Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `prompt` | `str` | The prompt to generate code from | Required |
| `model` | `str` | Model to use | "gpt-3.5-turbo" |
| `temperature` | `float` | Temperature parameter (0.0-1.0) | 0.7 |
| `max_tokens` | `int` | Maximum tokens to generate | 1024 |
| `top_p` | `float` | Top-p sampling parameter | 0.9 |
| `stop` | `list[str]` | Sequences where generation should stop | None |

#### Returns

`str`: The generated code.

#### Exceptions

- `ValueError`: If prompt is empty or parameters are invalid
- `ConnectionError`: If there's an issue connecting to the model API
- `AuthenticationError`: If API credentials are invalid

### `codegen_lab.enhance`

Enhance existing code with improvements, documentation, or tests.

```python
from codegen_lab import enhance

original_code = """
def fibonacci(n):
    if n <= 0:
        return []
    if n == 1:
        return [0]
    sequence = [0, 1]
    for i in range(2, n):
        sequence.append(sequence[i-1] + sequence[i-2])
    return sequence
"""

enhanced_code = enhance(
    code=original_code,
    enhancement_type="documentation",
    language="python"
)

print(enhanced_code)
```

#### Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `code` | `str` | The code to enhance | Required |
| `enhancement_type` | `str` | Type of enhancement ("documentation", "performance", "tests", "all") | "all" |
| `language` | `str` | Programming language of the code | "python" |
| `model` | `str` | Model to use | "gpt-3.5-turbo" |
| `temperature` | `float` | Temperature parameter (0.0-1.0) | 0.7 |

#### Returns

`str`: The enhanced code.

## Utility Functions

### `codegen_lab.utils.validate_code`

Validate generated code for syntax errors and other issues.

```python
from codegen_lab.utils import validate_code

code = """
def hello_world():
    print("Hello, world!")
"""

is_valid, issues = validate_code(code, language="python")

if is_valid:
    print("Code is valid!")
else:
    print("Issues found:", issues)
```

#### Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `code` | `str` | The code to validate | Required |
| `language` | `str` | Programming language of the code | "python" |
| `strict` | `bool` | Enable strict validation | False |

#### Returns

- `bool`: Whether the code is valid
- `list[str]`: List of issues found, empty if code is valid
