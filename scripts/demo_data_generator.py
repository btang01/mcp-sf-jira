#!/usr/bin/env python3
"""
Demo Data Generator for MCP Integration
Creates realistic Salesforce and Jira data with cross-system relationships
"""

import json
import requests
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
    
    response = requests.post(SALESFORCE_API, json=payload)
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            return json.loads(result["data"])
        else:
            print(f"Salesforce tool error: {result.get('error')}")
            return None
    else:
        print(f"HTTP error calling Salesforce: {response.status_code}")
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
    
    response = requests.post(JIRA_API, json=payload)
    if response.status_code == 200:
        result = response.json()
        if "result" in result:
            content = result["result"]["content"][0]["text"]
            return json.loads(content)
        else:
            print(f"Jira tool error: {result.get('error')}")
            return None
    else:
        print(f"HTTP error calling Jira: {response.status_code}")
        return None

def create_demo_accounts():
    """Create demo accounts"""
    accounts = [
        {
            "Name": "TechCorp Enterprise",
            "Industry": "Technology",
            "Type": "Customer - Direct",
            "Jira_Project_Keys__c": "TECH, IMPL"
        },
        {
            "Name": "StartupCo",
            "Industry": "Technology", 
            "Type": "Customer - Direct",
            "Jira_Project_Keys__c": "IMPL"
        },
        {
            "Name": "MegaCorp Industries",
            "Industry": "Manufacturing",
            "Type": "Customer - Channel",
            "Jira_Project_Keys__c": "TECH, IMPL, SUPPORT"
        },
        {
            "Name": "FinanceFirst Bank",
            "Industry": "Financial Services",
            "Type": "Customer - Direct",
            "Jira_Project_Keys__c": "SUPPORT"
        },
        {
            "Name": "HealthTech Solutions",
            "Industry": "Healthcare",
            "Type": "Prospect",
            "Jira_Project_Keys__c": "TECH"
        }
    ]
    
    created_accounts = []
    print("Creating demo accounts...")
    
    for account_data in accounts:
        result = call_salesforce_tool("salesforce_create", {
            "sobject_type": "Account",
            "data": account_data
        })
        
        if result and result.get("success"):
            account_id = result["id"]
            created_accounts.append({
                "id": account_id,
                "name": account_data["Name"],
                "jira_projects": account_data["Jira_Project_Keys__c"]
            })
            print(f"✓ Created account: {account_data['Name']} ({account_id})")
        else:
            print(f"✗ Failed to create account: {account_data['Name']}")
        
        time.sleep(0.5)  # Rate limiting
    
    return created_accounts

def create_demo_opportunities(accounts):
    """Create demo opportunities with custom fields"""
    opportunities = [
        {
            "account_name": "TechCorp Enterprise",
            "Name": "TechCorp Platform Expansion",
            "Amount": 500000,
            "StageName": "Negotiation/Review",
            "CloseDate": (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d'),
            "Jira_Project_Key__c": "IMPL",
            "Implementation_Status__c": "At Risk"
        },
        {
            "account_name": "StartupCo",
            "Name": "StartupCo Initial Implementation",
            "Amount": 150000,
            "StageName": "Closed Won",
            "CloseDate": (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            "Jira_Project_Key__c": "IMPL",
            "Implementation_Status__c": "Complete"
        },
        {
            "account_name": "MegaCorp Industries",
            "Name": "MegaCorp Enterprise License",
            "Amount": 1000000,
            "StageName": "Proposal/Price Quote",
            "CloseDate": (datetime.now() + timedelta(days=45)).strftime('%Y-%m-%d'),
            "Jira_Project_Key__c": "IMPL",
            "Implementation_Status__c": "Blocked"
        },
        {
            "account_name": "FinanceFirst Bank",
            "Name": "FinanceFirst Security Upgrade",
            "Amount": 250000,
            "StageName": "Needs Analysis",
            "CloseDate": (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d'),
            "Jira_Project_Key__c": "TECH",
            "Implementation_Status__c": "Not Started"
        }
    ]
    
    created_opportunities = []
    print("\nCreating demo opportunities...")
    
    for opp_data in opportunities:
        # Find account ID
        account_id = None
        for account in accounts:
            if account["name"] == opp_data["account_name"]:
                account_id = account["id"]
                break
        
        if not account_id:
            print(f"✗ Account not found for opportunity: {opp_data['Name']}")
            continue
        
        # Remove account_name from data and add AccountId
        opp_create_data = {k: v for k, v in opp_data.items() if k != "account_name"}
        opp_create_data["AccountId"] = account_id
        
        result = call_salesforce_tool("salesforce_create", {
            "sobject_type": "Opportunity",
            "data": opp_create_data
        })
        
        if result and result.get("success"):
            opp_id = result["id"]
            created_opportunities.append({
                "id": opp_id,
                "name": opp_data["Name"],
                "account_id": account_id,
                "account_name": opp_data["account_name"],
                "jira_project": opp_data["Jira_Project_Key__c"],
                "status": opp_data["Implementation_Status__c"]
            })
            print(f"✓ Created opportunity: {opp_data['Name']} ({opp_id})")
        else:
            print(f"✗ Failed to create opportunity: {opp_data['Name']}")
        
        time.sleep(0.5)
    
    return created_opportunities

def create_demo_cases(accounts):
    """Create demo cases with Jira issue links"""
    cases = [
        {
            "account_name": "TechCorp Enterprise",
            "Subject": "Performance Issues - Database Slowdown",
            "Priority": "High",
            "Status": "New",
            "Jira_Issue_Key__c": "TECH-1"
        },
        {
            "account_name": "TechCorp Enterprise", 
            "Subject": "Integration Timeout Errors",
            "Priority": "Critical",
            "Status": "Working",
            "Jira_Issue_Key__c": "TECH-2"
        },
        {
            "account_name": "MegaCorp Industries",
            "Subject": "Security Configuration Issues",
            "Priority": "High",
            "Status": "New",
            "Jira_Issue_Key__c": "TECH-3"
        },
        {
            "account_name": "MegaCorp Industries",
            "Subject": "Data Migration Problems",
            "Priority": "Critical",
            "Status": "Escalated",
            "Jira_Issue_Key__c": "IMPL-1"
        },
        {
            "account_name": "FinanceFirst Bank",
            "Subject": "Authentication Module Bug",
            "Priority": "Medium",
            "Status": "Working",
            "Jira_Issue_Key__c": "SUPPORT-1"
        }
    ]
    
    created_cases = []
    print("\nCreating demo cases...")
    
    for case_data in cases:
        # Find account ID
        account_id = None
        for account in accounts:
            if account["name"] == case_data["account_name"]:
                account_id = account["id"]
                break
        
        if not account_id:
            print(f"✗ Account not found for case: {case_data['Subject']}")
            continue
        
        # Remove account_name from data and add AccountId
        case_create_data = {k: v for k, v in case_data.items() if k != "account_name"}
        case_create_data["AccountId"] = account_id
        
        result = call_salesforce_tool("salesforce_create", {
            "sobject_type": "Case",
            "data": case_create_data
        })
        
        if result and result.get("success"):
            case_id = result["id"]
            created_cases.append({
                "id": case_id,
                "subject": case_data["Subject"],
                "account_id": account_id,
                "account_name": case_data["account_name"],
                "jira_issue": case_data["Jira_Issue_Key__c"],
                "priority": case_data["Priority"]
            })
            print(f"✓ Created case: {case_data['Subject']} ({case_id})")
        else:
            print(f"✗ Failed to create case: {case_data['Subject']}")
        
        time.sleep(0.5)
    
    return created_cases

def create_demo_jira_issues(cases):
    """Create Jira issues linked to Salesforce cases"""
    jira_issues = [
        {
            "project_key": "TECH",
            "summary": "Database Performance Optimization",
            "description": "Optimize database queries for TechCorp integration performance issues.\nSF_CASE_ID: {case_id}",
            "issue_type": "Bug",
            "case_subject": "Performance Issues - Database Slowdown"
        },
        {
            "project_key": "TECH", 
            "summary": "API Timeout Configuration Fix",
            "description": "Fix timeout configuration for TechCorp API integration.\nSF_CASE_ID: {case_id}",
            "issue_type": "Bug",
            "case_subject": "Integration Timeout Errors"
        },
        {
            "project_key": "TECH",
            "summary": "Security Configuration Review",
            "description": "Review and fix security configuration for MegaCorp.\nSF_CASE_ID: {case_id}",
            "issue_type": "Task",
            "case_subject": "Security Configuration Issues"
        },
        {
            "project_key": "IMPL",
            "summary": "Data Migration Script Fix",
            "description": "Fix data migration issues for MegaCorp implementation.\nSF_CASE_ID: {case_id}",
            "issue_type": "Bug",
            "case_subject": "Data Migration Problems"
        },
        {
            "project_key": "SUPPORT",
            "summary": "Authentication Module Debug",
            "description": "Debug authentication module for FinanceFirst.\nSF_CASE_ID: {case_id}",
            "issue_type": "Bug",
            "case_subject": "Authentication Module Bug"
        }
    ]
    
    created_jira_issues = []
    print("\nCreating Jira issues...")
    
    for jira_data in jira_issues:
        # Find corresponding case
        case_id = None
        for case in cases:
            if case["subject"] == jira_data["case_subject"]:
                case_id = case["id"]
                break
        
        if not case_id:
            print(f"✗ Case not found for Jira issue: {jira_data['summary']}")
            continue
        
        # Update description with actual case ID
        description = jira_data["description"].format(case_id=case_id)
        
        result = call_jira_tool("jira_create_issue", {
            "project_key": jira_data["project_key"],
            "summary": jira_data["summary"],
            "description": description,
            "issue_type": jira_data["issue_type"]
        })
        
        if result and result.get("key"):
            jira_key = result["key"]
            created_jira_issues.append({
                "key": jira_key,
                "summary": jira_data["summary"],
                "project": jira_data["project_key"],
                "case_id": case_id
            })
            print(f"✓ Created Jira issue: {jira_key} - {jira_data['summary']}")
        else:
            print(f"✗ Failed to create Jira issue: {jira_data['summary']}")
        
        time.sleep(0.5)
    
    return created_jira_issues

def create_demo_contacts(accounts):
    """Create demo contacts"""
    contacts = [
        {
            "account_name": "TechCorp Enterprise",
            "FirstName": "Sarah",
            "LastName": "Johnson",
            "Email": "sarah.johnson@techcorp.com",
            "Title": "CTO"
        },
        {
            "account_name": "TechCorp Enterprise",
            "FirstName": "Mike",
            "LastName": "Chen",
            "Email": "mike.chen@techcorp.com", 
            "Title": "VP Engineering"
        },
        {
            "account_name": "StartupCo",
            "FirstName": "Alex",
            "LastName": "Rodriguez",
            "Email": "alex@startupco.com",
            "Title": "CEO"
        },
        {
            "account_name": "MegaCorp Industries",
            "FirstName": "Jennifer",
            "LastName": "Williams",
            "Email": "j.williams@megacorp.com",
            "Title": "IT Director"
        }
    ]
    
    created_contacts = []
    print("\nCreating demo contacts...")
    
    for contact_data in contacts:
        # Find account ID
        account_id = None
        for account in accounts:
            if account["name"] == contact_data["account_name"]:
                account_id = account["id"]
                break
        
        if not account_id:
            print(f"✗ Account not found for contact: {contact_data['FirstName']} {contact_data['LastName']}")
            continue
        
        # Remove account_name from data and add AccountId
        contact_create_data = {k: v for k, v in contact_data.items() if k != "account_name"}
        contact_create_data["AccountId"] = account_id
        
        result = call_salesforce_tool("salesforce_create", {
            "sobject_type": "Contact",
            "data": contact_create_data
        })
        
        if result and result.get("success"):
            contact_id = result["id"]
            created_contacts.append({
                "id": contact_id,
                "name": f"{contact_data['FirstName']} {contact_data['LastName']}",
                "account_id": account_id,
                "title": contact_data["Title"]
            })
            print(f"✓ Created contact: {contact_data['FirstName']} {contact_data['LastName']} ({contact_id})")
        else:
            print(f"✗ Failed to create contact: {contact_data['FirstName']} {contact_data['LastName']}")
        
        time.sleep(0.5)
    
    return created_contacts

def main():
    """Generate all demo data"""
    print("🚀 Starting MCP Demo Data Generation")
    print("=" * 50)
    
    try:
        # Create accounts first (they're referenced by other objects)
        accounts = create_demo_accounts()
        
        # Create opportunities
        opportunities = create_demo_opportunities(accounts)
        
        # Create cases
        cases = create_demo_cases(accounts)
        
        # Create contacts
        contacts = create_demo_contacts(accounts)
        
        # Create Jira issues (linked to cases)
        jira_issues = create_demo_jira_issues(cases)
        
        print("\n" + "=" * 50)
        print("✅ Demo Data Generation Complete!")
        print(f"Created: {len(accounts)} accounts, {len(opportunities)} opportunities, {len(cases)} cases, {len(contacts)} contacts, {len(jira_issues)} Jira issues")
        
        # Print summary for demo
        print("\n🎯 Demo Scenarios Created:")
        print("1. TechCorp Enterprise - At Risk Deal ($500K)")
        print("   - 2 Critical cases with linked Jira issues (TECH-1, TECH-2)")
        print("   - Implementation Status: At Risk")
        
        print("2. MegaCorp Industries - Blocked Deal ($1M)")
        print("   - 2 High priority cases with linked Jira issues (TECH-3, IMPL-1)")
        print("   - Implementation Status: Blocked")
        
        print("3. StartupCo - Success Story ($150K)")
        print("   - Implementation Status: Complete")
        
        print("\n🤖 Try asking the agent:")
        print("- 'What opportunities are at risk?'")
        print("- 'Show me cases related to TechCorp'")
        print("- 'What Jira issues are blocking implementations?'")
        
    except Exception as e:
        print(f"\n❌ Error during demo data generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
