# Environment Guidelines

## Strictly No Local `.venv`

**⚠️ CRITICAL RULE: NEVER create a local `.venv` directory inside the repository.**

All dependency management and execution must be isolated from the repository path to ensure a clean monorepo experience and prevent state pollution. 

### Enforcing the Rule
Whenever you use `uv` to install dependencies, run scripts, execute tests, or perform CLI commands, you **MUST** prefix the command with environment variables that point the virtual environment and cache to the specified directories, and explicitly use copy linking.

Use this exact prefix:
```bash
UV_PROJECT_ENVIRONMENT=${HOME}/.local/venvs/env-alias \
UV_CACHE_DIR=/tmp/.uv-cache-env-alias \
UV_LINK_MODE=copy \
uv <command>
```

**Example (Running Tests):**
```bash
UV_PROJECT_ENVIRONMENT=${HOME}/.local/venvs/env-alias UV_CACHE_DIR=/tmp/.uv-cache-env-alias UV_LINK_MODE=copy uv run pytest
```

Failure to use this prefix may result in a `.venv` being created in the workspace, which is strictly prohibited.
