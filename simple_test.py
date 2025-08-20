#!/usr/bin/env python3
"""Simple test runner for ESTIEM EDA toolkit."""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    print("ESTIEM EDA Toolkit - Test Suite")
    print("=" * 40)
    
    passed = 0
    failed = 0
    
    # Test 1: MCP Server loads correctly
    print("\n1. MCP Server Initialization...")
    try:
        from estiem_eda.mcp_server import ESTIEMMCPServer
        server = ESTIEMMCPServer()
        assert len(server.tools) == 3
        print("   PASS: 3 core tools loaded")
        passed += 1
    except Exception as e:
        print(f"   FAIL: {e}")
        failed += 1
    
    # Test 2: Process Analysis Tool
    print("\n2. Process Analysis Tool...")
    try:
        from estiem_eda.tools.process_analysis import ProcessAnalysisTool
        
        tool = ProcessAnalysisTool()
        test_data = [9.8, 10.1, 9.9, 10.2, 10.0, 9.7, 10.3, 9.9, 10.1, 10.0] * 5
        
        result = tool.execute({
            "data": test_data,
            "specification_limits": {"lsl": 9.5, "usl": 10.5, "target": 10.0},
            "title": "Test Process Analysis"
        })
        
        assert result["success"] is True
        assert "process_summary" in result
        assert "stability_analysis" in result
        assert "capability_analysis" in result
        assert "distribution_analysis" in result
        assert "overall_assessment" in result
        assert "interpretation" in result
        
        print(f"   PASS: Process Analysis working")
        passed += 1
    except Exception as e:
        print(f"   FAIL: {e}")
        failed += 1
    
    # Test 3: ANOVA Tool
    print("\n3. ANOVA Tool...")
    try:
        from estiem_eda.tools.anova import ANOVATool
        tool = ANOVATool()
        groups = {
            "A": [10, 11, 9, 12, 8],
            "B": [13, 14, 12, 15, 11],
            "C": [16, 17, 15, 18, 14]
        }
        result = tool.execute({"groups": groups, "alpha": 0.05})
        assert result["success"] is True
        assert "anova_results" in result
        assert "group_statistics" in result
        print("   PASS: ANOVA working")
        passed += 1
    except Exception as e:
        print(f"   FAIL: {e}")
        failed += 1
    
    # Test 4: Pareto Tool  
    print("\n4. Pareto Tool...")
    try:
        from estiem_eda.tools.pareto import ParetoTool
        tool = ParetoTool()
        data = {"Issue A": 100, "Issue B": 50, "Issue C": 25, "Issue D": 10, "Issue E": 5}
        result = tool.execute({"data": data, "threshold": 0.8})
        assert result["success"] is True
        assert "vital_few" in result
        assert "categories" in result
        print("   PASS: Pareto working")
        passed += 1
    except Exception as e:
        print(f"   FAIL: {e}")
        failed += 1
    
    # Test 5: MCP Protocol
    print("\n5. MCP Protocol...")
    try:
        server = ESTIEMMCPServer()
        
        # Test initialize
        init_resp = server.handle_initialize({})
        assert "protocolVersion" in init_resp
        
        # Test list tools
        list_resp = server.handle_list_tools({})
        assert len(list_resp["tools"]) == 3
        
        # Test tool execution
        call_resp = server.handle_call_tool({
            "name": "process_analysis", 
            "arguments": {"data": [10, 11, 9, 10.5, 9.5, 10.2, 9.8]}
        })
        assert "content" in call_resp
        print("   PASS: MCP protocol working")
        passed += 1
    except Exception as e:
        print(f"   FAIL: {e}")
        failed += 1
    
    
    # Results
    print("\n" + "=" * 40)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("SUCCESS: All tests passed!")
        return True
    else:
        print("FAILURE: Some tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)