# bump package
[group('commit')]
commit-bump:
	uv run cz bump

# dry run bump package
[group('commit')]
commit-bump-dry:
	uv run cz bump --dry-run

# commit package
[group('commit')]
commit-files:
	uv run cz commit

# get commit info
[group('commit')]
commit-info:
	uv run cz info

# generate full changelog
[group('commit')]
commit-changelog:
	uv run cz changelog

# generate changelog for specific version (dry-run)
[group('commit')]
commit-changelog-version version:
	uv run cz changelog {{version}} --dry-run

# generate changelog for version range (dry-run)
[group('commit')]
commit-changelog-range start end:
	uv run cz changelog {{start}}..{{end}} --dry-run

# generate incremental changelog (builds from latest version found in changelog)
[group('commit')]
commit-changelog-incremental:
	uv run cz changelog --incremental

# check if commit message follows rules
[group('commit')]
commit-check message:
	uv run cz check --message "{{message}}"

# check commit messages in a range
[group('commit')]
commit-check-range range:
	uv run cz check --rev-range "{{range}}"

# check commit message from file
[group('commit')]
commit-check-file file:
	uv run cz check --commit-msg-file "{{file}}"

# bump version and generate changelog together
[group('commit')]
commit-bump-with-changelog:
	uv run cz bump --changelog

# list all available commit types
[group('commit')]
commit-list:
	uv run cz ls
