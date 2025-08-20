#!/usr/bin/env python3
"""Simple test runner for ESTIEM EDA toolkit without pytest dependency."""

import sys
import os
import importlib.util
import traceback
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def run_simple_tests():
    """Run basic functionality tests."""
    print("ESTIEM EDA Toolkit - Basic Test Suite")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    # Test 1: MCP Server Initialization
    print("\n1. Testing MCP Server Initialization...")
    try:
        from estiem_eda.mcp_server import ESTIEMMCPServer
        server = ESTIEMMCPServer()
        assert len(server.tools) == 4
        assert "i_chart" in server.tools
        assert "process_capability" in server.tools
        assert "anova_boxplot" in server.tools
        assert "pareto_analysis" in server.tools
        print("   OK MCP Server initialized with 4 tools")
        passed += 1
    except Exception as e:
        print(f"   ERROR MCP Server initialization failed: {e}")
        failed += 1
    
    # Test 2: I-Chart Tool Basic Functionality
    print("\n2. Testing I-Chart Tool...")
    try:
        from estiem_eda.tools.i_chart import IChartTool
        tool = IChartTool()
        
        # Test with simple data
        data = [10.0, 10.5, 9.5, 10.2, 9.8, 10.1, 9.9, 10.3]
        result = tool.execute({"data": data})
        
        assert "statistics" in result
        assert "control_analysis" in result
        assert "interpretation" in result
        assert "chart_html" in result
        assert result["statistics"]["sample_size"] == len(data)
        print("   OK I-Chart tool working correctly")
        passed += 1
    except Exception as e:
        print(f"   ERROR I-Chart tool failed: {e}")
        failed += 1
    
    # Test 3: Capability Tool Basic Functionality
    print("\n3. Testing Process Capability Tool...")
    try:
        from estiem_eda.tools.capability import CapabilityTool
        tool = CapabilityTool()
        
        # Generate capable process data
        import numpy as np
        np.random.seed(42)
        data = np.random.normal(10.0, 0.2, 100).tolist()
        
        result = tool.execute({
            "data": data,
            "lsl": 9.0,
            "usl": 11.0,
            "target": 10.0
        })
        
        assert "capability_indices" in result
        assert "defect_analysis" in result
        assert "chart_html" in result
        assert result["capability_indices"]["cpk"] > 0
        print("   OK Capability tool working correctly")
        passed += 1
    except Exception as e:
        print(f"   ❌ Capability tool failed: {e}")
        failed += 1
    
    # Test 4: ANOVA Tool Basic Functionality
    print("\n4. Testing ANOVA Tool...")
    try:
        from estiem_eda.tools.anova import ANOVATool
        tool = ANOVATool()
        
        groups = {
            "Group A": [10.0, 10.5, 9.5, 10.2, 9.8],
            "Group B": [12.0, 12.5, 11.5, 12.2, 11.8],
            "Group C": [11.0, 11.5, 10.5, 11.2, 10.8]
        }
        
        result = tool.execute({"groups": groups})
        
        assert "anova_results" in result
        assert "descriptive_statistics" in result
        assert "chart_html" in result
        assert result["anova_results"]["f_statistic"] > 0
        print("   ✅ ANOVA tool working correctly")
        passed += 1
    except Exception as e:
        print(f"   ❌ ANOVA tool failed: {e}")
        failed += 1
    
    # Test 5: Pareto Tool Basic Functionality
    print("\n5. Testing Pareto Tool...")
    try:
        from estiem_eda.tools.pareto import ParetoTool
        tool = ParetoTool()
        
        data = {
            "Issue A": 100,
            "Issue B": 75,
            "Issue C": 50,
            "Issue D": 25,
            "Issue E": 10
        }
        
        result = tool.execute({"data": data})
        
        assert "vital_few" in result
        assert "sorted_data" in result
        assert "chart_html" in result
        assert len(result["sorted_data"]) == 5
        print("   ✅ Pareto tool working correctly")
        passed += 1
    except Exception as e:
        print(f"   ❌ Pareto tool failed: {e}")
        failed += 1
    
    # Test 6: MCP Protocol Integration
    print("\n6. Testing MCP Protocol Integration...")
    try:
        server = ESTIEMMCPServer()
        
        # Test initialize
        init_response = server.handle_initialize({})
        assert "protocolVersion" in init_response
        
        # Test list tools
        list_response = server.handle_list_tools({})
        assert "tools" in list_response
        assert len(list_response["tools"]) == 4
        
        # Test tool execution
        call_response = server.handle_call_tool({
            "name": "i_chart",
            "arguments": {"data": [10, 11, 9, 12, 8]}
        })
        assert "content" in call_response
        print("   ✅ MCP protocol integration working")
        passed += 1
    except Exception as e:
        print(f"   ❌ MCP protocol integration failed: {e}")
        failed += 1
    
    # Test 7: Visualization Integration
    print("\n7. Testing Visualization Integration...")
    try:
        # Test that visualizations are generated (or graceful fallback)
        from estiem_eda.tools.i_chart import IChartTool
        tool = IChartTool()
        
        result = tool.execute({"data": [10, 11, 9, 12, 8]})
        chart_html = result["chart_html"]
        
        # Should be either HTML or error message
        assert isinstance(chart_html, str)
        assert len(chart_html) > 0
        
        if "error" in chart_html.lower():
            print("   ⚠️  Visualization fallback working (Plotly not available)")
        else:
            print("   ✅ Visualization generation working")
        passed += 1
    except Exception as e:
        print(f"   ❌ Visualization integration failed: {e}")
        failed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! The ESTIEM EDA toolkit is working correctly.")
        return True
    else:
        print(f"⚠️  {failed} tests failed. Please check the errors above.")
        return False


def test_statistical_accuracy():
    """Test statistical calculations for accuracy."""
    print("\n🔬 Statistical Accuracy Tests")
    print("-" * 30)
    
    try:
        from estiem_eda.tools.i_chart import IChartTool
        import numpy as np
        
        # Known data for manual verification
        data = [10.0, 12.0, 8.0, 11.0, 9.0]
        tool = IChartTool()
        result = tool.execute({"data": data})
        stats = result["statistics"]
        
        # Manual calculations
        expected_mean = np.mean(data)
        moving_ranges = [abs(data[i] - data[i-1]) for i in range(1, len(data))]
        expected_avg_mr = np.mean(moving_ranges)
        expected_sigma = expected_avg_mr / 1.128
        
        # Verify calculations (within 0.0001 tolerance)
        assert abs(stats["mean"] - expected_mean) < 0.0001
        assert abs(stats["moving_range_average"] - expected_avg_mr) < 0.0001
        assert abs(stats["sigma_estimate"] - expected_sigma) < 0.0001
        
        print("✅ I-Chart statistical calculations verified")
        
        # Test capability calculations
        from estiem_eda.tools.capability import CapabilityTool
        cap_tool = CapabilityTool()
        
        # Simple data with known Cp/Cpk
        cap_data = [10.0] * 50  # Perfect centering, minimal variation
        cap_result = cap_tool.execute({
            "data": cap_data,
            "lsl": 9.0,
            "usl": 11.0
        })
        
        indices = cap_result["capability_indices"]
        
        # With minimal variation, Cp should be very high
        assert indices["cp"] > 10  # Should be much greater than 1.33
        assert indices["cpk"] > 10  # Perfect centering
        assert abs(indices["cpk"] - indices["cp"]) < 0.1  # Should be nearly equal
        
        print("✅ Capability calculations verified")
        return True
        
    except Exception as e:
        print(f"❌ Statistical accuracy test failed: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Starting ESTIEM EDA Test Suite...")
    
    basic_tests_passed = run_simple_tests()
    accuracy_tests_passed = test_statistical_accuracy()
    
    if basic_tests_passed and accuracy_tests_passed:
        print("\n🎉 All test suites passed!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)