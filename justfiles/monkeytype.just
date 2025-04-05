# Run monkeytype to collect type information during test execution
[group('monkeytype')]
monkeytype_create:
    uv run monkeytype run `uv run which py.test`

# Apply collected type information to all modules
[group('monkeytype')]
monkeytype_apply:
    uv run monkeytype list-modules | xargs -n1 -I{} sh -c 'uv run monkeytype apply {}'
