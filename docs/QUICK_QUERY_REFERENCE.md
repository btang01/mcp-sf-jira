# Quick Query Reference Card

## 🚨 CRITICAL RULES

### SOQL (Salesforce)
- ✅ **READ**: `SELECT Id, Name FROM Account WHERE...`
- ❌ **NEVER**: `UPDATE Account SET Name = ...` (Use salesforce_create tool instead)
- ✅ **UPDATE**: `salesforce_create(sobject_type="Account", data={"Id": "123", "Name": "New"})`

### JQL (Jira)  
- ✅ **SEARCH**: `project = "TECH" AND summary ~ "bug"`
- ❌ **NEVER**: `SELECT * FROM issues WHERE...` (JQL is not SQL)

## 📋 Quick Templates

### SOQL Common Patterns
```sql
-- Accounts
SELECT Id, Name, Type, Industry FROM Account WHERE Name LIKE '%[term]%' LIMIT 10

-- Opportunities  
SELECT Id, Name, Amount, StageName, Account.Name, Implementation_Status__c 
FROM Opportunity WHERE AccountId = '[id]' LIMIT 10

-- Cases
SELECT Id, CaseNumber, Subject, Status, Priority, Account.Name, Jira_Issue_Key__c 
FROM Case WHERE Priority = 'High' LIMIT 10
```

### JQL Common Patterns
```jql
-- Project issues
project = "TECH" AND status != "Done" ORDER BY created DESC

-- Text search
project = "TECH" AND text ~ "power button"

-- Recent issues
project = "TECH" AND created >= -7d
```

## 🔧 Error Prevention Checklist

### Before SOQL:
- [ ] Using SELECT (not UPDATE/INSERT)?
- [ ] Included Id field?
- [ ] Used API field names (Custom__c)?
- [ ] Relationship fields use dot notation (Account.Name)?
- [ ] Added LIMIT clause?

### Before JQL:
- [ ] Using JQL syntax (not SQL)?
- [ ] Project key in quotes: `project = "TECH"`?
- [ ] Text search uses ~ (not LIKE)?
- [ ] Date format correct (-7d or "2024-01-01")?

## 💡 Pro Tips

### SOQL
- Always include `Id` field
- Use `LIKE '%term%'` for partial matches
- Custom fields end with `__c`
- Relationships: `Account.Name` not `Account_Name`

### JQL
- Use `~` for contains, `=` for exact match
- Project keys need quotes: `"TECH"`
- Relative dates: `-1d`, `-1w`, `-1M`
- Status names are case-sensitive

## 🔗 Integration Pattern
1. Query Salesforce for business context
2. Extract IDs/keys for linking
3. Query Jira using project keys
4. Update records using proper tools (not queries)

---
**Remember**: Queries are for READING, tools are for WRITING!
