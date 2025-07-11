import React, { useState, useEffect } from 'react';
import { Activity, Users, Building, Ticket, TrendingUp, Clock, AlertCircle, CheckCircle } from 'lucide-react';
import ThinkingIndicator from './ThinkingIndicator';
import CreateIssueModal from './CreateIssueModal';
import { useApi } from '../hooks/useApi';

const Dashboard = ({ onThinking, onActivity }) => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateIssueModal, setShowCreateIssueModal] = useState(false);
  const { callTool } = useApi();

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    onThinking(true);
    onActivity('Loading dashboard data');
    
    try {
      // Fetch data from both systems
      const [accountsResult, contactsResult, casesResult, issuesResult] = await Promise.all([
        callTool('salesforce', 'salesforce_query_accounts', { limit: 1000 }),
        callTool('salesforce', 'salesforce_query_contacts', { limit: 1000 }),
        callTool('salesforce', 'salesforce_query_cases', { limit: 1000 }),
        callTool('jira', 'jira_search_issues', { jql: 'ORDER BY created DESC', max_results: 1000 })
      ]);

      // Parse results, handling both success and error responses
      const parseResult = (result, defaultValue) => {
        if (!result.success || !result.data) {
          return defaultValue;
        }
        try {
          // Check if it's an error response
          const parsed = JSON.parse(result.data);
          if (parsed.error) {
            return defaultValue;
          }
          return parsed;
        } catch (e) {
          return defaultValue;
        }
      };

      const accounts = parseResult(accountsResult, { records: [], totalSize: 0 });
      const contacts = parseResult(contactsResult, { records: [], totalSize: 0 });
      const cases = parseResult(casesResult, { records: [], totalSize: 0 });
      const issues = parseResult(issuesResult, { issues: [], total: 0 });

      // Calculate metrics
      const openCases = cases.records.filter(c => c.Status !== 'Closed').length;
      const highPriorityCases = cases.records.filter(c => c.Priority === 'High').length;
      const openIssues = issues.issues ? issues.issues.filter(i => i.status !== 'Done').length : 0;
      const customerAccounts = accounts.records.filter(a => a.Type && a.Type.includes('Customer')).length;

      setMetrics({
        totalAccounts: accounts.totalSize || 0,
        customerAccounts,
        totalContacts: contacts.totalSize || 0,
        totalCases: cases.totalSize || 0,
        openCases,
        highPriorityCases,
        totalIssues: issues.total || 0,
        openIssues,
        recentCases: cases.records.slice(0, 5),
        recentIssues: issues.issues ? issues.issues.slice(0, 5) : []
      });
      
      // Show connection warnings if any service returned errors
      let warnings = [];
      if (accountsResult.data && accountsResult.data.startsWith('Error')) {
        warnings.push('Salesforce connection issue');
      }
      if (issuesResult.data && issuesResult.data.startsWith('Error')) {
        warnings.push('Jira connection issue');
      }
      if (warnings.length > 0) {
        onActivity(`Dashboard loaded with warnings: ${warnings.join(', ')}`);
      }
      
      onActivity('Dashboard loaded');
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      setError('Failed to load dashboard data');
      onActivity('Dashboard load failed');
    } finally {
      setLoading(false);
      onThinking(false);
    }
  };

  const handleCreateIssueSuccess = (result) => {
    onActivity('Jira issue created successfully');
    // Reload dashboard data to update metrics
    loadDashboardData();
  };

  const MetricCard = ({ title, value, icon: Icon, color, subtitle, trend }) => (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 card-hover">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-semibold text-gray-900">{value}</p>
          {subtitle && <p className="text-xs text-gray-500">{subtitle}</p>}
        </div>
        <div className={`p-3 rounded-full ${color}`}>
          <Icon className="h-6 w-6 text-white" />
        </div>
      </div>
      {trend && (
        <div className="mt-3 flex items-center">
          <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
          <span className="text-sm text-green-600">{trend}</span>
        </div>
      )}
    </div>
  );

  const RecentActivity = ({ title, items, type }) => (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      <div className="space-y-3">
        {items.map((item, index) => (
          <div key={index} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-b-0">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900">
                {type === 'case' ? item.Subject : item.summary || 'No summary'}
              </p>
              <p className="text-xs text-gray-500">
                {type === 'case' ? `Case #${item.CaseNumber}` : item.key}
              </p>
            </div>
            <div className="ml-3">
              <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                type === 'case' 
                  ? item.Status === 'Closed' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-yellow-100 text-yellow-800'
                  : item.status === 'Done'
                    ? 'bg-green-100 text-green-800'
                    : 'bg-blue-100 text-blue-800'
              }`}>
                {type === 'case' ? item.Status : item.status || 'Unknown'}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
          <ThinkingIndicator message="Loading dashboard data" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="loading-shimmer h-4 rounded mb-2"></div>
              <div className="loading-shimmer h-8 rounded mb-2"></div>
              <div className="loading-shimmer h-3 rounded"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-red-500 mr-2" />
            <span className="text-red-800">{error}</span>
          </div>
          <button
            onClick={loadDashboardData}
            className="mt-3 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
        <button
          onClick={loadDashboardData}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Activity className="h-4 w-4" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Accounts"
          value={metrics.totalAccounts}
          icon={Building}
          color="bg-blue-500"
          subtitle={`${metrics.customerAccounts} customers`}
        />
        <MetricCard
          title="Total Contacts"
          value={metrics.totalContacts}
          icon={Users}
          color="bg-green-500"
        />
        <MetricCard
          title="Open Cases"
          value={metrics.openCases}
          icon={AlertCircle}
          color="bg-yellow-500"
          subtitle={`${metrics.highPriorityCases} high priority`}
        />
        <MetricCard
          title="Open Issues"
          value={metrics.openIssues}
          icon={Ticket}
          color="bg-purple-500"
          subtitle={`${metrics.totalIssues} total`}
        />
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RecentActivity
          title="Recent Cases"
          items={metrics.recentCases}
          type="case"
        />
        <RecentActivity
          title="Recent Issues"
          items={metrics.recentIssues}
          type="issue"
        />
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="flex items-center justify-center space-x-2 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            <Building className="h-5 w-5 text-blue-600" />
            <span>Create Account</span>
          </button>
          <button 
            onClick={() => setShowCreateIssueModal(true)}
            className="flex items-center justify-center space-x-2 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors hover:border-blue-300"
          >
            <Ticket className="h-5 w-5 text-blue-600" />
            <span>Create Issue</span>
          </button>
          <button 
            onClick={loadDashboardData}
            className="flex items-center justify-center space-x-2 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Activity className="h-5 w-5 text-blue-600" />
            <span>Refresh Data</span>
          </button>
        </div>
      </div>

      {/* Create Issue Modal */}
      <CreateIssueModal
        isOpen={showCreateIssueModal}
        onClose={() => setShowCreateIssueModal(false)}
        onSuccess={handleCreateIssueSuccess}
      />
    </div>
  );
};

export default Dashboard;
