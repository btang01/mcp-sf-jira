import React, { useState, useEffect } from 'react';
import { Building, Users, Phone, Mail, Search, Plus, Filter, Download } from 'lucide-react';
import ThinkingIndicator from './ThinkingIndicator';
import { useApi } from '../hooks/useApi';

const SalesforcePanel = ({ onThinking, onActivity }) => {
  const [activeView, setActiveView] = useState('accounts');
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({});
  const { callTool } = useApi();

  const views = [
    { id: 'accounts', label: 'Accounts', icon: Building },
    { id: 'contacts', label: 'Contacts', icon: Users },
    { id: 'cases', label: 'Cases', icon: Phone },
    { id: 'activities', label: 'Activities', icon: Mail }
  ];

  useEffect(() => {
    loadData();
  }, [activeView]);

  const loadData = async () => {
    setLoading(true);
    onThinking(true);
    onActivity(`Loading ${activeView}`);
    
    try {
      let result;
      switch (activeView) {
        case 'accounts':
          result = await callTool('salesforce', 'salesforce_query_accounts', { limit: 50 });
          break;
        case 'contacts':
          result = await callTool('salesforce', 'salesforce_query_contacts', { limit: 50 });
          break;
        case 'cases':
          result = await callTool('salesforce', 'salesforce_query_cases', { limit: 50 });
          break;
        case 'activities':
          result = await callTool('salesforce', 'salesforce_query_activities', { limit: 50 });
          break;
        default:
          result = await callTool('salesforce', 'salesforce_query_accounts', { limit: 50 });
      }
      
      const parsed = JSON.parse(result.data);
      setData(activeView === 'activities' ? [...(parsed.tasks?.records || []), ...(parsed.events?.records || [])] : parsed.records || []);
      onActivity(`Loaded ${activeView}`);
    } catch (error) {
      console.error('Failed to load data:', error);
      onActivity('Load failed');
    } finally {
      setLoading(false);
      onThinking(false);
    }
  };

  const filteredData = data.filter(item => {
    if (!searchTerm) return true;
    
    const searchFields = {
      accounts: ['Name', 'Type', 'Industry'],
      contacts: ['Name', 'Email', 'Phone'],
      cases: ['Subject', 'CaseNumber', 'Status'],
      activities: ['Subject', 'Status']
    };
    
    return searchFields[activeView]?.some(field => 
      item[field]?.toLowerCase().includes(searchTerm.toLowerCase())
    );
  });

  const renderTableHeader = () => {
    const headers = {
      accounts: ['Name', 'Type', 'Industry', 'City', 'Phone'],
      contacts: ['Name', 'Email', 'Phone', 'Account'],
      cases: ['Case #', 'Subject', 'Status', 'Priority', 'Created'],
      activities: ['Subject', 'Type', 'Status', 'Date']
    };
    
    return (
      <thead className="bg-gray-50">
        <tr>
          {headers[activeView]?.map((header, index) => (
            <th
              key={index}
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              {header}
            </th>
          ))}
        </tr>
      </thead>
    );
  };

  const renderTableRow = (item, index) => {
    const getCellValue = (field) => {
      if (field === 'Account' && item.Account) {
        return item.Account.Name || 'N/A';
      }
      return item[field] || 'N/A';
    };

    switch (activeView) {
      case 'accounts':
        return (
          <tr key={index} className="hover:bg-gray-50">
            <td className="px-6 py-4 whitespace-nowrap">
              <div className="flex items-center">
                <Building className="h-5 w-5 text-gray-400 mr-3" />
                <span className="text-sm font-medium text-gray-900">{item.Name}</span>
              </div>
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.Type}</td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.Industry}</td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.BillingCity}</td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.Phone}</td>
          </tr>
        );
      case 'contacts':
        return (
          <tr key={index} className="hover:bg-gray-50">
            <td className="px-6 py-4 whitespace-nowrap">
              <div className="flex items-center">
                <Users className="h-5 w-5 text-gray-400 mr-3" />
                <span className="text-sm font-medium text-gray-900">{item.Name}</span>
              </div>
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.Email}</td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.Phone}</td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{getCellValue('Account')}</td>
          </tr>
        );
      case 'cases':
        return (
          <tr key={index} className="hover:bg-gray-50">
            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
              {item.CaseNumber}
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.Subject}</td>
            <td className="px-6 py-4 whitespace-nowrap">
              <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                item.Status === 'Closed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
              }`}>
                {item.Status}
              </span>
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.Priority}</td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {item.CreatedDate ? new Date(item.CreatedDate).toLocaleDateString() : 'N/A'}
            </td>
          </tr>
        );
      case 'activities':
        return (
          <tr key={index} className="hover:bg-gray-50">
            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
              {item.Subject}
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {item.ActivityDate ? 'Task' : 'Event'}
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.Status}</td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {item.ActivityDate || item.StartDateTime ? 
                new Date(item.ActivityDate || item.StartDateTime).toLocaleDateString() : 'N/A'}
            </td>
          </tr>
        );
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Salesforce</h2>
        <div className="flex items-center space-x-3">
          {loading && <ThinkingIndicator message="Loading data" variant="minimal" />}
          <button
            onClick={loadData}
            className="flex items-center space-x-2 px-4 py-2 bg-sf-blue text-white rounded-lg hover:bg-sf-dark transition-colors"
          >
            <Download className="h-4 w-4" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* View Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          {views.map((view) => {
            const Icon = view.icon;
            return (
              <button
                key={view.id}
                onClick={() => setActiveView(view.id)}
                className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeView === view.id
                    ? 'border-sf-blue text-sf-blue'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{view.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Search and Filters */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder={`Search ${activeView}...`}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sf-blue focus:border-transparent"
            />
          </div>
          <button className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
            <Filter className="h-4 w-4" />
            <span>Filters</span>
          </button>
        </div>
        <button className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
          <Plus className="h-4 w-4" />
          <span>Create {activeView.slice(0, -1)}</span>
        </button>
      </div>

      {/* Data Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            {renderTableHeader()}
            <tbody className="bg-white divide-y divide-gray-200">
              {loading ? (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center">
                    <div className="flex items-center justify-center">
                      <ThinkingIndicator message="Loading data" />
                    </div>
                  </td>
                </tr>
              ) : filteredData.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-gray-500">
                    No {activeView} found
                  </td>
                </tr>
              ) : (
                filteredData.map((item, index) => renderTableRow(item, index))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between">
        <div className="text-sm text-gray-500">
          Showing {filteredData.length} of {data.length} {activeView}
        </div>
        <div className="flex space-x-2">
          <button className="px-3 py-1 border border-gray-300 rounded text-sm hover:bg-gray-50">
            Previous
          </button>
          <button className="px-3 py-1 border border-gray-300 rounded text-sm hover:bg-gray-50">
            Next
          </button>
        </div>
      </div>
    </div>
  );
};

export default SalesforcePanel;