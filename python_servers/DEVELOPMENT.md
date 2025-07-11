# Development Guide

This project uses `uv` for fast, reliable Python dependency management.

## Setup

### 1. Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Install Dependencies

```bash
# Using the install script
./install.sh

# Or manually
uv venv --python 3.13
uv pip install -r pyproject.toml
```

### 3. Activate Virtual Environment

```bash
source .venv/bin/activate
```

## Common Tasks

### Running the Servers

```bash
# Run the main web server (includes MCP servers)
uv run python mcp_web_server.py

# Or use the Makefile
make run-backend
```

### Running Individual MCP Servers

```bash
# Salesforce server
uv run python salesforce_server_modern.py

# Jira server  
uv run python jira_server_modern.py
```

### Installing New Dependencies

```bash
# Add to pyproject.toml, then:
uv pip install -r pyproject.toml

# Or install directly
uv pip install package-name
```

### Development Tools

```bash
# Install dev dependencies
make dev

# Run linting
make lint

# Format code
make format

# Run tests
make test
```

## Why uv?

- **Fast**: 10-100x faster than pip
- **Reliable**: Built-in dependency resolution
- **Simple**: No need for pip-tools or poetry
- **Compatible**: Works with standard Python packaging

## Troubleshooting

### uv not found

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH if needed
export PATH="$HOME/.local/bin:$PATH"
```

### Python version issues

```bash
# uv will automatically download Python 3.13 if needed
uv venv --python 3.13
```

### Dependency conflicts

```bash
# uv handles dependency resolution automatically
uv pip install -r pyproject.toml
```