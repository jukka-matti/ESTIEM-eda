"""Integration tests for ESTIEM EDA MCP Server."""

import pytest
import json
from estiem_eda.mcp_server import ESTIEMMCPServer


class TestMCPServer:
    """Test suite for MCP Server integration."""
    
    def test_server_initialization(self):
        """Test server initializes correctly."""
        server = ESTIEMMCPServer()
        
        assert server.protocol_version == "1.0"
        assert server.server_info["name"] == "estiem-eda"
        assert len(server.tools) == 4
        
        # Check all expected tools are loaded
        expected_tools = ["i_chart", "process_capability", "anova_boxplot", "pareto_analysis"]
        for tool_name in expected_tools:
            assert tool_name in server.tools
    
    def test_initialize_request(self):
        """Test MCP initialize request handling."""
        server = ESTIEMMCPServer()
        
        response = server.handle_initialize({
            "protocolVersion": "1.0",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0.0"}
        })
        
        assert "protocolVersion" in response
        assert response["protocolVersion"] == "1.0"
        assert "capabilities" in response
        assert "serverInfo" in response
        
        # Check capabilities
        capabilities = response["capabilities"]
        assert "tools" in capabilities
        assert capabilities["tools"]["listChanged"] == True
    
    def test_list_tools_request(self):
        """Test tools list request handling."""
        server = ESTIEMMCPServer()
        
        response = server.handle_list_tools({})
        
        assert "tools" in response
        tools_list = response["tools"]
        
        # Should have 4 tools
        assert len(tools_list) == 4
        
        # Each tool should have required fields
        for tool in tools_list:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool
            
            # Schema should be valid JSON schema
            schema = tool["inputSchema"]
            assert "type" in schema
            assert "properties" in schema
            assert "required" in schema
    
    def test_tool_execution_i_chart(self, sample_stable_process):
        """Test I-chart tool execution through MCP."""
        server = ESTIEMMCPServer()
        
        response = server.handle_call_tool({
            "name": "i_chart",
            "arguments": {"data": sample_stable_process}
        })
        
        assert "content" in response
        assert len(response["content"]) == 1
        
        content = response["content"][0]
        assert content["type"] == "text"
        
        # Parse the JSON response
        result = json.loads(content["text"])
        
        # Verify structure matches tool output
        assert "statistics" in result
        assert "control_analysis" in result
        assert "interpretation" in result
        assert "chart_html" in result
    
    def test_tool_execution_capability(self, sample_capability_data):
        """Test capability tool execution through MCP."""
        server = ESTIEMMCPServer()
        
        response = server.handle_call_tool({
            "name": "process_capability",
            "arguments": {
                "data": sample_capability_data,
                "lsl": 9.0,
                "usl": 11.0,
                "target": 10.0
            }
        })
        
        assert "content" in response
        result = json.loads(response["content"][0]["text"])
        
        # Verify capability-specific structure
        assert "capability_indices" in result
        assert "defect_analysis" in result
        assert "process_assessment" in result
        assert "chart_html" in result
    
    def test_tool_execution_anova(self, sample_anova_groups):
        """Test ANOVA tool execution through MCP."""
        server = ESTIEMMCPServer()
        
        response = server.handle_call_tool({
            "name": "anova_boxplot",
            "arguments": {"groups": sample_anova_groups}
        })
        
        assert "content" in response
        result = json.loads(response["content"][0]["text"])
        
        # Verify ANOVA-specific structure
        assert "anova_results" in result
        assert "descriptive_statistics" in result
        assert "assumption_tests" in result
        assert "chart_html" in result
    
    def test_tool_execution_pareto(self, sample_pareto_data):
        """Test Pareto tool execution through MCP."""
        server = ESTIEMMCPServer()
        
        response = server.handle_call_tool({
            "name": "pareto_analysis",
            "arguments": {"data": sample_pareto_data}
        })
        
        assert "content" in response
        result = json.loads(response["content"][0]["text"])
        
        # Verify Pareto-specific structure
        assert "vital_few" in result
        assert "sorted_data" in result
        assert "insights" in result
        assert "chart_html" in result
    
    def test_invalid_tool_name(self):
        """Test handling of invalid tool names."""
        server = ESTIEMMCPServer()
        
        response = server.handle_call_tool({
            "name": "nonexistent_tool",
            "arguments": {}
        })
        
        assert "error" in response
        error = response["error"]
        assert error["code"] == -32602
        assert "Unknown tool" in error["message"]
    
    def test_tool_validation_errors(self):
        """Test handling of tool validation errors."""
        server = ESTIEMMCPServer()
        
        # Missing required parameters
        response = server.handle_call_tool({
            "name": "i_chart",
            "arguments": {}  # Missing required 'data'
        })
        
        assert "error" in response
        error = response["error"]
        assert error["code"] == -32602
        assert "Invalid parameters" in error["message"]
    
    def test_tool_execution_errors(self):
        """Test handling of tool execution errors."""
        server = ESTIEMMCPServer()
        
        # Invalid data that will cause execution error
        response = server.handle_call_tool({
            "name": "i_chart",
            "arguments": {"data": []}  # Empty data should cause error
        })
        
        assert "error" in response
        error = response["error"]
        assert error["code"] == -32602  # Validation error
    
    def test_unknown_method_handling(self):
        """Test handling of unknown MCP methods."""
        server = ESTIEMMCPServer()
        
        response = server.handle_request({
            "method": "unknown/method",
            "params": {}
        })
        
        assert "error" in response
        error = response["error"]
        assert error["code"] == -32601
        assert "Method not found" in error["message"]
    
    def test_json_response_format(self, sample_stable_process):
        """Test that all responses are valid JSON."""
        server = ESTIEMMCPServer()
        
        # Test each tool's JSON output
        tools_and_args = [
            ("i_chart", {"data": sample_stable_process}),
            ("process_capability", {"data": sample_stable_process, "lsl": 9.0, "usl": 11.0}),
            ("anova_boxplot", {"groups": {"A": [10, 11, 12], "B": [13, 14, 15]}}),
            ("pareto_analysis", {"data": {"Issue A": 100, "Issue B": 50}})
        ]
        
        for tool_name, arguments in tools_and_args:
            response = server.handle_call_tool({
                "name": tool_name,
                "arguments": arguments
            })
            
            assert "content" in response
            content_text = response["content"][0]["text"]
            
            # Should be valid JSON
            try:
                parsed_result = json.loads(content_text)
                assert isinstance(parsed_result, dict)
            except json.JSONDecodeError:
                pytest.fail(f"Tool {tool_name} returned invalid JSON")
    
    def test_error_response_format(self):
        """Test error responses follow proper format."""
        server = ESTIEMMCPServer()
        
        # Generate error response
        error_response = server.error_response(-32602, "Test error message")
        
        assert "error" in error_response
        error = error_response["error"]
        assert "code" in error
        assert "message" in error
        assert error["code"] == -32602
        assert error["message"] == "Test error message"
    
    def test_concurrent_tool_execution(self, sample_stable_process, sample_pareto_data):
        """Test that server can handle multiple tool executions."""
        server = ESTIEMMCPServer()
        
        # Execute multiple tools in sequence (simulating concurrent requests)
        responses = []
        
        test_calls = [
            ("i_chart", {"data": sample_stable_process}),
            ("pareto_analysis", {"data": sample_pareto_data}),
            ("i_chart", {"data": sample_stable_process[:10]}),  # Different data
        ]
        
        for tool_name, arguments in test_calls:
            response = server.handle_call_tool({
                "name": tool_name,
                "arguments": arguments
            })
            responses.append(response)
        
        # All should succeed
        for i, response in enumerate(responses):
            assert "content" in response, f"Request {i} failed: {response}"
            
            # Verify response content
            result = json.loads(response["content"][0]["text"])
            if test_calls[i][0] == "i_chart":
                assert "statistics" in result
            else:
                assert "vital_few" in result
    
    def test_large_data_handling(self):
        """Test server handles large datasets appropriately."""
        server = ESTIEMMCPServer()
        
        # Generate large dataset
        large_data = list(range(1000))
        
        response = server.handle_call_tool({
            "name": "i_chart",
            "arguments": {"data": large_data}
        })
        
        # Should handle without errors
        assert "content" in response
        result = json.loads(response["content"][0]["text"])
        assert result["statistics"]["sample_size"] == 1000
    
    def test_schema_validation(self):
        """Test that tool schemas are properly defined and valid."""
        server = ESTIEMMCPServer()
        
        tools_list = server.handle_list_tools({})["tools"]
        
        for tool in tools_list:
            schema = tool["inputSchema"]
            
            # Basic schema validation
            assert "type" in schema
            assert schema["type"] == "object"
            assert "properties" in schema
            assert "required" in schema
            
            # Properties should be properly defined
            properties = schema["properties"]
            assert isinstance(properties, dict)
            assert len(properties) > 0
            
            # Required fields should exist in properties
            for req_field in schema["required"]:
                assert req_field in properties
    
    def test_tool_descriptions(self):
        """Test that tools have meaningful descriptions."""
        server = ESTIEMMCPServer()
        
        tools_list = server.handle_list_tools({})["tools"]
        
        expected_descriptions = {
            "i_chart": ["individual", "control", "chart"],
            "process_capability": ["capability", "cp", "cpk"],
            "anova_boxplot": ["anova", "analysis", "variance"],
            "pareto_analysis": ["pareto", "80/20", "vital"]
        }
        
        for tool in tools_list:
            tool_name = tool["name"]
            description = tool["description"].lower()
            
            if tool_name in expected_descriptions:
                keywords = expected_descriptions[tool_name]
                # At least one keyword should be in description
                assert any(keyword in description for keyword in keywords), \
                    f"Tool {tool_name} description missing expected keywords: {keywords}"
    
    def test_visualization_integration(self, sample_stable_process):
        """Test that all tools include visualization output."""
        server = ESTIEMMCPServer()
        
        test_cases = [
            ("i_chart", {"data": sample_stable_process}),
            ("process_capability", {"data": sample_stable_process, "lsl": 9.0, "usl": 11.0}),
            ("anova_boxplot", {"groups": {"A": [10, 11, 9], "B": [12, 13, 14]}}),
            ("pareto_analysis", {"data": {"Issue A": 100, "Issue B": 50}})
        ]
        
        for tool_name, arguments in test_cases:
            response = server.handle_call_tool({
                "name": tool_name,
                "arguments": arguments
            })
            
            result = json.loads(response["content"][0]["text"])
            
            # Should have chart_html field
            assert "chart_html" in result, f"Tool {tool_name} missing chart_html"
            assert isinstance(result["chart_html"], str)
            
            # Should be either HTML content or error message
            chart_html = result["chart_html"]
            assert len(chart_html) > 0