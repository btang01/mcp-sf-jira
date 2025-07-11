# MCP Integration - Salesforce & Jira

Modern Model Context Protocol (MCP) integration with Salesforce and Jira using Python 3.12+, proper MCP library, and **Strands SDK v0.2.1**.

**🚀 POWERED BY: Strands SDK v0.2.1 with advanced agent orchestration, memory management, and production-grade telemetry!**

## Architecture

```
React UI (3000) 
    ↓ HTTP /api/chat
mcp_web_server.py (8000) + Claude AI + Strands SDK
    ↓ JSON-RPC MCP Protocol
salesforce_server_mcp.py ← → Salesforce REST API
jira_server_mcp.py ← → Jira REST API
```

## Features

### Core Features
- **🧠 AI Chat Assistant**: Claude-powered natural language queries
- **⚡ Real-time Data**: Live Salesforce and Jira integration
- **🔧 8 MCP Tools**: Salesforce and Jira operations with proper MCP protocol
- **🎯 Modern Architecture**: Python 3.12+ with proper MCP library support

### Strands SDK Integration
- **🚀 Connection Management**: Auto-retry with exponential backoff
- **📊 Performance Metrics**: Real-time monitoring and analytics  
- **🔍 Health Monitoring**: Detailed service health checks
- **🛡️ Enhanced Error Handling**: Structured errors with retry hints
- **📈 OpenTelemetry Tracing**: Production-grade observability
- **🔄 Circuit Breakers**: Prevents cascade failures

### Advanced Memory & Intelligence
- **🧠 Persistent Memory**: Entity and conversation memory that survives server restarts
- **💾 File-Based Persistence**: Automatic caching to `logs/entity_cache.json` and `logs/session_context.json`
- **🔗 Cross-System Intelligence**: Links Salesforce opportunities to Jira issues for root cause analysis
- **🎯 Context-Aware Responses**: Agent remembers previous conversations and discovered entities
- **⚡ Smart Error Recovery**: Multiple retry strategies with intelligent error parsing
- **🏃 Proactive Activity Creation**: Agent suggests and creates activities with rich technical context

## Quick Start

### Prerequisites

**Python 3.12+ Required**: The MCP library requires Python 3.10 or higher. We recommend Python 3.12+.

**Install Python 3.12 with uv**:
```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Python 3.12
uv python install 3.12

# Create virtual environment
uv venv --python 3.12 .venv-mcp

# Activate virtual environment
source .venv-mcp/bin/activate
```

### Setup

1. **Install Dependencies**:
```bash
# With virtual environment activated
cd python_servers
uv pip install -r requirements.txt

# Or install manually:
# uv pip install mcp strands-sdk tenacity simple-salesforce jira anthropic fastapi uvicorn python-dotenv aiohttp
```

2. **Configure credentials** in `.env`:
```bash
# Salesforce (simplified authentication)
SALESFORCE_USERNAME=your_username
SALESFORCE_PASSWORD=your_password
SALESFORCE_SECURITY_TOKEN=your_security_token

# Jira
JIRA_HOST=https://your-company.atlassian.net
JIRA_USERNAME=your_username
JIRA_API_TOKEN=your_api_token

# Anthropic
ANTHROPIC_API_KEY=your_anthropic_api_key
```

3. **Test the setup**:
```bash
# Run comprehensive test
python tests/test_mcp_setup.py

# Or run all tests
python tests/run_tests.py

# Quick health check
python tests/run_tests.py --quick
```

4. **Start the application**:
```bash
# Native mode (with virtual environment activated)
./start.sh

# OR Docker mode (if Docker available)
docker-compose up
```

5. **Open browser**: http://localhost:3000

## Docker Development

The application is fully containerized for consistent development and easy deployment.

### Architecture
```
Docker Network: mcp-network
├── mcp-ui:3000 (React development server)
├── mcp-web-server:8000 (FastAPI + Strands SDK + Python 3.12)
├── mcp-salesforce:8001 (Salesforce MCP server + Python 3.12)
└── mcp-jira:8002 (Jira MCP server + Python 3.12)
```

### Key Benefits
- **Consistent Environment**: Same setup across all development machines
- **Isolated Services**: Each component runs in its own container
- **Hot Reload**: React and Python code changes reflected immediately
- **Easy Debugging**: Individual service logs and health checks
- **Production Ready**: Same containers can be deployed to AWS ECS

### Manual Docker Commands
```bash
# Build containers
docker-compose build

# Start services in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart specific service
docker-compose restart mcp-web-server
```

### Service URLs
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000/api/health
- **Salesforce MCP**: http://localhost:8001/health
- **Jira MCP**: http://localhost:8002/health

## Available Tools

### Salesforce (5 tools)
- `salesforce_query` - Execute SOQL queries
- `salesforce_create` - Create new records
- `salesforce_query_accounts` - Query accounts with common fields
- `salesforce_query_contacts` - Query contacts with common fields
- `salesforce_connection_info` - Get connection status and details

### Jira (3 tools)
- `jira_search_issues` - Search issues with JQL
- `jira_get_issue` - Get detailed issue information
- `jira_create_issue` - Create new issues

## Memory & Intelligence Features

### 🧠 Persistent Memory System
The agent maintains memory across conversations and server restarts:

- **Entity Memory**: Remembers Salesforce opportunities, cases, accounts, and Jira issues
- **Conversation Memory**: Maintains context from previous chat interactions
- **Cross-System Links**: Connects Salesforce cases to Jira issues via custom fields
- **File Persistence**: Memory stored in `logs/entity_cache.json` and `logs/session_context.json`

### 🎯 Context-Aware Conversations
```
User: "Find at-risk opportunities"
Agent: [Queries and caches opportunity data]

User: "Create an activity for the opportunity"  
Agent: [Uses cached context - no need to ask which opportunity!]
```

### ⚡ Smart Error Recovery
The agent tries multiple approaches when tools fail:
- Parses error messages to understand what went wrong
- Uses cached data to fill missing parameters
- Tries alternative query approaches
- Suggests fixes for common issues

### 🔗 Root Cause Analysis
Links technical problems to business impact:
- Follows Jira Issue Keys from Salesforce cases
- Analyzes technical details from Jira issues
- Explains how technical problems affect business
- Provides actionable insights and next steps

## Example Queries

```
"Show me all accounts in Salesforce"
"Create a new contact for Burlington Textiles"
"What opportunities are in negotiation stage?"
"Create a Jira ticket for the highest value deal"
"Find all high-priority cases and their contacts"
"Update the stage of opportunity X to Closed Won"

# Memory-powered queries:
"Create an activity for that opportunity we discussed"
"What's the status of the Jira issue linked to this case?"
"Show me technical details for the at-risk opportunities"
```

## Project Structure

```
mcp-integration/
├── python_servers/
│   ├── salesforce_server_mcp.py     # Salesforce MCP server (Python 3.12)
│   ├── jira_server_mcp.py           # Jira MCP server (Python 3.12)
│   ├── mcp_web_server.py            # Web server + Claude AI + Strands SDK
│   ├── archive/                     # Legacy servers (archived)
│   └── test_mcp_setup.py            # Comprehensive test suite
├── react-ui/                        # React frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── AssistantChat.js     # AI chat interface
│   │   │   ├── Dashboard.js         # Main dashboard
│   │   │   ├── SalesforcePanel.js   # Salesforce data panel
│   │   │   └── JiraPanel.js         # Jira data panel
│   │   └── hooks/
│   │       └── useApi.js            # API hooks
│   └── package.json
├── Dockerfile.web-server            # Web server container
├── Dockerfile.mcp-server            # MCP server base container
├── Dockerfile.ui                    # React UI container
├── docker-compose.yml               # Local development orchestration
├── .dockerignore                    # Docker ignore file
├── .env                             # Environment variables
├── .venv-mcp/                       # Python 3.12 virtual environment
├── tests/                           # Test suite
│   ├── test_mcp_setup.py           # Setup verification script
│   ├── test_imports.py             # Import and version tests
│   ├── test_servers.py             # Server functionality tests
│   └── run_tests.py                # Test runner
└── start.sh                         # Startup script
```

## Prerequisites

### Development Setup Options

#### Option 1: Native Development (Recommended)
- **Python 3.12+** - Required for MCP library support
- **uv** - Fast Python package manager ([install guide](https://docs.astral.sh/uv/getting-started/installation/))
- **Git** - [Download from git-scm.com](https://git-scm.com/)
- **Node.js 18+** - For React UI development

#### Option 2: Docker Development
- **Docker** - [Download from docker.com](https://docs.docker.com/get-docker/)
- **Docker Compose** - [Install guide](https://docs.docker.com/compose/install/)
- **Git** - [Download from git-scm.com](https://git-scm.com/)

### Auto-Handled
- **Python 3.12** - Installed via uv or included in Docker containers
- **MCP Library** - Installed via uv pip or Docker build
- **Strands SDK** - Installed via uv pip or Docker build
- **All dependencies** - Managed by uv or Docker

### Required Credentials
- **Anthropic API key** - [Get from console.anthropic.com](https://console.anthropic.com/)
- **Salesforce credentials** - Username, password, security token from your Salesforce org
- **Jira API token** - From your Atlassian account settings

### Verification
Run the comprehensive test suite to verify your setup:
```bash
# With virtual environment activated
python tests/test_mcp_setup.py

# Or run full test suite
python tests/run_tests.py

# Quick health check only
python tests/run_tests.py --quick
```

This will test:
- ✅ Python 3.12+ compatibility
- ✅ MCP library import
- ✅ Strands SDK integration
- ✅ Service connections
- ✅ HTTP server functionality

## AWS ECS Deployment Path

The Docker containerization makes AWS ECS deployment straightforward. Here's what changes for cloud deployment:

### Current Docker Setup → ECS Migration

| Component | Local Docker | AWS ECS |
|-----------|-------------|---------|
| **Containers** | docker-compose.yml | ECS Task Definitions |
| **Networking** | Docker bridge network | VPC with private/public subnets |
| **Load Balancing** | Direct port access | Application Load Balancer |
| **Service Discovery** | Container names | AWS Cloud Map |
| **Secrets** | .env file | AWS Secrets Manager |
| **Logs** | Docker logs | CloudWatch Logs |
| **Scaling** | Manual | Auto Scaling based on metrics |

### Required AWS Services

1. **Amazon ECR** - Container registry for Docker images
2. **Amazon ECS** - Container orchestration (Fargate recommended)
3. **Application Load Balancer** - Routes traffic to UI and API
4. **AWS Secrets Manager** - Secure credential storage
5. **VPC** - Private networking for MCP servers
6. **CloudWatch** - Logging and monitoring

### ECS Architecture
```
Internet Gateway
    ↓
Application Load Balancer (Public Subnets)
    ↓
┌─────────────────────────────────────────────────┐
│ VPC - Private Subnets                           │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │ mcp-ui      │ │ mcp-web     │ │ mcp-servers │ │
│ │ ECS Service │ │ ECS Service │ │ ECS Service │ │
│ │ :3000       │ │ :8000       │ │ :8001,8002  │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────┘
```

### Migration Steps

1. **Push to ECR**:
   ```bash
   # Build and tag images
   docker build -f Dockerfile.web-server -t mcp-web-server .
   docker build -f Dockerfile.ui -t mcp-ui .
   docker build -f Dockerfile.mcp-server -t mcp-server .
   
   # Push to ECR
   docker tag mcp-web-server:latest 123456789.dkr.ecr.region.amazonaws.com/mcp-web-server:latest
   docker push 123456789.dkr.ecr.region.amazonaws.com/mcp-web-server:latest
   ```

2. **Create ECS Cluster**:
   ```bash
   # Using AWS Copilot (simplest)
   copilot app init mcp-integration
   copilot env init --name production
   
   # Or use AWS CLI/Console/CDK/Terraform
   ```

3. **Environment Changes**:
   - Replace `.env` file with AWS Secrets Manager
   - Update container URLs to use AWS service discovery
   - Configure ALB target groups for UI and API

### Key Configuration Changes

**Environment Variables** (Task Definition):
```json
{
  "environment": [
    {"name": "MCP_SALESFORCE_URL", "value": "http://mcp-salesforce.mcp-integration.local:8001"},
    {"name": "MCP_JIRA_URL", "value": "http://mcp-jira.mcp-integration.local:8002"}
  ],
  "secrets": [
    {"name": "ANTHROPIC_API_KEY", "valueFrom": "arn:aws:secretsmanager:..."},
    {"name": "SALESFORCE_CLIENT_SECRET", "valueFrom": "arn:aws:secretsmanager:..."}
  ]
}
```

**Health Checks** (Load Balancer):
- **UI**: `GET /` (React app)
- **API**: `GET /api/health` (FastAPI health endpoint)
- **MCP Servers**: `GET /health` (HTTP health endpoints)

### Cost Considerations

**Fargate Pricing** (approximate):
- **mcp-ui**: 0.25 vCPU, 0.5 GB RAM → ~$11/month
- **mcp-web-server**: 0.5 vCPU, 1 GB RAM → ~$22/month  
- **mcp-salesforce**: 0.25 vCPU, 0.5 GB RAM → ~$11/month
- **mcp-jira**: 0.25 vCPU, 0.5 GB RAM → ~$11/month
- **ALB**: ~$22/month
- **Total**: ~$77/month for basic setup

**Auto Scaling**: Services can scale down to 0 during off-hours to reduce costs.

### Quick Deploy with AWS Copilot

```bash
# Initialize
copilot app init mcp-integration
copilot env init --name production

# Deploy services
copilot svc init --name ui --svc-type "Load Balanced Web Service"
copilot svc init --name web-server --svc-type "Load Balanced Web Service"  
copilot svc init --name salesforce --svc-type "Worker Service"
copilot svc init --name jira --svc-type "Worker Service"

# Deploy
copilot svc deploy --name ui --env production
copilot svc deploy --name web-server --env production
copilot svc deploy --name salesforce --env production
copilot svc deploy --name jira --env production
```

The Docker foundation makes this migration smooth - the same containers that run locally will run in AWS ECS with minimal configuration changes.
