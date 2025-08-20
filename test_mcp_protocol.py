#!/usr/bin/env python3
"""Test script for MCP protocol communication."""

import json
import subprocess
import sys
import time
from typing import Dict, Any


def send_mcp_request(process: subprocess.Popen, request: Dict[str, Any]) -> Dict[str, Any]:
    """Send a JSON-RPC request and get response."""
    request_json = json.dumps(request) + "\n"
    process.stdin.write(request_json.encode())
    process.stdin.flush()
    
    # Read response
    response_line = process.stdout.readline().decode().strip()
    if not response_line:
        raise RuntimeError("No response received")
    
    return json.loads(response_line)


def test_mcp_server():
    """Test the MCP server with basic protocol commands."""
    print("Testing ESTIEM EDA MCP Server...")
    
    # Start the server process
    try:
        process = subprocess.Popen(
            [sys.executable, "-m", "estiem_eda.mcp_server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd="src"
        )
        
        # Test 1: Initialize
        print("\n1. Testing initialization...")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "1.0",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        response = send_mcp_request(process, init_request)
        print(f"Initialize response: {json.dumps(response, indent=2)}")
        
        if "result" in response:
            print("✅ Initialize successful")
        else:
            print("❌ Initialize failed")
            return False
        
        # Test 2: List tools
        print("\n2. Testing tools list...")
        list_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        response = send_mcp_request(process, list_request)
        print(f"Tools list response: {json.dumps(response, indent=2)}")
        
        if "result" in response and "tools" in response["result"]:
            tools = response["result"]["tools"]
            print(f"✅ Found {len(tools)} tools")
            for tool in tools:
                print(f"  - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
        else:
            print("❌ Tools list failed")
            return False
        
        # Test 3: Invalid method
        print("\n3. Testing invalid method...")
        invalid_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "invalid/method",
            "params": {}
        }
        
        response = send_mcp_request(process, invalid_request)
        print(f"Invalid method response: {json.dumps(response, indent=2)}")
        
        if "error" in response:
            print("✅ Error handling works correctly")
        else:
            print("❌ Error handling failed")
        
        print("\n🎉 MCP Server core functionality test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    
    finally:
        # Clean up
        if 'process' in locals():
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()


if __name__ == "__main__":
    success = test_mcp_server()
    sys.exit(0 if success else 1)