#!/bin/bash

echo "🚀 Creating MCP Demo Data"
echo "=========================="

# Create TechCorp Account
echo "Creating TechCorp Enterprise account..."
ACCOUNT_RESPONSE=$(curl -s -X POST http://localhost:8000/api/call-tool \
  -H "Content-Type: application/json" \
  -d '{
    "service": "salesforce",
    "tool_name": "salesforce_create",
    "params": {
      "sobject_type": "Account",
      "data": {
        "Name": "TechCorp Enterprise",
        "Industry": "Technology",
        "Type": "Customer - Direct",
        "Jira_Project_Keys__c": "TECH, IMPL"
      }
    }
  }')

# Extract account ID (basic parsing)
ACCOUNT_ID=$(echo $ACCOUNT_RESPONSE | grep -o '"id": "[^"]*"' | cut -d'"' -f4)
echo "✓ Created TechCorp Enterprise (ID: $ACCOUNT_ID)"

# Create At-Risk Opportunity
echo "Creating at-risk opportunity..."
CLOSE_DATE=$(date -v+15d +%Y-%m-%d)
OPP_RESPONSE=$(curl -s -X POST http://localhost:8000/api/call-tool \
  -H "Content-Type: application/json" \
  -d "{
    \"service\": \"salesforce\",
    \"tool_name\": \"salesforce_create\",
    \"params\": {
      \"sobject_type\": \"Opportunity\",
      \"data\": {
        \"Name\": \"TechCorp Platform Expansion\",
        \"Amount\": 500000,
        \"StageName\": \"Negotiation/Review\",
        \"CloseDate\": \"$CLOSE_DATE\",
        \"AccountId\": \"$ACCOUNT_ID\",
        \"Jira_Project_Key__c\": \"IMPL\",
        \"Implementation_Status__c\": \"At Risk\"
      }
    }
  }")

OPP_ID=$(echo $OPP_RESPONSE | grep -o '"id": "[^"]*"' | cut -d'"' -f4)
echo "✓ Created opportunity: TechCorp Platform Expansion (ID: $OPP_ID)"

# Create Critical Case 1
echo "Creating critical cases..."
CASE1_RESPONSE=$(curl -s -X POST http://localhost:8000/api/call-tool \
  -H "Content-Type: application/json" \
  -d "{
    \"service\": \"salesforce\",
    \"tool_name\": \"salesforce_create\",
    \"params\": {
      \"sobject_type\": \"Case\",
      \"data\": {
        \"Subject\": \"Performance Issues - Database Slowdown\",
        \"Priority\": \"High\",
        \"Status\": \"New\",
        \"AccountId\": \"$ACCOUNT_ID\",
        \"Jira_Issue_Key__c\": \"TECH-1\"
      }
    }
  }")

CASE1_ID=$(echo $CASE1_RESPONSE | grep -o '"id": "[^"]*"' | cut -d'"' -f4)
echo "✓ Created case: Performance Issues (ID: $CASE1_ID)"

# Create Critical Case 2
CASE2_RESPONSE=$(curl -s -X POST http://localhost:8000/api/call-tool \
  -H "Content-Type: application/json" \
  -d "{
    \"service\": \"salesforce\",
    \"tool_name\": \"salesforce_create\",
    \"params\": {
      \"sobject_type\": \"Case\",
      \"data\": {
        \"Subject\": \"Integration Timeout Errors\",
        \"Priority\": \"Critical\",
        \"Status\": \"Working\",
        \"AccountId\": \"$ACCOUNT_ID\",
        \"Jira_Issue_Key__c\": \"TECH-2\"
      }
    }
  }")

CASE2_ID=$(echo $CASE2_RESPONSE | grep -o '"id": "[^"]*"' | cut -d'"' -f4)
echo "✓ Created case: Integration Timeout (ID: $CASE2_ID)"

# Create Contact
echo "Creating key contact..."
CONTACT_RESPONSE=$(curl -s -X POST http://localhost:8000/api/call-tool \
  -H "Content-Type: application/json" \
  -d "{
    \"service\": \"salesforce\",
    \"tool_name\": \"salesforce_create\",
    \"params\": {
      \"sobject_type\": \"Contact\",
      \"data\": {
        \"FirstName\": \"Sarah\",
        \"LastName\": \"Johnson\",
        \"Email\": \"sarah.johnson@techcorp.com\",
        \"Title\": \"CTO\",
        \"AccountId\": \"$ACCOUNT_ID\"
      }
    }
  }")

CONTACT_ID=$(echo $CONTACT_RESPONSE | grep -o '"id": "[^"]*"' | cut -d'"' -f4)
echo "✓ Created contact: Sarah Johnson (ID: $CONTACT_ID)"

# Try to create Jira issues (may fail if projects don't exist)
echo "Attempting to create Jira issues..."

JIRA1_RESPONSE=$(curl -s -X POST http://localhost:8002/mcp/call \
  -H "Content-Type: application/json" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"method\": \"tools/call\",
    \"params\": {
      \"name\": \"jira_create_issue\",
      \"arguments\": {
        \"project_key\": \"TECH\",
        \"summary\": \"Database Performance Optimization\",
        \"description\": \"Optimize database queries for TechCorp integration performance issues.\\nSF_CASE_ID: $CASE1_ID\",
        \"issue_type\": \"Bug\"
      }
    },
    \"id\": 1
  }")

if echo $JIRA1_RESPONSE | grep -q '"key"'; then
  JIRA1_KEY=$(echo $JIRA1_RESPONSE | grep -o '"key":"[^"]*"' | cut -d'"' -f4)
  echo "✓ Created Jira issue: $JIRA1_KEY - Database Performance"
else
  echo "⚠️  Jira issue creation failed (may need project setup)"
fi

echo ""
echo "=========================="
echo "✅ Demo Data Creation Complete!"
echo ""
echo "🎯 Demo Scenario Created:"
echo "• TechCorp Enterprise - At Risk Deal (\$500K)"
echo "• 2 Critical cases with Jira issue references"
echo "• Implementation Status: At Risk"
echo "• Close Date: 15 days away"
echo ""
echo "📋 Record IDs:"
echo "• Account ID: $ACCOUNT_ID"
echo "• Opportunity ID: $OPP_ID"
echo "• Case 1 ID: $CASE1_ID"
echo "• Case 2 ID: $CASE2_ID"
echo "• Contact ID: $CONTACT_ID"
echo ""
echo "🤖 Try asking the agent:"
echo "• 'What opportunities are at risk?'"
echo "• 'Show me cases for TechCorp'"
echo "• 'What's blocking the TechCorp deal?'"
