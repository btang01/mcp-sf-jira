# MCP Servers - Python Implementation

Modern MCP servers for Salesforce and Jira integration with enhanced features and production-ready capabilities.

---

## 🏗️ Architecture

```
mcp_web_server.py (FastAPI + Claude AI)
    ↓ subprocess communication
salesforce_server_mcp.py (MCP Server)
jira_server_mcp.py (MCP Server)
    ↓ API calls
Salesforce API / Jira API
```

---

## 🚀 Core Components

### **`mcp_web_server.py`** - Main Web Server
- **FastAPI Web Server** with Claude AI integration
- **MCP Protocol Handler** for subprocess communication
- **21 Tool Integration** from both servers
- **Chat API** for natural language queries
- **Enhanced error handling** and monitoring

### **`salesforce_server_mcp.py`** - Salesforce Integration
- **11 MCP Tools** with `@mcp.tool` decorators
- **OAuth2 Authentication** with Salesforce
- **SOQL Query Support** for flexible data retrieval
- **CRUD Operations** for all Salesforce objects
- **Standard field compatibility** (no custom fields required)

### **`jira_server_mcp.py`** - Jira Integration
- **10 MCP Tools** with `@mcp.tool` decorators
- **REST API Integration** with Jira Cloud
- **JQL Search Support** for flexible querying
- **Issue Management** (create, update, transition, assign)
- **Project and attachment management**

---

## 🛠️ Development Setup

### Prerequisites
- Python 3.12+
- uv package manager (recommended)

### Quick Setup
```bash
# Install uv (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv pip install -r requirements.txt

# Or use the install script
./install.sh
```

### Environment Configuration
Create `.env` file with:
```bash
# Salesforce
SALESFORCE_USERNAME=your_username
SALESFORCE_PASSWORD=your_password
SALESFORCE_SECURITY_TOKEN=your_security_token

# Jira
JIRA_HOST=https://your-company.atlassian.net
JIRA_USERNAME=your_username
JIRA_API_TOKEN=your_api_token

# Anthropic (for AI chat)
ANTHROPIC_API_KEY=your_anthropic_api_key
```

---

## 🚀 Running the Servers

### All-in-One (Recommended)
```bash
# Start the main web server (includes MCP servers)
uv run python mcp_web_server.py

# Or use the Makefile
make run-backend
```

### Individual Servers (Development)
```bash
# Salesforce server only
uv run python salesforce_server_mcp.py

# Jira server only
uv run python jira_server_mcp.py
```

---

## 🔧 Enhanced Features

### **Connection Management & Resilience**
- **Auto-retry logic** with exponential backoff
- **Circuit breaker pattern** to prevent cascade failures
- **Connection pooling** for efficient resource usage
- **Health monitoring** with automatic recovery

### **Intelligent Caching**
- **5-minute TTL cache** for frequent queries
- **Cache hit/miss metrics** for optimization
- **Automatic cache invalidation**
- **Redis support** for distributed caching (optional)

### **Performance Monitoring**
- **Request/response metrics** with timing
- **Error rate tracking** per service/tool
- **Circuit breaker state monitoring**
- **Cache performance metrics**

### **Enhanced Error Handling**
- **Structured error responses** with context
- **Retry hints** for recoverable errors
- **Failure escalation** with proper logging
- **Graceful degradation** under load

---

## 📊 API Endpoints

### Web Server Endpoints
- `POST /api/chat` - AI chat with Claude + MCP tools
- `POST /api/call-tool` - Direct tool invocation
- `GET /api/status/{service}` - Connection status
- `GET /api/health` - Comprehensive health check
- `GET /api/metrics` - Performance metrics
- `POST /api/cache/clear` - Cache management

### Health Check Response
```json
{
  "status": "healthy",
  "connections": {
    "salesforce": {"connected": true},
    "jira": {"connected": true}
  },
  "available_tools": 21,
  "anthropic_enabled": true,
  "cache_stats": {
    "hits": 150,
    "misses": 25,
    "hit_rate": 0.857
  }
}
```

---

## 🔧 Development Tools

### Using uv (Recommended)
```bash
# Install new dependencies
uv pip install package-name

# Run with specific Python version
uv run --python 3.12 python mcp_web_server.py

# Create virtual environment
uv venv --python 3.12
```

### Development Commands
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

---

## 🚨 Troubleshooting

### Common Issues

#### **uv not found**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH if needed
export PATH="$HOME/.local/bin:$PATH"
```

#### **Connection Issues**
- Check credentials in `.env` file
- Verify API endpoints are accessible
- Review firewall and network settings

#### **Performance Issues**
- Monitor metrics at `/api/metrics`
- Check cache hit rates
- Review circuit breaker states

#### **High Error Rates**
- Check circuit breaker states in `/api/health`
- Review retry configuration
- Monitor service health

---

## 🎯 Why uv?

- **Fast**: 10-100x faster than pip
- **Reliable**: Built-in dependency resolution
- **Simple**: No need for pip-tools or poetry
- **Compatible**: Works with standard Python packaging

---

## 🔮 Future Enhancements

### Planned Features
- **Distributed tracing** with correlation IDs
- **Rate limiting** per client/tool
- **Advanced caching strategies** (write-through, write-back)
- **Prometheus integration** for metrics export
- **WebSocket support** for real-time updates

---

## 📋 Available Tools

### Salesforce Tools (11)
- Query accounts, contacts, opportunities, cases
- Create and update records
- Search with SOSL
- Discover object fields
- Connection health monitoring

### Jira Tools (10)
- Search issues with JQL
- Create and update issues
- Manage projects and issue types
- Add comments and attachments
- Connection health monitoring

**Total: 21 integrated tools** for comprehensive business intelligence and automation.

---

Your production-ready MCP server implementation with enhanced reliability, performance monitoring, and intelligent caching! 🚀
