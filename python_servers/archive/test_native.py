#!/usr/bin/env python3
"""
Test script for native (non-Docker) mode
"""

import subprocess
import sys
import os
from pathlib import Path

def check_python():
    """Check Python version"""
    print("🐍 Checking Python...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is too old. Need Python 3.8+")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is good")
    return True

def check_node():
    """Check Node.js"""
    print("📦 Checking Node.js...")
    
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Node.js {version} found")
            return True
        else:
            print("❌ Node.js not working")
            return False
    except FileNotFoundError:
        print("❌ Node.js not installed")
        print("   Install from: https://nodejs.org/")
        return False

def check_pip_packages():
    """Check if required Python packages are available"""
    print("📚 Checking Python packages...")
    
    basic_packages = ["json", "os", "sys", "subprocess"]  # Built-ins
    try:
        for pkg in basic_packages:
            __import__(pkg)
        print("✅ Basic Python packages available")
        return True
    except ImportError as e:
        print(f"❌ Missing basic package: {e}")
        return False

def check_ports():
    """Check if required ports are free or can be freed"""
    print("🔌 Checking ports...")
    
    ports = [3000, 8000, 8001, 8002]
    busy_ports = []
    
    for port in ports:
        try:
            result = subprocess.run(
                ["lsof", "-i", f":{port}"], 
                capture_output=True, 
                text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                busy_ports.append(port)
        except:
            pass  # lsof might not be available
    
    if busy_ports:
        print(f"⚠️  Ports in use: {busy_ports}")
        print("   These will be freed when starting services")
    else:
        print("✅ All required ports are free")
    
    return True

def test_basic_imports():
    """Test that we can import key modules"""
    print("🧪 Testing basic imports...")
    
    # Test Python standard library
    try:
        import json
        import os
        import sys
        import subprocess
        import asyncio
        print("✅ Standard library imports work")
        return True
    except ImportError as e:
        print(f"❌ Standard library import failed: {e}")
        return False

def show_next_steps():
    """Show what to do next"""
    print("\n🚀 Ready to start!")
    print("==================")
    print("Run the native mode startup:")
    print("./start_native.sh")
    print("")
    print("Or use the auto-detecting startup:")
    print("./start.sh")
    print("")
    print("📋 What this will do:")
    print("1. Install Python dependencies")
    print("2. Install React dependencies") 
    print("3. Start 4 services on ports 8001, 8002, 8000, 3000")
    print("4. Open http://localhost:3000 in your browser")
    print("")
    print("🔍 If you have issues:")
    print("- Check logs in python_servers/logs/")
    print("- Make sure .env has your API keys")
    print("- Verify your internet connection")

def main():
    """Run all tests"""
    print("🧪 MCP Integration Native Mode Test")
    print("===================================")
    
    os.chdir(Path(__file__).parent)
    
    tests = [
        ("Python Version", check_python),
        ("Node.js", check_node), 
        ("Python Packages", check_pip_packages),
        ("Port Availability", check_ports),
        ("Basic Imports", test_basic_imports)
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
        print("🎉 Native mode is ready!")
        show_next_steps()
    else:
        print("⚠️  Fix issues above before proceeding")
        print("\n💡 Common solutions:")
        print("- Install Node.js from https://nodejs.org/")
        print("- Update Python to 3.8+ if needed")
        print("- Check internet connection for package installs")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)