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
        assert "statistics" in result
        assert "chart_html" in result
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
        import numpy as np
        np.random.seed(42)
        data = np.random.normal(10.0, 0.2, 100).tolist()
        result = tool.execute({"data": data, "lsl": 9.0, "usl": 11.0})
        assert "capability_indices" in result
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
        result = tool.execute({"groups": groups})
        assert "anova_results" in result
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
        data = {"Issue A": 100, "Issue B": 50, "Issue C": 25}
        result = tool.execute({"data": data})
        assert "vital_few" in result
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
    
    # Test 5: Probability Plot functionality
    print("\n5. Probability Plot Analysis...")
    try:
        from estiem_eda.tools.probability_plot import ProbabilityPlotTool
        import numpy as np
        
        tool = ProbabilityPlotTool()
        np.random.seed(42)
        test_data = list(np.random.normal(10, 2, 30))
        
        result = tool.execute({
            "data": test_data,
            "distribution": "normal",
            "confidence_level": 0.95
        })
        
        assert result["success"] is True
        assert "goodness_of_fit" in result
        assert "confidence_intervals" in result
        assert "outliers" in result
        assert "percentile_estimates" in result
        
        print(f"   PASS: Probability plot (r={result['goodness_of_fit']['correlation_coefficient']:.3f})")
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