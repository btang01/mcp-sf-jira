import React, { useState } from 'react';
import { Zap, ArrowLeftRight, RefreshCw, Play, CheckCircle, AlertCircle, Clock } from 'lucide-react';
import ThinkingIndicator from './ThinkingIndicator';
import { useApi } from '../hooks/useApi';

const IntegrationPanel = ({ onThinking, onActivity }) => {
  const [activeSync, setActiveSync] = useState(null);
  const [syncResults, setSyncResults] = useState([]);
  const { callTool } = useApi();

  const syncOperations = [
    {
      id: 'sf-to-jira',
      title: 'Sync SF Cases to Jira',
      description: 'Create Jira issues from open Salesforce cases',
      icon: ArrowLeftRight,
      color: 'bg-blue-500',
      direction: 'sf → jira'
    },
    {
      id: 'jira-to-sf',
      title: 'Sync Jira to SF',
      description: 'Create SF cases from high-priority Jira bugs',
      icon: ArrowLeftRight,
      color: 'bg-purple-500',
      direction: 'jira → sf'
    },
    {
      id: 'bidirectional',
      title: 'Bidirectional Sync',
      description: 'Sync data in both directions',
      icon: RefreshCw,
      color: 'bg-green-500',
      direction: 'sf ↔ jira'
    }
  ];

  const runSync = async (syncId) => {
    setActiveSync(syncId);
    onThinking(true);
    onActivity(`Running ${syncId} sync`);
    
    try {
      let result;
      switch (syncId) {
        case 'sf-to-jira':
          result = await simulateSfToJiraSync();
          break;
        case 'jira-to-sf':
          result = await simulateJiraToSfSync();
          break;
        case 'bidirectional':
          result = await simulateBidirectionalSync();
          break;
        default:
          throw new Error('Unknown sync operation');
      }
      
      setSyncResults(prev => [
        {
          id: Date.now(),
          syncId,
          timestamp: new Date().toISOString(),
          status: 'success',
          message: result.message,
          details: result.details
        },
        ...prev.slice(0, 9) // Keep last 10 results
      ]);
      
      onActivity(`Sync completed: ${result.message}`);
    } catch (error) {
      setSyncResults(prev => [
        {
          id: Date.now(),
          syncId,
          timestamp: new Date().toISOString(),
          status: 'error',
          message: error.message,
          details: []
        },
        ...prev.slice(0, 9)
      ]);
      
      onActivity(`Sync failed: ${error.message}`);
    } finally {
      setActiveSync(null);
      onThinking(false);
    }
  };

  const simulateSfToJiraSync = async () => {
    // Simulate API calls
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    return {
      message: 'Successfully synced 3 cases to Jira',
      details: [
        'Case #00001002 → PROJ-123: Electrical wiring guidance',
        'Case #00001004 → PROJ-124: Generator maintenance',
        'Case #00001001 → PROJ-125: Performance issues'
      ]
    };
  };

  const simulateJiraToSfSync = async () => {
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    return {
      message: 'No high-priority bugs found to sync',
      details: [
        'Searched for bugs with priority = High',
        'Found 0 issues matching criteria',
        'No new cases created'
      ]
    };
  };

  const simulateBidirectionalSync = async () => {
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    return {
      message: 'Bidirectional sync completed',
      details: [
        'SF → Jira: 2 cases synced',
        'Jira → SF: 0 bugs synced',
        'Total operations: 2'
      ]
    };
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Clock className="h-5 w-5 text-yellow-500" />;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Integration</h2>
        <div className="flex items-center space-x-3">
          <Zap className="h-5 w-5 text-yellow-500" />
          <span className="text-sm text-gray-600">Automation Tools</span>
        </div>
      </div>

      {/* Sync Operations */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {syncOperations.map((operation) => {
          const Icon = operation.icon;
          const isActive = activeSync === operation.id;
          
          return (
            <div
              key={operation.id}
              className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 card-hover"
            >
              <div className="flex items-center justify-between mb-4">
                <div className={`p-3 rounded-full ${operation.color}`}>
                  <Icon className="h-6 w-6 text-white" />
                </div>
                <span className="text-xs font-medium text-gray-500 uppercase">
                  {operation.direction}
                </span>
              </div>
              
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {operation.title}
              </h3>
              
              <p className="text-sm text-gray-600 mb-4">
                {operation.description}
              </p>
              
              <button
                onClick={() => runSync(operation.id)}
                disabled={isActive}
                className={`w-full flex items-center justify-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
              >
                {isActive ? (
                  <ThinkingIndicator message="Running" variant="minimal" />
                ) : (
                  <>
                    <Play className="h-4 w-4" />
                    <span>Run Sync</span>
                  </>
                )}
              </button>
            </div>
          );
        })}
      </div>

      {/* Sync History */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Sync History</h3>
        
        {syncResults.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <RefreshCw className="h-12 w-12 mx-auto mb-2 text-gray-300" />
            <p>No sync operations performed yet</p>
          </div>
        ) : (
          <div className="space-y-3">
            {syncResults.map((result) => (
              <div
                key={result.id}
                className="flex items-start space-x-3 p-3 border border-gray-200 rounded-lg"
              >
                <div className="flex-shrink-0 mt-1">
                  {getStatusIcon(result.status)}
                </div>
                
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-gray-900">
                      {result.message}
                    </p>
                    <span className="text-xs text-gray-500">
                      {new Date(result.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  
                  {result.details.length > 0 && (
                    <div className="mt-2">
                      <ul className="text-xs text-gray-600 space-y-1">
                        {result.details.map((detail, index) => (
                          <li key={index} className="flex items-center">
                            <div className="w-1 h-1 bg-gray-400 rounded-full mr-2"></div>
                            {detail}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Integration Settings */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Integration Settings</h3>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">Auto-sync enabled</label>
              <p className="text-xs text-gray-500">Automatically sync data every hour</p>
            </div>
            <button className="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent bg-gray-200 transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">
              <span className="translate-x-0 pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"></span>
            </button>
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">Notifications</label>
              <p className="text-xs text-gray-500">Get notified when sync operations complete</p>
            </div>
            <button className="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent bg-blue-600 transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">
              <span className="translate-x-5 pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"></span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IntegrationPanel;