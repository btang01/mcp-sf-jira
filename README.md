# 🤖 **MCP Demo System**

AI-powered business intelligence that connects **Salesforce** and **Jira** for intelligent cross-system insights and automation.

---

## 🎯 **What It Does**

- **Ask natural language questions** about your business data
- **Get AI-powered insights** across Salesforce and Jira
- **Automate workflows** between systems
- **Create cross-system reports** and analysis

### **Example Queries**
- *"Show me high-priority opportunities that are at risk"*
- *"Which customers have both large deals and open support cases?"*
- *"Create a Jira issue for this Salesforce case"*
- *"What's the status of our biggest implementation projects?"*

---

## 🚀 **Quick Start**

### **1. Prerequisites**
- Docker Desktop
- Salesforce account (Developer Edition works)
- Jira Cloud account  
- Anthropic API key

### **2. Setup**
```bash
# 1. Clone the repository
git clone https://github.com/btang01/mcp-sf-jira.git
cd mcp-sf-jira

# 2. Configure credentials (see SETUP.md for details)
cp config/.env.example config/.env
# Edit config/.env with your credentials

# 3. Start the system
cd docker
docker-compose up -d
```

### **3. Access**
- **Web Interface**: http://localhost:3000
- **API Health**: http://localhost:8000/api/health

---

## 📚 **Documentation**

- **[SETUP.md](docs/SETUP.md)** - Complete setup instructions
- **[USAGE.md](docs/USAGE.md)** - How to use the system
- **[ERROR_FIXES_SUMMARY.md](docs/ERROR_FIXES_SUMMARY.md)** - Troubleshooting guide

---

## 🏗️ **Architecture**

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

### **Key Features**
- ✅ **MCP Protocol** for tool integration
- ✅ **Anthropic Claude** for AI processing
- ✅ **Docker containerization** for easy deployment
- ✅ **Cross-platform** (Windows, macOS, Linux)
- ✅ **Real-time streaming** responses
- ✅ **Comprehensive error handling**

---

## 🛠️ **Technology Stack**

- **Backend**: Python 3.12, FastAPI, MCP Protocol
- **Frontend**: React, Tailwind CSS
- **AI**: Anthropic Claude 3.5 Sonnet
- **Integrations**: Salesforce REST API, Jira REST API
- **Deployment**: Docker, Docker Compose

---

## 🎉 **What You Can Build**

### **Business Intelligence**
- Sales pipeline analysis
- Customer health scoring
- Implementation project tracking
- Support case correlation

### **Automation Workflows**
- Auto-create Jira issues from Salesforce cases
- Link opportunities to implementation projects
- Sync customer data between systems
- Generate cross-system reports

### **AI-Powered Insights**
- Identify at-risk customers
- Predict project delays
- Recommend next actions
- Analyze business patterns

---

## 🚀 **Getting Started**

1. **Read [SETUP.md](docs/SETUP.md)** for detailed setup instructions
2. **Follow the Quick Start** above to get running
3. **Check [USAGE.md](docs/USAGE.md)** for examples and best practices
4. **Start asking questions** in the web interface!

---

## 📊 **System Status**

Once running, check system health:
```bash
curl http://localhost:8000/api/health
```

Expected response:
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

## 🤝 **Contributing**

This is a demo system showcasing MCP protocol integration. Feel free to:
- Fork and extend functionality
- Add new integrations
- Improve the UI/UX
- Share your use cases

---

## 📄 **License**

MIT License - see LICENSE file for details.

---

**Ready to transform your business intelligence with AI? Get started with the setup guide!** 🚀
