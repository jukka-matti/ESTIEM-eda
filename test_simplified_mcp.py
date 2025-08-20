#!/usr/bin/env python3
"""Test script for simplified MCP server implementation."""

import json
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from estiem_eda.mcp_server import ESTIEMMCPServer


def test_simplified_i_chart():
    """Test the simplified I-Chart implementation."""
    print("Testing Simplified I-Chart Implementation...")
    
    # Create MCP server instance
    server = ESTIEMMCPServer()
    
    # Test data from the original example
    test_data = [10, 11, 13, 15, 12, 14, 15, 12, 12, 11, 11, 9]
    
    # Create MCP request
    request = {
        "method": "tools/call",
        "params": {
            "name": "i_chart",
            "arguments": {
                "data": test_data,
                "title": "Test I-Chart Analysis"
            }
        }
    }
    
    # Execute request
    try:
        response = server.handle_request(request)
        
        if "error" in response:
            print(f"❌ ERROR: {response['error']}")
            return False
        
        # Parse the response content
        content = response.get("content", [])
        if not content:
            print("❌ ERROR: No content in response")
            return False
        
        # Get the JSON response
        result_json = content[0].get("text", "")
        if not result_json:
            print("❌ ERROR: No text content in response")
            return False
        
        # Parse the result
        result = json.loads(result_json)
        
        # Verify key components
        print(f"OK Analysis Type: {result.get('analysis_type')}")
        print(f"OK Success: {result.get('success')}")
        
        # Check statistics
        stats = result.get("statistics", {})
        print(f"OK Mean: {stats.get('mean')}")
        print(f"OK UCL: {stats.get('ucl')}")
        print(f"OK LCL: {stats.get('lcl')}")
        
        # Check visualization
        html_viz = result.get("html_visualization")
        text_summary = result.get("text_summary")
        
        if html_viz:
            print(f"OK HTML Visualization: {len(html_viz)} characters")
        else:
            print("ERROR No HTML visualization generated")
        
        if text_summary:
            print(f"OK Text Summary: {len(text_summary)} characters")
        else:
            print("ERROR No text summary generated")
        
        # Check metadata
        metadata = result.get("visualization_metadata", {})
        print(f"OK Format: {metadata.get('format')}")
        print(f"OK Size: {metadata.get('size_kb')} KB")
        print(f"OK Generation Time: {metadata.get('generation_time_ms')} ms")
        
        print("\nSimplified I-Chart test PASSED!")
        return True
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_tool_listing():
    """Test that tools are properly listed."""
    print("\nTesting Tool Listing...")
    
    server = ESTIEMMCPServer()
    
    request = {
        "method": "tools/list",
        "params": {}
    }
    
    try:
        response = server.handle_request(request)
        tools = response.get("tools", [])
        
        print(f"OK Found {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool.get('name')}: {tool.get('description')}")
        
        return len(tools) > 0
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("Testing Simplified MCP Server Implementation")
    print("=" * 50)
    
    tests = [
        test_tool_listing,
        test_simplified_i_chart
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"Test failed with exception: {e}")
    
    print(f"\nResults: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("ALL TESTS PASSED! The simplified implementation works correctly.")
    else:
        print("Some tests failed. Check the implementation.")
    
    return passed == len(tests)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)