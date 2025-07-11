# MCP Integration Setup Guide

This guide walks through setting up the MCP Integration project with Python 3.12+ and proper MCP library support.

## Why Python 3.12+ is Required

The official MCP (Model Context Protocol) library requires Python 3.10 or higher. We recommend Python 3.12+ for:
- Full MCP protocol support
- Better type checking and performance
- Full Strands SDK v0.2.1 integration with agent orchestration
- Advanced memory management and persistent caching
- Modern async/await patterns with enhanced error handling

## Step-by-Step Setup

### 1. Install uv (Python Package Manager)

`uv` is a fast, modern Python package manager that makes it easy to manage Python versions and dependencies.

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
```

### 2. Install Python 3.12

```bash
# Install Python 3.12
uv python install 3.12

# Verify installation
uv python list
```

### 3. Create Virtual Environment

```bash
# Create virtual environment with Python 3.12
uv venv --python 3.12 .venv-mcp

# Activate the virtual environment
source .venv-mcp/bin/activate

# Verify Python version
python --version  # Should show Python 3.12.x
```

### 4. Install Dependencies

```bash
# Install all required packages
uv pip install \
    mcp \
    strands-agents \
    strands-agents-tools \
    simple-salesforce \
    jira \
    anthropic \
    fastapi \
    uvicorn \
    python-dotenv \
    aiohttp
```

### 5. Configure Environment

Create a `.env` file with your credentials:

```bash
# Salesforce - Simple authentication
SALESFORCE_USERNAME=your_username@company.com
SALESFORCE_PASSWORD=your_password
SALESFORCE_SECURITY_TOKEN=your_security_token

# Jira
JIRA_HOST=https://your-company.atlassian.net
JIRA_USERNAME=your_username@company.com
JIRA_API_TOKEN=your_api_token

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...
```

### 6. Test Your Setup

Run the comprehensive test suite:

```bash
python tests/test_mcp_setup.py
```

Expected output:
```
🚀 Testing MCP Integration with Python 3.12 and Strands SDK

🔍 Testing Python version: 3.12.11
✅ Python version is compatible

🔍 Testing package imports...
✅ MCP package imported
✅ Strands SDK imported
✅ Service packages imported
✅ Web framework packages imported

🔍 Testing MCP servers...
✅ Salesforce MCP server responds to health check
✅ Salesforce MCP server provides 5 tools

🔍 Testing MCP web server with Strands SDK...
✅ MCP web server with Strands SDK initializes successfully
✅ FastAPI app created
✅ Strands agent initialized

📊 Test Results: 4/4 tests passed
🎉 All tests passed! MCP integration is working correctly.
```

### 7. Start the Application

#### Native Mode (Recommended for Development)
```bash
# Make sure virtual environment is activated
source .venv-mcp/bin/activate

# Start all services
./start.sh
```

#### Docker Mode (If Docker Available)
```bash
docker-compose up
```

### 8. Verify Everything Works

1. **Open browser**: http://localhost:3000
2. **Check API health**: http://localhost:8000/api/health
3. **Test in chat**: "Show me my Salesforce accounts"

## Troubleshooting

### Python Version Issues

If you get import errors related to `typing` or `aiohttp`:
```bash
python --version  # Make sure it's 3.12+
```

### MCP Import Errors

If `import mcp` fails:
```bash
# Make sure virtual environment is activated
source .venv-mcp/bin/activate

# Reinstall MCP
uv pip install --force-reinstall mcp
```

### Strands SDK Issues

If Strands imports fail:
```bash
# Check what's available
python -c "import strands; print(dir(strands))"

# Should show: Agent, tool, and other components
```

### Virtual Environment Not Found

If you get "No such file or directory" for activation:
```bash
# Check if venv exists
ls -la .venv-mcp/

# If not, recreate it
uv venv --python 3.12 .venv-mcp
```

## Development Workflow

### Daily Development

1. **Activate environment**:
   ```bash
   source .venv-mcp/bin/activate
   ```

2. **Start services**:
   ```bash
   ./start.sh
   ```

3. **Make changes** to Python files

4. **Services auto-reload** on file changes

### Adding New Dependencies

```bash
# With virtual environment activated
uv pip install new-package

# Update documentation if needed
```

### Running Tests

```bash
# Comprehensive test
python tests/test_mcp_setup.py

# Run all tests
python tests/run_tests.py

# Quick health check
python tests/run_tests.py --quick

# Individual server test
MCP_SERVER_PORT=8001 python python_servers/salesforce_server_mcp.py
```

## Architecture Details

### File Structure
```
.venv-mcp/                          # Python 3.12 virtual environment
├── bin/python                      # Python 3.12 executable
├── lib/python3.12/site-packages/   # Installed packages
│   ├── mcp/                        # Official MCP library
│   ├── strands/                    # Strands SDK
│   └── ...

python_servers/
├── salesforce_server_mcp.py        # Proper MCP server
├── jira_server_mcp.py              # Proper MCP server
└── mcp_web_server.py               # Web server with Strands

tests/
├── test_mcp_setup.py               # Comprehensive setup test
├── test_imports.py                 # Import and version tests
├── test_servers.py                 # Server functionality tests
└── run_tests.py                    # Test runner
```

### Communication Flow
```
React UI → FastAPI Web Server → MCP Servers
                ↓
        Strands SDK Telemetry
                ↓
        OpenTelemetry Traces
```

### Environment Isolation

The virtual environment ensures:
- ✅ Python 3.12+ only
- ✅ Proper MCP library versions
- ✅ No conflicts with system Python
- ✅ Reproducible setup across machines
- ✅ Docker compatibility

## Next Steps

1. **Develop features** using the MCP protocol
2. **Add more tools** to extend functionality
3. **Deploy with Docker** for production
4. **Monitor with Strands** telemetry and observability

Your MCP integration is now ready for development! 🚀
