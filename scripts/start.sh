#!/bin/bash

# MCP Integration Docker Startup Script
# This launches the entire MCP system using Docker containers

set -e

echo "🚀 Starting MCP Integration with Docker & Strands SDK"
echo "======================================================"

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create it with your Salesforce and Jira credentials."
    echo "Required variables:"
    echo "  SALESFORCE_LOGIN_URL=https://your-instance.salesforce.com"
    echo "  SALESFORCE_CLIENT_ID=your_client_id"
    echo "  SALESFORCE_CLIENT_SECRET=your_client_secret"
    echo "  SALESFORCE_USERNAME=your_username"
    echo "  SALESFORCE_PASSWORD=your_password"
    echo "  JIRA_SERVER_URL=https://your-company.atlassian.net"
    echo "  JIRA_USERNAME=your_username"
    echo "  JIRA_API_TOKEN=your_api_token"
    echo "  ANTHROPIC_API_KEY=your_anthropic_api_key"
    exit 1
fi

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "⚠️  Docker is not installed."
    echo ""
    echo "🔄 Falling back to native mode..."
    echo "   This will run all services directly on your Mac"
    echo ""
    exec ./start_native.sh
fi

# Check for docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo "⚠️  docker-compose is not installed."
    echo ""
    echo "🔄 Falling back to native mode..."
    echo "   This will run all services directly on your Mac"
    echo ""
    exec ./start_native.sh
fi

# Create logs directory
mkdir -p python_servers/logs

echo "🐳 Building Docker containers..."
docker-compose build

echo "🚀 Starting MCP Integration services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🏥 Checking service health..."
echo "Web Server: $(curl -s http://localhost:8000/api/health | grep -o '"status":"[^"]*"' || echo 'Not ready')"
echo "Salesforce: $(curl -s http://localhost:8001/health | grep -o '"status":"[^"]*"' || echo 'Not ready')"
echo "Jira:       $(curl -s http://localhost:8002/health | grep -o '"status":"[^"]*"' || echo 'Not ready')"

echo ""
echo "🎉 MCP Integration with Docker is now running!"
echo "=============================================="
echo "🌐 Frontend:     http://localhost:3000"
echo "🔧 Backend API:  http://localhost:8000"
echo "📊 Health:       http://localhost:8000/api/health"
echo "📈 Metrics:      http://localhost:8000/api/metrics"
echo "🔗 Salesforce:   http://localhost:8001/health"
echo "🎫 Jira:         http://localhost:8002/health"
echo ""
echo "🐳 Docker Services Active:"
echo "  ✅ mcp-ui (React development server)"
echo "  ✅ mcp-web-server (FastAPI + Strands SDK)"
echo "  ✅ mcp-salesforce (Salesforce MCP server)"
echo "  ✅ mcp-jira (Jira MCP server)"
echo ""
echo "🚀 Features:"
echo "  ✅ HTTP-based MCP communication"
echo "  ✅ Real Strands Agent or Anthropic API"
echo "  ✅ OpenTelemetry Tracing"
echo "  ✅ Performance Metrics Collection"
echo "  ✅ Enhanced Error Handling with Retry"
echo "  ✅ Health Score Monitoring"
echo "  ✅ Docker containerization"
echo ""
echo "💡 This connects to your real Salesforce and Jira data via containerized MCP servers"
echo "🔒 Your credentials are loaded from .env file"
echo "🤖 Enhanced AI chat with production-grade observability"
echo "🧠 Ask complex questions about your data relationships"
echo ""
echo "📋 Management Commands:"
echo "  View logs:     docker-compose logs -f"
echo "  Stop services: docker-compose down"
echo "  Restart:       docker-compose restart"
echo ""
echo "Press Ctrl+C to stop all services"

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Stopping Docker services..."
    docker-compose down
    echo "✅ MCP Integration stopped"
    exit 0
}

trap cleanup INT TERM

# Wait for user to stop
wait