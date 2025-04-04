# Install taplo locally
[group('taplo')]
install-taplo:
    #!/usr/bin/env bash
    set -euo pipefail

    # Create local bin directory if it doesn't exist
    mkdir -p bin

    # Detect OS and architecture
    OS=$(uname -s | tr '[:upper:]' '[:lower:]')
    ARCH=$(uname -m)

    # Convert architecture names
    case "${ARCH}" in
        x86_64) ARCH="x86_64" ;;
        aarch64|arm64) ARCH="aarch64" ;;
        *) echo "Unsupported architecture: ${ARCH}" && exit 1 ;;
    esac

    # Set download URL based on OS and architecture
    case "${OS}" in
        darwin)
            URL="https://github.com/tamasfe/taplo/releases/latest/download/taplo-full-darwin-${ARCH}.gz"
            ;;
        linux)
            URL="https://github.com/tamasfe/taplo/releases/latest/download/taplo-full-linux-${ARCH}.gz"
            ;;
        *)
            echo "Unsupported OS: ${OS}"
            exit 1
            ;;
    esac

    echo "Downloading taplo from ${URL}..."
    curl -fsSL "${URL}" | gzip -d - > bin/taplo
    chmod +x bin/taplo
    echo "taplo installed successfully in bin/taplo"

    # Test the installation
    ./bin/taplo --version

# Show taplo version
[group('taplo')]
taplo-version:
    ./bin/taplo --version

# Format TOML files
[group('taplo')]
fmt src:
    ./bin/taplo fmt {{src}}

# Format TOML files in place
[group('taplo')]
fmt-inplace src:
    ./bin/taplo fmt --in-place {{src}}

# Check TOML formatting
[group('taplo')]
fmt-check src:
    ./bin/taplo fmt --check {{src}}

# Validate TOML files
[group('taplo')]
validate src:
    ./bin/taplo lint {{src}}
