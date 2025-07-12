# 🔧 **Salesforce Custom Fields Setup Guide**

This guide explains how to create the custom fields needed for the MCP demo system to work properly.

---

## 🚨 **Required Custom Fields**

The MCP system expects certain custom fields to exist in your Salesforce org. **You must create these fields** before the system will work without errors.

---

## 📋 **Step-by-Step Setup Instructions**

### **1. Access Salesforce Setup**
1. Log into your Salesforce org
2. Click the **gear icon** (⚙️) in the top right
3. Select **Setup**

### **2. Navigate to Object Manager**
1. In Setup, find **Object Manager** in the left sidebar
2. Click **Object Manager**

---

## 🏢 **Account Object Custom Fields**

### **Field 1: Jira_Project_Keys__c**
1. In Object Manager, click **Account**
2. Click **Fields & Relationships**
3. Click **New**
4. Select **Text** → **Next**
5. Configure:
   - **Field Label**: `Jira Project Keys`
   - **Length**: `255`
   - **Field Name**: `Jira_Project_Keys` (will auto-generate as `Jira_Project_Keys__c`)
   - **Description**: `Comma-separated list of Jira project keys associated with this account`
   - **Help Text**: `Example: TECH, IMPL, SUPPORT`
6. Click **Next** → **Next** → **Save**

---

## 💼 **Opportunity Object Custom Fields**

### **Field 1: Implementation_Status__c**
1. In Object Manager, click **Opportunity**
2. Click **Fields & Relationships**
3. Click **New**
4. Select **Picklist** → **Next**
5. Configure:
   - **Field Label**: `Implementation Status`
   - **Field Name**: `Implementation_Status` (will auto-generate as `Implementation_Status__c`)
   - **Values** (enter one per line):
     ```
     Not Started
     At Risk
     Blocked
     Complete
     ```
   - **Description**: `Current status of the implementation project`
   - **Default Value**: `Not Started`
6. Click **Next** → **Next** → **Save**

### **Field 2: Jira_Project_Key__c**
1. Still in **Opportunity** object
2. Click **New**
3. Select **Text** → **Next**
4. Configure:
   - **Field Label**: `Jira Project Key`
   - **Length**: `50`
   - **Field Name**: `Jira_Project_Key` (will auto-generate as `Jira_Project_Key__c`)
   - **Description**: `Primary Jira project key for this opportunity`
   - **Help Text**: `Example: IMPL, TECH`
5. Click **Next** → **Next** → **Save**

---

## 🎫 **Case Object Custom Fields**

### **Field 1: Jira_Issue_Key__c**
1. In Object Manager, click **Case**
2. Click **Fields & Relationships**
3. Click **New**
4. Select **Text** → **Next**
5. Configure:
   - **Field Label**: `Jira Issue Key`
   - **Length**: `50`
   - **Field Name**: `Jira_Issue_Key` (will auto-generate as `Jira_Issue_Key__c`)
   - **Description**: `Jira issue key linked to this case`
   - **Help Text**: `Example: TECH-1, IMPL-5, SUPPORT-123`
6. Click **Next** → **Next** → **Save**

---

## ✅ **Verification Steps**

After creating all fields, verify they exist:

### **Check Account Fields**
```sql
-- Test query in Developer Console or Workbench
SELECT Id, Name, Jira_Project_Keys__c FROM Account LIMIT 1
```

### **Check Opportunity Fields**
```sql
SELECT Id, Name, Implementation_Status__c, Jira_Project_Key__c FROM Opportunity LIMIT 1
```

### **Check Case Fields**
```sql
SELECT Id, CaseNumber, Jira_Issue_Key__c FROM Case LIMIT 1
```

---

## 🎯 **Field Usage Examples**

### **Account Example**
```json
{
  "Name": "TechCorp Enterprise",
  "Jira_Project_Keys__c": "TECH, IMPL, SUPPORT"
}
```

### **Opportunity Example**
```json
{
  "Name": "TechCorp Platform Expansion",
  "Implementation_Status__c": "At Risk",
  "Jira_Project_Key__c": "IMPL"
}
```

### **Case Example**
```json
{
  "Subject": "Database Performance Issues",
  "Jira_Issue_Key__c": "TECH-1"
}
```

---

## 🚀 **After Setup**

Once you've created all custom fields:

1. **Restart your MCP containers**:
   ```bash
   cd docker
   docker-compose down
   docker-compose up -d
   ```

2. **Test the system**:
   ```bash
   curl http://localhost:8000/api/health
   ```

3. **Run the demo data generator**:
   ```bash
   cd scripts
   python demo_data_generator.py
   ```

---

## 🔧 **Troubleshooting**

### **"No such column" Errors**
If you still see errors like `No such column 'Jira_Project_Keys__c'`:

1. **Double-check field names** - they must end with `__c`
2. **Verify field API names** in Salesforce Setup
3. **Check field-level security** - ensure fields are visible to your user
4. **Clear browser cache** and restart containers

### **Permission Issues**
If you get "insufficient access rights":

1. Go to **Setup** → **Profiles**
2. Edit your user's profile
3. Find **Field-Level Security**
4. Set all custom fields to **Visible** and **Editable**

---

## 💡 **Optional Enhancements**

### **Add to Page Layouts**
1. Go to **Object Manager** → **[Object]** → **Page Layouts**
2. Edit the layout
3. Drag custom fields to appropriate sections
4. Save the layout

### **Create Custom List Views**
1. Go to the object's tab (Accounts, Opportunities, Cases)
2. Create new list views that include your custom fields
3. This makes it easier to see the cross-system relationships

---

## 🎉 **You're Ready!**

After creating these custom fields, your MCP system will be able to:

- ✅ **Link Salesforce accounts to Jira projects**
- ✅ **Track opportunity implementation status**
- ✅ **Connect cases to specific Jira issues**
- ✅ **Provide intelligent cross-system insights**
- ✅ **Create comprehensive business workflows**

The AI assistant will now be able to understand relationships between your business data (Salesforce) and technical issues (Jira), providing much more intelligent and actionable responses!
