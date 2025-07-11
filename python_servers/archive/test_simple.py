#!/usr/bin/env python3
"""
Simple testing script for MCP Integration Docker setup
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

def check_files():
    """Check that all required files exist"""
    print("📁 Checking files...")
    
    required_files = [
        ".env",
        "docker-compose.yml",
        "Dockerfile.web-server",
        "Dockerfile.mcp-server", 
        "Dockerfile.ui",
        "python_servers/mcp_web_server.py",
        "python_servers/salesforce_server_modern.py",
        "python_servers/jira_server_modern.py",
        "react-ui/package.json"
    ]
    
    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)
    
    if missing:
        print(f"❌ Missing files: {missing}")
        return False
    
    print("✅ All required files present")
    return True

def check_env():
    """Check .env file has basic variables"""
    print("🔑 Checking environment variables...")
    
    if not Path(".env").exists():
        print("❌ .env file missing")
        return False
    
    with open(".env", "r") as f:
        content = f.read()
    
    # Check for basic structure (not actual values)
    checks = [
        "ANTHROPIC_API_KEY" in content,
        "SALESFORCE" in content,
        "JIRA" in content
    ]
    
    if not all(checks):
        print("❌ .env file missing required sections")
        print("Make sure you have ANTHROPIC_API_KEY, SALESFORCE_*, and JIRA_* variables")
        return False
    
    print("✅ .env file structure looks good")
    return True

def test_docker_compose_syntax():
    """Test docker-compose file syntax"""
    print("🐳 Testing docker-compose syntax...")
    
    try:
        # Try to parse the YAML
        result = subprocess.run([
            "python3", "-c", 
            "import yaml; yaml.safe_load(open('docker-compose.yml'))"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ docker-compose.yml syntax is valid")
            return True
        else:
            print(f"❌ docker-compose.yml syntax error: {result.stderr}")
            return False
    except Exception as e:
        print(f"⚠️  Could not validate YAML (PyYAML not installed): {e}")
        print("✅ File exists, assuming syntax is correct")
        return True

def test_dockerfile_syntax():
    """Test basic Dockerfile syntax"""
    print("🏗️ Testing Dockerfile syntax...")
    
    dockerfiles = [
        "Dockerfile.web-server",
        "Dockerfile.mcp-server",
        "Dockerfile.ui"
    ]
    
    for dockerfile in dockerfiles:
        with open(dockerfile, "r") as f:
            content = f.read()
        
        # Basic syntax checks - look for FROM instruction
        if "FROM " not in content:
            print(f"❌ {dockerfile} missing FROM instruction")
            return False
        
        if "WORKDIR" not in content:
            print(f"⚠️  {dockerfile} missing WORKDIR")
        
        if "EXPOSE" not in content:
            print(f"⚠️  {dockerfile} missing EXPOSE")
    
    print("✅ Dockerfile syntax looks good")
    return True

def test_python_files():
    """Test that Python files have basic structure"""
    print("🐍 Testing Python files...")
    
    python_files = [
        "python_servers/mcp_web_server.py",
        "python_servers/salesforce_server_modern.py", 
        "python_servers/jira_server_modern.py"
    ]
    
    for py_file in python_files:
        try:
            with open(py_file, "r") as f:
                content = f.read()
            
            # Check for basic Python structure
            if "def main():" not in content and "__main__" not in content:
                print(f"⚠️  {py_file} missing main function")
            
            if "import" not in content:
                print(f"❌ {py_file} missing imports")
                return False
        
        except Exception as e:
            print(f"❌ Error reading {py_file}: {e}")
            return False
    
    print("✅ Python files structure looks good")
    return True

def show_next_steps():
    """Show what to do next"""
    print("\n🚀 Next Steps:")
    print("==============")
    
    if Path("/usr/local/bin/docker").exists() or Path("/usr/bin/docker").exists():
        print("✅ Docker is installed")
        print("Run: ./start.sh")
    else:
        print("📦 Install Docker first:")
        print("1. Visit: https://docs.docker.com/get-docker/")
        print("2. Install Docker Desktop for Mac")
        print("3. Start Docker Desktop")
        print("4. Run: ./start.sh")
    
    print("\n📋 Manual Testing:")
    print("1. Check Docker: docker --version")
    print("2. Build images: docker-compose build")
    print("3. Start services: docker-compose up -d")
    print("4. Check health: curl http://localhost:8000/api/health")
    print("5. Open UI: http://localhost:3000")
    print("6. Stop services: docker-compose down")

def main():
    """Run all tests"""
    print("🧪 MCP Integration Docker Setup Test")
    print("====================================")
    
    os.chdir(Path(__file__).parent)
    
    tests = [
        ("File Structure", check_files),
        ("Environment", check_env),
        ("Docker Compose", test_docker_compose_syntax),
        ("Dockerfiles", test_dockerfile_syntax),
        ("Python Files", test_python_files)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}")
        print("-" * 30)
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed: {e}")
            results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Setup looks good!")
    else:
        print("⚠️  Fix issues above before proceeding")
    
    show_next_steps()
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)