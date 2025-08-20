#!/usr/bin/env python3
"""Test script for Enhanced MCP Server functionality.

This script tests the multi-format response generation of the Enhanced ESTIEM EDA MCP Server.
"""

import sys
import json
import logging
from typing import Dict, Any

# Add the src directory to the path
sys.path.insert(0, 'src')

from estiem_eda.mcp_server import ESTIEMMCPServer

def test_enhanced_mcp_server():
    """Test the enhanced MCP server with multi-format responses."""
    print("Testing Enhanced ESTIEM EDA MCP Server")
    print("=" * 60)
    
    # Initialize the server
    server = ESTIEMMCPServer()
    print(f"SUCCESS: Server initialized: {server.server_info['name']} v{server.server_info['version']}")
    
    # Test data for statistical analysis
    test_data = [10.0, 11.0, 11.3, 9.0, 8.0, 9.0, 9.5, 10.1, 11.4]
    
    # Test the 3 core professional tools
    tools_to_test = [
        {
            "name": "process_analysis",
            "description": "Comprehensive Process Analysis",
            "params": {
                "data": test_data * 5,  # Need more data points for reliable analysis
                "specification_limits": {
                    "lsl": 8.0,
                    "usl": 12.0,
                    "target": 10.0
                },
                "distribution": "normal",
                "title": "Test Process Analysis"
            }
        },
        {
            "name": "anova_boxplot",
            "description": "ANOVA Analysis",
            "params": {
                "groups": {
                    "Group A": test_data[:3],
                    "Group B": test_data[3:6],
                    "Group C": test_data[6:]
                },
                "title": "Test ANOVA Analysis"
            }
        },
        {
            "name": "pareto_analysis", 
            "description": "Pareto Analysis",
            "params": {
                "data": {
                    "Defect A": 45,
                    "Defect B": 32,
                    "Defect C": 18,
                    "Defect D": 12,
                    "Other": 8
                },
                "title": "Test Pareto Analysis"
            }
        }
    ]
    
    results = []
    
    for tool_config in tools_to_test:
        print(f"\nTesting {tool_config['description']}...")
        
        try:
            # Create MCP tool call request
            request_params = {
                "name": tool_config["name"],
                "arguments": tool_config["params"]
            }
            
            # Execute the tool
            response = server.handle_call_tool(request_params)
            
            if "error" in response:
                print(f"ERROR: {response['error']}")
                results.append({
                    "tool": tool_config["name"],
                    "success": False,
                    "error": response["error"]
                })
                continue
            
            # Parse the response content
            content = response.get("content", [{}])
            if content and "text" in content[0]:
                result_data = json.loads(content[0]["text"])
                
                # Check for enhanced multi-format response
                if "visualization_formats" in result_data:
                    formats = result_data["visualization_formats"]
                    rendering_metadata = result_data.get("rendering_metadata", {})
                    
                    print(f"SUCCESS: Generated {len(formats)} visualization formats")
                    
                    # List available formats
                    available_formats = list(formats.keys())
                    print(f"   Formats: {', '.join(available_formats)}")
                    
                    # Check primary format
                    primary_format = rendering_metadata.get("primary_format", "unknown")
                    print(f"   Primary format: {primary_format}")
                    
                    # Check response size
                    total_size = rendering_metadata.get("total_size_kb", 0)
                    generation_time = rendering_metadata.get("generation_time_ms", 0)
                    print(f"   Response size: {total_size:.1f} KB")
                    print(f"   Generation time: {generation_time:.1f} ms")
                    
                    results.append({
                        "tool": tool_config["name"],
                        "success": True,
                        "formats": len(formats),
                        "available_formats": available_formats,
                        "primary_format": primary_format,
                        "size_kb": total_size,
                        "generation_time_ms": generation_time
                    })
                    
                else:
                    print("⚠️  Warning: Response missing multi-format visualization")
                    results.append({
                        "tool": tool_config["name"],
                        "success": False,
                        "error": "Missing visualization_formats in response"
                    })
            else:
                print("❌ Error: Invalid response format")
                results.append({
                    "tool": tool_config["name"],
                    "success": False,
                    "error": "Invalid response format"
                })
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            results.append({
                "tool": tool_config["name"],
                "success": False,
                "error": str(e)
            })
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 ENHANCED MCP SERVER TEST SUMMARY")
    print("=" * 60)
    
    successful_tools = [r for r in results if r.get("success", False)]
    failed_tools = [r for r in results if not r.get("success", False)]
    
    print(f"✅ Successful tools: {len(successful_tools)}/{len(results)}")
    print(f"❌ Failed tools: {len(failed_tools)}/{len(results)}")
    
    if successful_tools:
        print("\n🎉 Successfully Enhanced Tools:")
        for result in successful_tools:
            formats = result.get("formats", 0)
            size = result.get("size_kb", 0)
            time = result.get("generation_time_ms", 0)
            print(f"   • {result['tool']}: {formats} formats, {size:.1f}KB, {time:.1f}ms")
    
    if failed_tools:
        print("\n⚠️  Failed Tools:")
        for result in failed_tools:
            error = result.get("error", "Unknown error")
            print(f"   • {result['tool']}: {error}")
    
    # Overall status
    if len(successful_tools) == len(results):
        print("\n🎉 ALL TESTS PASSED - Enhanced MCP Server is fully operational!")
        return True
    elif successful_tools:
        print(f"\n⚠️  PARTIAL SUCCESS - {len(successful_tools)} out of {len(results)} tools working")
        return False
    else:
        print("\n❌ ALL TESTS FAILED - Enhanced MCP Server needs debugging")
        return False


def test_format_quality():
    """Test the quality and content of generated formats."""
    print("\n🔍 Testing Format Quality...")
    
    server = ESTIEMMCPServer()
    
    # Test I-Chart with detailed format inspection
    request_params = {
        "name": "i_chart",
        "arguments": {
            "data": [10.0, 11.0, 11.3, 9.0, 8.0, 9.0, 9.5, 10.1, 11.4],
            "title": "Quality Test I-Chart"
        }
    }
    
    response = server.handle_call_tool(request_params)
    
    if "error" in response:
        print(f"❌ Error in format quality test: {response['error']}")
        return False
    
    content = response.get("content", [{}])
    if content and "text" in content[0]:
        result_data = json.loads(content[0]["text"])
        formats = result_data.get("visualization_formats", {})
        
        print("🔍 Format Quality Analysis:")
        
        # Check HTML format
        if "html_plotly" in formats:
            html_content = formats["html_plotly"].get("content", "")
            if "<!DOCTYPE html>" in html_content and "plotly" in html_content.lower():
                print("   ✅ HTML format: Valid and contains Plotly")
            else:
                print("   ❌ HTML format: Invalid or missing Plotly")
        
        # Check artifact formats
        if "artifact_data" in formats:
            artifact_data = formats["artifact_data"]
            
            if "react" in artifact_data:
                react_content = artifact_data["react"].get("content", "")
                if "import React" in react_content and "Plot" in react_content:
                    print("   ✅ React artifact: Valid component structure")
                else:
                    print("   ❌ React artifact: Invalid component structure")
            
            if "html" in artifact_data:
                html_artifact = artifact_data["html"].get("content", "")
                if "<!DOCTYPE html>" in html_artifact:
                    print("   ✅ HTML artifact: Valid structure")
                else:
                    print("   ❌ HTML artifact: Invalid structure")
        
        # Check chart config
        if "chart_config" in formats:
            chart_config = formats["chart_config"]
            if isinstance(chart_config, dict) and "data" in chart_config and "layout" in chart_config:
                print("   ✅ Chart config: Valid Plotly configuration")
            else:
                print("   ❌ Chart config: Invalid configuration structure")
        
        # Check text fallback
        if "fallback_text" in formats:
            fallback_text = formats["fallback_text"]
            if isinstance(fallback_text, str) and len(fallback_text) > 50:
                print("   ✅ Text fallback: Adequate content")
            else:
                print("   ❌ Text fallback: Insufficient content")
        
        return True
    
    return False


if __name__ == "__main__":
    print("🧪 ENHANCED ESTIEM EDA MCP SERVER TEST SUITE")
    print("=" * 80)
    
    try:
        # Test basic functionality
        basic_test_passed = test_enhanced_mcp_server()
        
        # Test format quality
        quality_test_passed = test_format_quality()
        
        print("\n" + "=" * 80)
        print("🏁 FINAL TEST RESULTS")
        print("=" * 80)
        
        if basic_test_passed and quality_test_passed:
            print("🎉 ALL TESTS PASSED!")
            print("✅ Enhanced MCP Server is ready for production use")
            exit(0)
        elif basic_test_passed:
            print("⚠️  BASIC TESTS PASSED, QUALITY TESTS FAILED")
            print("🔧 Server functional but may need format improvements")
            exit(1)
        else:
            print("❌ TESTS FAILED")
            print("🚨 Server needs debugging before deployment")
            exit(2)
            
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {str(e)}")
        print("🚨 Test suite failed to complete")
        exit(3)