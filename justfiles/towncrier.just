# Towncrier tasks

# Build the combined news file from news fragments
# If no fragments exist, adds "no significant changes" to the news file
# Processed fragments are removed after building (uses git rm for committed files)
# This is the default command if none is specified
[group('towncrier')]
towncrier-build:
    uv run towncrier build --yes

# Create a news fragment with towncrier
[group('towncrier')]
towncrier-create type issue content:
    #!/usr/bin/env zsh
    # Escape quotes in content to prevent shell interpretation issues
    ESCAPED_CONTENT=$(echo "{{content}}" | sed 's/"/\\"/g')
    # Note: towncrier expects {name}.{type}.md format
    uv run towncrier create --content "$ESCAPED_CONTENT" "{{issue}}.{{type}}.md"

# Check if any news fragments exist that need to be added to changelog
[group('towncrier')]
towncrier-check:
    uv run towncrier check

# Show draft of what would be added to changelog without actually adding it
[group('towncrier')]
towncrier-draft:
    uv run towncrier build --draft

# Build changelog without asking for confirmation
[group('towncrier')]
towncrier-build-yes:
    uv run towncrier build --yes

# Build changelog with version override
[group('towncrier')]
towncrier-build-version version:
    uv run towncrier build --yes --version {{version}}

# List all available news fragment types from config
[group('towncrier')]
towncrier-types:
    #!/usr/bin/env zsh
    echo "Available news fragment types from pyproject.toml:"
    echo "- breaking:  Breaking Changes"
    echo "- feat:      Features"
    echo "- fix:       Bug Fixes"
    echo "- docs:      Documentation"
    echo "- chore:     Chores"
    echo "- refactor:  Code Refactoring"
    echo "- perf:      Performance Improvements"
    echo "- ci:        CI/CD Improvements"
    echo "- deps:      Dependencies"
    echo "- security:  Security"
    echo "- test:      Testing"
    echo "- style:     Code Style"
    echo "- build:     Build System"

# Create a new changelog entry with optional type and message
# If type is not provided, will prompt for selection
# If message is not provided, will use PR title or last commit message
[group('towncrier')]
towncrier-new entry_type='' message='':
    #!/usr/bin/env zsh

    # Define valid entry types
    VALID_TYPES=("breaking" "feat" "fix" "docs" "chore" "refactor" "perf" "ci" "deps" "security" "test" "style" "build")

    # Get PR number and title/commit message for default content
    PR_NUMBER=$(gh pr view --json number -q .number 2>/dev/null || echo "")
    if [ -z "$PR_NUMBER" ]; then
        PR_NUMBER=$(gh issue list --json number --limit 1 --state all -q '.[0].number + 1')
        CONTENT=$(git log -1 --pretty=%s)
    else
        CONTENT=$(gh pr view --json title -q .title)
    fi

    # Handle entry type selection
    TYPE="{{entry_type}}"
    if [ -z "$TYPE" ]; then
        echo "Available entry types:"
        for t in "${VALID_TYPES[@]}"; do
            echo "- $t"
        done
        echo ""
        while true; do
            echo -n "Entry type? "
            read TYPE
            if [[ " ${VALID_TYPES[@]} " =~ " ${TYPE} " ]]; then
                break
            else
                echo "Invalid entry type. Please choose from the list above."
            fi
        done
    elif [[ ! " ${VALID_TYPES[@]} " =~ " ${TYPE} " ]]; then
        echo "Error: Unknown entry type: ${TYPE}"
        exit 1
    fi

    # Handle message content
    MSG="{{message}}"
    if [ -z "$MSG" ]; then
        # Create temporary file with default content
        TEMP_FILE=$(mktemp)
        echo "$CONTENT" > "$TEMP_FILE"

        # Open editor for message
        if [ -n "$EDITOR" ]; then
            $EDITOR "$TEMP_FILE"
        elif [ -n "$VISUAL" ]; then
            $VISUAL "$TEMP_FILE"
        else
            vim "$TEMP_FILE"
        fi

        # Read edited content
        MSG=$(cat "$TEMP_FILE")
        rm "$TEMP_FILE"

        # If no changes made, use default content
        if [ -z "$MSG" ]; then
            MSG="$CONTENT"
        fi
    fi

    # Create the changelog entry using towncrier-create
    just towncrier-create "$TYPE" "$PR_NUMBER" "$MSG"
    echo "Created changelog entry: $TYPE.$PR_NUMBER.md"

# Create changelog entries from commit messages between a tag and main branch
# Usage: just towncrier-from-commits v1.0.0
# Optional: specify branch (defaults to main)
[group('towncrier')]
towncrier-from-commits tag branch="main":
    #!/usr/bin/env zsh

    # Ensure we have the latest commits
    git fetch --tags origin {{branch}}

    # Get list of commits between tag and branch
    echo "Getting commits between {{tag}} and {{branch}}..."

    # Function to guess entry type from commit message
    guess_type() {
        local msg="$1"
        case "$msg" in
            feat*|feature*|add*) echo "feat" ;;
            fix*|bug*) echo "fix" ;;
            doc*) echo "docs" ;;
            test*) echo "test" ;;
            refactor*) echo "refactor" ;;
            perf*) echo "perf" ;;
            ci*) echo "ci" ;;
            chore*|misc*) echo "chore" ;;
            style*) echo "style" ;;
            security*) echo "security" ;;
            deps*|dependency*) echo "deps" ;;
            breaking*|BREAKING*) echo "breaking" ;;
            build*) echo "build" ;;
            *) echo "chore" ;; # default to chore if no pattern matches
        esac
    }

    # Process each commit
    git log --reverse --pretty=format:"%H %s" {{tag}}..{{branch}} | while read -r commit_hash commit_msg; do
        echo "\nProcessing commit: $commit_msg"

        # Try to find associated PR number
        PR_NUMBER=$(gh pr list --search "$commit_hash" --state all --json number -q '.[0].number')
        if [ -z "$PR_NUMBER" ]; then
            # If no PR found, use a timestamp-based unique identifier
            PR_NUMBER=$(date -r $(git show -s --format=%ct $commit_hash) +%Y%m%d%H%M%S)
        fi

        # Guess the type from commit message
        TYPE=$(guess_type "$commit_msg")

        # Clean up commit message
        # Remove common prefixes like "feat:", "fix:", etc.
        CLEAN_MSG=$(echo "$commit_msg" | sed -E 's/^(feat|fix|docs|test|refactor|perf|ci|chore|style|security|deps|breaking|build)(\([^)]+\))?://')
        # Trim whitespace
        CLEAN_MSG=$(echo "$CLEAN_MSG" | sed -E 's/^[[:space:]]+|[[:space:]]+$//')
        # Escape quotes to prevent shell interpretation issues
        CLEAN_MSG=$(echo "$CLEAN_MSG" | sed 's/"/\\"/g')

        echo "Creating entry:"
        echo "  Type: $TYPE"
        echo "  PR/ID: $PR_NUMBER"
        echo "  Message: $CLEAN_MSG"

        # Create the changelog entry using the corrected format ({name}.{type}.md)
        uv run towncrier create --content "$CLEAN_MSG" "$PR_NUMBER.$TYPE.md" || {
            echo "Warning: Failed to create changelog entry for commit $commit_hash"
            continue
        }
    done

    # Show summary of created entries
    echo "\nCreated changelog entries from commits between {{tag}} and {{branch}}"
    echo "You can review them with: just towncrier-draft"
