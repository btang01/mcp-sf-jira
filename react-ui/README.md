# MCP Integration React UI

A lightweight, modern React interface for the MCP Integration Dashboard providing real-time access to Salesforce and Jira data through a unified interface.

## ✨ Features

### 🧠 **Thinking Indicators**
- Real-time visual feedback when processing requests
- Smart loading states with context-aware messages
- Animated thinking dots and progress indicators

### 🔄 **Live Status Monitoring**
- Connection status for both Salesforce and Jira
- Last activity timestamps
- Auto-reconnection handling

### 📊 **Interactive Dashboard**
- Unified metrics from both platforms
- Recent activity feeds
- Quick action buttons
- Auto-refreshing data

### 🔍 **Advanced Data Views**
- **Salesforce Panel**: Accounts, Contacts, Cases, Activities
- **Jira Panel**: Issues with JQL search, filters, and status tracking
- **Integration Panel**: Sync operations and automation tools

### 🎨 **Quality of Life Features**
- Responsive design that works on all devices
- Smooth transitions and hover effects
- Keyboard shortcuts and accessibility
- Error handling with retry options
- Search and filter capabilities
- Export functionality

## 🚀 Quick Start

### Option 1: Use the startup script (Recommended)
```bash
cd mcp-integration
./start_ui.sh
```

### Option 2: Manual setup
```bash
# Install React dependencies
cd react-ui
npm install

# Start Python backend (in separate terminal)
cd ../python_servers
source venv/bin/activate
python3 web_server.py

# Start React frontend (in separate terminal)
cd ../react-ui
npm start
```

## 🌐 Access

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Health**: http://localhost:8000/api/health

## 📱 User Interface

### Navigation
- **Dashboard**: Overview metrics and recent activity
- **Salesforce**: Dedicated view for SF data with filtering
- **Jira**: Issue management with JQL search
- **Integration**: Sync tools and automation

### Smart Features
- **Thinking Indicators**: Visual feedback during data loading
- **Status Bar**: Real-time connection monitoring
- **Auto-refresh**: Periodic data updates
- **Error Recovery**: Automatic retry mechanisms
- **Search & Filter**: Find data quickly
- **Responsive Design**: Works on desktop and mobile

## 🛠️ Technical Stack

- **Frontend**: React 18, TailwindCSS, Lucide Icons
- **Backend**: FastAPI, Python 3.9+
- **State Management**: React Hooks
- **Styling**: Tailwind CSS with custom animations
- **API**: REST with async/await
- **WebSocket**: Real-time status updates

## 🔧 Development

### Available Scripts
- `npm start`: Start development server
- `npm run build`: Build for production
- `npm test`: Run tests
- `npm run dev`: Start with backend concurrently

### File Structure
```
react-ui/
├── src/
│   ├── components/
│   │   ├── Dashboard.js         # Main dashboard
│   │   ├── SalesforcePanel.js   # SF data views
│   │   ├── JiraPanel.js         # Jira issue management
│   │   ├── IntegrationPanel.js  # Sync tools
│   │   ├── ThinkingIndicator.js # Loading states
│   │   └── StatusBar.js         # Connection status
│   ├── hooks/
│   │   └── useApi.js           # API integration
│   ├── App.js                  # Main app component
│   └── index.js               # Entry point
├── public/
└── package.json
```

## 🎯 Key Components

### ThinkingIndicator
```jsx
<ThinkingIndicator 
  message="Loading data" 
  variant="default" 
  size="md" 
/>
```

### StatusBar
Shows real-time connection status for both services with last activity timestamps.

### Dashboard
Unified view with metrics cards, recent activity, and quick actions.

### Data Panels
Specialized views for Salesforce and Jira data with search, filters, and actions.

## 🔗 API Integration

The UI communicates with the Python backend through a REST API:

```javascript
// Example API call
const { callTool } = useApi();
const result = await callTool('salesforce', 'salesforce_query_accounts', {
  where_clause: "Type = 'Customer'",
  limit: 50
});
```

## 🎨 Styling

Uses Tailwind CSS with custom animations:
- Thinking dots animation
- Smooth transitions
- Loading shimmer effects
- Hover states and micro-interactions

## 📋 Future Enhancements

- Real-time WebSocket updates
- Drag-and-drop data operations
- Advanced filtering and sorting
- Data export capabilities
- Mobile-first optimizations
- Dark mode support

This React UI provides a modern, intuitive interface for managing your Salesforce and Jira integration with real-time feedback and quality of life improvements.