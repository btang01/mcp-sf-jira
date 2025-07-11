#!/usr/bin/env python3
"""
Simple Salesforce HTTP Server (No MCP dependencies)
Provides HTTP endpoints for Salesforce operations
"""

import json
import logging
import os
from typing import Dict, Any
from simple_salesforce import Salesforce
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
app = FastAPI(title="Salesforce HTTP Server", version="1.0.0")

# Global Salesforce connection
sf = None

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

def get_salesforce_connection():
    """Get or create Salesforce connection"""
    global sf
    if sf is None:
        try:
            # Use simple username/password authentication
            sf = Salesforce(
                username=os.getenv('SALESFORCE_USERNAME'),
                password=os.getenv('SALESFORCE_PASSWORD'),
                security_token=os.getenv('SALESFORCE_SECURITY_TOKEN')
            )
            logger.info("Salesforce connection established")
        except Exception as e:
            logger.error(f"Failed to connect to Salesforce: {e}")
            raise
    return sf

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        get_salesforce_connection()
        return {"status": "healthy", "service": "salesforce-simple"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/tools")
async def get_tools():
    """Get available tools"""
    tools = [
        {"name": "salesforce_query", "description": "Execute SOQL queries"},
        {"name": "salesforce_create", "description": "Create Salesforce records"},
        {"name": "salesforce_query_accounts", "description": "Query accounts"},
        {"name": "salesforce_query_contacts", "description": "Query contacts"},
        {"name": "salesforce_connection_info", "description": "Get connection info"}
    ]
    return {"tools": tools}

@app.post("/mcp/call")
async def call_tool(request: ToolRequest):
    """Handle tool calls via HTTP"""
    try:
        tool_name = request.params.get("name")
        arguments = request.params.get("arguments", {})
        
        if tool_name == "salesforce_query":
            result = salesforce_query(**arguments)
        elif tool_name == "salesforce_create":
            result = salesforce_create(**arguments)
        elif tool_name == "salesforce_query_accounts":
            result = salesforce_query_accounts(**arguments)
        elif tool_name == "salesforce_query_contacts":
            result = salesforce_query_contacts(**arguments)
        elif tool_name == "salesforce_connection_info":
            result = salesforce_connection_info()
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

def salesforce_query(query: str) -> str:
    """Execute SOQL query"""
    try:
        sf_conn = get_salesforce_connection()
        result = sf_conn.query(query)
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Query failed: {e}")
        return f"Error executing query: {str(e)}"

def salesforce_create(sobject_type: str, data: Dict[str, Any]) -> str:
    """Create a new record"""
    try:
        sf_conn = get_salesforce_connection()
        sobject = getattr(sf_conn, sobject_type)
        result = sobject.create(data)
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Create operation failed: {e}")
        return f"Error creating record: {str(e)}"

def salesforce_query_accounts(limit: int = 10, where_clause: str = "") -> str:
    """Query Salesforce accounts"""
    try:
        base_query = "SELECT Id, Name, Type, Industry, Phone, Website FROM Account"
        
        if where_clause:
            query = f"{base_query} WHERE {where_clause} LIMIT {limit}"
        else:
            query = f"{base_query} ORDER BY CreatedDate DESC LIMIT {limit}"
        
        sf_conn = get_salesforce_connection()
        result = sf_conn.query(query)
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Account query failed: {e}")
        return f"Error querying accounts: {str(e)}"

def salesforce_query_contacts(limit: int = 10, where_clause: str = "") -> str:
    """Query Salesforce contacts"""
    try:
        base_query = "SELECT Id, FirstName, LastName, Email, Phone, Account.Name FROM Contact"
        
        if where_clause:
            query = f"{base_query} WHERE {where_clause} LIMIT {limit}"
        else:
            query = f"{base_query} ORDER BY CreatedDate DESC LIMIT {limit}"
        
        sf_conn = get_salesforce_connection()
        result = sf_conn.query(query)
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Contact query failed: {e}")
        return f"Error querying contacts: {str(e)}"

def salesforce_connection_info() -> str:
    """Get connection info"""
    try:
        sf_conn = get_salesforce_connection()
        info = {
            "instance_url": sf_conn.sf_instance,
            "connected": True,
            "session_active": bool(sf_conn.session_id)
        }
        return json.dumps(info)
    except Exception as e:
        logger.error(f"Connection info failed: {e}")
        return f"Error getting connection info: {str(e)}"

if __name__ == "__main__":
    port = int(os.getenv('MCP_SERVER_PORT', 8001))
    host = os.getenv('MCP_SERVER_HOST', '0.0.0.0')
    
    logger.info(f"Starting Simple Salesforce HTTP server on {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")