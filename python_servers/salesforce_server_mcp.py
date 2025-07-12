#!/usr/bin/env python3
"""
Salesforce MCP Server with proper MCP integration
Supports both stdio and HTTP modes
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, List

from simple_salesforce import Salesforce
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
        logging.FileHandler('logs/salesforce.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global Salesforce connection
sf = None

def get_salesforce_connection():
    """Get or create Salesforce connection"""
    global sf
    if sf is None:
        try:
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

# Initialize MCP server
mcp = FastMCP("salesforce-mcp")

def validate_soql_query(query: str) -> tuple[bool, str]:
    """Validate SOQL query for common mistakes"""
    query_upper = query.upper().strip()
    
    # Check for UPDATE/INSERT/DELETE in query (should use tools instead)
    if any(keyword in query_upper for keyword in ['UPDATE ', 'INSERT ', 'DELETE ']):
        return False, "❌ SOQL Error: Use SELECT for queries. For updates, use salesforce_create tool instead."
    
    # Check if it starts with SELECT
    if not query_upper.startswith('SELECT'):
        return False, "❌ SOQL Error: Query must start with SELECT"
    
    # Check for basic structure
    if 'FROM' not in query_upper:
        return False, "❌ SOQL Error: Query must include FROM clause"
    
    # Check for LIMIT (recommended)
    if 'LIMIT' not in query_upper:
        logger.warning("SOQL Query missing LIMIT clause - consider adding for performance")
    
    # Check for common mistakes
    if 'LIKE \'' in query and '%' not in query:
        logger.warning("SOQL Query: Consider using % wildcards with LIKE for partial matches")
    
    return True, "✅ SOQL Query validation passed"

@mcp.tool()
async def salesforce_query(query: str) -> str:
    """Execute SOQL query with validation"""
    try:
        # Validate query first
        is_valid, message = validate_soql_query(query)
        if not is_valid:
            return message
        
        sf_conn = get_salesforce_connection()
        result = sf_conn.query(query)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Query failed: {e}")
        # Provide helpful error message based on common issues
        error_msg = str(e).lower()
        if "malformed" in error_msg and "update" in error_msg:
            return f"❌ SOQL Error: Cannot use UPDATE in queries. Use salesforce_create tool for updates.\nOriginal error: {str(e)}"
        elif "invalid field" in error_msg:
            return f"❌ SOQL Error: Invalid field name. Check API names (custom fields end with __c).\nOriginal error: {str(e)}"
        else:
            return f"❌ SOQL Error: {str(e)}"

@mcp.tool()
async def salesforce_create(sobject_type: str, data: Dict[str, Any]) -> str:
    """Create a new record"""
    try:
        sf_conn = get_salesforce_connection()
        sobject = getattr(sf_conn, sobject_type)
        result = sobject.create(data)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Create operation failed: {e}")
        return f"Error creating record: {str(e)}"

@mcp.tool()
async def salesforce_query_accounts(limit: int = 10, where_clause: str = "") -> str:
    """Query Salesforce accounts"""
    try:
        base_query = "SELECT Id, Name, Type, Industry, Phone, Website FROM Account"
        
        if where_clause:
            query = f"{base_query} WHERE {where_clause} LIMIT {limit}"
        else:
            query = f"{base_query} ORDER BY CreatedDate DESC LIMIT {limit}"
        
        sf_conn = get_salesforce_connection()
        result = sf_conn.query(query)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Account query failed: {e}")
        return f"Error querying accounts: {str(e)}"

@mcp.tool()
async def salesforce_query_activities(limit: int = 10, where_clause: str = "") -> str:
    """Query Salesforce activities (Tasks)"""
    try:
        base_query = "SELECT Id, Subject, Status, Priority, ActivityDate, WhatId, What.Name, WhoId, Who.Name FROM Task"
        
        if where_clause:
            query = f"{base_query} WHERE {where_clause} LIMIT {limit}"
        else:
            query = f"{base_query} ORDER BY CreatedDate DESC LIMIT {limit}"
        
        sf_conn = get_salesforce_connection()
        result = sf_conn.query(query)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Activity query failed: {e}")
        return f"Error querying activities: {str(e)}"

@mcp.tool()
async def salesforce_query_contacts(limit: int = 10, where_clause: str = "") -> str:
    """Query Salesforce contacts"""
    try:
        base_query = "SELECT Id, FirstName, LastName, Email, Phone, Account.Name FROM Contact"
        
        if where_clause:
            query = f"{base_query} WHERE {where_clause} LIMIT {limit}"
        else:
            query = f"{base_query} ORDER BY CreatedDate DESC LIMIT {limit}"
        
        sf_conn = get_salesforce_connection()
        result = sf_conn.query(query)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Contact query failed: {e}")
        return f"Error querying contacts: {str(e)}"

@mcp.tool()
async def salesforce_connection_info() -> str:
    """Get connection info"""
    try:
        sf_conn = get_salesforce_connection()
        info = {
            "instance_url": sf_conn.sf_instance,
            "connected": True,
            "session_active": bool(sf_conn.session_id)
        }
        return json.dumps(info, indent=2)
    except Exception as e:
        logger.error(f"Connection info failed: {e}")
        return f"Error getting connection info: {str(e)}"

@mcp.tool()
async def salesforce_query_opportunities(limit: int = 10, where_clause: str = "") -> str:
    """Query Salesforce opportunities"""
    try:
        # Use only standard fields that exist in all Salesforce orgs
        base_query = "SELECT Id, Name, Amount, StageName, CloseDate, AccountId, Account.Name FROM Opportunity"
        
        if where_clause:
            query = f"{base_query} WHERE {where_clause} LIMIT {limit}"
        else:
            query = f"{base_query} ORDER BY CreatedDate DESC LIMIT {limit}"
        
        sf_conn = get_salesforce_connection()
        result = sf_conn.query(query)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Opportunity query failed: {e}")
        return f"Error querying opportunities: {str(e)}"

@mcp.tool()
async def salesforce_query_cases(limit: int = 10, where_clause: str = "") -> str:
    """Query Salesforce cases"""
    try:
        # Use only standard fields that exist in all Salesforce orgs
        base_query = "SELECT Id, CaseNumber, Subject, Status, Priority, AccountId, Account.Name FROM Case"
        
        if where_clause:
            query = f"{base_query} WHERE {where_clause} LIMIT {limit}"
        else:
            query = f"{base_query} ORDER BY CreatedDate DESC LIMIT {limit}"
        
        sf_conn = get_salesforce_connection()
        result = sf_conn.query(query)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Case query failed: {e}")
        return f"Error querying cases: {str(e)}"

@mcp.tool()
async def salesforce_create_activity(subject: str, account_id: str, description: str = "", priority: str = "Normal") -> str:
    """Create a Salesforce activity (Task)"""
    try:
        sf_conn = get_salesforce_connection()
        
        # Use only standard Task fields that exist in all Salesforce orgs
        activity_data = {
            'Subject': subject,
            'WhatId': account_id,  # Link to Account or Opportunity
            'ActivityDate': datetime.now().strftime('%Y-%m-%d'),
            'Status': 'Not Started',
            'Priority': priority,
            'Description': description
        }
        
        result = sf_conn.Task.create(activity_data)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Activity creation failed: {e}")
        return f"Error creating activity: {str(e)}"

@mcp.tool()
async def salesforce_delete_activity(activity_id: str) -> str:
    """Delete a Salesforce activity (Task) by ID
    
    Args:
        activity_id: The ID of the Task/Activity to delete (starts with '00T')
    
    Returns:
        Success message or error details
    """
    try:
        sf_conn = get_salesforce_connection()
        
        # First, get the activity details before deletion for confirmation
        try:
            activity_query = f"SELECT Id, Subject, Status, Priority, ActivityDate, WhatId, What.Name, WhoId, Who.Name FROM Task WHERE Id = '{activity_id}'"
            activity_result = sf_conn.query(activity_query)
            
            if activity_result['totalSize'] == 0:
                return f"❌ Activity not found: No Task with ID '{activity_id}' exists"
            
            activity_details = activity_result['records'][0]
            
        except Exception as query_error:
            logger.warning(f"Could not query activity before deletion: {query_error}")
            activity_details = {"Id": activity_id, "Subject": "Unknown"}
        
        # Perform the deletion
        result = sf_conn.Task.delete(activity_id)
        
        if result == 204:  # HTTP 204 No Content indicates successful deletion
            return json.dumps({
                "success": True,
                "message": f"✅ Successfully deleted activity '{activity_details.get('Subject', 'Unknown')}'",
                "deleted_activity": activity_details,
                "activity_id": activity_id,
                "timestamp": datetime.now().isoformat()
            }, indent=2)
        else:
            return json.dumps({
                "success": False,
                "message": f"❌ Unexpected response from Salesforce: {result}",
                "activity_id": activity_id
            }, indent=2)
            
    except Exception as e:
        logger.error(f"Activity deletion failed: {e}")
        error_msg = str(e).lower()
        
        # Provide helpful error messages
        if "invalid id" in error_msg or "malformed id" in error_msg:
            return f"❌ Delete Error: Invalid activity ID '{activity_id}'. Task IDs should start with '00T'.\nOriginal error: {str(e)}"
        elif "insufficient access rights" in error_msg or "delete not allowed" in error_msg:
            return f"❌ Delete Error: Insufficient permissions to delete this activity.\nOriginal error: {str(e)}"
        elif "entity is deleted" in error_msg:
            return f"❌ Delete Error: Activity '{activity_id}' has already been deleted.\nOriginal error: {str(e)}"
        else:
            return f"❌ Delete Error: {str(e)}"


@mcp.tool()
async def salesforce_update_record(sobject_type: str, record_id: str, data: Dict[str, Any]) -> str:
    """Update any Salesforce record with flexible field support
    
    Args:
        sobject_type: The Salesforce object type (e.g., 'Contact', 'Account', 'Case', 'Opportunity')
        record_id: The ID of the record to update
        data: Dictionary of field names and values to update
    
    Examples:
        - Update Contact: sobject_type='Contact', record_id='003XX...', data={'FirstName': 'John', 'Email': 'john@example.com'}
        - Update Account: sobject_type='Account', record_id='001XX...', data={'Name': 'New Company Name', 'Industry': 'Technology'}
        - Update Case: sobject_type='Case', record_id='500XX...', data={'Status': 'Closed', 'Priority': 'High'}
        - Update custom fields: data={'Custom_Field__c': 'value', 'Another_Custom__c': 123}
    """
    try:
        sf_conn = get_salesforce_connection()
        
        # Get the SObject dynamically
        sobject = getattr(sf_conn, sobject_type)
        
        # Perform the update
        result = sobject.update(record_id, data)
        
        # Get updated record to show changes
        try:
            # Try to get common fields for the object type
            if sobject_type.lower() == 'contact':
                updated_record = sf_conn.query(f"SELECT Id, FirstName, LastName, Email, Phone, Account.Name FROM Contact WHERE Id = '{record_id}'")
            elif sobject_type.lower() == 'account':
                updated_record = sf_conn.query(f"SELECT Id, Name, Type, Industry, Phone, Website FROM Account WHERE Id = '{record_id}'")
            elif sobject_type.lower() == 'case':
                updated_record = sf_conn.query(f"SELECT Id, CaseNumber, Subject, Status, Priority, Account.Name FROM Case WHERE Id = '{record_id}'")
            elif sobject_type.lower() == 'opportunity':
                updated_record = sf_conn.query(f"SELECT Id, Name, Amount, StageName, CloseDate, Account.Name FROM Opportunity WHERE Id = '{record_id}'")
            else:
                # For other objects, just get Id and Name if available
                updated_record = sf_conn.query(f"SELECT Id FROM {sobject_type} WHERE Id = '{record_id}'")
            
            return json.dumps({
                "update_result": result,
                "updated_record": updated_record,
                "message": f"✅ Successfully updated {sobject_type} record {record_id}"
            }, indent=2)
            
        except Exception as query_error:
            # If we can't query the updated record, just return the update result
            logger.warning(f"Could not query updated record: {query_error}")
            return json.dumps({
                "update_result": result,
                "message": f"✅ Successfully updated {sobject_type} record {record_id}"
            }, indent=2)
            
    except Exception as e:
        logger.error(f"Update operation failed: {e}")
        error_msg = str(e).lower()
        
        # Provide helpful error messages
        if "invalid field" in error_msg:
            return f"❌ Update Error: Invalid field name. Check API names (custom fields end with __c).\nOriginal error: {str(e)}"
        elif "insufficient access rights" in error_msg:
            return f"❌ Update Error: Insufficient permissions to update this record.\nOriginal error: {str(e)}"
        elif "invalid id" in error_msg:
            return f"❌ Update Error: Invalid record ID '{record_id}'. Check the ID format.\nOriginal error: {str(e)}"
        else:
            return f"❌ Update Error: {str(e)}"

@mcp.tool()
async def salesforce_get_record_fields(sobject_type: str, record_id: str = None) -> str:
    """Get all available fields for a Salesforce object type, optionally with current values
    
    Args:
        sobject_type: The Salesforce object type (e.g., 'Contact', 'Account', 'Case')
        record_id: Optional - if provided, shows current field values for this record
    
    This helps you discover what fields are available for updates without being limited to predefined fields.
    """
    try:
        sf_conn = get_salesforce_connection()
        
        # Get object metadata to see all available fields
        sobject = getattr(sf_conn, sobject_type)
        describe_result = sobject.describe()
        
        # Extract field information
        fields_info = []
        updateable_fields = []
        
        for field in describe_result['fields']:
            field_info = {
                'name': field['name'],
                'label': field['label'],
                'type': field['type'],
                'updateable': field['updateable'],
                'required': not field['nillable'] and not field.get('defaultedOnCreate', False),
                'custom': field['custom']
            }
            
            fields_info.append(field_info)
            
            if field['updateable']:
                updateable_fields.append(field['name'])
        
        result = {
            'object_type': sobject_type,
            'total_fields': len(fields_info),
            'updateable_fields_count': len(updateable_fields),
            'updateable_fields': updateable_fields[:20],  # Show first 20 for readability
            'all_fields_info': fields_info[:10] if not record_id else fields_info[:5]  # Limit for readability
        }
        
        # If record_id provided, get current values
        if record_id:
            try:
                # Build a query with key fields
                key_fields = [f['name'] for f in fields_info if f['updateable']][:15]  # Limit to avoid query length issues
                fields_str = ', '.join(key_fields)
                
                current_record = sf_conn.query(f"SELECT {fields_str} FROM {sobject_type} WHERE Id = '{record_id}'")
                result['current_record_values'] = current_record
                result['message'] = f"✅ Found {len(updateable_fields)} updateable fields for {sobject_type}"
                
            except Exception as query_error:
                logger.warning(f"Could not query current record values: {query_error}")
                result['message'] = f"✅ Found {len(updateable_fields)} updateable fields for {sobject_type} (could not get current values)"
        else:
            result['message'] = f"✅ Found {len(updateable_fields)} updateable fields for {sobject_type}"
            result['usage_example'] = {
                'tool': 'salesforce_update_record',
                'example': {
                    'sobject_type': sobject_type,
                    'record_id': 'YOUR_RECORD_ID_HERE',
                    'data': {updateable_fields[0]: 'new_value'} if updateable_fields else {}
                }
            }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Get fields operation failed: {e}")
        return f"❌ Error getting fields for {sobject_type}: {str(e)}"

@mcp.tool()
async def salesforce_search_records(sobject_type: str, search_term: str, fields: List[str] = None, limit: int = 10) -> str:
    """Search for records using SOSL (Salesforce Object Search Language)
    
    Args:
        sobject_type: The Salesforce object type to search (e.g., 'Contact', 'Account', 'Case')
        search_term: The term to search for
        fields: Optional list of fields to return (if not provided, uses common fields)
        limit: Maximum number of results to return
    
    This is useful for finding records before updating them.
    """
    try:
        sf_conn = get_salesforce_connection()
        
        # Default fields for common object types
        if not fields:
            if sobject_type.lower() == 'contact':
                fields = ['Id', 'FirstName', 'LastName', 'Email', 'Phone', 'Account.Name']
            elif sobject_type.lower() == 'account':
                fields = ['Id', 'Name', 'Type', 'Industry', 'Phone', 'Website']
            elif sobject_type.lower() == 'case':
                fields = ['Id', 'CaseNumber', 'Subject', 'Status', 'Priority', 'Account.Name']
            elif sobject_type.lower() == 'opportunity':
                fields = ['Id', 'Name', 'Amount', 'StageName', 'CloseDate', 'Account.Name']
            else:
                fields = ['Id', 'Name']
        
        # Build SOSL query
        fields_str = ', '.join(fields)
        sosl_query = f"FIND {{{search_term}}} IN ALL FIELDS RETURNING {sobject_type}({fields_str}) LIMIT {limit}"
        
        result = sf_conn.search(sosl_query)
        
        return json.dumps({
            'search_term': search_term,
            'object_type': sobject_type,
            'results': result,
            'message': f"✅ Found {len(result)} records matching '{search_term}'"
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Search operation failed: {e}")
        return f"❌ Search Error: {str(e)}"

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
    app = FastAPI(title="Salesforce MCP Server", version="1.0.0")
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        try:
            get_salesforce_connection()
            return {"status": "healthy", "service": "salesforce-mcp"}
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
            
            # Check if tool exists
            available_tools = [
                "salesforce_query", "salesforce_create", "salesforce_query_accounts",
                "salesforce_query_contacts", "salesforce_connection_info", 
                "salesforce_query_opportunities", "salesforce_query_cases",
                "salesforce_create_activity", "salesforce_delete_activity", 
                "salesforce_update_record", "salesforce_get_record_fields", 
                "salesforce_search_records", "salesforce_query_activities"
            ]
            
            if tool_name not in available_tools:
                logger.error(f"HTTP tool execution error: Unknown tool: {tool_name}")
                return ToolResponse(
                    error={"code": -32601, "message": f"Unknown tool: {tool_name}"},
                    id=request.id
                )
            
            # Use the MCP server's call_tool method
            result = await mcp.call_tool(tool_name, arguments)
            
            # Handle the MCP result properly - fix the tuple issue
            result_text = ""
            
            if isinstance(result, CallToolResult):
                # Standard MCP CallToolResult
                if result.content and len(result.content) > 0:
                    first_content = result.content[0]
                    if isinstance(first_content, TextContent):
                        result_text = first_content.text
                    else:
                        result_text = str(first_content)
                else:
                    result_text = "No content returned"
            elif isinstance(result, tuple):
                # Handle tuple response (content_list, metadata)
                content_list = result[0] if len(result) > 0 else []
                if isinstance(content_list, list) and len(content_list) > 0:
                    first_content = content_list[0]
                    if isinstance(first_content, TextContent):
                        result_text = first_content.text
                    elif hasattr(first_content, 'text'):
                        result_text = first_content.text
                    else:
                        result_text = str(first_content)
                else:
                    result_text = str(content_list)
            elif isinstance(result, str):
                # Direct string result
                result_text = result
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
        port = int(os.getenv('MCP_SERVER_PORT', 8001))
        host = os.getenv('MCP_SERVER_HOST', '0.0.0.0')
        
        logger.info(f"Starting Salesforce MCP HTTP server on {host}:{port}")
        uvicorn.run(app, host=host, port=port, log_level="info")

else:
    # Original stdio mode
    if __name__ == "__main__":
        logger.info("Starting Salesforce MCP server in stdio mode")
        mcp.run()
