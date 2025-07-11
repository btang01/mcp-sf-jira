#!/bin/bash
# Install script using uv for Python dependency management

set -e

echo "🚀 Installing MCP Integration dependencies with uv"
echo "=============================================="

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "✅ uv installed successfully"
fi

# Create virtual environment with Python 3.13
echo "📦 Creating virtual environment with Python 3.13..."
uv venv --python 3.13

# Install dependencies
echo "📦 Installing dependencies..."
uv pip install -r pyproject.toml

echo ""
echo "✅ Installation complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source .venv/bin/activate"
echo ""
echo "To run the MCP servers:"
echo "  uv run python mcp_web_server.py"