#!/usr/bin/env python3
"""
Tests for package imports and Python version compatibility
"""

import sys
import pytest


class TestPythonVersion:
    """Test Python version compatibility"""
    
    def test_python_version_minimum(self):
        """Test that Python version is 3.10+"""
        major, minor = sys.version_info[:2]
        assert major == 3, f"Expected Python 3.x, got {major}.{minor}"
        assert minor >= 10, f"Python 3.10+ required, got {major}.{minor}"
    
    def test_python_version_recommended(self):
        """Test that Python version is 3.12+ (recommended)"""
        major, minor = sys.version_info[:2]
        if major == 3 and minor >= 12:
            print(f"✅ Using recommended Python {major}.{minor}")
        else:
            print(f"⚠️  Using Python {major}.{minor}, recommend upgrading to 3.12+")


class TestCoreImports:
    """Test core package imports"""
    
    def test_mcp_import(self):
        """Test that MCP package imports correctly"""
        try:
            import mcp
            # Test basic MCP classes
            from mcp.server import Server
            from mcp.types import Tool, CallToolResult
        except ImportError as e:
            pytest.fail(f"MCP import failed: {e}")
    
    def test_strands_import(self):
        """Test that Strands SDK imports correctly"""
        try:
            from strands import Agent, tool
            from strands.telemetry import get_tracer
        except ImportError as e:
            pytest.fail(f"Strands import failed: {e}")
    
    def test_service_imports(self):
        """Test that service packages import correctly"""
        try:
            from simple_salesforce import Salesforce
            from jira import JIRA
            from anthropic import Anthropic
        except ImportError as e:
            pytest.fail(f"Service package import failed: {e}")
    
    def test_web_framework_imports(self):
        """Test that web framework packages import correctly"""
        try:
            from fastapi import FastAPI
            import uvicorn
            from pydantic import BaseModel
        except ImportError as e:
            pytest.fail(f"Web framework import failed: {e}")
    
    def test_async_imports(self):
        """Test that async packages import correctly"""
        try:
            import asyncio
            import aiohttp
        except ImportError as e:
            pytest.fail(f"Async package import failed: {e}")


class TestOptionalImports:
    """Test optional package imports"""
    
    def test_dotenv_import(self):
        """Test python-dotenv import"""
        try:
            from dotenv import load_dotenv
        except ImportError as e:
            pytest.fail(f"python-dotenv import failed: {e}")
    
    def test_requests_import(self):
        """Test requests import"""
        try:
            import requests
        except ImportError as e:
            pytest.fail(f"requests import failed: {e}")


if __name__ == "__main__":
    # Run tests manually if pytest not available
    import unittest
    
    class TestPythonVersionManual(unittest.TestCase):
        def test_version(self):
            test = TestPythonVersion()
            test.test_python_version_minimum()
            test.test_python_version_recommended()
    
    class TestCoreImportsManual(unittest.TestCase):
        def test_all_imports(self):
            test = TestCoreImports()
            test.test_mcp_import()
            test.test_strands_import()
            test.test_service_imports()
            test.test_web_framework_imports()
            test.test_async_imports()
    
    class TestOptionalImportsManual(unittest.TestCase):
        def test_optional(self):
            test = TestOptionalImports()
            test.test_dotenv_import()
            test.test_requests_import()
    
    unittest.main()