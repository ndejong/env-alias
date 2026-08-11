---
name: uv-testing
description: Guidelines for running uv commands to prevent creating local .venv folders.
---

# UV Environment Rules

It is VERY IMPORTANT that you NEVER create a `.venv` folder anywhere in the project directory.

When running `uv` commands (like `uv run pytest`, `uv pip install`, etc.), you MUST prefix the command with environment variables to redirect the venv to `${HOME}/.local/venvs/` and the cache to `/tmp`.

Use the following pattern for this project:
`UV_PROJECT_ENVIRONMENT=${HOME}/.local/venvs/env-alias UV_CACHE_DIR=/tmp/.uv-cache-env-alias UV_LINK_MODE=copy uv <command>`

Example for running tests:
`UV_PROJECT_ENVIRONMENT=${HOME}/.local/venvs/env-alias UV_CACHE_DIR=/tmp/.uv-cache-env-alias UV_LINK_MODE=copy uv run pytest tests/ -v`
