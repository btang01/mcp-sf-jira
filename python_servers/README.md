# MCP Servers - Python Implementation

Modern MCP servers for Salesforce and Jira integration using `@mcp.tool` decorators.

## Core Files

### `salesforce_server_modern.py`
- **11 MCP Tools** with `@mcp.tool` decorators
- **OAuth2 Authentication** with Salesforce
- **SOQL Query Support** for flexible data retrieval
- **CRUD Operations** for all Salesforce objects
- **Bulk Operations** for efficient data processing

### `jira_server_modern.py`
- **10 MCP Tools** with `@mcp.tool` decorators
- **REST API Integration** with Jira
- **JQL Search Support** for flexible querying
- **Issue Management** (create, update, transition, assign)
- **Attachment and Linking** capabilities

### `mcp_web_server.py`
- **FastAPI Web Server** with Claude AI integration
- **MCP Protocol Handler** for subprocess communication
- **21 Tool Integration** from both servers
- **Chat API** for natural language queries

## Installation

```bash
# Install dependencies using uv (recommended)
uv pip install -r pyproject.toml

# Or use the install script
./install.sh
```

## Running Individual Servers

### Salesforce Server
```bash
uv run python salesforce_server_modern.py
```

### Jira Server
```bash
uv run python jira_server_modern.py
```

### Web Server
```bash
uv run python mcp_web_server.py
```

## Environment Variables

Required in `.env` file:
```bash
# Salesforce
SALESFORCE_USERNAME=your_username
SALESFORCE_PASSWORD=your_password
SALESFORCE_CLIENT_ID=your_client_id
SALESFORCE_CLIENT_SECRET=your_client_secret
SALESFORCE_SECURITY_TOKEN=your_security_token

# Jira
JIRA_HOST=https://your-company.atlassian.net
JIRA_USERNAME=your_username
JIRA_API_TOKEN=your_api_token

# Anthropic (for AI chat)
ANTHROPIC_API_KEY=your_anthropic_api_key
```

## API Endpoints

### Web Server Endpoints
- `POST /api/chat` - AI chat with Claude + MCP tools
- `POST /api/call-tool` - Direct tool invocation
- `GET /api/status/{service}` - Connection status
- `GET /api/health` - Health check

## Architecture

```
mcp_web_server.py (FastAPI + Claude)
    ↓ subprocess communication
salesforce_server_modern.py (MCP Server)
jira_server_modern.py (MCP Server)
    ↓ API calls
Salesforce API / Jira API
```