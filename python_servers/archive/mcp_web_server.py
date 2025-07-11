#!/usr/bin/env python3
"""
Simple MCP Web Server for Native Mode (No Strands SDK)
"""

import asyncio
import json
import logging
import aiohttp
import sys
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from anthropic import Anthropic
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
import os
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/mcp_web_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Pydantic models
class ToolCallRequest(BaseModel):
    service: str
    tool_name: str
    params: Dict[str, Any] = {}

class ToolCallResponse(BaseModel):
    success: bool
    data: Optional[str] = None
    error: Optional[str] = None
    timestamp: str
    execution_time_ms: Optional[float] = None

class ChatRequest(BaseModel):
    message: str
    
class ChatResponse(BaseModel):
    response: str
    success: bool
    timestamp: str
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None

@dataclass
class MCPService:
    url: str
    connected: bool
    last_activity: Optional[str]
    error: Optional[str]
    health_score: float = 1.0

class SimpleMCPWebServer:
    """Simple MCP Web Server with HTTP communication"""
    
    def __init__(self):
        from contextlib import asynccontextmanager
        
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            """Manage application lifecycle"""
            # Startup
            await self._start_mcp_services()
            yield
            # Shutdown
            await self._stop_mcp_services()
        
        self.app = FastAPI(
            title="Simple MCP Integration API", 
            version="1.0.0",
            lifespan=lifespan
        )
        
        # Track metrics manually
        self.execution_metrics: Dict[str, List[float]] = {}
        self.error_counts: Dict[str, int] = {}
        self.tool_usage_counts: Dict[str, int] = {}
        
        # HTTP-based MCP services
        self.services: Dict[str, MCPService] = {
            'salesforce': MCPService(
                url=os.getenv('MCP_SALESFORCE_URL', 'http://localhost:8001'),
                connected=False,
                last_activity=None,
                error=None
            ),
            'jira': MCPService(
                url=os.getenv('MCP_JIRA_URL', 'http://localhost:8002'),
                connected=False,
                last_activity=None,
                error=None
            )
        }
        
        self.available_tools: List[Dict[str, Any]] = []
        self.tool_to_server: Dict[str, str] = {}
        
        # HTTP session for MCP communication
        self.http_session: Optional[aiohttp.ClientSession] = None
        
        # Initialize Anthropic API
        self.anthropic = None
        if os.getenv('ANTHROPIC_API_KEY'):
            try:
                self.anthropic = Anthropic()
                logger.info("Anthropic API initialized successfully")
            except Exception as e:
                logger.warning(f"Anthropic API initialization failed: {e}")
                
        if not self.anthropic:
            logger.error("No AI services available! Please configure ANTHROPIC_API_KEY")
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:3000"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        self._setup_routes()
        
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/api/status/{service}")
        async def get_status(service: str):
            """Get connection status for a service"""
            if service not in self.services:
                raise HTTPException(status_code=404, detail="Service not found")
            
            svc = self.services[service]
            
            return {
                "service": service,
                "connected": svc.connected,
                "last_activity": svc.last_activity,
                "error": svc.error,
                "health_score": svc.health_score,
                "url": svc.url
            }
        
        @self.app.post("/api/call-tool")
        async def call_tool(request: ToolCallRequest) -> ToolCallResponse:
            """Call a tool"""
            service = request.service
            tool_name = request.tool_name
            params = request.params
            
            start_time = datetime.now()
            
            if service not in self.services:
                raise HTTPException(status_code=404, detail="Service not found")
            
            svc = self.services[service]
            
            if not svc.connected:
                raise HTTPException(status_code=503, detail=f"{service} service not connected")
            
            try:
                # Execute MCP tool via HTTP
                result = await self._execute_mcp_tool_http(
                    service,
                    tool_name,
                    params
                )
                
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                
                return ToolCallResponse(
                    success=True,
                    data=result,
                    timestamp=datetime.now().isoformat(),
                    execution_time_ms=execution_time
                )
                
            except Exception as e:
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                
                logger.error(f"Error calling tool {tool_name} on {service}: {e}")
                return ToolCallResponse(
                    success=False,
                    error=str(e),
                    timestamp=datetime.now().isoformat(),
                    execution_time_ms=execution_time
                )
        
        @self.app.post("/api/chat")
        async def chat(request: ChatRequest) -> ChatResponse:
            """Chat endpoint using Anthropic API"""
            start_time = datetime.now()
            
            logger.info(f"Chat request received: {request.message}")
            
            try:
                if self.anthropic:
                    response_text = await self._process_chat_query(request.message)
                else:
                    return ChatResponse(
                        response="AI services not configured. Please add ANTHROPIC_API_KEY.",
                        success=False,
                        timestamp=datetime.now().isoformat(),
                        error="No AI services available"
                    )
                
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                
                return ChatResponse(
                    response=response_text,
                    success=True,
                    timestamp=datetime.now().isoformat(),
                    execution_time_ms=execution_time
                )
                
            except Exception as e:
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                
                logger.error(f"Chat error: {e}")
                return ChatResponse(
                    response="I encountered an error processing your request. Please try again.",
                    success=False,
                    timestamp=datetime.now().isoformat(),
                    error=str(e),
                    execution_time_ms=execution_time
                )
        
        @self.app.get("/api/health")
        async def health_check():
            """Health check"""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "connections": {
                    service: {
                        "connected": svc.connected, 
                        "last_activity": svc.last_activity,
                        "health_score": svc.health_score,
                        "url": svc.url
                    }
                    for service, svc in self.services.items()
                },
                "available_tools": len(self.available_tools),
                "anthropic_enabled": self.anthropic is not None
            }
    
    async def _start_mcp_services(self):
        """Start HTTP session and connect to MCP services"""
        logger.info("Starting HTTP MCP client connections...")
        
        # Create HTTP session
        timeout = aiohttp.ClientTimeout(total=30)
        self.http_session = aiohttp.ClientSession(timeout=timeout)
        
        # Test connections to MCP services
        await asyncio.gather(
            self._connect_to_service("salesforce"),
            self._connect_to_service("jira")
        )
        
        # Collect available tools
        await self._collect_available_tools()
    
    async def _connect_to_service(self, service_name: str):
        """Connect to an MCP service via HTTP"""
        svc = self.services[service_name]
        
        try:
            # Test health endpoint
            async with self.http_session.get(f"{svc.url}/health") as response:
                if response.status == 200:
                    svc.connected = True
                    svc.error = None
                    svc.health_score = 1.0
                    logger.info(f"Connected to {service_name} MCP service at {svc.url}")
                else:
                    raise Exception(f"Health check failed with status {response.status}")
                    
        except Exception as e:
            svc.connected = False
            svc.error = str(e)
            svc.health_score = 0.0
            logger.error(f"Failed to connect to {service_name} service: {e}")
    
    async def _execute_mcp_tool_http(self, service: str, tool_name: str, params: Dict[str, Any]) -> str:
        """Execute MCP tool via HTTP"""
        svc = self.services[service]
        
        if not svc.connected:
            raise ValueError(f"Service {service} not connected")
        
        # Update last activity
        svc.last_activity = datetime.now().strftime("%H:%M:%S")
        
        try:
            # Prepare the MCP request for HTTP
            mcp_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": params
                },
                "id": int(datetime.now().timestamp() * 1000)
            }
            
            # Send HTTP request to MCP service
            async with self.http_session.post(
                f"{svc.url}/mcp/call",
                json=mcp_request,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    
                    if "result" in result:
                        # Extract content from MCP response
                        mcp_result = result["result"]
                        if isinstance(mcp_result, dict) and "content" in mcp_result:
                            content = mcp_result["content"]
                            if content and len(content) > 0:
                                first_content = content[0]
                                if isinstance(first_content, dict) and "text" in first_content:
                                    return first_content["text"]
                                else:
                                    return str(first_content)
                            else:
                                return json.dumps(mcp_result)
                        else:
                            return json.dumps(mcp_result)
                    
                    elif "error" in result:
                        error_msg = result["error"].get("message", "Unknown error")
                        raise Exception(f"MCP tool error: {error_msg}")
                else:
                    raise Exception(f"HTTP error: {response.status}")
                    
        except Exception as e:
            raise e
    
    async def _collect_available_tools(self):
        """Collect all available tools from connected services"""
        self.available_tools = []
        self.tool_to_server = {}
        
        for service, svc in self.services.items():
            if svc.connected:
                try:
                    tools = await self._get_service_tools(service)
                    self.available_tools.extend(tools)
                    # Map tool names to their services
                    for tool in tools:
                        self.tool_to_server[tool['name']] = service
                except Exception as e:
                    logger.error(f"Error collecting tools from {service}: {e}")
                    
        logger.info(f"Collected {len(self.available_tools)} tools: {[t['name'] for t in self.available_tools]}")
    
    async def _get_service_tools(self, service: str) -> List[Dict[str, Any]]:
        """Get tools from a service via HTTP"""
        svc = self.services[service]
        
        try:
            async with self.http_session.get(f"{svc.url}/tools") as response:
                if response.status == 200:
                    result = await response.json()
                    # Add input_schema if missing
                    tools = result.get("tools", [])
                    for tool in tools:
                        if "input_schema" not in tool:
                            tool["input_schema"] = {"type": "object"}
                    return tools
                else:
                    logger.error(f"Failed to get tools from {service}: HTTP {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error getting tools from {service}: {e}")
            return []
    
    async def _process_chat_query(self, query: str) -> str:
        """Process chat using Anthropic API"""
        if not self.available_tools:
            return "No MCP tools available. Please check service connections."
            
        messages = [{'role': 'user', 'content': query}]
        
        try:
            response = self.anthropic.messages.create(
                max_tokens=2024,
                model='claude-3-5-sonnet-20241022',
                tools=self.available_tools,
                messages=messages
            )
            
            process_query = True
            full_response = ""
            
            while process_query:
                assistant_content = []
                
                for content in response.content:
                    if content.type == 'text':
                        full_response += content.text
                        assistant_content.append(content)
                        if len(response.content) == 1:
                            process_query = False
                            
                    elif content.type == 'tool_use':
                        assistant_content.append(content)
                        messages.append({'role': 'assistant', 'content': assistant_content})
                        
                        tool_id = content.id
                        tool_args = content.input
                        tool_name = content.name
                        
                        logger.info(f"Claude calling tool {tool_name} with args {tool_args}")
                        
                        try:
                            # Find which service has this tool
                            server_name = self.tool_to_server.get(tool_name)
                            if not server_name:
                                raise ValueError(f"Tool {tool_name} not found")
                                
                            result = await self._call_mcp_tool_http(server_name, tool_name, tool_args)
                            
                            # Format result for Claude
                            tool_result = {
                                "type": "tool_result",
                                "tool_use_id": tool_id,
                                "content": result
                            }
                            
                            messages.append({"role": "user", "content": [tool_result]})
                            
                            # Get next response from Claude
                            response = self.anthropic.messages.create(
                                max_tokens=2024,
                                model='claude-3-5-sonnet-20241022',
                                tools=self.available_tools,
                                messages=messages
                            )
                            
                            if len(response.content) == 1 and response.content[0].type == "text":
                                full_response += response.content[0].text
                                process_query = False
                                
                        except Exception as e:
                            logger.error(f"Error calling tool {tool_name}: {e}")
                            # Send error as tool result
                            tool_result = {
                                "type": "tool_result",
                                "tool_use_id": tool_id,
                                "content": f"Error: {str(e)}"
                            }
                            
                            messages.append({"role": "user", "content": [tool_result]})
                            
                            response = self.anthropic.messages.create(
                                max_tokens=2024,
                                model='claude-3-5-sonnet-20241022',
                                tools=self.available_tools,
                                messages=messages
                            )
                            
                            if len(response.content) == 1 and response.content[0].type == "text":
                                full_response += f"I encountered an error: {str(e)}\n"
                                full_response += response.content[0].text
                                process_query = False
                                
            return full_response
            
        except Exception as e:
            logger.error(f"Error processing chat query: {e}")
            return f"I encountered an error processing your request: {str(e)}"
    
    async def _call_mcp_tool_http(self, service: str, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Call an MCP tool via HTTP"""
        svc = self.services[service]
        if not svc.connected:
            raise ValueError(f"Service {service} not connected")
            
        # Send tool call request via HTTP
        tool_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            },
            "id": int(datetime.now().timestamp() * 1000)
        }
        
        async with self.http_session.post(
            f"{svc.url}/mcp/call",
            json=tool_request,
            headers={"Content-Type": "application/json"}
        ) as response:
            
            if response.status == 200:
                result = await response.json()
                if "result" in result:
                    mcp_result = result["result"]
                    if isinstance(mcp_result, dict) and "content" in mcp_result:
                        content = mcp_result["content"]
                        if content and len(content) > 0:
                            first_content = content[0]
                            if isinstance(first_content, dict) and "text" in first_content:
                                return first_content["text"]
                    return str(result["result"])
                elif "error" in result:
                    raise Exception(f"Tool error: {result['error']}")
            else:
                raise Exception(f"HTTP error: {response.status}")
    
    async def _stop_mcp_services(self):
        """Stop HTTP session"""
        if self.http_session:
            await self.http_session.close()
            logger.info("HTTP session closed")

def main():
    """Main entry point"""
    server = SimpleMCPWebServer()
    
    logger.info("Starting Simple MCP Web Server")
    logger.info("Features: HTTP Communication, Anthropic API")
    logger.info("Frontend: http://localhost:3000")
    logger.info("Backend: http://localhost:8000")
    
    uvicorn.run(
        server.app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

if __name__ == "__main__":
    main()