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

# Format TOML from stdin (dry-run)
[group('taplo')]
fmt-dry-run src:
    #!/usr/bin/env bash
    set -euo pipefail
    cat {{src}} | ./bin/taplo fmt -

# Check TOML formatting
[group('taplo')]
fmt-check src:
    ./bin/taplo fmt --check --diff {{src}}

# Validate TOML files
[group('taplo')]
validate src:
    ./bin/taplo lint {{src}}

# Convert TOML to JSON
[group('taplo')]
to-json src output="output.json":
    #!/usr/bin/env bash
    set -euo pipefail
    ./bin/taplo get -f {{src}} -o json > {{output}}
    echo "Converted {{src}} to JSON at {{output}} 🔄"

# Convert TOML to JSON and pretty print
[group('taplo')]
to-json-pretty src output="output.json":
    #!/usr/bin/env bash
    set -euo pipefail
    ./bin/taplo get -f {{src}} -o json | jq '.' > {{output}}
    echo "Converted {{src}} to pretty JSON at {{output}} ✨"

# Extract a specific value from TOML file
[group('taplo')]
get-value src path:
    #!/usr/bin/env bash
    set -euo pipefail
    echo "Extracting '{{path}}' from {{src}}..."
    ./bin/taplo get -f {{src}} '{{path}}'

# Extract a specific value as JSON from TOML file
[group('taplo')]
get-value-json src path:
    #!/usr/bin/env bash
    set -euo pipefail
    echo "Extracting '{{path}}' as JSON from {{src}}..."
    ./bin/taplo get -f {{src}} -o json '{{path}}'

# Format TOML files with specific options
[group('taplo')]
fmt-with-options src *options:
    #!/usr/bin/env bash
    set -euo pipefail
    OPTIONS_STRING=""
    for opt in {{options}}; do
        OPTIONS_STRING="$OPTIONS_STRING --option $opt"
    done
    ./bin/taplo fmt $OPTIONS_STRING {{src}}

# Validate TOML against a specific schema
[group('taplo')]
validate-schema src schema:
    #!/usr/bin/env bash
    set -euo pipefail
    echo "Validating {{src}} against schema {{schema}}..."
    ./bin/taplo check --schema {{schema}} {{src}}

# Format all TOML files in a directory
[group('taplo')]
fmt-dir dir:
    #!/usr/bin/env bash
    set -euo pipefail
    find {{dir}} -name "*.toml" -type f -exec ./bin/taplo fmt --in-place {} \;
    echo "Formatted all TOML files in {{dir}} 📝"

# Check formatting of all TOML files in a directory
[group('taplo')]
fmt-check-dir dir:
    #!/usr/bin/env bash
    set -euo pipefail
    find {{dir}} -name "*.toml" -type f -exec ./bin/taplo fmt --check {} \;
    echo "Checked formatting of all TOML files in {{dir}} 🔍"

# Check formatting of multiple TOML files
[group('taplo')]
fmt-check-all:
    #!/usr/bin/env bash
    set -euo pipefail
    echo "Checking formatting of TOML files... 🔍"
    ./bin/taplo fmt --check --diff pyproject.toml
    ./bin/taplo fmt --check --diff taplo.toml
    ./bin/taplo fmt --check --diff mise.toml
    echo "All TOML files checked successfully ✨"
