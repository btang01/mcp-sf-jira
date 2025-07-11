# MCP Demo Project

A comprehensive demonstration of Model Context Protocol (MCP) integration with Salesforce and Jira, featuring Docker optimization, query validation, and organized project structure.

## 📁 Project Structure

```
mcpdemo/
├── 📂 config/           # Configuration files
│   └── .env            # Environment variables
├── 📂 docker/          # Docker configuration
│   ├── docker-compose.yml
│   ├── Dockerfile.mcp-server
│   ├── Dockerfile.ui
│   ├── Dockerfile.web-server
│   └── .dockerignore
├── 📂 docs/            # Documentation
│   ├── README.md
│   ├── SETUP.md
│   ├── TESTING.md
│   ├── CUSTOM_FIELDS_INTEGRATION.md
│   ├── DOCKER_OPTIMIZATION.md
│   ├── QUERY_PROMPT_TEMPLATES.md
│   └── QUICK_QUERY_REFERENCE.md
├── 📂 scripts/         # Build and utility scripts
│   ├── docker-build.sh
│   ├── start.sh
│   ├── start_native.sh
│   ├── create_demo_data.sh
│   ├── demo_data_generator.py
│   └── demo_data_generator_simple.py
├── 📂 python_servers/  # MCP server implementations
│   ├── mcp_web_server.py
│   ├── salesforce_server_mcp.py
│   ├── jira_server_mcp.py
│   └── requirements.txt
├── 📂 react-ui/        # React frontend
│   ├── src/
│   ├── public/
│   └── package.json
└── 📂 tests/           # Test files
    └── ...
```

## 🚀 Quick Start

### Quick Start
```bash
# From project root
cd docker
docker-compose up
```

### Using Build Scripts
```bash
# From project root
./scripts/docker-build.sh dev      # Build development images
./scripts/docker-build.sh clean    # Clean up Docker resources
./scripts/docker-build.sh rebuild  # Force rebuild without cache
```

## 🔧 Configuration

- **Environment Variables**: `config/.env`
- **Docker Compose**: `docker/docker-compose.yml`
- **Build Scripts**: `scripts/docker-build.sh`

## 📖 Documentation

- **Setup Guide**: `docs/SETUP.md`
- **Docker Optimization**: `docs/DOCKER_OPTIMIZATION.md`
- **Query Templates**: `docs/QUERY_PROMPT_TEMPLATES.md`
- **Quick Reference**: `docs/QUICK_QUERY_REFERENCE.md`
- **Testing Guide**: `docs/TESTING.md`

## 🛠️ Key Features

- **MCP Integration**: Salesforce and Jira connectivity with HTTP-based communication
- **Strands SDK v0.2.1**: Advanced AI agent orchestration with memory and telemetry
- **Query Validation**: Built-in SOQL and JQL validation with error handling
- **Docker Optimization**: Multi-stage builds with layer caching and Strands SDK support
- **Agent Memory**: Persistent entity caching and session context management
- **React UI**: Modern web interface with real-time status updates
- **Dual Environment**: Both containerized and native development support
- **Organized Structure**: Clean, maintainable project layout

## 🔗 Access Points

- **React UI**: http://localhost:3000
- **API Server**: http://localhost:8000
- **Health Check**: http://localhost:8000/api/health

## 📝 Recent Improvements

- ✅ **Project Organization**: Files organized into logical folders
- ✅ **Docker Optimization**: Faster builds with better caching
- ✅ **Query Validation**: Automatic SOQL/JQL error prevention
- ✅ **Documentation**: Comprehensive guides and references
- ✅ **Build Scripts**: Streamlined Docker management

For detailed setup and usage instructions, see the documentation in the `docs/` folder.
