#!/usr/bin/env python3
"""
Test runner for MCP Integration test suite
"""

import os
import sys
import subprocess


def run_all_tests():
    """Run all tests in the test suite"""
    print("🧪 Running MCP Integration Test Suite")
    print("=" * 50)
    
    # Change to project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    print(f"Running from: {project_root}")
    
    # Check if pytest is available
    try:
        import pytest
        print("✅ pytest found, running with pytest")
        
        # Run with pytest
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/", 
            "-v", 
            "--tb=short"
        ], capture_output=False)
        
        return result.returncode == 0
        
    except ImportError:
        print("⚠️  pytest not found, running manual tests")
        
        # Run manual tests
        test_files = [
            "tests/test_imports.py",
            "tests/test_servers.py", 
            "tests/test_mcp_setup.py"
        ]
        
        all_passed = True
        
        for test_file in test_files:
            print(f"\n📋 Running {test_file}...")
            try:
                result = subprocess.run([sys.executable, test_file], 
                                      capture_output=False, 
                                      timeout=60)
                if result.returncode != 0:
                    all_passed = False
                    print(f"❌ {test_file} failed")
                else:
                    print(f"✅ {test_file} passed")
            except subprocess.TimeoutExpired:
                print(f"⏰ {test_file} timed out")
                all_passed = False
            except Exception as e:
                print(f"💥 {test_file} crashed: {e}")
                all_passed = False
        
        return all_passed


def run_quick_check():
    """Run a quick health check"""
    print("⚡ Quick Health Check")
    print("=" * 30)
    
    # Change to project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    
    try:
        # Run the main setup test
        result = subprocess.run([
            sys.executable, "tests/test_mcp_setup.py"
        ], capture_output=False, timeout=30)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Quick check failed: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        success = run_quick_check()
    else:
        success = run_all_tests()
    
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)