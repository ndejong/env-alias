---
description: Guidelines for running uv commands to prevent creating local .venv folders.
---

It is VERY IMPORTANT that you NEVER create a `.venv` folder anywhere in the project directory.

When running `uv` commands (like `uv run pytest`, `uv pip install`, `uv run ruff check`, etc.), you MUST prefix the command with environment variables to redirect the `.venv` and cache directories to `/tmp`.

Use the following pattern for this project:
`UV_PROJECT_ENVIRONMENT=${HOME}/.local/venvs/env-alias UV_CACHE_DIR=/tmp/.uv-cache-env-alias UV_LINK_MODE=copy uv <command>`

Example for running tests:
`UV_PROJECT_ENVIRONMENT=${HOME}/.local/venvs/env-alias UV_CACHE_DIR=/tmp/.uv-cache-env-alias UV_LINK_MODE=copy uv run pytest tests/ -v`

Example for running lint checks:
`UV_PROJECT_ENVIRONMENT=${HOME}/.local/venvs/env-alias UV_CACHE_DIR=/tmp/.uv-cache-env-alias UV_LINK_MODE=copy uv run ruff check .`
