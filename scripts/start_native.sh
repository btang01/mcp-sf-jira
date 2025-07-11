#!/bin/bash

# MCP Integration Native Startup Script with Python 3.12
# Runs all services using the .venv-mcp virtual environment

set -e

echo "🚀 Starting MCP Integration (Native Mode with Python 3.12)"
echo "==========================================================="

# Check if we're in the right directory
if [ ! -f "test_mcp_setup.py" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create it with your credentials."
    echo "Required variables:"
    echo "  SALESFORCE_USERNAME=your_username@company.com"
    echo "  SALESFORCE_PASSWORD=your_password" 
    echo "  SALESFORCE_SECURITY_TOKEN=your_security_token"
    echo "  JIRA_HOST=https://your-company.atlassian.net"
    echo "  JIRA_USERNAME=your_username@company.com"
    echo "  JIRA_API_TOKEN=your_api_token"
    echo "  ANTHROPIC_API_KEY=sk-ant-..."
    exit 1
fi

# Check for virtual environment
if [ ! -d ".venv-mcp" ]; then
    echo "❌ Virtual environment not found. Please set it up first:"
    echo ""
    echo "1. Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "2. Install Python 3.12: uv python install 3.12"
    echo "3. Create venv: uv venv --python 3.12 .venv-mcp"
    echo "4. Install deps: source .venv-mcp/bin/activate && uv pip install mcp strands-agents strands-agents-tools simple-salesforce jira anthropic fastapi uvicorn python-dotenv aiohttp"
    echo ""
    echo "Or run: python tests/test_mcp_setup.py to verify setup"
    exit 1
fi

# Activate virtual environment
echo "🐍 Activating Python 3.12 virtual environment..."
source .venv-mcp/bin/activate

# Verify Python version
PYTHON_VERSION=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if [[ "$PYTHON_VERSION" < "3.10" ]]; then
    echo "❌ Python 3.10+ required, but found Python $PYTHON_VERSION"
    echo "Please ensure .venv-mcp uses Python 3.12+"
    exit 1
fi

echo "✅ Using Python $PYTHON_VERSION from virtual environment"

# Run setup test
echo "🔍 Running setup verification..."
if ! python tests/test_mcp_setup.py; then
    echo "❌ Setup test failed. Please check your environment."
    exit 1
fi

# Install React dependencies
echo "📦 Installing React dependencies..."
cd react-ui
if [ ! -d "node_modules" ]; then
    if command -v npm &> /dev/null; then
        npm install
    else
        echo "❌ npm not found. Please install Node.js first."
        exit 1
    fi
fi
cd ..

# Create logs directory
mkdir -p python_servers/logs

# Function to check if port is in use
check_port() {
    if lsof -i :$1 &> /dev/null; then
        echo "⚠️  Port $1 is in use. Attempting to free it..."
        lsof -ti :$1 | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# Check and free ports
check_port 8000
check_port 8001  
check_port 8002
check_port 3000

echo "🏥 Starting services..."

# Start Salesforce MCP server
echo "  🔗 Starting Salesforce MCP server (port 8001)..."
cd python_servers
MCP_SERVER_PORT=8001 MCP_SERVER_HOST=localhost python salesforce_server_mcp.py > logs/salesforce.log 2>&1 &
SALESFORCE_PID=$!
echo "    PID: $SALESFORCE_PID"
cd ..

# Wait a moment
sleep 2

# Start Jira MCP server  
echo "  🎫 Starting Jira MCP server (port 8002)..."
cd python_servers
MCP_SERVER_PORT=8002 MCP_SERVER_HOST=localhost python jira_server_mcp.py > logs/jira.log 2>&1 &
JIRA_PID=$!
echo "    PID: $JIRA_PID"
cd ..

# Wait for MCP servers to start
sleep 3

# Start Web server with Strands SDK
echo "  🖥️  Starting MCP web server with Strands SDK (port 8000)..."
cd python_servers
MCP_SALESFORCE_URL=http://localhost:8001 MCP_JIRA_URL=http://localhost:8002 python mcp_web_server.py > logs/web_server.log 2>&1 &
WEB_PID=$!
echo "    PID: $WEB_PID"
cd ..

# Wait for web server to start
sleep 3

# Start React UI
echo "  ⚛️  Starting React UI (port 3000)..."
cd react-ui
REACT_APP_API_URL=http://localhost:8000 npm start > ../python_servers/logs/react.log 2>&1 &
REACT_PID=$!
echo "    PID: $REACT_PID"
cd ..

# Wait for everything to start
echo ""
echo "⏳ Waiting for services to initialize..."
sleep 5

# Test health endpoints
echo "🏥 Checking service health..."

if curl -s http://localhost:8001/health &> /dev/null; then
    echo "  ✅ Salesforce MCP: $(curl -s http://localhost:8001/health | grep -o '"status":"[^"]*"' || echo 'Running')"
else
    echo "  ❌ Salesforce MCP: Not responding"
fi

if curl -s http://localhost:8002/health &> /dev/null; then
    echo "  ✅ Jira MCP: $(curl -s http://localhost:8002/health | grep -o '"status":"[^"]*"' || echo 'Running')"
else
    echo "  ❌ Jira MCP: Not responding"
fi

if curl -s http://localhost:8000/api/health &> /dev/null; then
    echo "  ✅ Web Server: $(curl -s http://localhost:8000/api/health | grep -o '"status":"[^"]*"' || echo 'Running')"
else
    echo "  ❌ Web Server: Not responding"
fi

if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "200"; then
    echo "  ✅ React UI: Ready"
else
    echo "  ⚠️  React UI: Still starting (this is normal)"
fi

echo ""
echo "🎉 MCP Integration with Python 3.12 is now running!"
echo "===================================================="
echo "🌐 Frontend:     http://localhost:3000"
echo "🔧 Backend API:  http://localhost:8000"
echo "📊 Health:       http://localhost:8000/api/health"
echo "🔗 Salesforce:   http://localhost:8001/health"
echo "🎫 Jira:         http://localhost:8002/health"
echo ""
echo "✅ Native Services Active:"
echo "  ✅ React UI (port 3000)"
echo "  ✅ MCP Web Server + Strands SDK (port 8000)"
echo "  ✅ Salesforce MCP Server (port 8001)"
echo "  ✅ Jira MCP Server (port 8002)"
echo ""
echo "🚀 Features:"
echo "  ✅ Python 3.12+ with proper MCP library"
echo "  ✅ Strands SDK with telemetry"
echo "  ✅ JSON-RPC MCP communication"
echo "  ✅ Anthropic Claude AI integration"
echo "  ✅ Real-time data from Salesforce & Jira"
echo ""
echo "📂 Logs located in: python_servers/logs/"
echo "   - salesforce.log"
echo "   - jira.log"
echo "   - web_server.log"
echo "   - react.log"
echo ""
echo "🔍 Troubleshooting:"
echo "   tail -f python_servers/logs/web_server.log"
echo ""
echo "Press Ctrl+C to stop all services"

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Stopping all services..."
    
    # Kill all processes
    kill $SALESFORCE_PID $JIRA_PID $WEB_PID $REACT_PID 2>/dev/null || true
    
    # Also kill any remaining processes on our ports
    lsof -ti :8000 | xargs kill -9 2>/dev/null || true
    lsof -ti :8001 | xargs kill -9 2>/dev/null || true  
    lsof -ti :8002 | xargs kill -9 2>/dev/null || true
    lsof -ti :3000 | xargs kill -9 2>/dev/null || true
    
    echo "✅ All services stopped"
    exit 0
}

trap cleanup INT TERM

# Wait for user to stop
wait