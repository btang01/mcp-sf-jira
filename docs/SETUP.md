# 🛠️ **MCP Demo System - Complete Setup Guide**

This guide will help you set up your AI-powered business intelligence system that connects Salesforce and Jira.

---

## 🚀 **Quick Start (Docker - Recommended)**

### **Prerequisites**
- Docker Desktop installed
- Salesforce account (Developer Edition is fine)
- Jira Cloud account
- Anthropic API key

### **1. Get Your Credentials**

#### **Salesforce**
1. Go to Salesforce Setup → My Personal Information → Reset My Security Token
2. Note your username, password, and security token

#### **Jira**
1. Go to Atlassian Account Settings → Security → API tokens
2. Create a new API token
3. Note your Jira URL (e.g., `https://yourcompany.atlassian.net`)

#### **Anthropic**
1. Go to https://console.anthropic.com/
2. Create an API key

### **2. Configure Environment**

Create `config/.env` file:
```bash
# Anthropic API
ANTHROPIC_API_KEY=sk-ant-your_key_here

# Salesforce Configuration
SALESFORCE_USERNAME=your_username@company.com
SALESFORCE_PASSWORD=your_password
SALESFORCE_SECURITY_TOKEN=your_security_token

# Jira Configuration
JIRA_HOST=https://yourcompany.atlassian.net
JIRA_USERNAME=your_email@company.com
JIRA_API_TOKEN=your_api_token
```

### **3. Start the System**

```bash
cd docker
docker-compose up -d
```

### **4. Access Your System**
- **Web Interface**: http://localhost:3000
- **API Health**: http://localhost:8000/api/health

---

## 🔧 **Advanced Setup (Native Python)**

### **Prerequisites**
- Python 3.12+
- uv package manager

### **1. Install uv**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### **2. Setup Environment**
```bash
# Install Python 3.12
uv python install 3.12

# Create virtual environment
uv venv --python 3.12 .venv-mcp
source .venv-mcp/bin/activate

# Install dependencies
uv pip install -r python_servers/requirements.txt
```

### **3. Start Services**
```bash
./scripts/start_native.sh
```

---

## 🎯 **Optional: Custom Fields Setup**

For advanced cross-system integration, you can create custom fields in Salesforce:

### **Account Object**
- **Field**: `Jira_Project_Keys__c` (Text, 255 chars)
- **Purpose**: Link accounts to Jira projects

### **Opportunity Object**  
- **Field**: `Implementation_Status__c` (Picklist: Not Started, At Risk, Blocked, Complete)
- **Field**: `Jira_Project_Key__c` (Text, 50 chars)
- **Purpose**: Track implementation projects

### **Case Object**
- **Field**: `Jira_Issue_Key__c` (Text, 50 chars)  
- **Purpose**: Link support cases to Jira issues

**How to Create**:
1. Salesforce Setup → Object Manager → [Object] → Fields & Relationships → New
2. Follow the field specifications above
3. Make fields visible to your user profile

---

## 🚨 **Troubleshooting**

### **Docker Issues**

#### **Containers Won't Start**
```bash
# Check Docker is running
docker --version

# Check logs
cd docker
docker-compose logs -f

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

#### **Port Already in Use**
```bash
# Find what's using the port
lsof -i :3000
lsof -i :8000

# Kill the process or change ports in docker-compose.yml
```

### **Connection Issues**

#### **Salesforce Connection Failed**
- ✅ Check username/password are correct
- ✅ Verify security token (reset if needed)
- ✅ Make sure account isn't locked
- ✅ Check if IP restrictions are enabled

#### **Jira Connection Failed**
- ✅ Verify Jira URL format: `https://yourcompany.atlassian.net`
- ✅ Check API token is valid
- ✅ Ensure email matches Jira account
- ✅ Verify account has API access

#### **Anthropic API Issues**
- ✅ Check API key format: starts with `sk-ant-`
- ✅ Verify account has credits
- ✅ Check rate limits

### **System Health Check**

```bash
# Check all services
curl http://localhost:8000/api/health

# Expected response:
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

### **Common Error Messages**

#### **"No such column" Errors**
- **Problem**: Trying to use custom fields that don't exist
- **Solution**: Either create the custom fields or use standard fields only

#### **"Unknown tool" Errors**  
- **Problem**: System trying to use tools that don't exist
- **Solution**: Restart containers to reload latest code

#### **"Connection timeout" Errors**
- **Problem**: Network connectivity issues
- **Solution**: Check internet connection and firewall settings

---

## 🔍 **Verification Steps**

### **1. System Health**
```bash
curl http://localhost:8000/api/health
```

### **2. Salesforce Connection**
```bash
curl http://localhost:8001/health
```

### **3. Jira Connection**  
```bash
curl http://localhost:8002/health
```

### **4. Web Interface**
1. Open http://localhost:3000
2. Try: *"Show me connection status"*
3. Try: *"What tools are available?"*

---

## 🚀 **Performance Optimization**

### **Docker Resources**
- **Memory**: Allocate 4GB+ to Docker Desktop
- **CPU**: 2+ cores recommended
- **Storage**: Ensure 10GB+ free space

### **Network Optimization**
- Use wired connection for better stability
- Consider VPN impact on API calls
- Check corporate firewall settings

### **Query Performance**
- Always use LIMIT in large queries
- Filter data appropriately
- Use specific field names instead of SELECT *

---

## 🎉 **You're Ready!**

Once setup is complete, you can:

1. **Ask business questions**: *"Show me high-priority opportunities"*
2. **Create cross-system workflows**: *"Create a Jira issue for this case"*
3. **Get AI insights**: *"What patterns do you see in our data?"*

Check out **USAGE.md** for examples and best practices!

---

## 📞 **Getting Help**

### **System Status**
- Health check: http://localhost:8000/api/health
- Logs: `docker-compose logs -f`

### **Documentation**
- **USAGE.md** - How to use the system
- **ERROR_FIXES_SUMMARY.md** - Technical troubleshooting

Your AI-powered business intelligence system is ready to provide insights across Salesforce and Jira! 🚀
