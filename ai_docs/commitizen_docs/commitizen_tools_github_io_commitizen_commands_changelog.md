[Skip to content](https://commitizen-tools.github.io/commitizen/commands/changelog/#about)

# changelog

## About [¶](https://commitizen-tools.github.io/commitizen/commands/changelog/\#about "Permanent link")

This command will generate a changelog following the committing rules established.

To create the changelog automatically on bump, add the setting [update\_changelog\_on\_bump](https://commitizen-tools.github.io/commitizen/commands/bump/#update_changelog_on_bump)

```
[tool.commitizen]
update_changelog_on_bump = true

```

## Usage [¶](https://commitizen-tools.github.io/commitizen/commands/changelog/\#usage "Permanent link")

![cz changelog --help](https://commitizen-tools.github.io/commitizen/images/cli_help/cz_changelog___help.svg)

### Examples [¶](https://commitizen-tools.github.io/commitizen/commands/changelog/\#examples "Permanent link")

#### Generate full changelog [¶](https://commitizen-tools.github.io/commitizen/commands/changelog/\#generate-full-changelog "Permanent link")

```
cz changelog

```

```
cz ch

```

#### Get the changelog for the given version [¶](https://commitizen-tools.github.io/commitizen/commands/changelog/\#get-the-changelog-for-the-given-version "Permanent link")

```
cz changelog 0.3.0 --dry-run

```

#### Get the changelog for the given version range [¶](https://commitizen-tools.github.io/commitizen/commands/changelog/\#get-the-changelog-for-the-given-version-range "Permanent link")

```
cz changelog 0.3.0..0.4.0 --dry-run

```

## Constrains [¶](https://commitizen-tools.github.io/commitizen/commands/changelog/\#constrains "Permanent link")

changelog generation is constrained only to **markdown** files.

## Description [¶](https://commitizen-tools.github.io/commitizen/commands/changelog/\#description "Permanent link")

These are the variables used by the changelog generator.

```
# <version> (<date>)

## <change_type>

- **<scope>**: <message>

```

It will create a full block like above per version found in the tags.
And it will create a list of the commits found.
The `change_type` and the `scope` are optional, they don't need to be provided,
but if your regex does they will be rendered.

The format followed by the changelog is the one from [keep a changelog](https://keepachangelog.com/)
and the following variables are expected:

| Variable | Description | Source |
| --- | --- | --- |
| `version` | Version number which should follow [semver](https://semver.org/) | `tags` |
| `date` | Date in which the tag was created | `tags` |
| `change_type` | The group where the commit belongs to, this is optional. Example: fix | `commit regex` |
| `message`\* | Information extracted from the commit message | `commit regex` |
| `scope` | Contextual information. Should be parsed using the regex from the message, it will be **bold** | `commit regex` |
| `breaking` | Whether is a breaking change or not | `commit regex` |

- **required**: is the only one required to be parsed by the regex

## Configuration [¶](https://commitizen-tools.github.io/commitizen/commands/changelog/\#configuration "Permanent link")

### `unreleased_version` [¶](https://commitizen-tools.github.io/commitizen/commands/changelog/\#unreleased_version "Permanent link")

There is usually a chicken and egg situation when automatically
bumping the version and creating the changelog.
If you bump the version first, you have no changelog, you have to
create it later, and it won't be included in
the release of the created version.

If you create the changelog before bumping the version, then you
usually don't have the latest tag, and the _Unreleased_ title appears.

By introducing `unreleased_version` you can prevent this situation.

Before bumping you can run:

```
cz changelog --unreleased-version="v1.0.0"

```

Remember to use the tag instead of the raw version number

For example if the format of your tag includes a `v` ( `v1.0.0`), then you should use that,
if your tag is the same as the raw version, then ignore this.

Alternatively you can directly bump the version and create the changelog by doing

```
cz bump --changelog

```

### `file-name` [¶](https://commitizen-tools.github.io/commitizen/commands/changelog/\#file-name "Permanent link")

This value can be updated in the `toml` file with the key `changelog_file` under `tools.commitizen`

Specify the name of the output file, remember that changelog only works with markdown.

```
cz changelog --file-name="CHANGES.md"

```

### `incremental` [¶](https://commitizen-tools.github.io/commitizen/commands/changelog/\#incremental "Permanent link")

This flag can be set in the `toml` file with the key `changelog_incremental` under `tools.commitizen`

Benefits:

- Build from latest version found in changelog, this is useful if you have a different changelog and want to use commitizen
- Update unreleased area
- Allows users to manually touch the changelog without being rewritten.

```
cz changelog --incremental

```

```
[tools.commitizen]
# ...
changelog_incremental = true

```

### `start-rev` [¶](https://commitizen-tools.github.io/commitizen/commands/changelog/\#start-rev "Permanent link")

This value can be set in the `toml` file with the key `changelog_start_rev` under `tools.commitizen`

Start from a given git rev to generate the changelog. Commits before that rev will not be considered. This is especially useful for long-running projects adopting conventional commits, where old commit messages might fail to be parsed for changelog generation.

```
cz changelog --start-rev="v0.2.0"

```

```
[tools.commitizen]
# ...
changelog_start_rev = "v0.2.0"

```

### merge-prerelease [¶](https://commitizen-tools.github.io/commitizen/commands/changelog/\#merge-prerelease "Permanent link")

This flag can be set in the `toml` file with the key `changelog_merge_prerelease` under `tools.commitizen`

Collects changes from prereleases into the next non-prerelease. This means that if you have a prerelease version, and then a normal release, the changelog will show the prerelease changes as part of the changes of the normal release. If not set, it will include prereleases in the changelog.

```
cz changelog --merge-prerelease

```

```
[tools.commitizen]
# ...
changelog_merge_prerelease = true

```

### `template` [¶](https://commitizen-tools.github.io/commitizen/commands/changelog/\#template "Permanent link")

Provides your own changelog jinja template by using the `template` settings or the `--template` parameter.
See [the template customization section](https://commitizen-tools.github.io/commitizen/customization/#customizing-the-changelog-template)

### `extras` [¶](https://commitizen-tools.github.io/commitizen/commands/changelog/\#extras "Permanent link")

Provides your own changelog extra variables by using the `extras` settings or the `--extra/-e` parameter.

```
cz changelog --extra key=value -e short="quoted value"

```

See [the template customization section](https://commitizen-tools.github.io/commitizen/customization/#customizing-the-changelog-template)

## Hooks [¶](https://commitizen-tools.github.io/commitizen/commands/changelog/\#hooks "Permanent link")

Supported hook methods:

- per parsed message: useful to add links
- end of changelog generation: useful to send slack or chat message, or notify another department

Read more about hooks in the [customization page](https://commitizen-tools.github.io/commitizen/customization/)
