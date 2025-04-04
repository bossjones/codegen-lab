[Skip to content](https://commitizen-tools.github.io/commitizen/getting_started/#initialize-commitizen)

# Getting Started

## Initialize commitizen [¶](https://commitizen-tools.github.io/commitizen/getting_started/\#initialize-commitizen "Permanent link")

If it's your first time, you'll need to create a commitizen configuration file.

The assistant utility will help you set up everything

```
cz init

```

Alternatively, create a file `.cz.toml` or `cz.toml` in your project's directory.

```
[tool.commitizen]
version = "0.1.0"
update_changelog_on_bump = true

```

## Usage [¶](https://commitizen-tools.github.io/commitizen/getting_started/\#usage "Permanent link")

### Bump version [¶](https://commitizen-tools.github.io/commitizen/getting_started/\#bump-version "Permanent link")

```
cz bump

```

This command will bump your project's version, and it will create a tag.

Because of the setting `update_changelog_on_bump`, bump will also create the **changelog**.
You can also [update files](https://commitizen-tools.github.io/commitizen/commands/bump/#version_files).
You can configure the [version scheme](https://commitizen-tools.github.io/commitizen/commands/bump/#version_scheme) and [version provider](https://commitizen-tools.github.io/commitizen/config/#version-providers).

There are many more options available, please read the docs for the [bump command](https://commitizen-tools.github.io/commitizen/commands/bump/).

### Committing [¶](https://commitizen-tools.github.io/commitizen/getting_started/\#committing "Permanent link")

Run in your terminal

```
cz commit

```

or the shortcut

```
cz c

```

#### Sign off the commit [¶](https://commitizen-tools.github.io/commitizen/getting_started/\#sign-off-the-commit "Permanent link")

Run in the terminal

```
cz commit -- --signoff

```

or the shortcut

```
cz commit -- -s

```

### Get project version [¶](https://commitizen-tools.github.io/commitizen/getting_started/\#get-project-version "Permanent link")

Running `cz version` will return the version of commitizen, but if you want
your project's version you can run:

```
cz version -p

```

This can be useful in many situations, where otherwise, you would require a way
to parse the version of your project. Maybe it's simple if you use a `VERSION` file,
but once you start working with many different projects, it becomes tricky.

A common example is, when you need to send to slack, the changes for the version that you
just created:

```
cz changelog --dry-run "$(cz version -p)"

```

### Integration with Pre-commit [¶](https://commitizen-tools.github.io/commitizen/getting_started/\#integration-with-pre-commit "Permanent link")

Commitizen can lint your commit message for you with `cz check`.

You can integrate this in your [pre-commit](https://pre-commit.com/) config with:

```
---
repos:
  - repo: https://github.com/commitizen-tools/commitizen
    rev: master
    hooks:
      - id: commitizen
      - id: commitizen-branch
        stages: [pre-push]

```

After the configuration is added, you'll need to run:

```
pre-commit install --hook-type commit-msg --hook-type pre-push

```

If you aren't using both hooks, you needn't install both stages.

| Hook | Recommended Stage |
| --- | --- |
| commitizen | commit-msg |
| commitizen-branch | pre-push |

Note that pre-commit discourages using `master` as a revision, and the above command will print a warning. You should replace the `master` revision with the [latest tag](https://github.com/commitizen-tools/commitizen/tags). This can be done automatically with:

```
pre-commit autoupdate

```

Read more about the `check` command [here](https://commitizen-tools.github.io/commitizen/commands/check/).
