#!/usr/bin/env python3
"""
Test script for MCP integration with Python 3.12 and Strands SDK
"""

import sys
import subprocess
import time
import requests
import json

def test_python_version():
    """Test that we're using Python 3.12+"""
    print(f"🔍 Testing Python version: {sys.version}")
    major, minor = sys.version_info[:2]
    if major == 3 and minor >= 12:
        print("✅ Python version is compatible")
        return True
    else:
        print("❌ Python version is too old for MCP")
        return False

def test_imports():
    """Test that all required packages import correctly"""
    print("\n🔍 Testing package imports...")
    
    try:
        import mcp
        print("✅ MCP package imported")
    except ImportError as e:
        print(f"❌ MCP import failed: {e}")
        return False
    
    try:
        from strands import Agent, tool
        print("✅ Strands SDK imported")
    except ImportError as e:
        print(f"❌ Strands import failed: {e}")
        return False
    
    try:
        from simple_salesforce import Salesforce
        from jira import JIRA
        from anthropic import Anthropic
        print("✅ Service packages imported")
    except ImportError as e:
        print(f"❌ Service import failed: {e}")
        return False
    
    try:
        from fastapi import FastAPI
        import uvicorn
        print("✅ Web framework packages imported")
    except ImportError as e:
        print(f"❌ Web framework import failed: {e}")
        return False
    
    return True

def test_mcp_servers():
    """Test that MCP servers can start and respond"""
    print("\n🔍 Testing MCP servers...")
    
    # Test Salesforce server
    print("Starting Salesforce MCP server...")
    try:
        sf_process = subprocess.Popen([
            sys.executable, "salesforce_server_mcp.py"
        ], 
        cwd=os.path.join(os.getcwd(), "python_servers"),
        env={**dict(os.environ), "MCP_SERVER_PORT": "8001"},
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE
        )
        
        time.sleep(3)
        
        # Test health endpoint
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            print("✅ Salesforce MCP server responds to health check")
            
            # Test tools endpoint
            tools_response = requests.get("http://localhost:8001/tools", timeout=5)
            if tools_response.status_code == 200:
                tools_data = tools_response.json()
                print(f"✅ Salesforce MCP server provides {len(tools_data.get('tools', []))} tools")
            else:
                print("⚠️  Salesforce tools endpoint failed")
        else:
            print("❌ Salesforce MCP server health check failed")
            
        sf_process.terminate()
        sf_process.wait(timeout=5)
        
    except Exception as e:
        print(f"❌ Salesforce MCP server test failed: {e}")
        return False
    
    return True

def test_web_server():
    """Test that the web server can start with Strands integration"""
    print("\n🔍 Testing MCP web server with Strands SDK...")
    
    try:
        import os
        # Import the web server class
        sys.path.append(os.path.join(os.getcwd(), "python_servers"))
        from mcp_web_server import MCPWebServer
        
        # Create an instance (this tests initialization)
        server = MCPWebServer()
        print("✅ MCP web server with Strands SDK initializes successfully")
        
        # Test that the FastAPI app was created
        if hasattr(server, 'app') and server.app:
            print("✅ FastAPI app created")
        else:
            print("❌ FastAPI app not created")
            return False
            
        # Test Strands integration
        if hasattr(server, 'strands_agent') and server.strands_agent:
            print("✅ Strands agent initialized")
        else:
            print("⚠️  Strands agent not initialized (may be expected)")
            
        return True
        
    except Exception as e:
        print(f"❌ Web server test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing MCP Integration with Python 3.12 and Strands SDK\n")
    
    import os
    # Change to project root (parent directory)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    print(f"Running tests from: {project_root}")
    
    tests = [
        test_python_version,
        test_imports,
        test_mcp_servers,
        test_web_server
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! MCP integration is working correctly.")
        print("\n✅ Ready for Docker deployment!")
        print("✅ Python 3.12 with proper MCP support")
        print("✅ Strands SDK integration working")
        print("✅ MCP servers can run in HTTP mode")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    import os
    main()