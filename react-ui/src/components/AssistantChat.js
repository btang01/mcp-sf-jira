import React, { useState, useRef, useEffect } from 'react';
import { Send, MessageCircle, X, Brain, Loader2, Database, Ticket, Link2, TrendingUp, AlertCircle, User, Bot } from 'lucide-react';
import ThinkingIndicator from './ThinkingIndicator';
import { useApi } from '../hooks/useApi';

const AssistantChat = ({ isOpen, onClose }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      content: "Hi! I'm your AI assistant. I can help you explore relationships between your Salesforce and Jira data. Try asking me about stalled opportunities, related cases, or cross-platform insights.",
      timestamp: new Date().toISOString()
    }
  ]);
  const [input, setInput] = useState('');
  const [isThinking, setIsThinking] = useState(false);
  const [currentThought, setCurrentThought] = useState('');
  const messagesEndRef = useRef(null);
  const { callTool } = useApi();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const analyzeQuery = (query) => {
    const lowerQuery = query.toLowerCase();
    
    // Complex query patterns
    if (lowerQuery.includes('stalled') && lowerQuery.includes('opportunit')) {
      return { type: 'stalled_opportunities_analysis' };
    }
    if (lowerQuery.includes('jira') && lowerQuery.includes('case')) {
      return { type: 'jira_case_correlation' };
    }
    if (lowerQuery.includes('account') && lowerQuery.includes('issue')) {
      return { type: 'account_issues_trace' };
    }
    if (lowerQuery.includes('high') && lowerQuery.includes('priority')) {
      return { type: 'priority_analysis' };
    }
    
    // Simple queries
    if (lowerQuery.includes('account')) {
      return { type: 'accounts' };
    }
    if (lowerQuery.includes('case')) {
      return { type: 'cases' };
    }
    if (lowerQuery.includes('contact')) {
      return { type: 'contacts' };
    }
    if (lowerQuery.includes('jira') || lowerQuery.includes('issue')) {
      return { type: 'jira_issues' };
    }
    
    return { type: 'general' };
  };

  const executeComplexQuery = async (queryType, userQuery) => {
    const thoughts = [];
    const results = {};
    
    try {
      if (queryType === 'stalled_opportunities_analysis') {
        // Step 1: Find stalled opportunities
        thoughts.push("Searching for stalled opportunities...");
        setCurrentThought(thoughts[thoughts.length - 1]);
        
        const oppsResult = await callTool('salesforce', 'salesforce_query', {
          query: "SELECT Id, Name, AccountId, Account.Name, StageName, Amount, CloseDate, LastActivityDate FROM Opportunity WHERE IsClosed = false AND LastActivityDate < LAST_N_DAYS:30 ORDER BY Amount DESC"
        });
        const opportunities = JSON.parse(oppsResult.data);
        results.opportunities = opportunities.records || [];
        
        // Step 2: Get accounts from opportunities
        thoughts.push("Finding accounts with stalled opportunities...");
        setCurrentThought(thoughts[thoughts.length - 1]);
        
        const accountIds = [...new Set(results.opportunities.map(opp => opp.AccountId).filter(Boolean))];
        if (accountIds.length > 0) {
          const accountsResult = await callTool('salesforce', 'salesforce_query', {
            query: `SELECT Id, Name, Type, Industry FROM Account WHERE Id IN ('${accountIds.join("','")}')`
          });
          results.accounts = JSON.parse(accountsResult.data).records || [];
        }
        
        // Step 3: Find cases for these accounts
        thoughts.push("Checking for related support cases...");
        setCurrentThought(thoughts[thoughts.length - 1]);
        
        if (accountIds.length > 0) {
          const casesResult = await callTool('salesforce', 'salesforce_query', {
            query: `SELECT Id, CaseNumber, Subject, Status, Priority, AccountId, Account.Name FROM Case WHERE AccountId IN ('${accountIds.join("','")}') AND Status != 'Closed' ORDER BY CreatedDate DESC`
          });
          results.cases = JSON.parse(casesResult.data).records || [];
        }
        
        // Step 4: Search for related Jira issues
        thoughts.push("Looking for related Jira issues...");
        setCurrentThought(thoughts[thoughts.length - 1]);
        
        // Search Jira for issues mentioning account names or case numbers
        const jiraQueries = [];
        if (results.accounts && results.accounts.length > 0) {
          results.accounts.forEach(account => {
            jiraQueries.push(`text ~ "${account.Name}"`);
          });
        }
        if (results.cases && results.cases.length > 0) {
          results.cases.forEach(case_ => {
            jiraQueries.push(`text ~ "${case_.CaseNumber}"`);
          });
        }
        
        if (jiraQueries.length > 0) {
          const jql = `(${jiraQueries.join(' OR ')}) AND resolution = Unresolved ORDER BY priority DESC`;
          const jiraResult = await callTool('jira', 'jira_search_issues', {
            jql: jql,
            max_results: 20
          });
          results.jiraIssues = JSON.parse(jiraResult.data).issues || [];
        }
        
        // Analyze and format results
        thoughts.push("Analyzing relationships...");
        setCurrentThought(thoughts[thoughts.length - 1]);
        
        return formatStalledOpportunityAnalysis(results);
        
      } else if (queryType === 'account_issues_trace') {
        // Trace from accounts to cases to Jira issues
        thoughts.push("Analyzing account relationships...");
        setCurrentThought(thoughts[thoughts.length - 1]);
        
        const accountsResult = await callTool('salesforce', 'salesforce_query_accounts', { limit: 20 });
        const accounts = JSON.parse(accountsResult.data).records || [];
        
        thoughts.push("Finding related cases...");
        setCurrentThought(thoughts[thoughts.length - 1]);
        
        const casesResult = await callTool('salesforce', 'salesforce_query_cases', {
          where_clause: "Status != 'Closed'",
          limit: 50
        });
        const cases = JSON.parse(casesResult.data).records || [];
        
        thoughts.push("Correlating with Jira issues...");
        setCurrentThought(thoughts[thoughts.length - 1]);
        
        // Find Jira issues
        const jiraResult = await callTool('jira', 'jira_search_issues', {
          jql: "resolution = Unresolved ORDER BY created DESC",
          max_results: 50
        });
        const jiraIssues = JSON.parse(jiraResult.data).issues || [];
        
        return formatAccountIssuesTrace(accounts, cases, jiraIssues);
        
      } else {
        // Handle simple queries
        return await executeSimpleQuery(queryType);
      }
      
    } catch (error) {
      console.error('Query execution error:', error);
      return {
        content: `I encountered an error while analyzing your request: ${error.message}. Please try again or rephrase your question.`,
        data: null
      };
    }
  };

  const formatStalledOpportunityAnalysis = (results) => {
    const { opportunities = [], accounts = [], cases = [], jiraIssues = [] } = results;
    
    let content = "## Stalled Opportunities Analysis\n\n";
    
    if (opportunities.length === 0) {
      content += "No stalled opportunities found (no opportunities without activity in the last 30 days).\n";
    } else {
      content += `Found **${opportunities.length} stalled opportunities** (no activity in 30+ days):\n\n`;
      
      opportunities.slice(0, 5).forEach(opp => {
        content += `### 📊 ${opp.Name}\n`;
        content += `- **Account**: ${opp.Account?.Name || 'Unknown'}\n`;
        content += `- **Stage**: ${opp.StageName}\n`;
        content += `- **Amount**: $${(opp.Amount || 0).toLocaleString()}\n`;
        content += `- **Close Date**: ${new Date(opp.CloseDate).toLocaleDateString()}\n`;
        content += `- **Last Activity**: ${opp.LastActivityDate ? new Date(opp.LastActivityDate).toLocaleDateString() : 'Never'}\n\n`;
      });
      
      if (cases.length > 0) {
        content += `\n### 🎫 Related Support Cases (${cases.length} open):\n`;
        cases.slice(0, 5).forEach(case_ => {
          content += `- **[${case_.CaseNumber}]** ${case_.Subject} (${case_.Status}, ${case_.Priority} priority)\n`;
        });
      }
      
      if (jiraIssues.length > 0) {
        content += `\n### 🐛 Potentially Related Jira Issues (${jiraIssues.length}):\n`;
        jiraIssues.slice(0, 5).forEach(issue => {
          content += `- **[${issue.key}]** ${issue.fields.summary} (${issue.fields.status.name})\n`;
        });
      }
      
      content += "\n### 💡 Insights:\n";
      content += `- ${opportunities.filter(o => o.Amount > 50000).length} high-value opportunities (>$50k) are stalled\n`;
      content += `- ${cases.filter(c => c.Priority === 'High').length} high-priority cases may be blocking progress\n`;
      content += `- Consider reaching out to these accounts to re-engage\n`;
    }
    
    return { content, data: results };
  };

  const formatAccountIssuesTrace = (accounts, cases, jiraIssues) => {
    let content = "## Account → Cases → Jira Issues Analysis\n\n";
    
    // Group cases by account
    const casesByAccount = {};
    cases.forEach(case_ => {
      if (case_.AccountId) {
        if (!casesByAccount[case_.AccountId]) {
          casesByAccount[case_.AccountId] = [];
        }
        casesByAccount[case_.AccountId].push(case_);
      }
    });
    
    // Find accounts with cases
    const accountsWithIssues = accounts.filter(acc => casesByAccount[acc.Id]);
    
    content += `Found **${accountsWithIssues.length} accounts** with open cases:\n\n`;
    
    accountsWithIssues.slice(0, 5).forEach(account => {
      const accountCases = casesByAccount[account.Id] || [];
      content += `### 🏢 ${account.Name}\n`;
      content += `- Type: ${account.Type || 'N/A'}\n`;
      content += `- Open Cases: ${accountCases.length}\n`;
      
      accountCases.slice(0, 3).forEach(case_ => {
        content += `  - [${case_.CaseNumber}] ${case_.Subject}\n`;
      });
      
      // Look for Jira issues mentioning this account
      const relatedJira = jiraIssues.filter(issue => 
        issue.fields.summary.includes(account.Name) || 
        (issue.fields.description && issue.fields.description.includes(account.Name))
      );
      
      if (relatedJira.length > 0) {
        content += `- Related Jira Issues: ${relatedJira.length}\n`;
        relatedJira.slice(0, 2).forEach(issue => {
          content += `  - [${issue.key}] ${issue.fields.summary}\n`;
        });
      }
      content += '\n';
    });
    
    return { content, data: { accounts: accountsWithIssues, cases, jiraIssues } };
  };

  const executeSimpleQuery = async (queryType) => {
    switch (queryType) {
      case 'accounts':
        const accountsResult = await callTool('salesforce', 'salesforce_query_accounts', { limit: 10 });
        const accounts = JSON.parse(accountsResult.data);
        return {
          content: `Found ${accounts.totalSize} accounts. Here are some examples:\n${
            accounts.records.map(a => `- ${a.Name} (${a.Type || 'No type'})`).join('\n')
          }`,
          data: accounts
        };
        
      case 'cases':
        const casesResult = await callTool('salesforce', 'salesforce_query_cases', { limit: 10 });
        const cases = JSON.parse(casesResult.data);
        return {
          content: `Found ${cases.totalSize} cases. Recent ones:\n${
            cases.records.map(c => `- [${c.CaseNumber}] ${c.Subject} (${c.Status})`).join('\n')
          }`,
          data: cases
        };
        
      default:
        return {
          content: "I can help you analyze relationships between Salesforce and Jira data. Try asking about:\n- Stalled opportunities and their related cases\n- Accounts with open issues\n- High-priority cases and their Jira tickets",
          data: null
        };
    }
  };

  const handleSend = async () => {
    if (!input.trim() || isThinking) return;
    
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsThinking(true);
    setCurrentThought('Processing your request with AI...');
    
    // Add thinking message
    const thinkingMessage = {
      id: Date.now() + 1,
      type: 'thinking',
      content: '',
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, thinkingMessage]);
    
    try {
      // Use the thinking-enabled chat endpoint
      const response = await fetch('http://localhost:8000/api/chat-with-thinking', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: input,
          capture_thinking: true
        })
      });
      
      if (response.ok) {
        const chatResponse = await response.json();
        
        // Remove thinking message and add response
        setMessages(prev => [
          ...prev.filter(m => m.type !== 'thinking'),
          {
            id: Date.now() + 2,
            type: 'assistant',
            content: chatResponse.success ? chatResponse.response : 
                     `${chatResponse.response || 'I encountered an error. Please try again.'}`,
            timestamp: new Date().toISOString()
          }
        ]);
      } else {
        // Fall back to original method if enhanced endpoint fails
        const queryAnalysis = analyzeQuery(input);
        const result = await executeComplexQuery(queryAnalysis.type, input);
        
        setMessages(prev => [
          ...prev.filter(m => m.type !== 'thinking'),
          {
            id: Date.now() + 2,
            type: 'assistant',
            content: result.content,
            data: result.data,
            timestamp: new Date().toISOString()
          }
        ]);
      }
      
    } catch (error) {
      // Fall back to original method if fetch fails
      try {
        const queryAnalysis = analyzeQuery(input);
        const result = await executeComplexQuery(queryAnalysis.type, input);
        
        setMessages(prev => [
          ...prev.filter(m => m.type !== 'thinking'),
          {
            id: Date.now() + 2,
            type: 'assistant',
            content: result.content,
            data: result.data,
            timestamp: new Date().toISOString()
          }
        ]);
      } catch (fallbackError) {
        setMessages(prev => [
          ...prev.filter(m => m.type !== 'thinking'),
          {
            id: Date.now() + 2,
            type: 'assistant',
            content: `I encountered an error: ${fallbackError.message}. Please try again.`,
            timestamp: new Date().toISOString()
          }
        ]);
      }
    } finally {
      setIsThinking(false);
      setCurrentThought('');
    }
  };

  const renderMessage = (message) => {
    if (message.type === 'thinking') {
      return (
        <div className="flex items-start space-x-3">
          <div className="flex-shrink-0">
            <Brain className="h-8 w-8 text-blue-600 animate-pulse" />
          </div>
          <div className="flex-1">
            <ThinkingIndicator message={currentThought} variant="minimal" />
          </div>
        </div>
      );
    }

    const isUser = message.type === 'user';
    
    return (
      <div className={`flex items-start space-x-3 ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
        <div className="flex-shrink-0">
          {isUser ? (
            <User className="h-8 w-8 text-gray-600" />
          ) : (
            <Bot className="h-8 w-8 text-blue-600" />
          )}
        </div>
        <div className={`flex-1 ${isUser ? 'text-right' : ''}`}>
          <div className={`inline-block px-4 py-2 rounded-lg ${
            isUser ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-900'
          }`}>
            <div className="whitespace-pre-wrap text-sm">{message.content}</div>
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {new Date(message.timestamp).toLocaleTimeString()}
          </div>
        </div>
      </div>
    );
  };

  if (!isOpen) return null;

  return (
    <div className="fixed bottom-4 right-4 w-96 h-[600px] bg-white rounded-lg shadow-2xl border border-gray-200 flex flex-col z-50">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-t-lg">
        <div className="flex items-center space-x-2">
          <Brain className="h-5 w-5" />
          <h3 className="font-semibold">AI Assistant</h3>
        </div>
        <button
          onClick={onClose}
          className="hover:bg-white/20 p-1 rounded transition-colors"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map(message => (
          <div key={message.id}>
            {renderMessage(message)}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex items-center space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask about stalled opportunities, related cases..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            disabled={isThinking}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isThinking}
            className={`p-2 rounded-lg transition-colors ${
              input.trim() && !isThinking
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-gray-100 text-gray-400 cursor-not-allowed'
            }`}
          >
            {isThinking ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              <Send className="h-5 w-5" />
            )}
          </button>
        </div>
        <div className="mt-2 text-xs text-gray-500">
          Try: "Show me stalled opportunities with related Jira issues"
        </div>
      </div>
    </div>
  );
};

// Chat Toggle Button Component
export const ChatToggle = ({ onClick }) => {
  return (
    <button
      onClick={onClick}
      className="fixed bottom-4 right-4 p-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-200 hover:scale-105 z-40"
    >
      <MessageCircle className="h-6 w-6" />
    </button>
  );
};

export default AssistantChat;
