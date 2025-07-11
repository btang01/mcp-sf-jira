# Custom Fields Integration Guide

## How the Agent Becomes Aware of Custom Fields

The MCP demo system makes the AI agent aware of custom fields through several key mechanisms:

## 1. Enhanced System Prompt

The `mcp_web_server.py` includes a comprehensive system prompt that explicitly tells the agent about:

### **Salesforce Custom Fields:**
- `Case.Jira_Issue_Key__c` - Links Salesforce cases to Jira issues
- `Opportunity.Jira_Project_Key__c` - Links opportunities to Jira projects  
- `Opportunity.Implementation_Status__c` - Tracks implementation risk
- `Account.Jira_Project_Keys__c` - Account-level Jira project mapping

### **Cross-System Intelligence Instructions:**
- When to look for "At Risk" opportunities using `Implementation_Status__c`
- How to correlate cases with Jira issues using `Jira_Issue_Key__c`
- Pattern recognition for business risk analysis
- Demo data context and relationships

## 2. System Prompt Location

```python
# In python_servers/mcp_web_server.py, _process_chat_query method:
system_prompt = """You are an AI assistant with access to Salesforce and Jira systems...

CRITICAL: JIRA ISSUE KEYS ARE ROOT CAUSE DIAGNOSTIC CLUES

When you see a Jira Issue Key on a Salesforce Case (Case.Jira_Issue_Key__c field), this is a DIRECT CLUE to the root cause of the problem. You MUST:

1. **IMMEDIATELY investigate the linked Jira issue** - The Jira Issue Key is not just a reference, it's a diagnostic pointer to the technical root cause
2. **Analyze the Jira issue details** - Status, priority, description, comments, and resolution details
3. **Connect technical problems to business impact** - Link Jira technical issues to Salesforce business problems
4. **Provide root cause analysis** - Explain how the technical issue (Jira) is causing the business problem (Case)

IMPORTANT CUSTOM FIELDS AND CROSS-SYSTEM INTEGRATION:

Salesforce Custom Fields:
- Case.Jira_Issue_Key__c: **ROOT CAUSE DIAGNOSTIC LINK** - Links Salesforce cases to Jira issues (e.g., "TECH-1", "IMPL-1")
- Opportunity.Jira_Project_Key__c: Links opportunities to Jira projects (e.g., "IMPL", "TECH")
- Opportunity.Implementation_Status__c: Tracks implementation risk ("At Risk", "Blocked", "Complete", "Not Started")
- Account.Jira_Project_Keys__c: Account-level Jira project mapping (e.g., "TECH, IMPL, SUPPORT")

ROOT CAUSE ANALYSIS WORKFLOW:
1. **When analyzing any Case** - ALWAYS check for Jira_Issue_Key__c field
2. **If Jira Issue Key exists** - IMMEDIATELY query the corresponding Jira issue
3. **Analyze the technical details** - What's broken, blocked, or causing problems in Jira
4. **Explain the connection** - How does the technical issue cause the business problem
5. **Provide actionable insights** - What needs to be fixed technically to resolve the business issue

Cross-System Intelligence:
- When analyzing opportunities "at risk", look for Implementation_Status__c = "At Risk"
- **ALWAYS follow Jira Issue Key trails** - They lead to root causes
- Identify patterns: High-priority cases + blocked Jira issues = business risk
- Use custom fields to provide cross-system insights and recommendations
- **Treat Jira Issue Keys as diagnostic breadcrumbs** - Follow them to find root causes

DIAGNOSTIC MINDSET:
- Jira Issue Key = Root Cause Clue
- Always investigate linked Jira issues for technical details
- Connect technical problems to business symptoms
- Provide comprehensive root cause analysis
"""
```

## 3. Demo Data Context

The system prompt also includes specific context about the demo data:

- **TechCorp Platform Expansion**: $500K opportunity with `Implementation_Status__c = "At Risk"`
- **Related cases**: Have `Jira_Issue_Key__c` values linking to technical issues
- **Business correlation**: Links between opportunities, cases, and Jira issues

## 4. Query Instructions

The agent is instructed to:
- Always include custom fields in SOQL queries
- Look for cross-system relationships
- Provide comprehensive analysis using custom field data

## 5. Testing the Integration

### **Example Queries That Work:**

1. **"Show me opportunities with Implementation Status of At Risk"**
   - Agent queries using `Implementation_Status__c = 'At Risk'`
   - Finds TechCorp Platform Expansion opportunity

2. **"Show me cases that have Jira Issue Key references"**
   - Agent queries using `Jira_Issue_Key__c` field
   - Finds cases linked to TECH-1 and TECH-2

3. **"What technical issues might be blocking the TechCorp deal?"**
   - Agent correlates opportunity status with related cases
   - Uses Jira issue keys to find technical problems

## 6. Custom Field Creation

The custom fields were created using the demo data generator:

```bash
# In create_demo_data.sh and demo_data_generator_simple.py:
"Jira_Project_Keys__c": "TECH, IMPL"
"Implementation_Status__c": "At Risk"  
"Jira_Issue_Key__c": "TECH-1"
```

## 7. Benefits of This Approach

### **Intelligent Cross-System Analysis:**
- Agent understands business impact of technical issues
- Correlates support cases with revenue opportunities
- Provides proactive risk identification

### **Context-Aware Responses:**
- Agent knows to look for specific field patterns
- Understands the demo scenario relationships
- Provides actionable insights

### **Extensible Framework:**
- Easy to add new custom fields to system prompt
- Can include field validation rules and business logic
- Supports complex multi-system workflows

## 8. Root Cause Analysis Enhancement

### **The Problem:**
Previously, the agent would see Jira Issue Keys on Salesforce Cases but treat them as simple references rather than diagnostic clues pointing to root causes.

### **The Solution:**
Enhanced the system prompt to explicitly instruct the agent that:
- **Jira Issue Keys are diagnostic breadcrumbs** - They lead directly to technical root causes
- **Immediate investigation is required** - When a Jira Issue Key is found, the agent must immediately query the linked Jira issue
- **Root cause analysis is mandatory** - The agent must explain how technical issues cause business problems

### **Key Behavioral Changes:**
1. **Automatic Investigation**: Agent now automatically follows Jira Issue Key links
2. **Technical Deep Dive**: Agent analyzes Jira issue status, priority, description, and comments
3. **Business Impact Connection**: Agent explains how technical problems affect business outcomes
4. **Actionable Insights**: Agent provides specific recommendations for resolving root causes

### **Example Workflow:**
```
User: "Why is this customer case taking so long to resolve?"
Agent: 
1. Queries Salesforce case details
2. Finds Jira_Issue_Key__c = "TECH-1" 
3. IMMEDIATELY queries Jira issue TECH-1
4. Analyzes technical details (blocked, high priority, database performance issue)
5. Explains: "The case is delayed because it's linked to TECH-1, a high-priority database performance issue that's currently blocked waiting for infrastructure team approval"
6. Provides actionable insight: "To resolve this case, the infrastructure team needs to approve the database optimization changes in TECH-1"
```

## 9. Implementation Results

The enhanced system prompt enables the agent to:

✅ **Identify at-risk opportunities** using custom status fields
✅ **Correlate technical issues** with business impact
✅ **Provide cross-system insights** linking Salesforce and Jira
✅ **Understand demo data relationships** for realistic scenarios
✅ **Generate actionable recommendations** based on custom field analysis
✅ **Perform automatic root cause analysis** using Jira Issue Key diagnostic clues
✅ **Follow diagnostic breadcrumbs** to find technical root causes
✅ **Connect technical problems to business symptoms** with detailed explanations

## 9. Future Enhancements

### **Additional Custom Fields:**
- `Case.Business_Impact__c` - Quantify revenue impact
- `Opportunity.Technical_Complexity__c` - Implementation difficulty
- `Account.Support_Tier__c` - Service level agreements

### **Enhanced Intelligence:**
- Machine learning on custom field patterns
- Predictive analytics for risk assessment
- Automated escalation based on field combinations

This approach demonstrates how MCP systems can provide AI agents with deep, contextual understanding of enterprise data relationships through enhanced system prompts and custom field awareness.
