# 🚀 **MCP Demo System - Usage Guide**

This guide shows you how to use your AI-powered business intelligence system that connects Salesforce and Jira.

---

## 🎯 **What You Can Do**

### **Business Intelligence Queries**
Ask natural language questions about your business data:
- *"Show me all high-priority opportunities that are at risk"*
- *"What Jira issues are blocking our biggest deals?"*
- *"Find customers with recent support cases"*

### **Cross-System Workflows**
- Create Jira issues from Salesforce cases
- Link opportunities to implementation projects
- Track customer issues across both systems

### **AI-Powered Insights**
- Get intelligent analysis of your business data
- Identify patterns and trends
- Receive actionable recommendations

---

## 🖥️ **How to Access**

### **Web Interface** (Recommended)
1. Open your browser to: **http://localhost:3000**
2. Use the chat interface to ask questions
3. View results in an easy-to-read format

### **API Endpoints**
- **Main API**: http://localhost:8000/api/health
- **Salesforce**: http://localhost:8001/health  
- **Jira**: http://localhost:8002/health

---

## 💬 **Example Queries**

### **Salesforce Queries**
```
"Show me all accounts in the technology industry"
"Find opportunities closing this quarter"
"List all open cases with high priority"
"Who are our biggest customers by revenue?"
```

### **Jira Queries**
```
"Show me all open bugs in the TECH project"
"What issues are assigned to me?"
"List all projects and their current status"
"Find issues created in the last week"
```

### **Cross-System Intelligence**
```
"Which customers have both large opportunities and open support cases?"
"Show me implementation projects for our biggest deals"
"Find accounts that might need technical support"
"What's the status of Project X across both systems?"
```

---

## 🔧 **Advanced Usage**

### **Direct SOQL Queries** (Salesforce)
```sql
SELECT Id, Name, Amount FROM Opportunity 
WHERE StageName = 'Negotiation/Review' 
LIMIT 10
```

### **Direct JQL Queries** (Jira)
```sql
project = "TECH" AND status != "Done" 
ORDER BY priority DESC
```

### **Creating Records**
- **New Jira Issue**: *"Create a bug report for login issues"*
- **New Salesforce Task**: *"Create a follow-up task for Acme Corp"*
- **Update Records**: *"Update the status of opportunity ABC-123"*

---

## ⚡ **Quick Reference**

### **Salesforce Objects**
- **Accounts** - Companies and organizations
- **Contacts** - Individual people
- **Opportunities** - Sales deals and prospects
- **Cases** - Customer support tickets
- **Tasks** - Activities and follow-ups

### **Jira Objects**
- **Issues** - Tasks, bugs, stories, epics
- **Projects** - Collections of related issues
- **Comments** - Discussion on issues
- **Issue Types** - Bug, Task, Story, Epic, etc.

### **Common Fields**
**Salesforce:**
- `Name`, `Id`, `CreatedDate`, `LastModifiedDate`
- `Amount` (Opportunities), `Status` (Cases), `Priority` (Tasks)

**Jira:**
- `key`, `summary`, `description`, `status`, `assignee`
- `created`, `updated`, `priority`, `project`

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### **"No such column" Error**
- **Problem**: Trying to use custom fields that don't exist
- **Solution**: Use standard fields or create custom fields (see SETUP.md)

#### **"Project does not exist" Error**
- **Problem**: Invalid Jira project key
- **Solution**: Use `"Show me all projects"` to see available projects

#### **Connection Issues**
- **Problem**: Can't connect to Salesforce/Jira
- **Solution**: Check your credentials in `config/.env`

### **Getting Help**
1. Check the system health: http://localhost:8000/api/health
2. Ask: *"What tools are available?"*
3. Try: *"Show me connection status"*

---

## 🎯 **Best Practices**

### **Writing Good Queries**
- **Be specific**: *"Show me high-priority cases"* vs *"Show me cases"*
- **Use timeframes**: *"opportunities closing this month"*
- **Combine systems**: *"customers with both deals and support cases"*

### **Performance Tips**
- Limit large queries: *"Show me top 10 opportunities"*
- Use filters: *"accounts in California"*
- Be patient with complex cross-system queries

### **Data Privacy**
- This system accesses your real business data
- Use appropriate filters for sensitive information
- Test queries with small datasets first

---

## 🚀 **Getting Started**

1. **Start Simple**: Try *"Show me all accounts"*
2. **Explore**: Ask *"What can you help me with?"*
3. **Get Creative**: Combine data from both systems
4. **Ask Questions**: The AI can explain results and suggest next steps

Your MCP system is ready to provide intelligent insights across your business data! 🎉
