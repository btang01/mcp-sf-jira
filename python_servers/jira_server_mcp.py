#!/usr/bin/env python3
"""
Jira MCP Server with proper MCP integration
Supports both stdio and HTTP modes
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any, List

from jira import JIRA
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.types import (
    TextContent, Tool, CallToolResult, INVALID_PARAMS,
    JSONRPCError, ListToolsResult
)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Load environment variables
load_dotenv()

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/jira.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global Jira connection
jira_client = None

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

# Initialize MCP server
mcp = FastMCP("jira-mcp")


def validate_jql_query(jql: str) -> tuple[bool, str]:
    """Validate JQL query for common mistakes"""
    jql_upper = jql.upper().strip()
    
    # Check for SQL syntax (common mistake)
    if any(keyword in jql_upper for keyword in ['SELECT ', 'FROM ', 'INSERT ', 'UPDATE ', 'DELETE ']):
        return False, "❌ JQL Error: Use JQL syntax, not SQL. Example: project = \"TECH\" AND status != \"Done\""
    
    # Check for LIKE instead of ~ (common mistake)
    if 'LIKE' in jql_upper:
        return False, "❌ JQL Error: Use ~ for text search, not LIKE. Example: summary ~ \"bug\""
    
    # Check for unquoted project keys
    if 'PROJECT =' in jql_upper and '"' not in jql:
        logger.warning("JQL Query: Consider quoting project keys. Example: project = \"TECH\"")
    
    # Check for common field names
    if any(field in jql_upper for field in ['TITLE', 'NAME']):
        logger.warning("JQL Query: Use 'summary' for issue titles, not 'title' or 'name'")
    
    return True, "✅ JQL Query validation passed"

@mcp.tool()
async def jira_search_issues(jql: str = "project is not empty", max_results: int = 10) -> str:
    """Search for Jira issues using JQL with validation"""
    try:
        # Validate JQL first
        is_valid, message = validate_jql_query(jql)
        if not is_valid:
            return message
        
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
        
        return json.dumps({"issues": result, "total": len(result)}, indent=2)
    except Exception as e:
        logger.error(f"Search failed: {e}")
        # Provide helpful error message based on common issues
        error_msg = str(e).lower()
        if "field" in error_msg and "does not exist" in error_msg:
            return f"❌ JQL Error: Invalid field name. Check Jira field names (use 'summary' not 'title').\nOriginal error: {str(e)}"
        elif "project" in error_msg and "does not exist" in error_msg:
            return f"❌ JQL Error: Invalid project key. Check project exists and use quotes.\nOriginal error: {str(e)}"
        else:
            return f"❌ JQL Error: {str(e)}"

@mcp.tool()
async def jira_get_issue(issue_key: str) -> str:
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
        
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Get issue failed: {e}")
        return f"Error getting issue {issue_key}: {str(e)}"

@mcp.tool()
async def jira_create_issue(project_key: str, summary: str, description: str = "", issue_type: str = "Task") -> str:
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
        
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Create issue failed: {e}")
        return f"Error creating issue: {str(e)}"

# HTTP mode support
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

# Check if we should run in HTTP mode
if os.getenv('MCP_SERVER_PORT'):
    # HTTP mode with FastAPI
    app = FastAPI(title="Jira MCP Server", version="1.0.0")
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        try:
            jira = get_jira_connection()
            # Simple test - get server info
            server_info = jira.server_info()
            return {"status": "healthy", "service": "jira-mcp"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    @app.get("/tools")
    async def get_tools():
        """Get available tools"""
        # Get tools from the MCP server directly
        tools = await mcp.list_tools()
        return {"tools": [tool.model_dump() for tool in tools]}
    
    @app.post("/mcp/call")
    async def call_tool_http(request: ToolRequest):
        """Handle tool calls via HTTP"""
        try:
            tool_name = request.params.get("name")
            arguments = request.params.get("arguments", {})
            
            # Use the MCP server's call_tool method
            result = await mcp.call_tool(tool_name, arguments)
            
            # Handle the MCP result properly
            if isinstance(result, tuple) and len(result) >= 2:
                # MCP returns a tuple (content_list, metadata)
                content_list = result[0]
                if isinstance(content_list, list) and len(content_list) > 0:
                    first_content = content_list[0]
                    if hasattr(first_content, 'text'):
                        result_text = first_content.text
                    else:
                        result_text = str(first_content)
                else:
                    result_text = str(content_list)
            elif hasattr(result, 'content') and result.content:
                # Extract text from MCP result
                if isinstance(result.content, list) and len(result.content) > 0:
                    first_content = result.content[0]
                    if hasattr(first_content, 'text'):
                        result_text = first_content.text
                    else:
                        result_text = str(first_content)
                else:
                    result_text = str(result.content)
            else:
                # Fallback to string representation
                result_text = str(result)
            
            # Format result for HTTP response
            mcp_result = {
                "content": [{"type": "text", "text": result_text}]
            }
            
            return ToolResponse(result=mcp_result, id=request.id)
            
        except Exception as e:
            logger.error(f"HTTP tool execution error: {e}")
            return ToolResponse(
                error={"code": -32603, "message": f"Tool execution failed: {str(e)}"},
                id=request.id
            )
    
    if __name__ == "__main__":
        port = int(os.getenv('MCP_SERVER_PORT', 8002))
        host = os.getenv('MCP_SERVER_HOST', '0.0.0.0')
        
        logger.info(f"Starting Jira MCP HTTP server on {host}:{port}")
        uvicorn.run(app, host=host, port=port, log_level="info")

else:
    # Original stdio mode
    if __name__ == "__main__":
        logger.info("Starting Jira MCP server in stdio mode")
        mcp.run()
