[Skip to content](https://commitizen-tools.github.io/commitizen/#about)

# Introduction

[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/commitizen-tools/commitizen/pythonpackage.yml?label=python%20package&logo=github&logoColor=white&style=flat-square)](https://github.com/commitizen-tools/commitizen/actions)[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg?style=flat-square)](https://conventionalcommits.org/)[![PyPI Package latest release](https://img.shields.io/pypi/v/commitizen.svg?style=flat-square)](https://pypi.org/project/commitizen/)[![PyPI Package download count (per month)](https://img.shields.io/pypi/dm/commitizen?style=flat-square)](https://pypi.org/project/commitizen/)[![Supported versions](https://img.shields.io/pypi/pyversions/commitizen.svg?style=flat-square)](https://pypi.org/project/commitizen/)[![Conda Version](https://img.shields.io/conda/vn/conda-forge/commitizen?style=flat-square)](https://anaconda.org/conda-forge/commitizen)[![homebrew](https://img.shields.io/homebrew/v/commitizen?color=teal&style=flat-square)](https://formulae.brew.sh/formula/commitizen)[![Codecov](https://img.shields.io/codecov/c/github/commitizen-tools/commitizen.svg?style=flat-square)](https://codecov.io/gh/commitizen-tools/commitizen)[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?style=flat-square&logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

![Using commitizen cli](https://commitizen-tools.github.io/commitizen/images/demo.gif)

* * *

**Documentation:** [https://commitizen-tools.github.io/commitizen/](https://commitizen-tools.github.io/commitizen/)

* * *

## About [¶](https://commitizen-tools.github.io/commitizen/\#about "Permanent link")

Commitizen is release management tool designed for teams.

Commitizen assumes your team uses a standard way of committing rules
and from that foundation, it can bump your project's version, create
the changelog, and update files.

By default, commitizen uses [conventional commits](https://www.conventionalcommits.org/), but you
can build your own set of rules, and publish them.

Using a standardized set of rules to write commits, makes commits easier to read, and enforces writing
descriptive commits.

### Features [¶](https://commitizen-tools.github.io/commitizen/\#features "Permanent link")

- Command-line utility to create commits with your rules. Defaults: [Conventional commits](https://www.conventionalcommits.org/)
- Bump version automatically using [semantic versioning](https://semver.org/) based on the commits. [Read More](https://commitizen-tools.github.io/commitizen/commands/bump/)
- Generate a changelog using [Keep a changelog](https://keepachangelog.com/)
- Update your project's version files automatically
- Display information about your commit rules (commands: schema, example, info)
- Create your own set of rules and publish them to pip. Read more on [Customization](https://commitizen-tools.github.io/commitizen/customization/)

## Requirements [¶](https://commitizen-tools.github.io/commitizen/\#requirements "Permanent link")

[Python](https://www.python.org/downloads/) `3.9+`

[Git](https://git-scm.com/downloads) `1.8.5.2+`

## Installation [¶](https://commitizen-tools.github.io/commitizen/\#installation "Permanent link")

Install commitizen in your system using `pipx` (Recommended, [https://pypa.github.io/pipx/installation/](https://pypa.github.io/pipx/installation/)):

```
pipx ensurepath
pipx install commitizen
pipx upgrade commitizen

```

Install commitizen using `pip` with `--user` flag:

```
pip install --user -U commitizen

```

### Python project [¶](https://commitizen-tools.github.io/commitizen/\#python-project "Permanent link")

You can add it to your local project using one of the following.

With `pip`:

```
pip install -U commitizen

```

With `conda`:

```
conda install -c conda-forge commitizen

```

With Poetry >= 1.2.0:

```
poetry add commitizen --group dev

```

With Poetry < 1.2.0:

```
poetry add commitizen --dev

```

### macOS [¶](https://commitizen-tools.github.io/commitizen/\#macos "Permanent link")

via [homebrew](https://formulae.brew.sh/formula/commitizen):

```
brew install commitizen

```

## Usage [¶](https://commitizen-tools.github.io/commitizen/\#usage "Permanent link")

Most of the time this is the only command you'll run:

```
cz bump

```

On top of that, you can use commitizen to assist you with the creation of commits:

```
cz commit

```

Read more in the section [Getting Started](https://commitizen-tools.github.io/commitizen/getting_started/).

### Help [¶](https://commitizen-tools.github.io/commitizen/\#help "Permanent link")

```
$ cz --help
usage: cz [-h] [--debug] [-n NAME] [-nr NO_RAISE] {init,commit,c,ls,example,info,schema,bump,changelog,ch,check,version} ...

Commitizen is a cli tool to generate conventional commits.
For more information about the topic go to https://conventionalcommits.org/

optional arguments:
  -h, --help            show this help message and exit
  --config              the path of configuration file
  --debug               use debug mode
  -n NAME, --name NAME  use the given commitizen (default: cz_conventional_commits)
  -nr NO_RAISE, --no-raise NO_RAISE
                        comma separated error codes that won't rise error, e.g: cz -nr 1,2,3 bump. See codes at https://commitizen-
                        tools.github.io/commitizen/exit_codes/

commands:
  {init,commit,c,ls,example,info,schema,bump,changelog,ch,check,version}
    init                init commitizen configuration
    commit (c)          create new commit
    ls                  show available commitizens
    example             show commit example
    info                show information about the cz
    schema              show commit schema
    bump                bump semantic version based on the git log
    changelog (ch)      generate changelog (note that it will overwrite existing file)
    check               validates that a commit message matches the commitizen schema
    version             get the version of the installed commitizen or the current project (default: installed commitizen)

```

## Setting up bash completion [¶](https://commitizen-tools.github.io/commitizen/\#setting-up-bash-completion "Permanent link")

When using bash as your shell (limited support for zsh, fish, and tcsh is available), Commitizen can use [argcomplete](https://kislyuk.github.io/argcomplete/) for auto-completion. For this argcomplete needs to be enabled.

argcomplete is installed when you install Commitizen since it's a dependency.

If Commitizen is installed globally, global activation can be executed:

```
sudo activate-global-python-argcomplete

```

For permanent (but not global) Commitizen activation, use:

```
register-python-argcomplete cz >> ~/.bashrc

```

For one-time activation of argcomplete for Commitizen only, use:

```
eval "$(register-python-argcomplete cz)"

```

For further information on activation, please visit the [argcomplete website](https://kislyuk.github.io/argcomplete/).

## Sponsors [¶](https://commitizen-tools.github.io/commitizen/\#sponsors "Permanent link")

These are our cool sponsors!
