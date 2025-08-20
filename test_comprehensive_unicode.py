#!/usr/bin/env python3
"""Comprehensive Unicode and Chart Generation Test"""

import sys
import os
from pathlib import Path
import subprocess
import re

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def find_unicode_in_python_files():
    """Find Unicode characters in Python files that could break execution"""
    print("=" * 60)
    print("UNICODE CHECK IN CRITICAL PYTHON FILES")
    print("=" * 60)
    
    critical_files = [
        "docs/eda_tools.py",
        "docs/app.js", 
        "src/estiem_eda/core/calculations.py",
        "src/estiem_eda/core/validation.py",
        "src/estiem_eda/utils/visualization.py",
        "src/estiem_eda/utils/branding.py",
        "src/estiem_eda/mcp_server.py",
        "src/estiem_eda/tools/i_chart.py",
        "src/estiem_eda/tools/capability.py",
        "src/estiem_eda/tools/anova.py",
        "src/estiem_eda/tools/pareto.py",
        "src/estiem_eda/tools/probability_plot.py"
    ]
    
    issues_found = []
    
    for file_path in critical_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find Unicode characters (non-ASCII)
                unicode_matches = []
                for line_num, line in enumerate(content.split('\n'), 1):
                    for char_pos, char in enumerate(line):
                        if ord(char) > 127:  # Non-ASCII character
                            unicode_matches.append((line_num, char_pos, char, repr(char)))
                
                if unicode_matches:
                    print(f"\nERROR {file_path}:")
                    for line_num, char_pos, char, repr_char in unicode_matches[:5]:  # Show first 5
                        print(f"   Line {line_num}, Pos {char_pos}: {repr_char}")
                    if len(unicode_matches) > 5:
                        print(f"   ... and {len(unicode_matches) - 5} more")
                    issues_found.extend([(file_path, line_num, char) for line_num, _, char, _ in unicode_matches])
                else:
                    print(f"OK {file_path}: No Unicode issues")
                    
            except Exception as e:
                print(f"WARNING {file_path}: Could not read - {e}")
        else:
            print(f"WARNING {file_path}: File not found")
    
    return issues_found

def test_web_app_components():
    """Test web app components for chart generation"""
    print("\n" + "=" * 60)
    print("WEB APP CHART GENERATION TEST")
    print("=" * 60)
    
    try:
        # Test Python components that run in browser
        from estiem_eda.core.calculations import (
            calculate_i_chart, calculate_process_capability, 
            calculate_anova, calculate_pareto, calculate_probability_plot
        )
        from estiem_eda.core.validation import validate_numeric_data, validate_groups_data
        
        print("SUCCESS: Core calculation modules imported successfully")
        
        # Test sample data
        test_data = [10.0, 10.5, 9.5, 10.2, 9.8, 10.1, 9.9, 10.3, 10.0, 9.7]
        values = validate_numeric_data(test_data)
        
        # Test each calculation
        print("\nTesting Core Calculations:")
        
        # I-Chart
        i_result = calculate_i_chart(values, "Test I-Chart")
        print(f"   OK I-Chart: Success={i_result['success']}")
        
        # Capability  
        cap_result = calculate_process_capability(values, lsl=9.0, usl=11.0)
        print(f"   OK Capability: Success={cap_result['success']}")
        
        # ANOVA
        groups = {"A": values[:3], "B": values[3:6], "C": values[6:]}
        anova_result = calculate_anova(groups)
        print(f"   OK ANOVA: Success={anova_result['success']}")
        
        # Pareto
        pareto_data = {"Issue_A": 50, "Issue_B": 30, "Issue_C": 20}
        pareto_result = calculate_pareto(pareto_data)
        print(f"   OK Pareto: Success={pareto_result['success']}")
        
        # Probability Plot
        prob_result = calculate_probability_plot(values, distribution='normal')
        print(f"   OK Probability: Success={prob_result['success']}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Web app component test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mcp_chart_generation():
    """Test MCP tool chart generation"""
    print("\n" + "=" * 60) 
    print("MCP CHART GENERATION TEST")
    print("=" * 60)
    
    try:
        from estiem_eda.tools.i_chart import IChartTool
        from estiem_eda.tools.capability import CapabilityTool
        import numpy as np
        
        print("Testing MCP Chart Generation:")
        
        # Test I-Chart
        i_tool = IChartTool()
        i_result = i_tool.execute({
            'data': [10.0, 10.5, 9.5, 10.2, 9.8, 10.1, 9.9, 10.3, 10.0, 9.7],
            'title': 'MCP Test Chart'
        })
        chart_generated = 'visualization' in i_result and i_result['visualization']
        print(f"   OK I-Chart: Success={i_result['success']}, Chart Generated={chart_generated}")
        if 'visualization_error' in i_result:
            print(f"      Error: {i_result['visualization_error']}")
        
        # Test Capability
        np.random.seed(42)
        large_data = np.random.normal(10.0, 0.3, 50).tolist()
        cap_tool = CapabilityTool()
        cap_result = cap_tool.execute({
            'data': large_data,
            'lsl': 9.0,
            'usl': 11.0,
            'title': 'MCP Capability Test'
        })
        cap_chart_generated = 'visualization' in cap_result and cap_result['visualization']
        print(f"   OK Capability: Success={cap_result['success']}, Chart Generated={cap_chart_generated}")
        if 'visualization_error' in cap_result:
            print(f"      Error: {cap_result['visualization_error']}")
        
        return chart_generated and cap_chart_generated
        
    except Exception as e:
        print(f"ERROR: MCP chart test failed: {e}")
        return False

def test_plotly_availability():
    """Test if Plotly is available and working"""
    print("\n" + "=" * 60)
    print("PLOTLY VISUALIZATION TEST")
    print("=" * 60)
    
    try:
        import plotly.graph_objects as go
        print(f"OK: Plotly {plotly.__version__} available")
        
        # Test basic chart creation
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[1, 2, 3], y=[1, 4, 2], name='Test'))
        html = fig.to_html(include_plotlyjs='cdn')
        
        chart_valid = len(html) > 1000 and 'plotly' in html.lower()
        print(f"OK: Chart generation working: {chart_valid}")
        
        return True
        
    except ImportError:
        print("ERROR: Plotly not available - charts will not generate")
        return False
    except Exception as e:
        print(f"ERROR: Plotly test failed: {e}")
        return False

def main():
    """Run comprehensive test suite"""
    print("COMPREHENSIVE UNICODE & CHART GENERATION TEST")
    print("=" * 60)
    
    # Test 1: Unicode issues
    unicode_issues = find_unicode_in_python_files()
    
    # Test 2: Plotly availability
    plotly_ok = test_plotly_availability()
    
    # Test 3: Web app components
    webapp_ok = test_web_app_components()
    
    # Test 4: MCP chart generation
    mcp_ok = test_mcp_chart_generation()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    print(f"Unicode Issues Found: {len(unicode_issues)}")
    print(f"Plotly Available: {plotly_ok}")
    print(f"Web App Components: {webapp_ok}")
    print(f"MCP Chart Generation: {mcp_ok}")
    
    if len(unicode_issues) == 0 and plotly_ok and webapp_ok and mcp_ok:
        print("\nSUCCESS: ALL TESTS PASSED - CHARTS SHOULD BE WORKING!")
        return True
    else:
        print(f"\nWARNING: ISSUES FOUND - CHART GENERATION MAY BE AFFECTED")
        if len(unicode_issues) > 0:
            print(f"   - {len(unicode_issues)} Unicode characters in critical files")
        if not plotly_ok:
            print("   - Plotly visualization library issues")
        if not webapp_ok:
            print("   - Web app core component issues")
        if not mcp_ok:
            print("   - MCP chart generation issues")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"ERROR: Test script failed: {e}")
        sys.exit(1)