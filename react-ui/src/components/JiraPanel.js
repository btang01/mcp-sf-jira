import React, { useState, useEffect } from 'react';
import { Ticket, User, AlertCircle, CheckCircle, Clock, Search, Plus, Filter } from 'lucide-react';
import ThinkingIndicator from './ThinkingIndicator';
import { useApi } from '../hooks/useApi';

const JiraPanel = ({ onThinking, onActivity }) => {
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [jql, setJql] = useState('ORDER BY created DESC');
  const { callTool } = useApi();

  useEffect(() => {
    loadIssues();
  }, []);

  const loadIssues = async () => {
    setLoading(true);
    onThinking(true);
    onActivity('Loading Jira issues');
    
    try {
      const result = await callTool('jira', 'jira_search_issues', {
        jql: jql,
        max_results: 50
      });
      
      const parsed = JSON.parse(result.data);
      setIssues(parsed.issues || []);
      onActivity(`Loaded ${parsed.issues?.length || 0} issues`);
    } catch (error) {
      console.error('Failed to load issues:', error);
      setIssues([]);
      onActivity('Load failed');
    } finally {
      setLoading(false);
      onThinking(false);
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'highest':
        return 'bg-red-100 text-red-800';
      case 'high':
        return 'bg-orange-100 text-orange-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'done':
        return 'bg-green-100 text-green-800';
      case 'in progress':
        return 'bg-blue-100 text-blue-800';
      case 'todo':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredIssues = issues.filter(issue => {
    if (!searchTerm) return true;
    return (
      issue.key?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      issue.summary?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      issue.status?.toLowerCase().includes(searchTerm.toLowerCase())
    );
  });

  const quickFilters = [
    { label: 'All Issues', jql: 'ORDER BY created DESC' },
    { label: 'Open Issues', jql: 'resolution = Unresolved ORDER BY created DESC' },
    { label: 'My Issues', jql: 'assignee = currentUser() ORDER BY created DESC' },
    { label: 'High Priority', jql: 'priority = High ORDER BY created DESC' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Jira</h2>
        <div className="flex items-center space-x-3">
          {loading && <ThinkingIndicator message="Loading issues" variant="minimal" />}
          <button
            onClick={loadIssues}
            className="flex items-center space-x-2 px-4 py-2 bg-jira-blue text-white rounded-lg hover:bg-jira-dark transition-colors"
          >
            <Ticket className="h-4 w-4" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Quick Filters */}
      <div className="flex flex-wrap gap-2">
        {quickFilters.map((filter, index) => (
          <button
            key={index}
            onClick={() => {
              setJql(filter.jql);
              setTimeout(loadIssues, 100);
            }}
            className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
              jql === filter.jql
                ? 'bg-jira-blue text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {filter.label}
          </button>
        ))}
      </div>

      {/* Search and JQL */}
      <div className="space-y-4">
        <div className="flex items-center space-x-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search issues..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jira-blue focus:border-transparent"
            />
          </div>
          <button className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
            <Plus className="h-4 w-4" />
            <span>Create Issue</span>
          </button>
        </div>
        
        <div className="flex items-center space-x-2">
          <label className="text-sm font-medium text-gray-700">JQL:</label>
          <input
            type="text"
            value={jql}
            onChange={(e) => setJql(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && loadIssues()}
            className="flex-1 px-3 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-jira-blue focus:border-transparent"
            placeholder="Enter JQL query..."
          />
          <button
            onClick={loadIssues}
            className="px-3 py-1 bg-jira-blue text-white rounded text-sm hover:bg-jira-dark transition-colors"
          >
            Search
          </button>
        </div>
      </div>

      {/* Issues Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Issue
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Summary
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Priority
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Assignee
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {loading ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center">
                    <div className="flex items-center justify-center">
                      <ThinkingIndicator message="Loading issues" />
                    </div>
                  </td>
                </tr>
              ) : filteredIssues.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                    No issues found
                  </td>
                </tr>
              ) : (
                filteredIssues.map((issue, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <Ticket className="h-4 w-4 text-jira-blue mr-2" />
                        <span className="text-sm font-medium text-jira-blue">
                          {issue.key || 'N/A'}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900 max-w-xs truncate">
                        {issue.summary || 'No summary'}
                      </div>
                      <div className="text-xs text-gray-500">
                        Task
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(issue.status)}`}>
                        {issue.status || 'Unknown'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getPriorityColor('Medium')}`}>
                        Medium
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {issue.assignee || 'Unassigned'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {issue.created ? new Date(issue.created).toLocaleDateString() : 'N/A'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Summary */}
      <div className="flex items-center justify-between text-sm text-gray-500">
        <div>
          Showing {filteredIssues.length} of {issues.length} issues
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center">
            <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
            <span>Done: {issues.filter(i => i.status === 'Done').length}</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-blue-500 rounded-full mr-2"></div>
            <span>In Progress: {issues.filter(i => i.status === 'In Progress').length}</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-gray-500 rounded-full mr-2"></div>
            <span>Todo: {issues.filter(i => i.status === 'To Do').length}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default JiraPanel;
