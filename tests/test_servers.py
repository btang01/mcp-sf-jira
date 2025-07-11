#!/usr/bin/env python3
"""
Unit tests for individual MCP servers
"""

import sys
import os
import subprocess
import time
import requests
import pytest


class TestSalesforceServer:
    """Test Salesforce MCP server"""
    
    def test_http_mode_startup(self):
        """Test that Salesforce server starts in HTTP mode"""
        # Change to project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        process = subprocess.Popen([
            sys.executable, "salesforce_server_mcp.py"
        ], 
        cwd=os.path.join(project_root, "python_servers"),
        env={**dict(os.environ), "MCP_SERVER_PORT": "8001"},
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE
        )
        
        try:
            time.sleep(3)
            
            # Test health endpoint
            response = requests.get("http://localhost:8001/health", timeout=5)
            assert response.status_code == 200
            
            health_data = response.json()
            assert health_data["status"] == "healthy"
            assert health_data["service"] == "salesforce-mcp"
            
            # Test tools endpoint
            tools_response = requests.get("http://localhost:8001/tools", timeout=5)
            assert tools_response.status_code == 200
            
            tools_data = tools_response.json()
            assert "tools" in tools_data
            assert len(tools_data["tools"]) == 5  # Expected 5 Salesforce tools
            
        finally:
            process.terminate()
            process.wait(timeout=5)


class TestJiraServer:
    """Test Jira MCP server"""
    
    def test_http_mode_startup(self):
        """Test that Jira server starts in HTTP mode"""
        # Change to project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        process = subprocess.Popen([
            sys.executable, "jira_server_mcp.py"
        ], 
        cwd=os.path.join(project_root, "python_servers"),
        env={**dict(os.environ), "MCP_SERVER_PORT": "8002"},
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE
        )
        
        try:
            time.sleep(3)
            
            # Test health endpoint
            response = requests.get("http://localhost:8002/health", timeout=5)
            assert response.status_code == 200
            
            health_data = response.json()
            assert health_data["status"] == "healthy"
            assert health_data["service"] == "jira-mcp"
            
            # Test tools endpoint
            tools_response = requests.get("http://localhost:8002/tools", timeout=5)
            assert tools_response.status_code == 200
            
            tools_data = tools_response.json()
            assert "tools" in tools_data
            assert len(tools_data["tools"]) == 3  # Expected 3 Jira tools
            
        finally:
            process.terminate()
            process.wait(timeout=5)


class TestWebServer:
    """Test MCP web server with Strands SDK"""
    
    def test_initialization(self):
        """Test that web server initializes correctly"""
        # Change to project root and add to path
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.append(os.path.join(project_root, "python_servers"))
        
        from mcp_web_server import MCPWebServer
        
        # Create an instance (this tests initialization)
        server = MCPWebServer()
        
        # Test that the FastAPI app was created
        assert hasattr(server, 'app')
        assert server.app is not None
        
        # Test that MCP processes dict exists
        assert hasattr(server, 'mcp_processes')
        assert isinstance(server.mcp_processes, dict)
        
        # Test that tools tracking exists
        assert hasattr(server, 'available_tools')
        assert hasattr(server, 'tool_to_server')


if __name__ == "__main__":
    # Run tests manually if pytest not available
    import unittest
    
    class TestSalesforceServerManual(unittest.TestCase):
        def test_startup(self):
            test = TestSalesforceServer()
            test.test_http_mode_startup()
    
    class TestJiraServerManual(unittest.TestCase):
        def test_startup(self):
            test = TestJiraServer()
            test.test_http_mode_startup()
    
    class TestWebServerManual(unittest.TestCase):
        def test_init(self):
            test = TestWebServer()
            test.test_initialization()
    
    unittest.main()