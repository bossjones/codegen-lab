# Install uv-secure tool
[group('security')]
install-uv-secure:
    uv tool install uv-secure

# Run security audit with uv-secure
[group('security')]
audit:
    uv-secure --forbid-yanked --desc --aliases
