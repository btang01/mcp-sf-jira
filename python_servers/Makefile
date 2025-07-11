# Makefile for MCP Integration - Using uv for all Python operations

.PHONY: install dev test lint format clean run-backend run-salesforce run-jira

# Default Python version
PYTHON_VERSION = 3.13

# Install dependencies
install:
	@echo "📦 Installing dependencies with uv..."
	@if ! command -v uv >/dev/null 2>&1; then \
		echo "Installing uv..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
	fi
	@uv venv --python $(PYTHON_VERSION)
	@uv pip install -r pyproject.toml
	@echo "✅ Installation complete!"

# Install dev dependencies
dev:
	@echo "📦 Installing dev dependencies..."
	@uv pip install -e ".[dev]"

# Run tests
test:
	@echo "🧪 Running tests..."
	@uv run pytest

# Run linting
lint:
	@echo "🔍 Running linting..."
	@uv run ruff check .

# Format code
format:
	@echo "✨ Formatting code..."
	@uv run black .
	@uv run ruff check --fix .

# Clean up
clean:
	@echo "🧹 Cleaning up..."
	@rm -rf .venv
	@rm -rf __pycache__
	@rm -rf .pytest_cache
	@rm -rf .ruff_cache
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete

# Run backend server
run-backend:
	@echo "🚀 Starting MCP backend server..."
	@uv run python mcp_web_server.py

# Run Salesforce server standalone
run-salesforce:
	@echo "🚀 Starting Salesforce MCP server..."
	@uv run python salesforce_server_modern.py

# Run Jira server standalone
run-jira:
	@echo "🚀 Starting Jira MCP server..."
	@uv run python jira_server_modern.py

# Show help
help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies with uv"
	@echo "  make dev          - Install dev dependencies"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linting"
	@echo "  make format       - Format code"
	@echo "  make clean        - Clean up generated files"
	@echo "  make run-backend  - Run the MCP web server"
	@echo "  make run-salesforce - Run Salesforce server standalone"
	@echo "  make run-jira     - Run Jira server standalone"