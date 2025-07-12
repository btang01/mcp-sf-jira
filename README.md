# 🤖 MCP Demo System

AI-powered business intelligence that connects **Salesforce** and **Jira** for intelligent cross-system insights and automation.

---

## 🎯 What It Does

Transform your business data into actionable insights with natural language queries:

- **Ask questions** about your business data across systems
- **Get AI-powered insights** from Salesforce and Jira
- **Automate workflows** between platforms
- **Create cross-system reports** and analysis

### Example Queries
- *"Show me high-priority opportunities that are at risk"*
- *"Which customers have both large deals and open support cases?"*
- *"Create a Jira issue for this Salesforce case"*
- *"What's the status of our biggest implementation projects?"*

---

## 🚀 Quick Start

### Prerequisites
- Docker Desktop
- Salesforce account (Developer Edition works)
- Jira Cloud account  
- Anthropic API key

### Setup & Launch
```bash
# 1. Clone and navigate
git clone https://github.com/btang01/mcp-sf-jira.git
cd mcp-sf-jira

# 2. Configure credentials
cp config/.env.example config/.env
# Edit config/.env with your API keys and credentials

# 3. Start the system
cd docker
docker-compose up -d
```

### Access Points
- **Web Interface**: http://localhost:3000
- **API Health**: http://localhost:8000/api/health

---

## 🏗️ Architecture

```
React UI (Port 3000)
    ↓
FastAPI Web Server (Port 8000)
    ↓
┌─────────────────┬─────────────────┐
│  Salesforce MCP │    Jira MCP     │
│   (Port 8001)   │   (Port 8002)   │
└─────────────────┴─────────────────┘
    ↓                    ↓
Salesforce API      Jira Cloud API
```

### Technology Stack
- **Backend**: Python 3.12, FastAPI, MCP Protocol
- **Frontend**: React, Tailwind CSS
- **AI**: Anthropic Claude 3.5 Sonnet
- **Deployment**: Docker, Docker Compose

---

## 📚 Documentation

- **[Setup Guide](docs/SETUP.md)** - Complete installation and configuration
- **[Usage Guide](docs/USAGE.md)** - How to use the system effectively
- **[Troubleshooting](docs/ERROR_FIXES_SUMMARY.md)** - Common issues and solutions
- **[Custom Fields](docs/SALESFORCE_CUSTOM_FIELDS_SETUP.md)** - Advanced Salesforce integration

---

## 🎉 What You Can Build

### Business Intelligence
- Sales pipeline analysis with risk assessment
- Customer health scoring across systems
- Implementation project tracking
- Support case correlation and trends

### Automation Workflows
- Auto-create Jira issues from Salesforce cases
- Link opportunities to implementation projects
- Sync customer data between systems
- Generate cross-system reports

### AI-Powered Insights
- Identify at-risk customers and deals
- Predict project delays and bottlenecks
- Recommend next actions based on data patterns
- Analyze business trends across platforms

---

## 🚀 Getting Started

1. **Complete the Quick Start** above to get running
2. **Test the connection**: Visit http://localhost:8000/api/health
3. **Start asking questions** in the web interface
4. **Explore the documentation** for advanced features

Expected health check response:
```json
{
  "status": "healthy",
  "connections": {
    "salesforce": {"connected": true},
    "jira": {"connected": true}
  },
  "available_tools": 20,
  "anthropic_enabled": true
}
```

---

## 🤝 Contributing

This demo showcases MCP protocol integration. Feel free to:
- Fork and extend functionality
- Add new integrations
- Improve the UI/UX
- Share your use cases

---

## 📄 License

MIT License - see LICENSE file for details.

---

**Ready to transform your business intelligence with AI?** 🚀
