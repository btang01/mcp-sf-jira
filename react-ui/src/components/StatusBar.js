import React from 'react';
import { CheckCircle, AlertCircle, XCircle, Clock, Database, Ticket } from 'lucide-react';

const StatusBar = ({ salesforceStatus, jiraStatus, lastActivity }) => {
  const getStatusIcon = (status) => {
    switch (status) {
      case 'connected':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'connecting':
        return <Clock className="h-4 w-4 text-yellow-500 animate-spin" />;
      case 'error':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <AlertCircle className="h-4 w-4 text-gray-400" />;
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'connected':
        return 'Connected';
      case 'connecting':
        return 'Connecting...';
      case 'error':
        return 'Error';
      default:
        return 'Disconnected';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'connected':
        return 'text-green-600';
      case 'connecting':
        return 'text-yellow-600';
      case 'error':
        return 'text-red-600';
      default:
        return 'text-gray-500';
    }
  };

  return (
    <div className="flex items-center space-x-6 text-sm">
      {/* Salesforce Status */}
      <div className="flex items-center space-x-2">
        <Database className="h-4 w-4 text-blue-600" />
        <span className="text-gray-700">SF:</span>
        <div className="flex items-center space-x-1">
          {getStatusIcon(salesforceStatus)}
          <span className={getStatusColor(salesforceStatus)}>
            {getStatusText(salesforceStatus)}
          </span>
        </div>
      </div>

      {/* Jira Status */}
      <div className="flex items-center space-x-2">
        <Ticket className="h-4 w-4 text-blue-600" />
        <span className="text-gray-700">Jira:</span>
        <div className="flex items-center space-x-1">
          {getStatusIcon(jiraStatus)}
          <span className={getStatusColor(jiraStatus)}>
            {getStatusText(jiraStatus)}
          </span>
        </div>
      </div>

      {/* Last Activity */}
      {lastActivity && (
        <div className="flex items-center space-x-2 text-gray-500">
          <Clock className="h-4 w-4" />
          <span>Last: {lastActivity}</span>
        </div>
      )}
    </div>
  );
};

export default StatusBar;