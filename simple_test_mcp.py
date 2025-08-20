#!/usr/bin/env python3
"""Simple test for Enhanced MCP Server functionality."""

import sys
import json

# Add the src directory to the path
sys.path.insert(0, 'src')

from estiem_eda.mcp_server import ESTIEMMCPServer

def test_i_chart():
    """Test I-Chart tool with enhanced response."""
    print("Testing I-Chart tool...")
    
    server = ESTIEMMCPServer()
    
    # Test data
    test_data = [10.0, 11.0, 11.3, 9.0, 8.0, 9.0, 9.5, 10.1, 11.4]
    
    request_params = {
        "name": "i_chart",
        "arguments": {
            "data": test_data,
            "title": "Test I-Chart"
        }
    }
    
    response = server.handle_call_tool(request_params)
    
    if "error" in response:
        print(f"ERROR: {response['error']}")
        return False
    
    # Parse response
    content = response.get("content", [{}])
    if content and "text" in content[0]:
        result_data = json.loads(content[0]["text"])
        
        if "visualization_formats" in result_data:
            formats = result_data["visualization_formats"]
            print(f"SUCCESS: Generated {len(formats)} formats")
            print(f"Available formats: {list(formats.keys())}")
            
            # Check specific formats
            if "html_plotly" in formats:
                html_content = formats["html_plotly"].get("content", "")
                if len(html_content) > 1000:
                    print("HTML format: OK")
                else:
                    print("HTML format: Too small")
            
            if "artifact_data" in formats:
                print("Artifact format: Available")
            
            if "chart_config" in formats:
                config = formats["chart_config"]
                if "data" in config and "layout" in config:
                    print("Chart config: Valid")
                else:
                    print("Chart config: Invalid")
            
            if "fallback_text" in formats:
                text = formats["fallback_text"]
                if len(text) > 50:
                    print("Text fallback: OK")
                else:
                    print("Text fallback: Too short")
            
            return True
        else:
            print("ERROR: No visualization_formats in response")
            return False
    else:
        print("ERROR: Invalid response format")
        return False

def test_server_info():
    """Test server initialization and info."""
    print("Testing server initialization...")
    
    server = ESTIEMMCPServer()
    
    print(f"Server name: {server.server_info['name']}")
    print(f"Server version: {server.server_info['version']}")
    print(f"Server description: {server.server_info['description']}")
    print(f"Tools loaded: {len(server.tools)}")
    
    return server.server_info['version'] == '2.0.0'

if __name__ == "__main__":
    print("ENHANCED MCP SERVER SIMPLE TEST")
    print("=" * 40)
    
    try:
        # Test server info
        server_ok = test_server_info()
        print(f"Server test: {'PASS' if server_ok else 'FAIL'}")
        
        print()
        
        # Test I-Chart functionality
        i_chart_ok = test_i_chart()
        print(f"I-Chart test: {'PASS' if i_chart_ok else 'FAIL'}")
        
        print()
        print("=" * 40)
        
        if server_ok and i_chart_ok:
            print("ALL TESTS PASSED")
            exit(0)
        else:
            print("SOME TESTS FAILED")
            exit(1)
            
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        exit(2)