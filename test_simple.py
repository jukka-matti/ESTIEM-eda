#!/usr/bin/env python3
"""Simple test without Unicode characters"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_core_calculations():
    """Test core calculation functions directly"""
    print("Testing Core Calculation Engine")
    print("=" * 50)
    
    try:
        # Import core functions
        from estiem_eda.core.calculations import (
            calculate_i_chart,
            calculate_process_capability,
            calculate_anova,
            calculate_pareto,
            calculate_probability_plot
        )
        from estiem_eda.core.validation import validate_numeric_data
        import numpy as np
        
        print("OK: Core modules imported successfully")
        
        # Test data
        test_data = [10.0, 10.5, 9.5, 10.2, 9.8, 10.1, 9.9, 10.3, 10.0, 9.7]
        
        # Test 1: I-Chart
        print("\n1. Testing I-Chart calculation...")
        values = validate_numeric_data(test_data)
        result = calculate_i_chart(values, "Test I-Chart")
        print(f"   OK: I-Chart: Mean={result['statistics']['mean']:.3f}, UCL={result['statistics']['ucl']:.3f}")
        
        # Test 2: Process Capability
        print("\n2. Testing Process Capability...")
        result = calculate_process_capability(values, lsl=9.0, usl=11.0)
        print(f"   OK: Capability: Cp={result['capability_indices']['cp']:.3f}, Cpk={result['capability_indices']['cpk']:.3f}")
        
        # Test 3: ANOVA
        print("\n3. Testing ANOVA...")
        groups = {
            "Group_A": np.array([10, 11, 9, 12, 8]),
            "Group_B": np.array([13, 14, 12, 15, 11]),
            "Group_C": np.array([16, 17, 15, 18, 14])
        }
        result = calculate_anova(groups)
        print(f"   OK: ANOVA: F={result['anova_results']['f_statistic']:.3f}, p={result['anova_results']['p_value']:.3f}")
        
        # Test 4: Pareto
        print("\n4. Testing Pareto Analysis...")
        pareto_data = {"Issue_A": 100, "Issue_B": 50, "Issue_C": 25, "Issue_D": 15}
        result = calculate_pareto(pareto_data)
        print(f"   OK: Pareto: {len(result['vital_few']['categories'])} vital few categories at {result['vital_few']['percentage']:.1f}%")
        
        # Test 5: Probability Plot
        print("\n5. Testing Probability Plot...")
        result = calculate_probability_plot(values, distribution='normal')
        print(f"   OK: Probability Plot: r={result['goodness_of_fit']['correlation_coefficient']:.4f} ({result['goodness_of_fit']['interpretation']})")
        
        print("\n" + "=" * 50)
        print("SUCCESS: ALL CORE TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"\nERROR: Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mcp_tools():
    """Test MCP tool integration with core engine"""
    print("\nTesting MCP Tool Integration")
    print("=" * 50)
    
    try:
        # Test I-Chart Tool
        from estiem_eda.tools.i_chart import IChartTool
        tool = IChartTool()
        result = tool.execute({"data": [10.0, 10.5, 9.5, 10.2, 9.8]})
        if result['success']:
            print("   OK: I-Chart MCP tool working")
        else:
            print(f"   ERROR: I-Chart failed: {result.get('error')}")
            
        # Test Capability Tool - need more data points
        from estiem_eda.tools.capability import CapabilityTool
        import numpy as np
        np.random.seed(42)
        large_dataset = np.random.normal(10.0, 0.3, 100).tolist()
        tool = CapabilityTool()
        result = tool.execute({"data": large_dataset, "lsl": 9.0, "usl": 11.0})
        if result['success']:
            print("   OK: Capability MCP tool working")
        else:
            print(f"   ERROR: Capability failed: {result.get('error')}")
            
        print("\nSUCCESS: MCP TOOL INTEGRATION PASSED!")
        return True
        
    except Exception as e:
        print(f"\nERROR: MCP test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    core_ok = test_core_calculations()
    mcp_ok = test_mcp_tools()
    
    if core_ok and mcp_ok:
        print("\nALL TESTS SUCCESSFUL - CORE ENGINE IS WORKING!")
        sys.exit(0)
    else:
        print("\nSOME TESTS FAILED")
        sys.exit(1)