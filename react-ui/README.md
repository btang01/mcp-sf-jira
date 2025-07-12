# MCP Integration React UI

Modern React interface for the MCP Demo System providing real-time access to Salesforce and Jira data through AI-powered business intelligence.

---

## ✨ Key Features

### 🧠 **AI Assistant Chat**
- Natural language queries to your business data
- Real-time streaming responses from Claude AI
- Context-aware conversations with memory
- Smart thinking indicators during processing

### 📊 **Interactive Dashboard**
- Unified metrics from Salesforce and Jira
- Recent activity feeds and quick actions
- Auto-refreshing data with live status monitoring
- Connection health indicators

### 🔍 **Specialized Data Panels**
- **Salesforce Panel**: Accounts, contacts, opportunities, cases
- **Jira Panel**: Issues with JQL search and filtering
- **Integration Panel**: Cross-system workflows and automation
- **Memory Panel**: Conversation history and context

### 🎨 **Quality of Life Features**
- Responsive design for all devices
- Smooth animations and hover effects
- Keyboard shortcuts and accessibility
- Error handling with retry mechanisms
- Search and filter capabilities

---

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Backend MCP servers running (see `../python_servers/README.md`)

### Setup & Launch
```bash
# Install dependencies
cd react-ui
npm install

# Start development server
npm start
```

### Access Points
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Health Check**: http://localhost:8000/api/health

---

## 🛠️ Technical Stack

- **Frontend**: React 18, TailwindCSS, Lucide Icons
- **State Management**: React Hooks with custom API integration
- **Styling**: Tailwind CSS with custom animations
- **API Communication**: REST with async/await patterns
- **Real-time Updates**: Polling with auto-refresh capabilities

---

## 📱 User Interface

### Main Components
- **AssistantChat**: AI-powered chat interface with streaming
- **Dashboard**: Overview metrics and system status
- **StatusBar**: Real-time connection monitoring
- **ThinkingIndicator**: Visual feedback during processing
- **MemoryPanel**: Conversation history and context management

### Navigation Flow
1. **Dashboard**: Start with system overview and health status
2. **Chat**: Ask natural language questions about your data
3. **Panels**: Dive deep into specific Salesforce or Jira data
4. **Integration**: Set up cross-system workflows

---

## 🔧 Development

### Available Scripts
```bash
npm start          # Development server
npm run build      # Production build
npm test           # Run tests
npm run lint       # Code linting
```

### Project Structure
```
react-ui/
├── src/
│   ├── components/
│   │   ├── AssistantChat.js      # Main AI chat interface
│   │   ├── Dashboard.js          # System overview
│   │   ├── MemoryPanel.js        # Conversation history
│   │   ├── StatusBar.js          # Connection status
│   │   └── ThinkingIndicator.js  # Loading states
│   ├── hooks/
│   │   └── useApi.js            # API integration
│   └── App.js                   # Main application
└── package.json
```

### Key Hooks
```javascript
// API integration with error handling
const { callTool, isLoading, error } = useApi();

// Example usage
const result = await callTool('salesforce', 'salesforce_query_accounts', {
  where_clause: "Type = 'Customer'",
  limit: 50
});
```

---

## 🎯 Usage Examples

### Business Intelligence Queries
```
"Show me all high-priority opportunities closing this quarter"
"Which customers have both large deals and open support cases?"
"What's the implementation status across our biggest projects?"
```

### Cross-System Workflows
```
"Create a Jira issue for this Salesforce case"
"Link this opportunity to the IMPL project"
"Show me all accounts with technical issues"
```

### System Management
```
"What's the connection status?"
"Show me available tools"
"Clear the conversation history"
```

---

## 🚨 Troubleshooting

### Common Issues

#### **Backend Connection Failed**
- Ensure MCP servers are running: `cd ../python_servers && python mcp_web_server.py`
- Check health endpoint: http://localhost:8000/api/health

#### **Slow Response Times**
- Check network connectivity
- Monitor backend performance at `/api/metrics`
- Verify Salesforce/Jira API limits

#### **UI Not Loading**
- Clear browser cache and cookies
- Check console for JavaScript errors
- Verify Node.js version (18+ required)

---

## 🔮 Future Enhancements

- Real-time WebSocket updates
- Advanced data visualization
- Drag-and-drop workflow builder
- Mobile-first optimizations
- Dark mode support
- Export and sharing capabilities

---

Your modern, AI-powered interface for intelligent business data management! 🚀
