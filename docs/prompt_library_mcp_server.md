# Cursor Rules Prompt Library

This FastMCP server exposes cursor rules as resources and provides a prompt endpoint for creating custom cursor rules based on user input.

## Features

- **Resource Endpoints**:
  - `cursor-rules://list` - List all available cursor rules
  - `cursor-rule://{name}` - Get a cursor rule by name (parsed structure)
  - `cursor-rule-raw://{name}` - Get the raw content of a cursor rule by name

- **Prompt Endpoints**:
  - `repo-analysis` - Analyze a repository to gather information for cursor rule creation
  - `generate-cursor-rule` - Generate a custom cursor rule based on repository information

- **Tool Endpoints**:
  - `save_cursor_rule` - Save a cursor rule to the cursor rules directory

## Usage

### Running the Server

```bash
python -m examples.fastmcp.prompt_library
```

### Listing Cursor Rules

```python
from mcp.client import Client
from pydantic import AnyUrl

async with Client() as client:
    result = await client.read_resource(AnyUrl("cursor-rules://list"))
    rules = json.loads(result.contents[0].text)
    for rule in rules:
        print(f"{rule['name']}: {rule['description']}")
```

### Getting a Cursor Rule

```python
from mcp.client import Client
from pydantic import AnyUrl

async with Client() as client:
    result = await client.read_resource(AnyUrl("cursor-rule://anthropic-chain-of-thought"))
    rule = json.loads(result.contents[0].text)
    print(f"Title: {rule['title']}")
    print(f"Description: {rule['description']}")
    print(f"Rule: {rule['rule']['name']}")
```

### Analyzing a Repository

```python
from mcp.client import Client

async with Client() as client:
    result = await client.get_prompt("repo-analysis", {
        "repo_description": "A Python web application using FastAPI and SQLAlchemy",
        "main_languages": "Python",
        "file_patterns": "*.py",
        "key_features": "API, Database, Authentication"
    })

    # Send the prompt to an LLM for completion
    completion = await client.create_message(result.messages)
    print(completion.content[0].text)
```

### Generating a Custom Cursor Rule

```python
from mcp.client import Client
import json

async with Client() as client:
    result = await client.get_prompt("generate-cursor-rule", {
        "rule_name": "fastapi-best-practices",
        "description": "Best practices for FastAPI applications",
        "file_patterns": "*.py",
        "content_patterns": "fastapi, APIRouter, Depends",
        "action_message": "When using FastAPI, follow these best practices:\n\n1. Use dependency injection\n2. Validate input with Pydantic models\n3. Use proper status codes\n4. Document your endpoints",
        "examples": json.dumps([
            {
                "input": "# Bad: No input validation\n@app.post('/users')\ndef create_user(user_data: dict):\n    return db.create_user(user_data)\n\n# Good: Proper input validation\n@app.post('/users', status_code=201)\ndef create_user(user: UserCreate):\n    return db.create_user(user.dict())",
                "output": "Using Pydantic models for input validation"
            }
        ]),
        "tags": "fastapi, best-practices, web-development",
        "priority": "high"
    })

    # Send the prompt to an LLM for completion
    completion = await client.create_message(result.messages)
    print(completion.content[0].text)

    # Save the generated rule
    rule_content = completion.content[0].text.split("```markdown\n")[1].split("```")[0]
    result = await client.call_tool("save_cursor_rule", {
        "rule_name": "fastapi-best-practices",
        "rule_content": rule_content
    })
    print(result.content[0].text)
```

## Development

### Running Tests

```bash
pytest tests/unittests/test_prompt_library.py -v
```

### Adding New Features

- To add a new resource endpoint, use the `@mcp.resource()` decorator
- To add a new prompt endpoint, use the `@mcp.prompt()` decorator
- To add a new tool endpoint, use the `@mcp.tool()` decorator

### Project Structure

- `examples/fastmcp/prompt_library.py` - Main FastMCP server implementation
- `tests/unittests/test_prompt_library.py` - Tests for the FastMCP server
- `hack/drafts/cursor_rules/` - Directory containing cursor rule files
