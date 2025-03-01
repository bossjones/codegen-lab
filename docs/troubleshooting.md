# Troubleshooting

This page provides solutions to common issues you might encounter when using Codegen Lab.

## Installation Issues

### Python Version Compatibility

**Issue**: Error indicating an incompatible Python version.

**Solution**: Codegen Lab requires Python 3.10 or higher. Upgrade your Python installation or use a tool like pyenv to manage multiple Python versions.

```bash
# Install pyenv (macOS)
brew install pyenv

# Install Python 3.12 with pyenv
pyenv install 3.12.0

# Set Python 3.12 as the local version for this project
pyenv local 3.12.0
```

### Dependency Conflicts

**Issue**: Dependency resolution failures or conflicts during installation.

**Solution**: Try reinstalling with the `--reinstall` flag or in a fresh virtual environment.

```bash
# Using UV (recommended)
uv sync --frozen --reinstall

# Alternative: Create a fresh environment
rm -rf .venv
uv venv --python 3.12.0
source .venv/bin/activate
uv sync --frozen
```

## Runtime Issues

### Import Errors

**Issue**: `ModuleNotFoundError` or similar import errors when running Codegen Lab.

**Solution**: Ensure you've activated the virtual environment and installed all dependencies.

```bash
# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Verify installation
uv pip list
```

### Performance Issues

**Issue**: Code generation is slow or unstable.

**Solution**:

1. Check your internet connection if using cloud-based models
2. Verify system resources (RAM, CPU) are sufficient
3. Try reducing model complexity or batch size
4. Update to the latest version of Codegen Lab

```bash
# Update to latest version
uv add --upgrade codegen-lab
```

## Model-Specific Issues

### API Rate Limits

**Issue**: Encountering rate limits when using external API-based models.

**Solution**: Implement exponential backoff retry logic or upgrade your API subscription tier.

### Model Output Quality

**Issue**: Poor quality code generation results.

**Solution**:

1. Improve your prompts with more context and examples
2. Try a different model or adjust temperature settings
3. Fine-tune the model on your specific use case (if applicable)

## Environment and Configuration Issues

### Configuration File Not Found

**Issue**: Codegen Lab can't find your configuration file.

**Solution**: Ensure your configuration file is in the correct location or explicitly specify the path.

```bash
python -m codegen_lab --config path/to/config.yaml
```

### Environment Variables Not Applied

**Issue**: Environment variable configurations aren't being applied.

**Solution**: Verify environment variables are correctly set and take precedence over config files.

```bash
# Set environment variables
export CODEGEN_MODEL_NAME="gpt-4"
export CODEGEN_DEBUG=true

# Verify environment variables
echo $CODEGEN_MODEL_NAME
```

## Getting Further Help

If you encounter issues not covered in this guide:

1. Check the [GitHub Issues](https://github.com/bossjones/codegen-lab/issues) for similar problems and solutions
2. Open a new issue with detailed information about your problem
3. Join the community discussion in [Discussions](https://github.com/bossjones/codegen-lab/discussions)
