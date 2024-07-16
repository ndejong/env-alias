# Development

This project uses the very awesome [slap-cli](https://niklasrosenstein.github.io/slap/) utility to help with packaging and release management.

## slap-cli
```shell
# Create a new venv "env-alias" to work within
slap venv -cg env-alias

# Activate the "env-alias" venv
slap venv -ag env-alias

# Install the requirements for the "env-alias" development venv
slap install --upgrade --link

# Update code formatting
slap run format

# Test the package (pytest, black, isort, flake8, safety)
slap test

# Write a "feature" changelog entry
slap changelog add -t "feature" -d "<changelog message>" [--issue <issue_url>]

# Bump the package version at the "patch" semver level
slap release patch --dry
slap release patch --tag [--push]

# Build a package
slap publish --build-directory build --dry

# Publish a package
slap publish
```
