import React, { useState, useEffect } from 'react';
import { Activity, Database, Ticket, Users, Building, Phone, Mail, Calendar, AlertCircle, CheckCircle, Clock, Brain, Zap, TrendingUp } from 'lucide-react';
import Dashboard from './components/Dashboard';
import SalesforcePanel from './components/SalesforcePanel';
import JiraPanel from './components/JiraPanel';
import IntegrationPanel from './components/IntegrationPanel';
import MemoryPanel from './components/MemoryPanel';
import ThinkingIndicator from './components/ThinkingIndicator';
import StatusBar from './components/StatusBar';
import AssistantChat, { ChatToggle } from './components/AssistantChat';
import { useApi } from './hooks/useApi';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [connectionStatus, setConnectionStatus] = useState({
    salesforce: 'disconnected',
    jira: 'disconnected'
  });
  const [globalThinking, setGlobalThinking] = useState(false);
  const [lastActivity, setLastActivity] = useState(null);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const { checkConnection } = useApi();

  useEffect(() => {
    // Check connection status on startup
    const checkConnections = async () => {
      setGlobalThinking(true);
      try {
        const sfStatus = await checkConnection('salesforce');
        const jiraStatus = await checkConnection('jira');
        
        setConnectionStatus({
          salesforce: sfStatus ? 'connected' : 'error',
          jira: jiraStatus ? 'connected' : 'error'
        });
      } catch (error) {
        console.error('Connection check failed:', error);
        setConnectionStatus({
          salesforce: 'error',
          jira: 'error'
        });
      } finally {
        setGlobalThinking(false);
      }
    };

    checkConnections();
    
    // Set up periodic connection checks
    const interval = setInterval(checkConnections, 30000); // Check every 30 seconds
    
    return () => clearInterval(interval);
  }, [checkConnection]);

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: Activity, color: 'gradient-bg' },
    { id: 'salesforce', label: 'Salesforce', icon: Database, color: 'sf-gradient' },
    { id: 'jira', label: 'Jira', icon: Ticket, color: 'jira-gradient' },
    { id: 'integration', label: 'Integration', icon: Zap, color: 'bg-gradient-to-r from-purple-500 to-pink-500' },
    { id: 'memory', label: 'Memory', icon: Brain, color: 'bg-gradient-to-r from-purple-600 to-indigo-600' },
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard onThinking={setGlobalThinking} onActivity={setLastActivity} />;
      case 'salesforce':
        return <SalesforcePanel onThinking={setGlobalThinking} onActivity={setLastActivity} />;
      case 'jira':
        return <JiraPanel onThinking={setGlobalThinking} onActivity={setLastActivity} />;
      case 'integration':
        return <IntegrationPanel onThinking={setGlobalThinking} onActivity={setLastActivity} />;
      case 'memory':
        return <MemoryPanel onThinking={setGlobalThinking} onActivity={setLastActivity} />;
      default:
        return <Dashboard onThinking={setGlobalThinking} onActivity={setLastActivity} />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2">
                <Brain className="h-8 w-8 text-blue-600" />
                <h1 className="text-xl font-bold text-gray-900">MCP Integration</h1>
              </div>
              {globalThinking && (
                <ThinkingIndicator message="Processing..." />
              )}
            </div>
            
            <div className="flex items-center space-x-4">
              <StatusBar 
                salesforceStatus={connectionStatus.salesforce}
                jiraStatus={connectionStatus.jira}
                lastActivity={lastActivity}
              />
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {renderContent()}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-auto">
        <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-gray-500">
            MCP Integration Dashboard • Powered by React & Python
          </p>
        </div>
      </footer>

      {/* Chat Assistant */}
      <AssistantChat isOpen={isChatOpen} onClose={() => setIsChatOpen(false)} />
      {!isChatOpen && <ChatToggle onClick={() => setIsChatOpen(true)} />}
    </div>
  );
}

export default App;
