# pre-commit install hook-types

The commands `uv run pre-commit install --hook-type=pre-push` and `uv run pre-commit install --hook-type=commit-msg` are used to install specific Git hooks provided by the `pre-commit` framework.

1. **`uv run pre-commit install --hook-type=pre-push`**:
   - Installs the `pre-push` Git hook.
   - This hook runs automatically before a `git push` operation. It is typically used for checks that may take longer to execute, such as linting, running tests, or ensuring compliance with project standards before code is pushed to a remote repository[1][5][8].

2. **`uv run pre-commit install --hook-type=commit-msg`**:
   - Installs the `commit-msg` Git hook.
   - This hook runs automatically when a commit message is created. It is often used to enforce commit message formatting standards (e.g., conventional commits) or validate the content of the commit message[1][7][8].

By using these commands, developers can ensure automated quality checks at different stages of the Git workflow, improving code consistency and reducing errors.
