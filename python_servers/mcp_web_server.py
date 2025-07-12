#!/usr/bin/env python3
"""
MCP Web Server with HTTP Communication for Docker
Communicates with MCP servers via HTTP instead of subprocesses
"""

import asyncio
import json
import logging
import aiohttp
import sys
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from anthropic import Anthropic
from dotenv import load_dotenv
import re

# Strands SDK imports (correct API from documentation)
try:
    from strands import Agent, tool
    from strands.agent.conversation_manager.sliding_window_conversation_manager import (
        SlidingWindowConversationManager,
    )
    STRANDS_AVAILABLE = True
    STRANDS_MEMORY_AVAILABLE = True
    print("✅ Strands SDK imported successfully!")
except ImportError as e:
    print(f"Strands import error: {e}")
    STRANDS_AVAILABLE = False
    STRANDS_MEMORY_AVAILABLE = False

# Enhanced error handling
import traceback

# Load environment variables
load_dotenv()

# Configure logging
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

# Initialize Strands telemetry if available
if STRANDS_AVAILABLE:
    try:
        # Import telemetry components
        from strands.telemetry import StrandsTelemetry, get_tracer, Tracer
        
        # Initialize telemetry with console output
        telemetry = StrandsTelemetry()
        telemetry.setup_console_exporter()  # Enable console output for telemetry
        
        # Get a tracer for this application (no arguments)
        tracer = get_tracer()
        
        logger.info("✅ Strands telemetry enabled with console exporter")
        logger.info("Telemetry will trace agent decisions and tool calls")
        logger.info("Note: Telemetry output will appear in console/logs")
        
        # Log tracer info
        logger.info(f"Tracer type: {type(tracer)}")
        logger.info(f"Tracer methods: {[m for m in dir(tracer) if not m.startswith('_')]}")
    except Exception as e:
        logger.warning(f"Strands telemetry setup failed: {e}")
        logger.info("Continuing without telemetry")
        tracer = None
else:
    tracer = None

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
    trace_id: Optional[str] = None

class ThinkingStep(BaseModel):
    step_number: int
    timestamp: str
    type: str  # 'reasoning', 'tool_selection', 'parameter_decision', 'analysis'
    content: str
    confidence: Optional[float] = None
    alternatives_considered: Optional[List[str]] = None

class ChatRequest(BaseModel):
    message: str
    capture_thinking: bool = False
    
class ChatResponse(BaseModel):
    response: str
    success: bool
    timestamp: str
    thinking_steps: Optional[List[ThinkingStep]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None
    trace_id: Optional[str] = None

@dataclass
class MCPService:
    url: str
    connected: bool
    last_activity: Optional[str]
    error: Optional[str]
    health_score: float = 1.0

class MCPWebServer:
    """MCP Web Server with HTTP communication for Docker"""
    
    def __init__(self):
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            """Manage application lifecycle"""
            # Startup
            await self._start_mcp_services()
            yield
            # Shutdown
            await self._stop_mcp_services()
        
        self.app = FastAPI(
            title="Strands MCP Integration API", 
            version="1.0.0",
            lifespan=lifespan
        )
        
        # HTTP-based MCP services
        self.services: Dict[str, MCPService] = {
            'salesforce': MCPService(
                url=os.getenv('MCP_SALESFORCE_URL', 'http://mcp-salesforce:8001'),
                connected=False,
                last_activity=None,
                error=None
            ),
            'jira': MCPService(
                url=os.getenv('MCP_JIRA_URL', 'http://mcp-jira:8002'),
                connected=False,
                last_activity=None,
                error=None
            )
        }
        
        # Available tools and mappings
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
        
        # Simple memory system - just use basic caching with file persistence
        self.cache_file = "logs/entity_cache.json"
        self.context_file = "logs/session_context.json"
        self.conversation_file = "logs/conversation_history.json"
        self.entity_cache = self._load_cache_from_file(self.cache_file)
        self.session_context = self._load_cache_from_file(self.context_file)
        
        # Initialize conversation history with proper persistence
        self.conversation_history = self._load_conversation_history()
        
        # Thinking capture storage
        self.thinking_sessions: Dict[str, List[ThinkingStep]] = {}
        
        # Initialize Strands components
        self.strands_agent = None
        self.conversation_memory = None
        self.entity_memory = None
        self.context_memory = None
        self.retry_config = None
        
        if STRANDS_AVAILABLE:
            try:
                logger.info("🔄 Initializing Strands SDK with proper memory...")
                
                # Step 1: Create conversation manager
                logger.info("Step 1: Creating SlidingWindowConversationManager...")
                self.conversation_memory = SlidingWindowConversationManager(
                    window_size=20,
                    should_truncate_results=True
                )
                logger.info("✅ Conversation memory created")
                
                # Step 2: Create Strands Agent with conversation memory and Anthropic model
                logger.info("Step 2: Creating Strands Agent with conversation memory and Anthropic model...")
                self.strands_agent = Agent(
                    name="mcp-integration-agent",
                    description="Salesforce/Jira MCP helper with persistent memory",
                    tools=[],  # Will be populated with MCP tools
                    conversation_manager=self.conversation_memory,
                    model="anthropic.claude-3-5-sonnet-20241022"  # Use Anthropic instead of AWS Bedrock
                )
                logger.info(f"✅ Strands agent created with memory!")
                logger.info(f"Agent methods available: {len([m for m in dir(self.strands_agent) if not m.startswith('_')])}")
                
                logger.info("✅ Strands SDK initialized with full memory system!")
                
            except Exception as e:
                logger.error(f"❌ Strands initialization failed: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                logger.info("Using simple memory system instead")
                self.strands_agent = None
                self.conversation_memory = None
                self.entity_memory = None
                self.context_memory = None
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:3000",
                "http://127.0.0.1:3000"
            ],
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
            """Call a tool with Strands tracing"""
            service = request.service
            tool_name = request.tool_name
            params = request.params
            
            start_time = datetime.now()
            trace_id = None
            
            # Add basic tracing info if available
            if STRANDS_AVAILABLE:
                try:
                    # Simple trace context for now
                    trace_id = f"call_tool_{int(start_time.timestamp() * 1000)}"
                except Exception:
                    pass
            
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
                    execution_time_ms=execution_time,
                    trace_id=trace_id
                )
                
            except Exception as e:
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                
                logger.error(f"Error calling tool {tool_name} on {service}: {e}")
                return ToolCallResponse(
                    success=False,
                    error=str(e),
                    timestamp=datetime.now().isoformat(),
                    execution_time_ms=execution_time,
                    trace_id=trace_id
                )
        
        @self.app.post("/api/chat")
        async def chat(request: ChatRequest) -> ChatResponse:
            """Chat endpoint with Strands tracing"""
            start_time = datetime.now()
            trace_id = None
            
            # Add basic tracing info if available
            if STRANDS_AVAILABLE:
                try:
                    # Simple trace context for now
                    trace_id = f"chat_{int(start_time.timestamp() * 1000)}"
                except Exception:
                    pass
            
            logger.info(f"Chat request received: {request.message}")
            
            try:
                if self.anthropic:
                    # Check if this is a complex multi-step task that should use Strands agent
                    if self._is_complex_task(request.message):
                        response_text = await self._process_complex_task(request.message)
                    else:
                        response_text = await self._process_chat_query(request.message)
                else:
                    return ChatResponse(
                        response="AI services not configured. Please add ANTHROPIC_API_KEY.",
                        success=False,
                        timestamp=datetime.now().isoformat(),
                        error="No AI services available",
                        trace_id=trace_id
                    )
                
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                
                return ChatResponse(
                    response=response_text,
                    success=True,
                    timestamp=datetime.now().isoformat(),
                    execution_time_ms=execution_time,
                    trace_id=trace_id
                )
                
            except Exception as e:
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                
                logger.error(f"Chat error: {e}")
                return ChatResponse(
                    response="I encountered an error processing your request. Please try again.",
                    success=False,
                    timestamp=datetime.now().isoformat(),
                    error=str(e),
                    execution_time_ms=execution_time,
                    trace_id=trace_id
                )
        
        @self.app.post("/api/complex-task")
        async def complex_task(request: ChatRequest) -> ChatResponse:
            """Complex multi-step task endpoint using Strands agent"""
            start_time = datetime.now()
            trace_id = None
            
            if STRANDS_AVAILABLE:
                try:
                    trace_id = f"complex_task_{int(start_time.timestamp() * 1000)}"
                except Exception:
                    pass
            
            logger.info(f"Complex task request received: {request.message}")
            
            try:
                if self.strands_agent and self.anthropic:
                    response_text = await self._process_complex_task(request.message)
                else:
                    # Fallback to regular chat processing
                    response_text = await self._process_chat_query(request.message)
                
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                
                return ChatResponse(
                    response=response_text,
                    success=True,
                    timestamp=datetime.now().isoformat(),
                    execution_time_ms=execution_time,
                    trace_id=trace_id
                )
                
            except Exception as e:
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                
                logger.error(f"Complex task error: {e}")
                return ChatResponse(
                    response="I encountered an error processing your complex task. Please try again.",
                    success=False,
                    timestamp=datetime.now().isoformat(),
                    error=str(e),
                    execution_time_ms=execution_time,
                    trace_id=trace_id
                )
        
        @self.app.get("/api/memory/status")
        async def get_memory_status():
            """Get current memory status for the UI"""
            try:
                # Collect entity data
                entities = []
                for cache_key, entity_data in self.entity_cache.items():
                    if ':' in cache_key and not cache_key.startswith(('Opportunity:Name:', 'Case:Number:', 'Case:JiraKey:', 'Account:Name:')):
                        entity_info = {
                            'type': entity_data.get('type', 'Unknown'),
                            'id': entity_data.get('id', cache_key.split(':', 1)[1]),
                            'name': self._extract_entity_name(entity_data),
                            'description': self._extract_entity_description(entity_data),
                            'metadata': self._extract_entity_metadata(entity_data),
                            'cached_at': entity_data.get('cached_at'),
                            'timestamp': entity_data.get('timestamp')
                        }
                        entities.append(entity_info)
                
                # Collect conversation data
                conversations = []
                if 'conversation_history' in self.session_context:
                    conversations = self.session_context['conversation_history'][-20:]  # Last 20 messages
                
                # Collect context data
                context = {}
                for key, value in self.session_context.items():
                    if key != 'conversation_history':  # Exclude conversation history from context
                        context[key] = value
                
                # Calculate stats
                stats = {
                    'totalEntities': len(entities),
                    'totalConversations': len(conversations),
                    'memoryUsage': min(100, (len(entities) + len(conversations)) * 2)  # Simple usage calculation
                }
                
                return {
                    'entities': entities,
                    'conversations': conversations,
                    'context': context,
                    'stats': stats,
                    'timestamp': datetime.now().isoformat(),
                    'strands_available': STRANDS_AVAILABLE,
                    'strands_agent_active': self.strands_agent is not None
                }
                
            except Exception as e:
                logger.error(f"Error getting memory status: {e}")
                return {
                    'entities': [],
                    'conversations': [],
                    'context': {},
                    'stats': {'totalEntities': 0, 'totalConversations': 0, 'memoryUsage': 0},
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }

        @self.app.post("/api/chat-with-thinking")
        async def chat_with_thinking(request: ChatRequest) -> ChatResponse:
            """Enhanced chat endpoint that captures thinking process"""
            start_time = datetime.now()
            session_id = f"session_{int(start_time.timestamp() * 1000)}"
            
            logger.info(f"Chat with thinking capture: {request.message}")
            
            try:
                if not self.anthropic:
                    return ChatResponse(
                        response="AI services not configured. Please add ANTHROPIC_API_KEY.",
                        success=False,
                        timestamp=datetime.now().isoformat(),
                        error="No AI services available"
                    )
                
                # Process with thinking capture
                response_text, thinking_steps, tool_calls = await self._process_with_thinking_capture(
                    request.message, session_id, request.capture_thinking
                )
                
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                
                return ChatResponse(
                    response=response_text,
                    success=True,
                    timestamp=datetime.now().isoformat(),
                    thinking_steps=thinking_steps if request.capture_thinking else None,
                    tool_calls=tool_calls,
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
        
        @self.app.get("/api/thinking/{session_id}")
        async def get_thinking_steps(session_id: str):
            """Get thinking steps for a specific session"""
            if session_id in self.thinking_sessions:
                return {
                    "session_id": session_id,
                    "thinking_steps": self.thinking_sessions[session_id],
                    "total_steps": len(self.thinking_sessions[session_id])
                }
            else:
                raise HTTPException(status_code=404, detail="Session not found")
        
        @self.app.get("/api/thinking-sessions")
        async def list_thinking_sessions():
            """List all available thinking sessions"""
            sessions = []
            for session_id, steps in self.thinking_sessions.items():
                sessions.append({
                    "session_id": session_id,
                    "step_count": len(steps),
                    "first_step_time": steps[0].timestamp if steps else None,
                    "last_step_time": steps[-1].timestamp if steps else None
                })
            return {"sessions": sessions}
        
        @self.app.delete("/api/thinking/{session_id}")
        async def delete_thinking_session(session_id: str):
            """Delete a specific thinking session"""
            if session_id in self.thinking_sessions:
                del self.thinking_sessions[session_id]
                return {
                    "success": True,
                    "message": f"Thinking session {session_id} deleted successfully",
                    "remaining_sessions": len(self.thinking_sessions)
                }
            else:
                raise HTTPException(status_code=404, detail="Thinking session not found")
        
        @self.app.delete("/api/thinking-sessions")
        async def delete_all_thinking_sessions():
            """Delete all thinking sessions"""
            session_count = len(self.thinking_sessions)
            self.thinking_sessions.clear()
            return {
                "success": True,
                "message": f"All {session_count} thinking sessions deleted successfully",
                "remaining_sessions": 0
            }

        @self.app.get("/api/health")
        async def health_check():
            """Health check with Strands integration status"""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "thinking_capture_enabled": True,
                "active_thinking_sessions": len(self.thinking_sessions),
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
                "anthropic_enabled": self.anthropic is not None,
                "strands_enabled": STRANDS_AVAILABLE,
                "strands_agent": self.strands_agent is not None
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
        
        # Register MCP tools with Strands agent
        await self._register_mcp_tools_with_agent()
    
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
                    tools = result.get("tools", [])
                    
                    # Convert MCP tool format to Claude tool format
                    claude_tools = []
                    for tool in tools:
                        claude_tool = {
                            "name": tool["name"],
                            "description": tool["description"],
                            "input_schema": tool.get("inputSchema", {"type": "object"})
                        }
                        claude_tools.append(claude_tool)
                    
                    return claude_tools
                else:
                    logger.error(f"Failed to get tools from {service}: HTTP {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error getting tools from {service}: {e}")
            return []
    
    async def _register_mcp_tools_with_agent(self):
        """Register MCP tools with Strands agent"""
        # Note: Strands Agent doesn't support dynamic tool addition
        # Tools must be passed during Agent initialization
        # The agent will use the Anthropic API directly with the available_tools
        logger.info("Strands agent will use MCP tools via Anthropic API")
        logger.info(f"Available tools for agent: {len(self.available_tools)} tools")
    
    def _create_strands_tool_wrapper(self, tool_name: str, service: str, tool_info: Dict[str, Any]):
        """Create a Strands tool wrapper for an MCP tool"""
        
        @tool
        async def mcp_tool_wrapper(**params):
            """Dynamically created MCP tool wrapper"""
            try:
                result = await self._call_mcp_tool(service, tool_name, params)
                
                # Cache entities from tool results
                await self._cache_entities_from_result(tool_name, params, result)
                
                return result
            except Exception as e:
                logger.error(f"Error in MCP tool wrapper for {tool_name}: {e}")
                return f"Error calling {tool_name}: {str(e)}"
        
        # Set the tool name and description
        mcp_tool_wrapper.__name__ = tool_name
        mcp_tool_wrapper.__doc__ = tool_info.get('description', f'MCP tool: {tool_name}')
        
        return mcp_tool_wrapper
    
    async def _process_chat_query(self, query: str) -> str:
        """Process chat using Strands Agent with fallback to Anthropic API"""
        
        # Try Strands agent first if available
        if self.strands_agent:
            try:
                # Use Strands agent for chat processing with memory
                # The Strands Agent should handle conversation memory automatically
                logger.info("🔄 Processing chat through Strands agent with automatic memory...")
                
                # Call the Strands agent directly - it handles memory internally
                response_text = await self.strands_agent.run(query)
                
                logger.info("✅ Chat processed through Strands agent with automatic memory")
                return str(response_text)
                
            except Exception as e:
                logger.warning(f"Strands agent failed ({str(e)}), falling back to Anthropic API")
                logger.warning(f"Available Strands agent methods: {[m for m in dir(self.strands_agent) if not m.startswith('_')]}")
                # Fall through to Anthropic fallback
        
        # Fallback to regular Anthropic API processing
        if not self.anthropic:
            return "No AI services available. Please configure ANTHROPIC_API_KEY or AWS credentials."
        
        if not self.available_tools:
            return "No MCP tools available. Please check service connections."
        
        # Add cached context to system prompt
        cached_context = self._build_cached_context_prompt()
        
        # Enhanced system prompt with custom field awareness and root cause analysis
        system_prompt = f"""You are an AI assistant with access to Salesforce and Jira systems through MCP (Model Context Protocol) tools. 

{cached_context}

CRITICAL INSTRUCTION FOR CONTEXT USAGE:
When users refer to previously discussed entities like "the opportunity", "that case", "Big Opps", etc., you MUST use the cached context above to identify the specific entity and its details (including IDs, Account IDs, etc.). Do NOT ask for information that is already available in the cached context.

For activity creation specifically:
- You CAN create activities linked directly to accounts using account_id parameter
- If user refers to "the opportunity" or mentions a specific opportunity name from cached context, use the Account ID from that cached opportunity
- If user mentions creating an activity "for the opportunity that was identified" or similar, reference the cached at-risk opportunities above
- Include rich context from cached Jira issues and case details in activity descriptions
- If you don't have cached context but user wants to create an activity, try querying for opportunities or accounts first

ERROR HANDLING AND PERSISTENCE:
- If a tool call fails, try alternative approaches (e.g., different query parameters, related entities)
- Parse error messages to understand what went wrong and suggest fixes
- If you get "required field missing" errors, try to find the missing information from cached context or query for it
- Don't give up after one failure - try multiple approaches to accomplish the user's goal
- Use cached entity data to fill in missing parameters when possible

CRITICAL: JIRA ISSUE KEYS ARE ROOT CAUSE DIAGNOSTIC CLUES

When you see a Jira Issue Key on a Salesforce Case (Case.Jira_Issue_Key__c field), this is a DIRECT CLUE to the root cause of the problem. You MUST:

1. **IMMEDIATELY investigate the linked Jira issue** - The Jira Issue Key is not just a reference, it's a diagnostic pointer to the technical root cause
2. **Analyze the Jira issue details** - Status, priority, description, comments, and resolution details
3. **Connect technical problems to business impact** - Link Jira technical issues to Salesforce business problems
4. **Provide root cause analysis** - Explain how the technical issue (Jira) is causing the business problem (Case)

IMPORTANT CUSTOM FIELDS AND CROSS-SYSTEM INTEGRATION:

Salesforce Custom Fields:
- Case.Jira_Issue_Key__c: **ROOT CAUSE DIAGNOSTIC LINK** - Links Salesforce cases to Jira issues (e.g., "TECH-1", "IMPL-1")
- Opportunity.Jira_Project_Key__c: Links opportunities to Jira projects (e.g., "IMPL", "TECH")
- Opportunity.Implementation_Status__c: Tracks implementation risk ("At Risk", "Blocked", "Complete", "Not Started")
- Account.Jira_Project_Keys__c: Account-level Jira project mapping (e.g., "TECH, IMPL, SUPPORT")

ROOT CAUSE ANALYSIS WORKFLOW:
1. **When analyzing any Case** - ALWAYS check for Jira_Issue_Key__c field
2. **If Jira Issue Key exists** - IMMEDIATELY query the corresponding Jira issue
3. **Analyze the technical details** - What's broken, blocked, or causing problems in Jira
4. **Explain the connection** - How does the technical issue cause the business problem
5. **Provide actionable insights** - What needs to be fixed technically to resolve the business issue

Cross-System Intelligence:
- When analyzing opportunities "at risk", look for Implementation_Status__c = "At Risk"
- **ALWAYS follow Jira Issue Key trails** - They lead to root causes
- Identify patterns: High-priority cases + blocked Jira issues = business risk
- Use custom fields to provide cross-system insights and recommendations
- **Treat Jira Issue Keys as diagnostic breadcrumbs** - Follow them to find root causes

Demo Data Context:
- Look for opportunities with Implementation_Status__c = "At Risk" to identify business risks
- Related cases may have Jira_Issue_Key__c values linking to technical issues
- **The Jira issues contain the actual technical problems causing business impact**
- Look for relationships between business impact (opportunities) and technical problems (cases/Jira)
- Always focus on the specific account/opportunity being discussed, not generic examples

DIAGNOSTIC MINDSET:
- Jira Issue Key = Root Cause Clue
- Always investigate linked Jira issues for technical details
- Connect technical problems to business symptoms
- Provide comprehensive root cause analysis

PROACTIVE ACTIVITY CREATION:
After performing root cause analysis, you should be EAGER to help create activities on opportunities with comprehensive context:

1. **Suggest Activity Creation** - Proactively offer to create activities when you discover important information
2. **Rich Context Activities** - Use all gathered intelligence (Jira details, case information, technical status) to create meaningful activity descriptions
3. **Actionable Information** - Include specific technical details, blockers, and next steps in activity descriptions
4. **Business Impact Focus** - Explain how technical issues affect the opportunity and what actions are needed

ACTIVITY CREATION EXAMPLES:
- "I found that this opportunity is at risk due to TECH-1 (database performance issue). Would you like me to create an activity to track this technical blocker?"
- "Based on the linked Jira issues, I can create a comprehensive activity with all the technical details and recommended next steps."
- "I've gathered detailed information from the related cases and Jira issues. Let me create an activity that captures all this context for the opportunity team."

ALWAYS BE HELPFUL AND PERSISTENT:
- Offer to create activities when you discover valuable cross-system information
- Make activity descriptions rich with technical context and business impact
- Include specific Jira issue details, case information, and recommended actions
- Be proactive in suggesting how to document and track important findings
- If one approach fails, try alternative approaches to accomplish the user's goal
- Parse error messages and work through problems systematically
- Use cached context to fill in missing information

When querying data, always include custom fields in your SOQL queries to provide comprehensive analysis."""
        
        # Build messages with conversation memory if available
        messages = []
        
        # Add conversation history from fallback memory
        if 'conversation_history' in self.session_context:
            try:
                history = self.session_context['conversation_history'][-10:]  # Last 10 messages
                for msg in history:
                    if msg.get('role') in ['user', 'assistant']:
                        messages.append({'role': msg['role'], 'content': msg['content']})
                logger.info(f"Added {len(messages)} messages from fallback memory")
            except Exception as e:
                logger.warning(f"Failed to retrieve fallback conversation memory: {e}")
        
        # Add current user message
        messages.append({'role': 'user', 'content': query})
        
        try:
            response = self.anthropic.messages.create(
                max_tokens=2024,
                model='claude-3-5-sonnet-20241022',
                system=system_prompt,
                tools=self.available_tools,
                messages=messages
            )
            
            process_query = True
            full_response = ""
            
            while process_query:
                assistant_content = []
                
                for content in response.content:
                    if content.type == 'text':
                        # Add spacing and formatting if there's already content
                        if full_response and not full_response.endswith('\n'):
                            full_response += '\n\n---\n\n'
                        full_response += self._format_response_text(content.text)
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
                                
                            result = await self._call_mcp_tool(server_name, tool_name, tool_args)
                            
                            # Cache discovered entities from tool results
                            await self._cache_entities_from_result(tool_name, tool_args, result)
                            
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
                                system=system_prompt,
                                tools=self.available_tools,
                                messages=messages
                            )
                            
                            if len(response.content) == 1 and response.content[0].type == "text":
                                # Add spacing if there's already content
                                if full_response and not full_response.endswith('\n'):
                                    full_response += '\n\n'
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
                                system=system_prompt,
                                tools=self.available_tools,
                                messages=messages
                            )
                            
                            if len(response.content) == 1 and response.content[0].type == "text":
                                full_response += f"I encountered an error: {str(e)}\n"
                                full_response += response.content[0].text
                                process_query = False
                                
            # Store conversation in fallback memory
            try:
                if 'conversation_history' not in self.session_context:
                    self.session_context['conversation_history'] = []
                self.session_context['conversation_history'].append({'role': 'user', 'content': query, 'timestamp': datetime.now().isoformat()})
                self.session_context['conversation_history'].append({'role': 'assistant', 'content': full_response, 'timestamp': datetime.now().isoformat()})
                # Keep only recent conversations
                if len(self.session_context['conversation_history']) > 20:
                    self.session_context['conversation_history'] = self.session_context['conversation_history'][-20:]
                logger.info("Stored conversation in fallback memory")
            except Exception as e:
                logger.warning(f"Failed to store conversation in memory: {e}")
            
            # Ensure memory persistence after each chat
            self._ensure_memory_persistence()
            
            return full_response
            
        except Exception as e:
            logger.error(f"Error processing chat query: {e}")
            return f"I encountered an error processing your request: {str(e)}"
    
    async def _call_mcp_tool(self, service: str, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Call an MCP tool via HTTP"""
        svc = self.services[service]
        if not svc.connected:
            raise ValueError(f"Service {service} not connected")
        
        # Call MCP tool directly (Strands SDK handles its own retry logic internally)
        return await self._call_mcp_tool_direct(service, tool_name, arguments)
    
    
    async def _call_mcp_tool_direct(self, service: str, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Direct MCP tool call with enhanced error handling and retry logic"""
        svc = self.services[service]
        
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
        
        try:
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
                        error_info = result["error"]
                        error_msg = error_info.get("message", "Unknown error")
                        error_code = error_info.get("code", "unknown")
                        
                        # Enhanced error parsing for better recovery
                        if "required field" in error_msg.lower():
                            raise ValueError(f"Missing required field: {error_msg}")
                        elif "invalid" in error_msg.lower():
                            raise ValueError(f"Invalid parameter: {error_msg}")
                        elif "not found" in error_msg.lower():
                            raise ValueError(f"Resource not found: {error_msg}")
                        else:
                            raise Exception(f"MCP tool error [{error_code}]: {error_msg}")
                else:
                    raise aiohttp.ClientError(f"HTTP error: {response.status}")
                    
        except aiohttp.ClientError as e:
            logger.warning(f"HTTP client error calling {tool_name}: {e}")
            raise
        except asyncio.TimeoutError as e:
            logger.warning(f"Timeout calling {tool_name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling {tool_name}: {e}")
            raise
    
    async def _cache_entities_from_result(self, tool_name: str, tool_args: Dict[str, Any], result: str):
        """Cache discovered entities from tool results for future reference"""
        try:
            # Parse JSON results to extract entities
            if result.startswith('[') or result.startswith('{'):
                try:
                    data = json.loads(result)
                except json.JSONDecodeError:
                    return
                
                # Cache Salesforce entities
                if tool_name in ['salesforce_query', 'salesforce_get_record']:
                    await self._cache_salesforce_entities(data)
                
                # Cache Jira entities  
                elif tool_name in ['jira_search_issues', 'jira_get_issue']:
                    await self._cache_jira_entities(data)
                    
            logger.info(f"✅ Cached entities from {tool_name}")
            
        except Exception as e:
            logger.warning(f"Failed to cache entities from {tool_name}: {e}")
    
    async def _cache_salesforce_entities(self, data: Any):
        """Cache Salesforce entities (Opportunities, Cases, Accounts)"""
        try:
            # Handle list of records
            if isinstance(data, list):
                for record in data:
                    if isinstance(record, dict):
                        await self._cache_single_sf_record(record)
            
            # Handle single record
            elif isinstance(data, dict):
                await self._cache_single_sf_record(data)
                
        except Exception as e:
            logger.warning(f"Failed to cache Salesforce entities: {e}")
    
    async def _cache_single_sf_record(self, record: Dict[str, Any]):
        """Cache a single Salesforce record using Strands EntityMemory"""
        try:
            # Extract record type and ID
            record_id = record.get('Id')
            if not record_id:
                return
                
            # Determine record type from ID prefix or attributes
            record_type = None
            if record_id.startswith('006'):
                record_type = 'Opportunity'
            elif record_id.startswith('500'):
                record_type = 'Case'
            elif record_id.startswith('001'):
                record_type = 'Account'
            elif record_id.startswith('003'):
                record_type = 'Contact'
                
            if record_type:
                entity_data = {
                    'type': record_type,
                    'id': record_id,
                    'data': record,
                    'cached_at': datetime.now().isoformat()
                }
                
                # Use Strands EntityMemory if available, otherwise fallback to basic cache
                if self.entity_memory:
                    try:
                        # Store in Strands EntityMemory
                        await self.entity_memory.store_entity(
                            entity_id=record_id,
                            entity_type=record_type,
                            entity_data=entity_data,
                            metadata={
                                'name': record.get('Name', ''),
                                'case_number': record.get('CaseNumber', ''),
                                'jira_key': record.get('Jira_Issue_Key__c', ''),
                                'implementation_status': record.get('Implementation_Status__c', '')
                            }
                        )
                        
                        # Store additional lookup keys
                        if record_type == 'Opportunity':
                            name = record.get('Name')
                            if name:
                                await self.entity_memory.store_entity(
                                    entity_id=f"name:{name}",
                                    entity_type=f"{record_type}_by_name",
                                    entity_data={'reference_id': record_id}
                                )
                        
                        logger.debug(f"Stored {record_type} {record_id} in Strands EntityMemory")
                    except Exception as e:
                        logger.warning(f"Failed to store in EntityMemory, using fallback: {e}")
                        # Fallback to basic cache
                        cache_key = f"{record_type}:{record_id}"
                        self.entity_cache[cache_key] = entity_data
                else:
                    # Fallback to basic cache
                    cache_key = f"{record_type}:{record_id}"
                    self.entity_cache[cache_key] = entity_data
                
                # Store context information using Strands ContextMemory
                if record_type == 'Opportunity' and record.get('Implementation_Status__c') == 'At Risk':
                    at_risk_data = {
                        'id': record_id,
                        'name': record.get('Name'),
                        'account': record.get('Account', {}).get('Name'),
                        'amount': record.get('Amount', 0),
                        'account_id': record.get('AccountId')
                    }
                    
                    if self.context_memory:
                        try:
                            await self.context_memory.store_context(
                                context_key="at_risk_opportunities",
                                context_data=at_risk_data,
                                context_type="business_risk"
                            )
                            logger.debug(f"Stored at-risk opportunity context in Strands ContextMemory")
                        except Exception as e:
                            logger.warning(f"Failed to store in ContextMemory, using fallback: {e}")
                            # Fallback to basic context
                            if 'at_risk_opportunities' not in self.session_context:
                                self.session_context['at_risk_opportunities'] = []
                            self.session_context['at_risk_opportunities'].append(at_risk_data)
                    else:
                        # Fallback to basic context
                        if 'at_risk_opportunities' not in self.session_context:
                            self.session_context['at_risk_opportunities'] = []
                        self.session_context['at_risk_opportunities'].append(at_risk_data)
                        
        except Exception as e:
            logger.warning(f"Failed to cache SF record: {e}")
    
    async def _cache_jira_entities(self, data: Any):
        """Cache Jira entities (Issues)"""
        try:
            # Handle Jira search results
            if isinstance(data, dict) and 'issues' in data:
                for issue in data['issues']:
                    await self._cache_single_jira_issue(issue)
            
            # Handle single issue
            elif isinstance(data, dict) and 'key' in data:
                await self._cache_single_jira_issue(data)
                
        except Exception as e:
            logger.warning(f"Failed to cache Jira entities: {e}")
    
    async def _cache_single_jira_issue(self, issue: Dict[str, Any]):
        """Cache a single Jira issue"""
        try:
            issue_key = issue.get('key')
            if not issue_key:
                return
                
            # Cache the issue
            cache_key = f"Jira:{issue_key}"
            self.entity_cache[cache_key] = {
                'type': 'Jira',
                'key': issue_key,
                'data': issue,
                'cached_at': datetime.now().isoformat()
            }
            
            # Track high-priority or blocked issues
            fields = issue.get('fields', {})
            priority = fields.get('priority', {}).get('name', '')
            status = fields.get('status', {}).get('name', '')
            
            if priority in ['High', 'Highest'] or status in ['Blocked', 'To Do']:
                if 'critical_jira_issues' not in self.session_context:
                    self.session_context['critical_jira_issues'] = []
                self.session_context['critical_jira_issues'].append({
                    'key': issue_key,
                    'summary': fields.get('summary', ''),
                    'status': status,
                    'priority': priority
                })
                
        except Exception as e:
            logger.warning(f"Failed to cache Jira issue: {e}")
    
    def get_cached_entity(self, entity_type: str, identifier: str) -> Optional[Dict[str, Any]]:
        """Retrieve a cached entity by type and identifier"""
        cache_key = f"{entity_type}:{identifier}"
        return self.entity_cache.get(cache_key)
    
    def get_session_context(self, key: str) -> Any:
        """Get session context data"""
        return self.session_context.get(key)
    
    def _build_cached_context_prompt(self) -> str:
        """Build context prompt from cached entities and session data"""
        context_parts = []
        
        # Add at-risk opportunities context
        at_risk_opps = self.session_context.get('at_risk_opportunities', [])
        if at_risk_opps:
            context_parts.append("CACHED CONTEXT - AT-RISK OPPORTUNITIES:")
            for opp in at_risk_opps:
                # Get full cached data for this opportunity
                cached_opp = self.entity_cache.get(f"Opportunity:{opp['id']}")
                if cached_opp:
                    opp_data = cached_opp['data']
                    account_id = opp_data.get('AccountId', 'Unknown')
                    context_parts.append(f"- Opportunity: '{opp['name']}' (ID: {opp['id']}, Account ID: {account_id})")
                    context_parts.append(f"  Status: At Risk, Account: {opp.get('account', 'Unknown')}")
                    
                    # Add Jira project key if available
                    jira_project = opp_data.get('Jira_Project_Key__c')
                    if jira_project:
                        context_parts.append(f"  Linked Jira Project: {jira_project}")
        
        # Add critical Jira issues context
        critical_jira = self.session_context.get('critical_jira_issues', [])
        if critical_jira:
            context_parts.append("\nCACHED CONTEXT - CRITICAL JIRA ISSUES:")
            for issue in critical_jira:
                context_parts.append(f"- {issue['key']}: {issue['summary']}")
                context_parts.append(f"  Status: {issue['status']}, Priority: {issue['priority']}")
        
        # Add recently cached entities summary
        recent_entities = []
        for cache_key, entity in self.entity_cache.items():
            if ':' in cache_key and not cache_key.startswith(('Opportunity:Name:', 'Case:Number:', 'Case:JiraKey:', 'Account:Name:')):
                recent_entities.append(entity)
        
        if recent_entities:
            context_parts.append(f"\nCACHED ENTITIES AVAILABLE ({len(recent_entities)} total):")
            entity_summary = {}
            for entity in recent_entities:
                entity_type = entity['type']
                if entity_type not in entity_summary:
                    entity_summary[entity_type] = 0
                entity_summary[entity_type] += 1
            
            for entity_type, count in entity_summary.items():
                context_parts.append(f"- {count} {entity_type}(s) cached and available")
        
        if context_parts:
            context_parts.append("\nIMPORTANT: Use this cached context to make intelligent inferences about user requests.")
            context_parts.append("When users refer to 'the opportunity', 'that case', or similar references, use the cached context above.")
            context_parts.append("For activity creation, use the Account ID from cached opportunity data when the user refers to a previously discussed opportunity.")
            context_parts.append("")
            return "\n".join(context_parts)
        
        return ""
    
    def _load_conversation_history(self) -> List[Dict[str, Any]]:
        """Load conversation history from file"""
        try:
            if os.path.exists(self.conversation_file):
                with open(self.conversation_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    conversations = data.get('conversations', [])
                    logger.info(f"Loaded {len(conversations)} conversation messages")
                    return conversations
            else:
                logger.info("No existing conversation history found")
                return []
        except Exception as e:
            logger.error(f"Failed to load conversation history: {e}")
            return []
    
    def _save_conversation_history(self):
        """Save conversation history to file"""
        try:
            data = {
                'conversations': self.conversation_history,
                'last_updated': datetime.now().isoformat(),
                'total_messages': len(self.conversation_history)
            }
            
            with open(self.conversation_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            logger.debug(f"Saved {len(self.conversation_history)} conversation messages")
            
        except Exception as e:
            logger.error(f"Failed to save conversation history: {e}")

    def _load_cache_from_file(self, file_path: str) -> Dict[str, Any]:
        """Load cache from file with error handling"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    logger.info(f"Loaded {len(data)} items from {file_path}")
                    return data
        except Exception as e:
            logger.warning(f"Failed to load cache from {file_path}: {e}")
        return {}
    
    def _save_cache_to_file(self, data: Dict[str, Any], file_path: str):
        """Save cache to file with error handling"""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                logger.debug(f"Saved {len(data)} items to {file_path}")
        except Exception as e:
            logger.warning(f"Failed to save cache to {file_path}: {e}")
    
    def _is_complex_task(self, message: str) -> bool:
        """Detect if a message describes a complex multi-step task"""
        complex_indicators = [
            "update the opportunity status",
            "create a jira task",
            "create a case",
            "link everything together",
            "then create",
            "also create",
            "and put that",
            "relate the case to",
            "apply the jira ticket",
            "multi-step",
            "workflow",
            "process",
            "first", "then", "next", "finally",
            "step 1", "step 2", "step 3",
            "opportunity is at risk",
            "implementation is at risk"
        ]
        
        message_lower = message.lower()
        complex_count = sum(1 for indicator in complex_indicators if indicator in message_lower)
        
        # If we find multiple indicators or specific workflow language, treat as complex
        return complex_count >= 2 or any(phrase in message_lower for phrase in [
            "jordan jones", "critical migration", "walkmart",
            "update", "create", "link", "relate"
        ])
    
    async def _process_complex_task(self, query: str) -> str:
        """Process complex multi-step tasks using Strands agent orchestration"""
        logger.info("Processing complex task with Strands agent orchestration")
        
        if not self.strands_agent:
            logger.warning("Strands agent not available, falling back to regular processing")
            return await self._process_chat_query(query)
        
        try:
            # Enhanced system prompt for complex task orchestration
            complex_task_prompt = f"""You are a specialized AI agent for complex multi-step business workflows involving Salesforce and Jira integration.

COMPLEX TASK ORCHESTRATION MODE:
You excel at breaking down complex requests into sequential steps and executing them systematically. 

WORKFLOW EXECUTION PRINCIPLES:
1. **Parse the Request**: Break down complex requests into discrete, actionable steps
2. **Execute Sequentially**: Complete each step before moving to the next
3. **Maintain Context**: Use information from previous steps to inform subsequent actions
4. **Error Recovery**: If a step fails, try alternative approaches or gather missing information
5. **Cross-System Integration**: Seamlessly coordinate between Salesforce and Jira systems
6. **Comprehensive Updates**: Ensure all related records are properly linked and updated

EXAMPLE COMPLEX WORKFLOW:
"Jordan Jones mentioned that the Critical Migration Opportunity is at risk due to a back button bug. Update the opportunity status to At Risk, create a Jira task in TECH project, and create a case with the Jira ticket reference."

EXECUTION STEPS:
1. Find Jordan Jones's account (WalkMart) and Critical Migration opportunity
2. Update opportunity Implementation_Status__c to "At Risk"
3. Create Jira task in TECH project about the back button bug
4. Create Salesforce case linked to the account
5. Update case with Jira ticket key reference
6. Link Jira project to opportunity if needed

CRITICAL SUCCESS FACTORS:
- Always search for existing records before creating new ones
- Use exact names and IDs when available
- Include rich context in descriptions (technical details, business impact)
- Verify all cross-system links are properly established
- Provide comprehensive status updates throughout the process

CURRENT CONTEXT:
{self._build_cached_context_prompt()}

Execute the complex workflow systematically, providing detailed progress updates for each step."""

            # Use Strands agent for complex task orchestration
            if hasattr(self.strands_agent, 'invoke') or hasattr(self.strands_agent, '__call__'):
                try:
                    # Try to use Strands agent directly
                    if hasattr(self.strands_agent, 'invoke'):
                        result = await self.strands_agent.invoke(query, context=complex_task_prompt)
                    else:
                        result = await self.strands_agent(query)
                    
                    return str(result)
                except Exception as e:
                    logger.warning(f"Strands agent invocation failed: {e}")
                    # Fall back to enhanced regular processing
                    return await self._process_enhanced_complex_task(query, complex_task_prompt)
            else:
                # Fall back to enhanced regular processing with complex task awareness
                return await self._process_enhanced_complex_task(query, complex_task_prompt)
                
        except Exception as e:
            logger.error(f"Error in complex task processing: {e}")
            return f"I encountered an error processing your complex task: {str(e)}. Let me try a simpler approach."
    
    async def _process_enhanced_complex_task(self, query: str, system_prompt: str) -> str:
        """Enhanced processing for complex tasks using regular Claude with complex task awareness"""
        if not self.available_tools:
            return "No MCP tools available. Please check service connections."
        
        # Build messages with conversation memory if available
        messages = []
        
        # Add conversation history from Strands memory if available
        if self.conversation_memory:
            try:
                history = self.conversation_memory.get_recent_messages()
                filtered_history = [msg for msg in history if msg.get('role') != 'system']
                messages.extend(filtered_history)
                logger.info(f"Added {len(filtered_history)} messages from conversation memory")
            except Exception as e:
                logger.warning(f"Failed to retrieve conversation memory: {e}")
        
        # Add current user message
        messages.append({'role': 'user', 'content': query})
        
        try:
            response = self.anthropic.messages.create(
                max_tokens=3000,  # Increased for complex tasks
                model='claude-3-5-sonnet-20241022',
                system=system_prompt,
                tools=self.available_tools,
                messages=messages
            )
            
            process_query = True
            full_response = ""
            step_count = 0
            max_steps = 15  # Prevent infinite loops in complex workflows
            
            while process_query and step_count < max_steps:
                step_count += 1
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
                        
                        logger.info(f"Complex task step {step_count}: {tool_name} with args {tool_args}")
                        
                        try:
                            # Find which service has this tool
                            server_name = self.tool_to_server.get(tool_name)
                            if not server_name:
                                raise ValueError(f"Tool {tool_name} not found")
                                
                            result = await self._call_mcp_tool(server_name, tool_name, tool_args)
                            
                            # Cache discovered entities from tool results
                            await self._cache_entities_from_result(tool_name, tool_args, result)
                            
                            # Format result for Claude
                            tool_result = {
                                "type": "tool_result",
                                "tool_use_id": tool_id,
                                "content": result
                            }
                            
                            messages.append({"role": "user", "content": [tool_result]})
                            
                            # Get next response from Claude
                            response = self.anthropic.messages.create(
                                max_tokens=3000,
                                model='claude-3-5-sonnet-20241022',
                                system=system_prompt,
                                tools=self.available_tools,
                                messages=messages
                            )
                            
                            if len(response.content) == 1 and response.content[0].type == "text":
                                full_response += response.content[0].text
                                process_query = False
                                
                        except Exception as e:
                            logger.error(f"Error in complex task step {step_count} - {tool_name}: {e}")
                            # Send error as tool result
                            tool_result = {
                                "type": "tool_result",
                                "tool_use_id": tool_id,
                                "content": f"Error: {str(e)}"
                            }
                            
                            messages.append({"role": "user", "content": [tool_result]})
                            
                            response = self.anthropic.messages.create(
                                max_tokens=3000,
                                model='claude-3-5-sonnet-20241022',
                                system=system_prompt,
                                tools=self.available_tools,
                                messages=messages
                            )
                            
                            if len(response.content) == 1 and response.content[0].type == "text":
                                full_response += f"\nStep {step_count} encountered an error: {str(e)}\n"
                                full_response += response.content[0].text
                                process_query = False
            
            if step_count >= max_steps:
                full_response += f"\n\nCompleted {step_count} steps in complex workflow. Task processing complete."
                
            # Store conversation in memory if available
            if self.conversation_memory:
                try:
                    self.conversation_memory.add_message({'role': 'user', 'content': query})
                    self.conversation_memory.add_message({'role': 'assistant', 'content': full_response})
                    logger.info("Stored complex task conversation in memory")
                except Exception as e:
                    logger.warning(f"Failed to store conversation in memory: {e}")
            
            return full_response
            
        except Exception as e:
            logger.error(f"Error processing enhanced complex task: {e}")
            return f"I encountered an error processing your complex task: {str(e)}"
    
    def _format_response_text(self, text: str) -> str:
        """Apply advanced formatting to response text for better readability"""
        import re
        
        # Don't format if text is too short
        if len(text.strip()) < 50:
            return text
        
        formatted_text = text
        
        # 1. Add status badges for common operations
        status_patterns = {
            r'\b(successfully created|created successfully)\b': '✅ **Successfully Created**',
            r'\b(successfully updated|updated successfully)\b': '✅ **Successfully Updated**',
            r'\b(successfully deleted|deleted successfully)\b': '✅ **Successfully Deleted**',
            r'\b(completed successfully|successfully completed)\b': '✅ **Successfully Completed**',
            r'\b(failed to|error|unable to)\b': '❌ **Error**',
            r'\b(warning|caution|note)\b': '⚠️ **Warning**',
            r'\b(in progress|processing|working on)\b': '🔄 **In Progress**',
            r'\b(found|discovered|identified)\b': '🔍 **Found**',
        }
        
        for pattern, replacement in status_patterns.items():
            formatted_text = re.sub(pattern, replacement, formatted_text, flags=re.IGNORECASE)
        
        # 2. Format technical identifiers and IDs
        id_patterns = {
            r'\b([A-Z0-9]{15,18})\b': '`$1`',  # Salesforce IDs
            r'\b([A-Z]+-\d+)\b': '**$1**',     # Jira issue keys
            r'\b(Account ID|Opportunity ID|Case ID|Contact ID):\s*([A-Z0-9]+)': '$1: `$2`',
        }
        
        for pattern, replacement in id_patterns.items():
            formatted_text = re.sub(pattern, replacement, formatted_text)
        
        # 3. Structure multi-step processes
        if re.search(r'\b(step \d+|first|then|next|finally)\b', formatted_text, re.IGNORECASE):
            # Add step indicators
            formatted_text = re.sub(r'\b(step \d+):', r'### 🔸 $1:', formatted_text, flags=re.IGNORECASE)
            formatted_text = re.sub(r'\b(first):', r'### 1️⃣ First:', formatted_text, flags=re.IGNORECASE)
            formatted_text = re.sub(r'\b(then):', r'### 2️⃣ Then:', formatted_text, flags=re.IGNORECASE)
            formatted_text = re.sub(r'\b(next):', r'### 3️⃣ Next:', formatted_text, flags=re.IGNORECASE)
            formatted_text = re.sub(r'\b(finally):', r'### ✅ Finally:', formatted_text, flags=re.IGNORECASE)
        
        # 4. Highlight important business entities
        entity_patterns = {
            r'\b(Opportunity|Account|Case|Contact|Lead):\s*([^,\n]+)': '**$1**: *$2*',
            r'\b(Implementation Status|Priority|Status):\s*([^,\n]+)': '**$1**: `$2`',
        }
        
        for pattern, replacement in entity_patterns.items():
            formatted_text = re.sub(pattern, replacement, formatted_text)
        
        # 5. Format lists and bullet points
        lines = formatted_text.split('\n')
        formatted_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            # Convert simple lists to formatted bullet points
            if stripped.startswith('- ') and not stripped.startswith('- **'):
                formatted_lines.append(f"• {stripped[2:]}")
            elif re.match(r'^\d+\.\s', stripped):
                # Number lists
                formatted_lines.append(f"**{stripped}**")
            else:
                formatted_lines.append(line)
        
        formatted_text = '\n'.join(formatted_lines)
        
        # 6. Add section breaks for long responses
        if len(formatted_text) > 500:
            # Add summary section if response is long
            if 'successfully' in formatted_text.lower() and 'created' in formatted_text.lower():
                formatted_text = "## 📋 **Operation Summary**\n\n" + formatted_text
        
        # 7. Format code-like content
        formatted_text = re.sub(r'\b(SOQL|SQL):\s*([^,\n]+)', r'**$1**: ```sql\n$2\n```', formatted_text)
        
        return formatted_text
    
    def _persist_caches(self):
        """Persist both entity cache and session context to files"""
        try:
            self._save_cache_to_file(self.entity_cache, self.cache_file)
            self._save_cache_to_file(self.session_context, self.context_file)
            logger.info(f"Persisted {len(self.entity_cache)} entities and {len(self.session_context)} context items")
        except Exception as e:
            logger.warning(f"Failed to persist caches: {e}")
    
    def _extract_entity_name(self, entity_data: Dict[str, Any]) -> str:
        """Extract a display name from entity data"""
        try:
            data = entity_data.get('data', {})
            # Try common name fields
            for field in ['Name', 'CaseNumber', 'summary', 'key', 'Subject']:
                if field in data and data[field]:
                    return str(data[field])
            
            # Fallback to ID or type
            return entity_data.get('id', entity_data.get('type', 'Unknown'))
        except Exception:
            return 'Unknown'
    
    def _extract_entity_description(self, entity_data: Dict[str, Any]) -> Optional[str]:
        """Extract a description from entity data"""
        try:
            data = entity_data.get('data', {})
            # Try common description fields
            for field in ['Description', 'Subject', 'summary', 'Status']:
                if field in data and data[field]:
                    return str(data[field])[:200]  # Limit length
            return None
        except Exception:
            return None
    
    def _extract_entity_metadata(self, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from entity data"""
        try:
            data = entity_data.get('data', {})
            metadata = {}
            
            # Common metadata fields
            metadata_fields = [
                'Status', 'Priority', 'Implementation_Status__c', 
                'Jira_Issue_Key__c', 'Jira_Project_Key__c', 'AccountId',
                'Amount', 'CloseDate', 'StageName', 'Type'
            ]
            
            for field in metadata_fields:
                if field in data and data[field] is not None:
                    metadata[field] = data[field]
            
            return metadata
        except Exception:
            return {}

    async def _process_with_thinking_capture(self, query: str, session_id: str, capture_thinking: bool = True) -> tuple:
        """Process chat with enhanced thinking capture"""
        
        if not self.available_tools:
            return "No MCP tools available. Please check service connections.", [], []
        
        # Initialize thinking steps for this session
        if capture_thinking:
            self.thinking_sessions[session_id] = []
        
        # Enhanced system prompt that encourages explicit reasoning
        system_prompt = f"""You are an AI assistant with access to Salesforce and Jira systems through MCP tools.

THINKING PROCESS INSTRUCTIONS:
When processing requests, you should think step-by-step and be explicit about your reasoning process. 

For each major decision, consider:
1. What information do I need to gather?
2. Which tools should I use and why?
3. What parameters should I pass and why?
4. How does this step connect to the overall goal?
5. What are alternative approaches I could take?

Be thorough in your analysis and explain your reasoning clearly.

Available tools: {[tool['name'] for tool in self.available_tools]}

Your goal is to provide comprehensive, well-reasoned responses while being transparent about your decision-making process."""
        
        messages = [{'role': 'user', 'content': query}]
        
        try:
            response = self.anthropic.messages.create(
                max_tokens=2024,
                model='claude-3-5-sonnet-20241022',
                system=system_prompt,
                tools=self.available_tools,
                messages=messages
            )
            
            process_query = True
            full_response = ""
            tool_calls = []
            step_counter = 0
            
            while process_query:
                assistant_content = []
                
                for content in response.content:
                    if content.type == 'text':
                        # Capture thinking from text content
                        if capture_thinking:
                            await self._extract_thinking_from_text(content.text, session_id, step_counter)
                            step_counter += 1
                        
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
                        
                        # Capture tool selection thinking
                        if capture_thinking:
                            await self._capture_tool_selection_thinking(
                                tool_name, tool_args, session_id, step_counter
                            )
                            step_counter += 1
                        
                        logger.info(f"Claude calling tool {tool_name} with args {tool_args}")
                        
                        # Record tool call
                        tool_call_record = {
                            "tool_name": tool_name,
                            "arguments": tool_args,
                            "timestamp": datetime.now().isoformat()
                        }
                        tool_calls.append(tool_call_record)
                        
                        try:
                            # Find which service has this tool
                            server_name = self.tool_to_server.get(tool_name)
                            if not server_name:
                                raise ValueError(f"Tool {tool_name} not found")
                                
                            result = await self._call_mcp_tool(server_name, tool_name, tool_args)
                            
                            # Capture result analysis thinking
                            if capture_thinking:
                                await self._capture_result_analysis_thinking(
                                    tool_name, result, session_id, step_counter
                                )
                                step_counter += 1
                            
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
                                system=system_prompt,
                                tools=self.available_tools,
                                messages=messages
                            )
                            
                            if len(response.content) == 1 and response.content[0].type == "text":
                                # Capture final analysis thinking
                                if capture_thinking:
                                    await self._extract_thinking_from_text(
                                        response.content[0].text, session_id, step_counter
                                    )
                                
                                full_response += "\n\n" + response.content[0].text
                                process_query = False
                                
                        except Exception as e:
                            logger.error(f"Error calling tool {tool_name}: {e}")
                            
                            # Capture error handling thinking
                            if capture_thinking:
                                await self._capture_error_handling_thinking(
                                    tool_name, str(e), session_id, step_counter
                                )
                            
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
                                system=system_prompt,
                                tools=self.available_tools,
                                messages=messages
                            )
                            
                            if len(response.content) == 1 and response.content[0].type == "text":
                                full_response += f"\nI encountered an error: {str(e)}\n"
                                full_response += response.content[0].text
                                process_query = False
            
            thinking_steps = self.thinking_sessions.get(session_id, []) if capture_thinking else []
            return full_response, thinking_steps, tool_calls
            
        except Exception as e:
            logger.error(f"Error processing chat query: {e}")
            return f"I encountered an error processing your request: {str(e)}", [], []
    
    async def _extract_thinking_from_text(self, text: str, session_id: str, step_number: int):
        """Extract thinking patterns from Claude's text responses"""
        thinking_patterns = [
            (r"I need to|I should|I'll|Let me", "reasoning"),
            (r"First|Then|Next|Finally", "sequential_planning"),
            (r"because|since|due to|as a result", "causal_reasoning"),
            (r"Looking at|Analyzing|Examining", "analysis"),
            (r"This means|This indicates|This suggests", "inference"),
            (r"I'll use|I'll call|I'll query", "tool_selection"),
            (r"The best approach|I could also|Alternatively", "strategy_consideration")
        ]
        
        for pattern, thinking_type in thinking_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Extract sentence containing the thinking pattern
                sentences = re.split(r'[.!?]+', text)
                for sentence in sentences:
                    if match.group() in sentence:
                        thinking_step = ThinkingStep(
                            step_number=step_number,
                            timestamp=datetime.now().isoformat(),
                            type=thinking_type,
                            content=sentence.strip(),
                            confidence=0.8  # Default confidence for extracted thinking
                        )
                        self.thinking_sessions[session_id].append(thinking_step)
                        break
                break
    
    async def _capture_tool_selection_thinking(self, tool_name: str, tool_args: Dict[str, Any], session_id: str, step_number: int):
        """Capture thinking about tool selection"""
        thinking_step = ThinkingStep(
            step_number=step_number,
            timestamp=datetime.now().isoformat(),
            type="tool_selection",
            content=f"Selected tool '{tool_name}' to accomplish the task. Parameters chosen: {json.dumps(tool_args, indent=2)}",
            confidence=0.9,
            alternatives_considered=[f"Could have used other tools: {list(self.tool_to_server.keys())}"]
        )
        self.thinking_sessions[session_id].append(thinking_step)
    
    async def _capture_result_analysis_thinking(self, tool_name: str, result: str, session_id: str, step_number: int):
        """Capture thinking about tool result analysis"""
        # Analyze result to infer thinking
        result_preview = result[:200] + "..." if len(result) > 200 else result
        
        thinking_step = ThinkingStep(
            step_number=step_number,
            timestamp=datetime.now().isoformat(),
            type="result_analysis",
            content=f"Analyzing result from '{tool_name}': {result_preview}. This data will help me formulate the response and determine if additional tool calls are needed.",
            confidence=0.7
        )
        self.thinking_sessions[session_id].append(thinking_step)
    
    async def _capture_error_handling_thinking(self, tool_name: str, error: str, session_id: str, step_number: int):
        """Capture thinking about error handling"""
        thinking_step = ThinkingStep(
            step_number=step_number,
            timestamp=datetime.now().isoformat(),
            type="error_handling",
            content=f"Encountered error with '{tool_name}': {error}. Need to handle this gracefully and potentially try alternative approaches.",
            confidence=0.8
        )
        self.thinking_sessions[session_id].append(thinking_step)

    def _ensure_memory_persistence(self):
        """Ensure memory is persisted after each significant operation"""
        try:
            # Always persist after chat operations
            self._persist_caches()
        except Exception as e:
            logger.warning(f"Failed to ensure memory persistence: {e}")

    async def _stop_mcp_services(self):
        """Stop HTTP session and persist caches"""
        # Persist fallback caches
        self._persist_caches()

        # Persist Strands memories
        if self.entity_memory:
            try:
                all_entities = await self.entity_memory.get_all_entities()
                self._save_cache_to_file(all_entities, "logs/strands_entity_memory.json")
                logger.info("Persisted Strands entity memory")
            except Exception as e:
                logger.warning(f"Failed to persist entity_memory: {e}")
        
        if self.context_memory:
            try:
                all_contexts = await self.context_memory.get_all_contexts()
                self._save_cache_to_file(all_contexts, "logs/strands_context_memory.json")
                logger.info("Persisted Strands context memory")
            except Exception as e:
                logger.warning(f"Failed to persist context_memory: {e}")

        if self.http_session:
            await self.http_session.close()
            logger.info("HTTP session closed")

def main():
    """Main entry point"""
    server = MCPWebServer()
    
    logger.info("Starting Strands MCP Web Server")
    logger.info("Features: MCP Integration, Strands SDK, Anthropic API")
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
