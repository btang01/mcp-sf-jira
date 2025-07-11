#!/usr/bin/env python3
"""
Simple Demo Data Generator for MCP Integration
Creates realistic Salesforce and Jira data with cross-system relationships
Uses urllib instead of requests to avoid dependencies
"""

import json
import urllib.request
import urllib.parse
import time
from datetime import datetime, timedelta

# Configuration
SALESFORCE_API = "http://localhost:8000/api/call-tool"
JIRA_API = "http://localhost:8002/mcp/call"

def call_salesforce_tool(tool_name, params):
    """Call Salesforce MCP tool via web server"""
    payload = {
        "service": "salesforce",
        "tool_name": tool_name,
        "params": params
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(SALESFORCE_API, data=data, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get("success"):
                return json.loads(result["data"])
            else:
                print(f"Salesforce tool error: {result.get('error')}")
                return None
    except Exception as e:
        print(f"HTTP error calling Salesforce: {e}")
        return None

def call_jira_tool(tool_name, params):
    """Call Jira MCP tool directly"""
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": params
        },
        "id": int(time.time() * 1000)
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(JIRA_API, data=data, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            if "result" in result:
                content = result["result"]["content"][0]["text"]
                return json.loads(content)
            else:
                print(f"Jira tool error: {result.get('error')}")
                return None
    except Exception as e:
        print(f"HTTP error calling Jira: {e}")
        return None

def create_demo_data():
    """Create all demo data in sequence"""
    print("🚀 Starting MCP Demo Data Generation")
    print("=" * 50)
    
    # Step 1: Create TechCorp Account
    print("Creating TechCorp Enterprise account...")
    techcorp_result = call_salesforce_tool("salesforce_create", {
        "sobject_type": "Account",
        "data": {
            "Name": "TechCorp Enterprise",
            "Industry": "Technology",
            "Type": "Customer - Direct",
            "Jira_Project_Keys__c": "TECH, IMPL"
        }
    })
    
    if not techcorp_result or not techcorp_result.get("success"):
        print("❌ Failed to create TechCorp account")
        return
    
    techcorp_id = techcorp_result["id"]
    print(f"✓ Created TechCorp Enterprise ({techcorp_id})")
    
    # Step 2: Create At-Risk Opportunity
    print("\nCreating at-risk opportunity...")
    opp_result = call_salesforce_tool("salesforce_create", {
        "sobject_type": "Opportunity",
        "data": {
            "Name": "TechCorp Platform Expansion",
            "Amount": 500000,
            "StageName": "Negotiation/Review",
            "CloseDate": (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d'),
            "AccountId": techcorp_id,
            "Jira_Project_Key__c": "IMPL",
            "Implementation_Status__c": "At Risk"
        }
    })
    
    if opp_result and opp_result.get("success"):
        opp_id = opp_result["id"]
        print(f"✓ Created opportunity: TechCorp Platform Expansion ({opp_id})")
    else:
        print("❌ Failed to create opportunity")
    
    # Step 3: Create Critical Cases
    print("\nCreating critical cases...")
    
    case1_result = call_salesforce_tool("salesforce_create", {
        "sobject_type": "Case",
        "data": {
            "Subject": "Performance Issues - Database Slowdown",
            "Priority": "High",
            "Status": "New",
            "AccountId": techcorp_id,
            "Jira_Issue_Key__c": "TECH-1"
        }
    })
    
    case2_result = call_salesforce_tool("salesforce_create", {
        "sobject_type": "Case", 
        "data": {
            "Subject": "Integration Timeout Errors",
            "Priority": "Critical",
            "Status": "Working",
            "AccountId": techcorp_id,
            "Jira_Issue_Key__c": "TECH-2"
        }
    })
    
    case1_id = case1_result["id"] if case1_result and case1_result.get("success") else None
    case2_id = case2_result["id"] if case2_result and case2_result.get("success") else None
    
    if case1_id:
        print(f"✓ Created case: Performance Issues ({case1_id})")
    if case2_id:
        print(f"✓ Created case: Integration Timeout ({case2_id})")
    
    # Step 4: Create Jira Issues (if Jira is working)
    print("\nCreating Jira issues...")
    
    if case1_id:
        jira1_result = call_jira_tool("jira_create_issue", {
            "project_key": "TECH",
            "summary": "Database Performance Optimization",
            "description": f"Optimize database queries for TechCorp integration performance issues.\nSF_CASE_ID: {case1_id}",
            "issue_type": "Bug"
        })
        
        if jira1_result and jira1_result.get("key"):
            print(f"✓ Created Jira issue: {jira1_result['key']} - Database Performance")
        else:
            print("⚠️  Jira issue creation failed (may need project setup)")
    
    if case2_id:
        jira2_result = call_jira_tool("jira_create_issue", {
            "project_key": "TECH",
            "summary": "API Timeout Configuration Fix", 
            "description": f"Fix timeout configuration for TechCorp API integration.\nSF_CASE_ID: {case2_id}",
            "issue_type": "Bug"
        })
        
        if jira2_result and jira2_result.get("key"):
            print(f"✓ Created Jira issue: {jira2_result['key']} - API Timeout Fix")
        else:
            print("⚠️  Jira issue creation failed (may need project setup)")
    
    # Step 5: Create Contact
    print("\nCreating key contact...")
    contact_result = call_salesforce_tool("salesforce_create", {
        "sobject_type": "Contact",
        "data": {
            "FirstName": "Sarah",
            "LastName": "Johnson", 
            "Email": "sarah.johnson@techcorp.com",
            "Title": "CTO",
            "AccountId": techcorp_id
        }
    })
    
    if contact_result and contact_result.get("success"):
        contact_id = contact_result["id"]
        print(f"✓ Created contact: Sarah Johnson ({contact_id})")
    
    print("\n" + "=" * 50)
    print("✅ Demo Data Generation Complete!")
    print("\n🎯 Demo Scenario Created:")
    print("• TechCorp Enterprise - At Risk Deal ($500K)")
    print("• 2 Critical cases with potential Jira links")
    print("• Implementation Status: At Risk")
    print("• Close Date: 15 days away")
    
    print("\n🤖 Try asking the agent:")
    print("• 'What opportunities are at risk?'")
    print("• 'Show me cases for TechCorp'")
    print("• 'What's blocking the TechCorp deal?'")

if __name__ == "__main__":
    create_demo_data()
