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
        assert len(server.tools) == 5
        print("   PASS: 5 tools loaded")
        passed += 1
    except Exception as e:
        print(f"   FAIL: {e}")
        failed += 1
    
    # Test 2: I-Chart basic functionality
    print("\n2. I-Chart Tool...")
    try:
        from estiem_eda.tools.i_chart import IChartTool
        tool = IChartTool()
        data = [10.0, 10.5, 9.5, 10.2, 9.8, 10.1, 9.9, 10.3]
        result = tool.execute({"data": data})
        assert result["success"] is True
        assert "statistics" in result
        assert "out_of_control_indices" in result
        assert "interpretation" in result
        print("   PASS: I-Chart working")
        passed += 1
    except Exception as e:
        print(f"   FAIL: {e}")
        failed += 1
    
    # Test 3: Capability Tool
    print("\n3. Capability Tool...")
    try:
        from estiem_eda.tools.capability import CapabilityTool
        tool = CapabilityTool()
        # Use simple test data instead of numpy random
        data = [9.8, 10.1, 9.9, 10.2, 10.0, 9.7, 10.3, 9.9, 10.1, 10.0] * 10  # 100 points
        result = tool.execute({"data": data, "lsl": 9.0, "usl": 11.0, "target": 10.0})
        assert result["success"] is True
        assert "capability_indices" in result
        assert "statistics" in result
        print("   PASS: Capability working")
        passed += 1
    except Exception as e:
        print(f"   FAIL: {e}")
        failed += 1
    
    # Test 4: ANOVA Tool
    print("\n4. ANOVA Tool...")
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
    
    # Test 5: Pareto Tool  
    print("\n5. Pareto Tool...")
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
    
    # Test 6: MCP Protocol
    print("\n6. MCP Protocol...")
    try:
        server = ESTIEMMCPServer()
        
        # Test initialize
        init_resp = server.handle_initialize({})
        assert "protocolVersion" in init_resp
        
        # Test list tools
        list_resp = server.handle_list_tools({})
        assert len(list_resp["tools"]) == 5
        
        # Test tool execution
        call_resp = server.handle_call_tool({
            "name": "i_chart", 
            "arguments": {"data": [10, 11, 9]}
        })
        assert "content" in call_resp
        print("   PASS: MCP protocol working")
        passed += 1
    except Exception as e:
        print(f"   FAIL: {e}")
        failed += 1
    
    # Test 7: Probability Plot functionality
    print("\n7. Probability Plot Analysis...")
    try:
        from estiem_eda.tools.probability_plot import ProbabilityPlotTool
        
        tool = ProbabilityPlotTool()
        # Use deterministic test data instead of numpy random
        test_data = [8.1, 8.5, 9.2, 9.8, 10.1, 10.3, 10.7, 11.1, 11.5, 12.0,
                    8.3, 8.9, 9.5, 10.0, 10.4, 10.8, 11.2, 11.6, 12.2, 8.7,
                    9.1, 9.6, 10.2, 10.5, 10.9, 11.3, 11.7, 12.1, 8.2, 8.8]
        
        result = tool.execute({
            "data": test_data,
            "distribution": "normal",
            "confidence_level": 0.95
        })
        
        assert result["success"] is True
        assert "goodness_of_fit" in result
        assert "sorted_values" in result
        assert "theoretical_quantiles" in result
        
        print(f"   PASS: Probability plot working")
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