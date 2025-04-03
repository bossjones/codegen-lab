# https://just.systems/man/en/

# Import common configuration and variables
import "justfiles/common.just"
import "justfiles/variables.just"

# Import task groups
import "justfiles/commit.just"
import "justfiles/check.just"
import "justfiles/clean.just"
import "justfiles/format.just"
import "justfiles/package.just"
import "justfiles/install.just"
import "justfiles/doc.just"
import "justfiles/release.just"
import "justfiles/uv.just"
import "justfiles/changelog.just"
import "justfiles/towncrier.just"
import "justfiles/validate.just"
import "justfiles/security.just"

# display help information
default:
	@just --list
