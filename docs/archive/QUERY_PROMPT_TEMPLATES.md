# Query Prompt Templates for SOQL and JQL Consistency

This document provides prompt templates and best practices to improve the consistency and reliability of SOQL (Salesforce) and JQL (Jira) queries in your MCP system.

## SOQL (Salesforce Object Query Language) Prompts

### 🔧 Core SOQL Rules Prompt
```
When working with Salesforce SOQL queries, ALWAYS follow these rules:

1. **QUERY vs UPDATE Operations**:
   - Use SELECT for reading data: `SELECT Id, Name FROM Account`
   - NEVER use UPDATE in SOQL queries - use the salesforce_create tool with update operations
   - For updates, use: `salesforce_create(sobject_type="Account", data={"Id": "123", "Name": "New Name"})`

2. **Standard SOQL Structure**:
   - SELECT [fields] FROM [object] WHERE [conditions] ORDER BY [field] LIMIT [number]
   - Always include Id field in SELECT statements
   - Use proper field API names (not labels)

3. **Common Field Patterns**:
   - Accounts: Id, Name, Type, Industry, Phone, Website, BillingCity, BillingState
   - Contacts: Id, FirstName, LastName, Email, Phone, AccountId, Account.Name
   - Opportunities: Id, Name, Amount, StageName, CloseDate, AccountId, Account.Name
   - Cases: Id, CaseNumber, Subject, Status, Priority, AccountId, Account.Name

4. **Relationship Queries**:
   - Parent-to-child: Account.Name (not Account_Name)
   - Use dot notation for relationships: Contact.Account.Name
   - Limit relationship depth to avoid performance issues
```

### 📋 SOQL Query Templates

#### Account Queries
```
# Basic Account Query
SELECT Id, Name, Type, Industry, Phone, Website, BillingCity, BillingState 
FROM Account 
WHERE [condition] 
ORDER BY CreatedDate DESC 
LIMIT 10

# Account with Opportunities
SELECT Id, Name, Type, (SELECT Id, Name, Amount, StageName FROM Opportunities) 
FROM Account 
WHERE [condition]

# Search Accounts by Name
SELECT Id, Name, Type, Industry, Phone 
FROM Account 
WHERE Name LIKE '%[search_term]%' 
ORDER BY Name ASC 
LIMIT 20
```

#### Contact Queries
```
# Basic Contact Query
SELECT Id, FirstName, LastName, Email, Phone, AccountId, Account.Name 
FROM Contact 
WHERE [condition] 
ORDER BY LastName ASC 
LIMIT 10

# Contacts by Account
SELECT Id, FirstName, LastName, Email, Phone 
FROM Contact 
WHERE AccountId = '[account_id]' 
ORDER BY LastName ASC
```

#### Opportunity Queries
```
# Basic Opportunity Query
SELECT Id, Name, Amount, StageName, CloseDate, AccountId, Account.Name, 
       Implementation_Status__c, Jira_Project_Key__c 
FROM Opportunity 
WHERE [condition] 
ORDER BY CloseDate DESC 
LIMIT 10

# Opportunities at Risk
SELECT Id, Name, Amount, StageName, Account.Name, Implementation_Status__c 
FROM Opportunity 
WHERE Implementation_Status__c = 'At Risk' 
ORDER BY CloseDate ASC
```

#### Case Queries
```
# Basic Case Query
SELECT Id, CaseNumber, Subject, Status, Priority, AccountId, Account.Name, 
       Jira_Issue_Key__c 
FROM Case 
WHERE [condition] 
ORDER BY CreatedDate DESC 
LIMIT 10

# High Priority Cases
SELECT Id, CaseNumber, Subject, Status, Account.Name 
FROM Case 
WHERE Priority = 'High' AND Status != 'Closed' 
ORDER BY CreatedDate ASC
```

### 🚨 SOQL Error Prevention Prompt
```
Before executing any Salesforce operation, ask yourself:

1. **Am I trying to read or write data?**
   - READ: Use SELECT queries with salesforce_query()
   - WRITE: Use salesforce_create() for insert/update operations

2. **Is my WHERE clause properly formatted?**
   - Text fields: Name = 'Exact Match' or Name LIKE '%Partial%'
   - Dates: CreatedDate = TODAY or CloseDate >= 2024-01-01
   - Numbers: Amount > 1000
   - Booleans: IsActive = true

3. **Are my field names correct?**
   - Use API names, not labels
   - Custom fields end with __c
   - Relationship fields use dot notation

4. **Common Mistakes to Avoid**:
   - ❌ UPDATE Opportunity SET... (This is NOT SOQL)
   - ❌ Name LIKE 'Stella Pavlova' (Use % wildcards)
   - ❌ Account_Name (Use Account.Name for relationships)
   - ❌ Missing quotes around text values
```

## JQL (Jira Query Language) Prompts

### 🔧 Core JQL Rules Prompt
```
When working with Jira JQL queries, ALWAYS follow these rules:

1. **Basic JQL Structure**:
   - field operator value
   - Use AND, OR for multiple conditions
   - Use parentheses for complex logic
   - Case-sensitive for field names, case-insensitive for values

2. **Common Fields**:
   - project: Project key or name
   - summary: Issue title/summary
   - description: Issue description
   - status: Current status
   - assignee: Assigned user
   - reporter: User who created the issue
   - created: Creation date
   - updated: Last update date
   - priority: Issue priority
   - type: Issue type (Bug, Task, Story, etc.)

3. **Operators**:
   - = (equals), != (not equals)
   - ~ (contains), !~ (does not contain)
   - IN, NOT IN (list of values)
   - IS EMPTY, IS NOT EMPTY
   - >, <, >=, <= (for dates and numbers)

4. **Date Formats**:
   - Relative: -1d, -1w, -1M, -1y
   - Absolute: "2024-01-01", "2024/01/01"
   - Functions: now(), startOfDay(), endOfWeek()
```

### 📋 JQL Query Templates

#### Project-Based Queries
```
# All issues in a project
project = "TECH"

# Recent issues in project
project = "TECH" AND created >= -7d

# Open issues in project
project = "TECH" AND status != "Done" AND status != "Closed"

# High priority issues
project = "TECH" AND priority = "High" ORDER BY created DESC
```

#### Status-Based Queries
```
# Open issues
status IN ("To Do", "In Progress", "In Review")

# Recently closed issues
status IN ("Done", "Closed") AND resolved >= -7d

# Overdue issues
status != "Done" AND duedate < now()
```

#### Assignment Queries
```
# Unassigned issues
assignee IS EMPTY

# My assigned issues
assignee = currentUser()

# Issues assigned to specific user
assignee = "john.doe@company.com"
```

#### Text Search Queries
```
# Search in summary
summary ~ "bug"

# Search in summary and description
text ~ "Everything Power Button"

# Exact match in summary
summary = "Everything Power Button Bug"
```

#### Date-Based Queries
```
# Created today
created >= startOfDay()

# Updated this week
updated >= startOfWeek()

# Created in date range
created >= "2024-01-01" AND created <= "2024-01-31"
```

### 🚨 JQL Error Prevention Prompt
```
Before executing any JQL query, verify:

1. **Project Key Format**:
   - ✅ project = "TECH"
   - ❌ project = TECH (missing quotes)

2. **Text Search**:
   - ✅ summary ~ "power button" (contains)
   - ✅ summary = "Exact Title" (exact match)
   - ❌ summary LIKE "%power%" (LIKE is not JQL)

3. **Status Values**:
   - Use exact status names: "To Do", "In Progress", "Done"
   - Check your Jira instance for exact status names

4. **Date Formats**:
   - ✅ created >= -7d (relative)
   - ✅ created >= "2024-01-01" (absolute)
   - ❌ created >= 2024-01-01 (missing quotes)

5. **Common Mistakes**:
   - ❌ Using SQL syntax (SELECT, FROM, WHERE)
   - ❌ Using LIKE instead of ~ (contains)
   - ❌ Forgetting quotes around text values
   - ❌ Using wrong field names (check Jira field names)
```

## Integration Best Practices

### 🔄 Cross-System Query Coordination
```
When working with both Salesforce and Jira:

1. **Consistent Naming**:
   - Use same identifiers across systems
   - Store Jira keys in Salesforce: Jira_Project_Key__c, Jira_Issue_Key__c
   - Store Salesforce IDs in Jira custom fields

2. **Query Sequence**:
   - First query Salesforce for business context
   - Then query Jira for technical details
   - Link results using stored keys/IDs

3. **Error Handling**:
   - Always validate query syntax before execution
   - Provide fallback queries if primary query fails
   - Log query patterns for debugging
```

### 📊 Query Performance Tips
```
SOQL Performance:
- Always use LIMIT clauses
- Index WHERE clause fields when possible
- Avoid complex relationship queries in loops
- Use selective WHERE clauses

JQL Performance:
- Use specific project filters
- Limit date ranges when possible
- Avoid complex text searches on large datasets
- Use ORDER BY sparingly
```

## Usage Examples

### Example 1: Finding Related Records
```
# Step 1: Find Salesforce Account
SOQL: SELECT Id, Name FROM Account WHERE Name LIKE '%Stella Pavlova%' LIMIT 1

# Step 2: Find related Opportunities
SOQL: SELECT Id, Name, Jira_Project_Key__c FROM Opportunity WHERE AccountId = '[account_id]'

# Step 3: Find related Jira issues
JQL: project = "TECH" AND summary ~ "Modernization"
```

### Example 2: Status Updates
```
# Step 1: Query current status
SOQL: SELECT Id, Implementation_Status__c FROM Opportunity WHERE Id = '[opp_id]'

# Step 2: Update status (NOT with SOQL!)
Use: salesforce_create(sobject_type="Opportunity", data={"Id": "[opp_id]", "Implementation_Status__c": "At Risk"})

# Step 3: Create related Jira issue
Use: jira_create_issue(project_key="TECH", summary="Issue Title", description="Details")
```

## Prompt Templates for AI Assistants

### SOQL Query Generation Prompt
```
Generate a SOQL query following these requirements:
- Always include Id field
- Use proper API field names
- Include relationship fields with dot notation
- Add appropriate WHERE, ORDER BY, and LIMIT clauses
- Validate that this is a SELECT query, not an UPDATE

Query purpose: [describe what you need]
Object: [Salesforce object name]
Conditions: [filtering criteria]
```

### JQL Query Generation Prompt
```
Generate a JQL query following these requirements:
- Use proper JQL syntax (not SQL)
- Include project filter when relevant
- Use appropriate operators (=, ~, IN, etc.)
- Format dates correctly
- Add ORDER BY if needed

Query purpose: [describe what you need]
Project: [Jira project key]
Conditions: [filtering criteria]
```

This comprehensive guide should significantly improve the consistency and reliability of your SOQL and JQL queries!
