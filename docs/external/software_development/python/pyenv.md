# pyenv

[pyenv][] is a good tool to install and manage Python versions.

## Install

=== "On a Mac with Homebrew"

    ```shell
    brew install pyenv
    ```

=== "With curl and bash"

    ```shell
    curl https://pyenv.run | bash
    ```

More installation info [here](https://github.com/pyenv/pyenv?tab=readme-ov-file#installation)

## Usage

### Install version of Python

```shell
pyenv install 3.10.12
```

### Set global version

setting a version:

```shell
pyenv global 3.10.12
```

### Get current Python version

Get your current python version:

```shell
python --version
```

[pyenv]: https://github.com/pyenv/pyenv
[Homebrew]: https://brew.sh/
