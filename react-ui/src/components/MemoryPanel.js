import React, { useState, useEffect } from 'react';
import { Brain, Database, Clock, Users, FileText, AlertCircle, RefreshCw, Eye, EyeOff, Zap, Target, Lightbulb, Cog, TrendingUp, ArrowRight, CheckCircle } from 'lucide-react';

const MemoryPanel = ({ onThinking, onActivity }) => {
  const [memoryData, setMemoryData] = useState({
    entities: [],
    conversations: [],
    context: {},
    stats: {
      totalEntities: 0,
      totalConversations: 0,
      memoryUsage: 0
    }
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [expandedSections, setExpandedSections] = useState({
    entities: true,
    conversations: true,
    context: true,
    thinking: true
  });
  const [thinkingSessions, setThinkingSessions] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);

  // Fetch memory data from the backend
  const fetchMemoryData = async () => {
    setLoading(true);
    setError(null);
    onThinking?.(true);

    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/memory/status`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      setMemoryData(data);
      onActivity?.(`Memory refreshed - ${data.stats.totalEntities} entities, ${data.stats.totalConversations} conversations`);
    } catch (err) {
      console.error('Failed to fetch memory data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
      onThinking?.(false);
    }
  };

  // Fetch thinking sessions
  const fetchThinkingSessions = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/thinking-sessions`);
      if (response.ok) {
        const data = await response.json();
        setThinkingSessions(data.sessions || []);
      }
    } catch (err) {
      console.error('Failed to fetch thinking sessions:', err);
    }
  };

  // Fetch detailed thinking steps for a session
  const fetchThinkingSteps = async (sessionId) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/thinking/${sessionId}`);
      if (response.ok) {
        const data = await response.json();
        setSelectedSession(data);
      }
    } catch (err) {
      console.error('Failed to fetch thinking steps:', err);
    }
  };

  // Delete a specific thinking session
  const deleteThinkingSession = async (sessionId) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/thinking/${sessionId}`, {
        method: 'DELETE'
      });
      if (response.ok) {
        // Refresh the sessions list
        await fetchThinkingSessions();
        // Clear selected session if it was deleted
        if (selectedSession?.session_id === sessionId) {
          setSelectedSession(null);
        }
        onActivity?.(`Deleted thinking session ${sessionId.split('_')[1]}`);
      }
    } catch (err) {
      console.error('Failed to delete thinking session:', err);
    }
  };

  // Delete all thinking sessions
  const deleteAllThinkingSessions = async () => {
    if (!window.confirm('Are you sure you want to delete all thinking sessions? This cannot be undone.')) {
      return;
    }
    
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/thinking-sessions`, {
        method: 'DELETE'
      });
      if (response.ok) {
        const data = await response.json();
        await fetchThinkingSessions();
        setSelectedSession(null);
        onActivity?.(data.message);
      }
    } catch (err) {
      console.error('Failed to delete all thinking sessions:', err);
    }
  };

  // Get thinking step icon and color
  const getThinkingStepIcon = (type) => {
    switch (type) {
      case 'reasoning':
        return <Lightbulb className="h-4 w-4" />;
      case 'tool_selection':
        return <Cog className="h-4 w-4" />;
      case 'result_analysis':
        return <TrendingUp className="h-4 w-4" />;
      case 'sequential_planning':
        return <Target className="h-4 w-4" />;
      case 'causal_reasoning':
        return <Zap className="h-4 w-4" />;
      case 'error_handling':
        return <AlertCircle className="h-4 w-4" />;
      default:
        return <Brain className="h-4 w-4" />;
    }
  };

  const getThinkingStepColor = (type) => {
    switch (type) {
      case 'reasoning':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'tool_selection':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'result_analysis':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'sequential_planning':
        return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'causal_reasoning':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'error_handling':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  // Auto-refresh memory data
  useEffect(() => {
    fetchMemoryData();
    fetchThinkingSessions();
    
    if (autoRefresh) {
      const interval = setInterval(() => {
        fetchMemoryData();
        fetchThinkingSessions();
      }, 5000); // Refresh every 5 seconds
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'Unknown';
    try {
      return new Date(timestamp).toLocaleString();
    } catch {
      return timestamp;
    }
  };

  const getEntityTypeIcon = (type) => {
    switch (type?.toLowerCase()) {
      case 'opportunity':
        return '💰';
      case 'account':
        return '🏢';
      case 'case':
        return '🎫';
      case 'contact':
        return '👤';
      case 'jira':
        return '🔧';
      default:
        return '📄';
    }
  };

  const getEntityTypeColor = (type) => {
    switch (type?.toLowerCase()) {
      case 'opportunity':
        return 'bg-green-100 text-green-800';
      case 'account':
        return 'bg-blue-100 text-blue-800';
      case 'case':
        return 'bg-red-100 text-red-800';
      case 'contact':
        return 'bg-purple-100 text-purple-800';
      case 'jira':
        return 'bg-orange-100 text-orange-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <Brain className="h-8 w-8 text-purple-600" />
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Strands Memory</h2>
              <p className="text-gray-600">Real-time view of agent memory and context</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                autoRefresh 
                  ? 'bg-green-100 text-green-800 hover:bg-green-200' 
                  : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
              }`}
            >
              <RefreshCw className={`h-4 w-4 ${autoRefresh ? 'animate-spin' : ''}`} />
              <span>{autoRefresh ? 'Auto-refresh ON' : 'Auto-refresh OFF'}</span>
            </button>
            
            <button
              onClick={fetchMemoryData}
              disabled={loading}
              className="flex items-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
          </div>
        </div>

        {/* Memory Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg p-4 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-100">Total Entities</p>
                <p className="text-2xl font-bold">{memoryData.stats.totalEntities}</p>
              </div>
              <Database className="h-8 w-8 text-purple-200" />
            </div>
          </div>
          
          <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg p-4 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-100">Conversations</p>
                <p className="text-2xl font-bold">{memoryData.stats.totalConversations}</p>
              </div>
              <Users className="h-8 w-8 text-blue-200" />
            </div>
          </div>
          
          <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-lg p-4 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-100">Memory Usage</p>
                <p className="text-2xl font-bold">{memoryData.stats.memoryUsage}%</p>
              </div>
              <Brain className="h-8 w-8 text-green-200" />
            </div>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <AlertCircle className="h-5 w-5 text-red-600" />
            <span className="text-red-800 font-medium">Error loading memory data</span>
          </div>
          <p className="text-red-700 mt-1">{error}</p>
        </div>
      )}

      {/* Entity Memory */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-4 border-b border-gray-200">
          <button
            onClick={() => toggleSection('entities')}
            className="flex items-center justify-between w-full text-left"
          >
            <div className="flex items-center space-x-2">
              <Database className="h-5 w-5 text-purple-600" />
              <h3 className="text-lg font-semibold text-gray-900">Entity Memory</h3>
              <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded-full text-xs font-medium">
                {memoryData.entities.length} entities
              </span>
            </div>
            {expandedSections.entities ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
          </button>
        </div>
        
        {expandedSections.entities && (
          <div className="p-4">
            {memoryData.entities.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No entities in memory yet</p>
            ) : (
              <div className="space-y-3">
                {memoryData.entities.map((entity, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-3 hover:bg-gray-50 transition-colors">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-3">
                        <span className="text-2xl">{getEntityTypeIcon(entity.type)}</span>
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-1">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getEntityTypeColor(entity.type)}`}>
                              {entity.type}
                            </span>
                            <span className="text-sm text-gray-500">ID: {entity.id}</span>
                          </div>
                          <h4 className="font-medium text-gray-900">{entity.name || entity.summary || 'Unnamed'}</h4>
                          {entity.description && (
                            <p className="text-sm text-gray-600 mt-1">{entity.description}</p>
                          )}
                          {entity.metadata && Object.keys(entity.metadata).length > 0 && (
                            <div className="mt-2 flex flex-wrap gap-1">
                              {Object.entries(entity.metadata).map(([key, value]) => (
                                <span key={key} className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs">
                                  {key}: {String(value)}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                      <div className="text-right text-xs text-gray-500">
                        <div className="flex items-center space-x-1">
                          <Clock className="h-3 w-3" />
                          <span>{formatTimestamp(entity.cached_at || entity.timestamp)}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Conversation Memory */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-4 border-b border-gray-200">
          <button
            onClick={() => toggleSection('conversations')}
            className="flex items-center justify-between w-full text-left"
          >
            <div className="flex items-center space-x-2">
              <Users className="h-5 w-5 text-blue-600" />
              <h3 className="text-lg font-semibold text-gray-900">Conversation Memory</h3>
              <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-medium">
                {memoryData.conversations.length} messages
              </span>
            </div>
            {expandedSections.conversations ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
          </button>
        </div>
        
        {expandedSections.conversations && (
          <div className="p-4">
            {memoryData.conversations.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No conversation history yet</p>
            ) : (
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {memoryData.conversations.slice(-10).map((message, index) => (
                  <div key={index} className={`p-3 rounded-lg ${
                    message.role === 'user' 
                      ? 'bg-blue-50 border-l-4 border-blue-400' 
                      : 'bg-green-50 border-l-4 border-green-400'
                  }`}>
                    <div className="flex items-center justify-between mb-1">
                      <span className={`text-xs font-medium ${
                        message.role === 'user' ? 'text-blue-800' : 'text-green-800'
                      }`}>
                        {message.role === 'user' ? '👤 User' : '🤖 Assistant'}
                      </span>
                      <span className="text-xs text-gray-500">
                        {formatTimestamp(message.timestamp)}
                      </span>
                    </div>
                    <div className="text-sm text-gray-700 whitespace-pre-wrap">
                      {message.content}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Context Memory */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-4 border-b border-gray-200">
          <button
            onClick={() => toggleSection('context')}
            className="flex items-center justify-between w-full text-left"
          >
            <div className="flex items-center space-x-2">
              <FileText className="h-5 w-5 text-green-600" />
              <h3 className="text-lg font-semibold text-gray-900">Context Memory</h3>
              <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">
                {Object.keys(memoryData.context).length} contexts
              </span>
            </div>
            {expandedSections.context ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
          </button>
        </div>
        
        {expandedSections.context && (
          <div className="p-4">
            {Object.keys(memoryData.context).length === 0 ? (
              <p className="text-gray-500 text-center py-8">No context data available</p>
            ) : (
              <div className="space-y-3">
                {Object.entries(memoryData.context).map(([key, value]) => (
                  <div key={key} className="border border-gray-200 rounded-lg p-3">
                    <h4 className="font-medium text-gray-900 mb-2">{key}</h4>
                    <div className="bg-gray-50 rounded p-2">
                      <pre className="text-xs text-gray-700 whitespace-pre-wrap overflow-x-auto">
                        {typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
                      </pre>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Thinking Process Visualization */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <button
              onClick={() => toggleSection('thinking')}
              className="flex items-center space-x-2 text-left"
            >
              <Brain className="h-5 w-5 text-indigo-600" />
              <h3 className="text-lg font-semibold text-gray-900">Claude's Thinking Process</h3>
              <span className="bg-indigo-100 text-indigo-800 px-2 py-1 rounded-full text-xs font-medium">
                {thinkingSessions.length} sessions
              </span>
              {expandedSections.thinking ? <EyeOff className="h-5 w-5 ml-2" /> : <Eye className="h-5 w-5 ml-2" />}
            </button>
            
            {thinkingSessions.length > 0 && (
              <button
                onClick={deleteAllThinkingSessions}
                className="flex items-center space-x-1 px-3 py-1 text-red-600 hover:text-red-800 hover:bg-red-50 rounded transition-colors text-sm"
                title="Delete all thinking sessions"
              >
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                <span>Clear All</span>
              </button>
            )}
          </div>
        </div>
        
        {expandedSections.thinking && (
          <div className="p-4">
            {thinkingSessions.length === 0 ? (
              <div className="text-center py-8">
                <Brain className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                <p className="text-gray-500">No thinking sessions captured yet</p>
                <p className="text-sm text-gray-400 mt-1">Start a conversation to see Claude's thought process</p>
              </div>
            ) : (
              <div className="space-y-4">
                {/* Session List */}
                <div className="grid gap-3">
                  {thinkingSessions.slice(-5).map((session, index) => (
                    <div 
                      key={session.session_id}
                      className={`border rounded-lg p-3 transition-all hover:shadow-md ${
                        selectedSession?.session_id === session.session_id 
                          ? 'border-indigo-300 bg-indigo-50' 
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div 
                          className="flex items-center space-x-3 cursor-pointer flex-1"
                          onClick={() => fetchThinkingSteps(session.session_id)}
                        >
                          <div className="bg-indigo-100 p-2 rounded-full">
                            <Brain className="h-4 w-4 text-indigo-600" />
                          </div>
                          <div>
                            <h4 className="font-medium text-gray-900">
                              Session {session.session_id.split('_')[1]}
                            </h4>
                            <p className="text-sm text-gray-600">
                              {session.step_count} thinking steps
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <div className="text-right text-xs text-gray-500">
                            <div>{formatTimestamp(session.first_step_time)}</div>
                            <div className="flex items-center space-x-1 mt-1">
                              <Clock className="h-3 w-3" />
                              <span>
                                {Math.round((new Date(session.last_step_time) - new Date(session.first_step_time)) / 1000)}s
                              </span>
                            </div>
                          </div>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              deleteThinkingSession(session.session_id);
                            }}
                            className="p-1 text-red-500 hover:text-red-700 hover:bg-red-50 rounded transition-colors"
                            title="Delete this thinking session"
                          >
                            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Detailed Thinking Steps */}
                {selectedSession && (
                  <div className="mt-6 border-t pt-6">
                    <div className="flex items-center space-x-2 mb-4">
                      <Zap className="h-5 w-5 text-indigo-600" />
                      <h4 className="text-lg font-semibold text-gray-900">
                        Thinking Flow - Session {selectedSession.session_id.split('_')[1]}
                      </h4>
                    </div>
                    
                    {/* Thinking Flow Visualization */}
                    <div className="relative">
                      {selectedSession.thinking_steps.map((step, index) => (
                        <div key={index} className="relative flex items-start space-x-4 pb-6">
                          {/* Connection Line */}
                          {index < selectedSession.thinking_steps.length - 1 && (
                            <div className="absolute left-6 top-12 w-0.5 h-full bg-gray-200"></div>
                          )}
                          
                          {/* Step Icon */}
                          <div className={`flex-shrink-0 w-12 h-12 rounded-full border-2 flex items-center justify-center ${getThinkingStepColor(step.type)}`}>
                            {getThinkingStepIcon(step.type)}
                          </div>
                          
                          {/* Step Content */}
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center space-x-2 mb-2">
                              <h5 className="font-medium text-gray-900 capitalize">
                                {step.type.replace('_', ' ')}
                              </h5>
                              <span className="text-xs text-gray-500">
                                Step {step.step_number + 1}
                              </span>
                              {step.confidence && (
                                <div className="flex items-center space-x-1">
                                  <div className="w-16 bg-gray-200 rounded-full h-2">
                                    <div 
                                      className="bg-green-500 h-2 rounded-full transition-all duration-300"
                                      style={{ width: `${step.confidence * 100}%` }}
                                    ></div>
                                  </div>
                                  <span className="text-xs text-gray-600">
                                    {Math.round(step.confidence * 100)}%
                                  </span>
                                </div>
                              )}
                            </div>
                            
                            <div className="bg-gray-50 rounded-lg p-3 mb-2">
                              <p className="text-sm text-gray-700 whitespace-pre-wrap">
                                {step.content}
                              </p>
                            </div>
                            
                            {step.alternatives_considered && step.alternatives_considered.length > 0 && (
                              <div className="mt-2">
                                <details className="group">
                                  <summary className="cursor-pointer text-xs text-indigo-600 hover:text-indigo-800 flex items-center space-x-1">
                                    <span>Alternatives Considered</span>
                                    <ArrowRight className="h-3 w-3 group-open:rotate-90 transition-transform" />
                                  </summary>
                                  <div className="mt-2 pl-4 border-l-2 border-indigo-200">
                                    {step.alternatives_considered.map((alt, altIndex) => (
                                      <div key={altIndex} className="text-xs text-gray-600 mb-1">
                                        • {alt}
                                      </div>
                                    ))}
                                  </div>
                                </details>
                              </div>
                            )}
                            
                            <div className="text-xs text-gray-500 mt-2">
                              {formatTimestamp(step.timestamp)}
                            </div>
                          </div>
                        </div>
                      ))}
                      
                      {/* Completion Indicator */}
                      <div className="flex items-center space-x-4">
                        <div className="flex-shrink-0 w-12 h-12 rounded-full bg-green-100 border-2 border-green-200 flex items-center justify-center">
                          <CheckCircle className="h-6 w-6 text-green-600" />
                        </div>
                        <div className="text-sm text-green-700 font-medium">
                          Thinking process completed
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default MemoryPanel;
