"""Simple test for MCP protocol handling."""

import sys
sys.path.append('src')

from estiem_eda.mcp_server import ESTIEMMCPServer

def test_protocol():
    """Test MCP protocol methods."""
    server = ESTIEMMCPServer()
    
    # Test initialize
    print("Testing initialize...")
    init_response = server.handle_initialize({})
    assert "protocolVersion" in init_response
    assert "serverInfo" in init_response
    print("OK Initialize works")
    
    # Test list tools  
    print("Testing tools list...")
    list_response = server.handle_list_tools({})
    assert "tools" in list_response
    print(f"OK Tools list works - found {len(list_response['tools'])} tools")
    
    # Test invalid tool call
    print("Testing invalid tool call...")
    call_response = server.handle_call_tool({"name": "nonexistent", "arguments": {}})
    assert "error" in call_response
    print("OK Error handling works")
    
    print("\nPhase 1 Complete: MCP Server Core Implementation")
    return True

if __name__ == "__main__":
    test_protocol()