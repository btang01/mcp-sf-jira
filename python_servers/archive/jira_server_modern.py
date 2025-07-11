#!/usr/bin/env python3
"""
Simple Jira HTTP Server (No MCP dependencies)
Provides HTTP endpoints for Jira operations
"""

import json
import logging
import os
from typing import Dict, Any
from jira import JIRA
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="Jira HTTP Server", version="1.0.0")

# Global Jira connection
jira_client = None

class ToolRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: dict
    id: int

class ToolResponse(BaseModel):
    jsonrpc: str = "2.0"
    result: dict = None
    error: dict = None
    id: int

def get_jira_connection():
    """Get or create Jira connection"""
    global jira_client
    if jira_client is None:
        try:
            jira_host = os.getenv('JIRA_HOST')
            jira_username = os.getenv('JIRA_USERNAME')
            jira_api_token = os.getenv('JIRA_API_TOKEN')
            
            if not all([jira_host, jira_username, jira_api_token]):
                raise ValueError("Missing Jira credentials in environment variables")
            
            jira_client = JIRA(
                server=jira_host,
                basic_auth=(jira_username, jira_api_token)
            )
            logger.info("Jira connection established")
        except Exception as e:
            logger.error(f"Failed to connect to Jira: {e}")
            raise
    return jira_client

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        jira = get_jira_connection()
        # Simple test - get server info
        server_info = jira.server_info()
        return {"status": "healthy", "service": "jira-simple"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/tools")
async def get_tools():
    """Get available tools"""
    tools = [
        {"name": "jira_search_issues", "description": "Search Jira issues"},
        {"name": "jira_get_issue", "description": "Get issue details"},
        {"name": "jira_create_issue", "description": "Create new issues"}
    ]
    return {"tools": tools}

@app.post("/mcp/call")
async def call_tool(request: ToolRequest):
    """Handle tool calls via HTTP"""
    try:
        tool_name = request.params.get("name")
        arguments = request.params.get("arguments", {})
        
        if tool_name == "jira_search_issues":
            result = jira_search_issues(**arguments)
        elif tool_name == "jira_get_issue":
            result = jira_get_issue(**arguments)
        elif tool_name == "jira_create_issue":
            result = jira_create_issue(**arguments)
        else:
            return ToolResponse(
                error={"code": -32601, "message": f"Tool {tool_name} not found"},
                id=request.id
            )
        
        # Format result for MCP
        mcp_result = {
            "content": [{"type": "text", "text": str(result)}]
        }
        
        return ToolResponse(result=mcp_result, id=request.id)
        
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        return ToolResponse(
            error={"code": -32603, "message": f"Tool execution failed: {str(e)}"},
            id=request.id
        )

def jira_search_issues(jql: str = "project is not empty", max_results: int = 10) -> str:
    """Search for Jira issues using JQL"""
    try:
        jira = get_jira_connection()
        issues = jira.search_issues(jql, maxResults=max_results)
        
        result = []
        for issue in issues:
            result.append({
                "key": issue.key,
                "summary": issue.fields.summary,
                "status": str(issue.fields.status),
                "assignee": str(issue.fields.assignee) if issue.fields.assignee else "Unassigned",
                "created": str(issue.fields.created)
            })
        
        return json.dumps({"issues": result, "total": len(result)})
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return f"Error searching issues: {str(e)}"

def jira_get_issue(issue_key: str) -> str:
    """Get details of a specific issue"""
    try:
        jira = get_jira_connection()
        issue = jira.issue(issue_key)
        
        result = {
            "key": issue.key,
            "summary": issue.fields.summary,
            "description": issue.fields.description or "",
            "status": str(issue.fields.status),
            "assignee": str(issue.fields.assignee) if issue.fields.assignee else "Unassigned",
            "reporter": str(issue.fields.reporter) if issue.fields.reporter else "Unknown",
            "created": str(issue.fields.created),
            "updated": str(issue.fields.updated)
        }
        
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Get issue failed: {e}")
        return f"Error getting issue {issue_key}: {str(e)}"

def jira_create_issue(project_key: str, summary: str, description: str = "", issue_type: str = "Task") -> str:
    """Create a new Jira issue"""
    try:
        jira = get_jira_connection()
        
        issue_dict = {
            'project': {'key': project_key},
            'summary': summary,
            'description': description,
            'issuetype': {'name': issue_type}
        }
        
        new_issue = jira.create_issue(fields=issue_dict)
        
        result = {
            "key": new_issue.key,
            "id": new_issue.id,
            "url": f"{jira.server_url}/browse/{new_issue.key}",
            "summary": summary
        }
        
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Create issue failed: {e}")
        return f"Error creating issue: {str(e)}"

if __name__ == "__main__":
    port = int(os.getenv('MCP_SERVER_PORT', 8002))
    host = os.getenv('MCP_SERVER_HOST', '0.0.0.0')
    
    logger.info(f"Starting Simple Jira HTTP server on {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")