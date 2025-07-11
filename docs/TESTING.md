# 🧪 Testing Guide for MCP Integration

This guide shows you how to test the Docker containerized MCP integration system.

## 🚀 Quick Test (Recommended)

First, run our automated test:

```bash
python3 test_simple.py
```

This checks that all files are in place and properly structured.

## 📋 Testing Options

### Option 1: Docker Testing (Requires Docker)

**Prerequisites:**
- Docker Desktop installed ([Get it here](https://docs.docker.com/get-docker/))
- Docker Desktop running

**Steps:**

1. **Check Docker installation:**
   ```bash
   docker --version
   docker-compose --version
   ```

2. **Test build (builds all containers):**
   ```bash
   docker-compose build
   ```
   
   Expected: All 4 services build successfully
   - ✅ `mcp-ui` - React frontend
   - ✅ `mcp-web-server` - FastAPI backend  
   - ✅ `mcp-salesforce` - Salesforce MCP server
   - ✅ `mcp-jira` - Jira MCP server

3. **Test startup:**
   ```bash
   docker-compose up -d
   ```
   
   Expected: All services start and show "done"

4. **Test health checks:**
   ```bash
   # Web server health
   curl http://localhost:8000/api/health
   
   # Salesforce MCP health  
   curl http://localhost:8001/health
   
   # Jira MCP health
   curl http://localhost:8002/health
   
   # UI (should return HTML)
   curl http://localhost:3000
   ```

5. **View logs:**
   ```bash
   # All services
   docker-compose logs
   
   # Specific service
   docker-compose logs mcp-web-server
   ```

6. **Test UI:**
   - Open http://localhost:3000 in browser
   - Should see MCP Integration dashboard
   - Check that Salesforce and Jira panels load

7. **Clean up:**
   ```bash
   docker-compose down
   ```

### Option 2: Local Testing (No Docker)

**Prerequisites:**
- Python 3.13+ 
- Node.js 18+
- All dependencies installed

**Steps:**

1. **Install Python dependencies:**
   ```bash
   cd python_servers
   pip install -r requirements.txt
   ```

2. **Install React dependencies:**
   ```bash
   cd react-ui
   npm install
   cd ..
   ```

3. **Test MCP servers individually:**
   ```bash
   # Terminal 1: Salesforce server
   cd python_servers
   MCP_SERVER_PORT=8001 python salesforce_server_modern.py
   
   # Terminal 2: Jira server  
   cd python_servers
   MCP_SERVER_PORT=8002 python jira_server_modern.py
   
   # Terminal 3: Web server
   cd python_servers
   MCP_SALESFORCE_URL=http://localhost:8001 MCP_JIRA_URL=http://localhost:8002 python mcp_web_server.py
   
   # Terminal 4: React UI
   cd react-ui
   REACT_APP_API_URL=http://localhost:8000 npm start
   ```

4. **Test endpoints:**
   ```bash
   curl http://localhost:8001/health  # Salesforce
   curl http://localhost:8002/health  # Jira
   curl http://localhost:8000/api/health  # Web server
   ```

## 🔍 Troubleshooting

### Common Issues

**1. Port conflicts:**
```bash
# Check what's using ports
lsof -i :3000
lsof -i :8000
lsof -i :8001
lsof -i :8002

# Kill processes if needed
kill -9 <PID>
```

**2. Docker build fails:**
```bash
# Clean Docker cache
docker system prune -f

# Build with no cache
docker-compose build --no-cache
```

**3. Services won't start:**
```bash
# Check logs for errors
docker-compose logs mcp-web-server
docker-compose logs mcp-salesforce
docker-compose logs mcp-jira

# Restart individual service
docker-compose restart mcp-web-server
```

**4. Connection refused errors:**
- Wait 30 seconds after `docker-compose up -d`
- Services need time to initialize
- Check that .env file has correct credentials

**5. UI shows empty dashboard:**
- Check browser console for JavaScript errors
- Verify API endpoints are responding
- Check CORS settings (should allow localhost:3000)

### Health Check Commands

```bash
# Quick health check all services
echo "Web Server:" && curl -s http://localhost:8000/api/health | grep status
echo "Salesforce:" && curl -s http://localhost:8001/health | grep status  
echo "Jira:" && curl -s http://localhost:8002/health | grep status
echo "UI:" && curl -s -o /dev/null -w "%{http_code}" http://localhost:3000
```

### Log Analysis

```bash
# Follow logs in real-time
docker-compose logs -f

# Search for errors
docker-compose logs | grep -i error

# Check specific timeframe
docker-compose logs --since="5m"
```

## 🧪 Test Scenarios

### 1. Basic Functionality
- ✅ All containers start
- ✅ Health endpoints respond  
- ✅ UI loads and shows dashboard
- ✅ No critical errors in logs

### 2. MCP Communication
- ✅ Web server connects to MCP servers
- ✅ Tools are discovered and listed
- ✅ Tool calls work end-to-end

### 3. AI Integration  
- ✅ Anthropic API key works
- ✅ Chat interface responds
- ✅ AI can call Salesforce/Jira tools

### 4. Data Integration
- ✅ Salesforce connection works
- ✅ Jira connection works  
- ✅ Data displays in UI panels

## 📊 Success Criteria

Your system is working correctly when:

1. **All services start:** `docker-compose ps` shows 4 running services
2. **Health checks pass:** All endpoints return `{"status": "healthy"}`
3. **UI loads:** http://localhost:3000 shows the dashboard
4. **No errors:** Logs show INFO level messages, no ERRORs
5. **Tools work:** You can ask questions and get responses

## 🚀 Ready for Production?

If all tests pass, your system is ready for:
- ✅ **Local development** using Docker
- ✅ **AWS ECS deployment** (see README.md AWS section)
- ✅ **Team collaboration** with consistent Docker environment
- ✅ **CI/CD integration** using the same containers

---

**Need help?** Check the logs and error messages above, or refer to the troubleshooting section.