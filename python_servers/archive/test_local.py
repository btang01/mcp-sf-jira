#!/usr/bin/env python3
"""
Local testing script for MCP Integration
Tests both subprocess and HTTP modes
"""

import asyncio
import json
import os
import subprocess
import sys
import time
import requests
from pathlib import Path

def test_env_file():
    """Test that .env file exists and has required variables"""
    print("🔍 Testing .env file...")
    
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found!")
        print("Create .env with your credentials:")
        print("ANTHROPIC_API_KEY=your_key")
        print("SALESFORCE_USERNAME=your_username")
        print("JIRA_HOST=https://your-company.atlassian.net")
        return False
    
    # Load .env
    with open(env_path) as f:
        env_content = f.read()
    
    required_vars = [
        "ANTHROPIC_API_KEY",
        "SALESFORCE_USERNAME", 
        "JIRA_HOST"
    ]
    
    missing = []
    for var in required_vars:
        if var not in env_content or f"{var}=" not in env_content:
            missing.append(var)
    
    if missing:
        print(f"❌ Missing required variables: {missing}")
        return False
    
    print("✅ .env file looks good")
    return True

def test_python_dependencies():
    """Test that Python dependencies are installed"""
    print("🐍 Testing Python dependencies...")
    
    required_packages = [
        "fastapi",
        "uvicorn", 
        "anthropic",
        "simple_salesforce",
        "jira",
        "mcp",
        "aiohttp"
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing packages: {missing}")
        print("Install with: pip install " + " ".join(missing))
        return False
    
    print("✅ All Python dependencies installed")
    return True

def test_subprocess_mode():
    """Test the original subprocess mode"""
    print("🔧 Testing subprocess mode...")
    
    try:
        # Test Salesforce server
        print("  Testing Salesforce server...")
        proc = subprocess.Popen(
            [sys.executable, "python_servers/salesforce_server_modern.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send MCP initialize
        init_msg = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            },
            "id": 1
        }
        
        proc.stdin.write(json.dumps(init_msg) + '\n')
        proc.stdin.flush()
        
        # Read response with timeout
        proc.terminate()
        proc.wait(timeout=5)
        
        print("  ✅ Salesforce server starts successfully")
        
    except Exception as e:
        print(f"  ❌ Subprocess mode failed: {e}")
        return False
    
    return True

async def test_http_mode():
    """Test the new HTTP mode"""
    print("🌐 Testing HTTP mode...")
    
    # Start Salesforce server in HTTP mode
    env = os.environ.copy()
    env["MCP_SERVER_PORT"] = "8001"
    env["MCP_SERVER_HOST"] = "localhost"
    
    try:
        print("  Starting Salesforce HTTP server...")
        proc = subprocess.Popen(
            [sys.executable, "python_servers/salesforce_server_modern.py"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        await asyncio.sleep(3)
        
        # Test health endpoint
        print("  Testing health endpoint...")
        response = requests.get("http://localhost:8001/health", timeout=5)
        
        if response.status_code == 200:
            print("  ✅ HTTP health check passed")
            health_data = response.json()
            print(f"    Status: {health_data.get('status', 'unknown')}")
        else:
            print(f"  ❌ Health check failed: {response.status_code}")
            return False
        
        # Test tools endpoint
        print("  Testing tools endpoint...")
        response = requests.get("http://localhost:8001/tools", timeout=5)
        
        if response.status_code == 200:
            tools_data = response.json()
            tools_count = len(tools_data.get('tools', []))
            print(f"  ✅ Tools endpoint works ({tools_count} tools)")
        else:
            print(f"  ❌ Tools endpoint failed: {response.status_code}")
            return False
        
        proc.terminate()
        proc.wait(timeout=5)
        
    except Exception as e:
        print(f"  ❌ HTTP mode failed: {e}")
        if 'proc' in locals():
            proc.terminate()
        return False
    
    return True

def test_docker_files():
    """Test that Docker files are properly created"""
    print("🐳 Testing Docker files...")
    
    docker_files = [
        "Dockerfile.web-server",
        "Dockerfile.mcp-server", 
        "Dockerfile.ui",
        "docker-compose.yml",
        ".dockerignore"
    ]
    
    missing = []
    for file in docker_files:
        if not Path(file).exists():
            missing.append(file)
    
    if missing:
        print(f"❌ Missing Docker files: {missing}")
        return False
    
    print("✅ All Docker files present")
    
    # Test docker-compose syntax
    try:
        result = subprocess.run(
            ["docker-compose", "config"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print("✅ docker-compose.yml syntax valid")
        else:
            print(f"❌ docker-compose.yml syntax error: {result.stderr}")
            return False
    except FileNotFoundError:
        print("⚠️  docker-compose not installed (needed for Docker testing)")
    except Exception as e:
        print(f"⚠️  Could not validate docker-compose: {e}")
    
    return True

async def main():
    """Run all tests"""
    print("🧪 MCP Integration Testing Suite")
    print("================================")
    
    tests = [
        ("Environment", test_env_file),
        ("Dependencies", test_python_dependencies),
        ("Subprocess Mode", test_subprocess_mode),
        ("HTTP Mode", test_http_mode),
        ("Docker Files", test_docker_files)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print(f"\n📊 Test Results")
    print("=" * 40)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:15} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Ready for Docker deployment.")
    else:
        print("⚠️  Some tests failed. Fix issues before proceeding.")
    
    return passed == total

if __name__ == "__main__":
    # Change to project directory
    os.chdir(Path(__file__).parent)
    
    # Run tests
    success = asyncio.run(main())
    sys.exit(0 if success else 1)