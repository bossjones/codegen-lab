[Skip to content](https://commitizen-tools.github.io/commitizen/commands/init/#usage)

# init

## Usage [¶](https://commitizen-tools.github.io/commitizen/commands/init/\#usage "Permanent link")

![cz init --help](https://commitizen-tools.github.io/commitizen/images/cli_help/cz_init___help.svg)

## Example [¶](https://commitizen-tools.github.io/commitizen/commands/init/\#example "Permanent link")

To start using commitizen, the recommended approach is to run

```
cz init

```

![init](https://commitizen-tools.github.io/commitizen/images/init.gif)

This command will ask you for information about the project and will
configure the selected file type ( `pyproject.toml`, `.cz.toml`, etc.).

The `init` will help you with

1. Choose a convention rules ( `name`)
2. Choosing a version provider ( `commitizen` or for example `Cargo.toml`)
3. Detecting your project's version
4. Detecting the tag format used
5. Choosing a version type ( `semver` or `pep440`)
6. Whether to create the changelog automatically or not during bump
7. Whether you want to keep the major as zero while building alpha software.
8. Whether to setup pre-commit hooks.
