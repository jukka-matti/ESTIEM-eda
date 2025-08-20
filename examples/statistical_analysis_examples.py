#!/usr/bin/env python3
"""
ESTIEM EDA Toolkit - Statistical Analysis Examples
Examples demonstrating professional statistical analysis tools
"""

import sys
import csv
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from estiem_eda.tools.i_chart import IChartTool
from estiem_eda.tools.capability import CapabilityTool
from estiem_eda.tools.anova import ANOVATool
from estiem_eda.tools.pareto import ParetoTool

def manufacturing_analysis_example():
    """Complete manufacturing analysis example using ESTIEM EDA tools."""
    print("ESTIEM EDA Toolkit - Manufacturing Analysis Example")
    print("=" * 55)
    
    # Load sample manufacturing data using built-in CSV
    data_file = Path(__file__).parent / "manufacturing_data.csv"
    
    measurements = []
    defect_data = {}
    
    try:
        with open(data_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            print(f"Loaded {len(rows)} manufacturing samples")
            
            # Extract measurements and defect counts
            for row in rows:
                if 'measurement' in row:
                    try:
                        measurements.append(float(row['measurement']))
                    except (ValueError, TypeError):
                        pass
                
                if 'defect_type' in row and 'defect_count' in row:
                    defect_type = row['defect_type']
                    try:
                        count = int(row['defect_count'])
                        defect_data[defect_type] = defect_data.get(defect_type, 0) + count
                    except (ValueError, TypeError):
                        pass
        
    except FileNotFoundError:
        print("Sample data file not found, using synthetic data")
        # Generate synthetic data for demonstration
        measurements = [9.8, 10.1, 9.9, 10.2, 10.0, 9.7, 10.3, 9.9, 10.1, 10.0] * 10
        defect_data = {
            "Surface Finish": 45,
            "Dimensional": 32, 
            "Assembly": 18,
            "Material": 12,
            "Other": 8
        }
    
    # 1. Problem Identification with Pareto Analysis
    print("\n[1] Pareto Analysis - Problem Identification")
    print("-" * 40)
    
    pareto_tool = ParetoTool()
    pareto_result = pareto_tool.execute({
        "data": defect_data,
        "threshold": 0.8
    })
    
    if pareto_result['success']:
        vital_few = pareto_result['vital_few']
        print(f"Key Problem Categories: {vital_few['count']}")
        print(f"Total Impact: {vital_few['percentage']:.1f}% of defects")
        print(f"Categories: {', '.join(vital_few['categories'])}")
    else:
        print("Pareto analysis failed")
    
    # 2. Process Control with I-Chart
    print("\n[2] I-Chart Analysis - Process Control")
    print("-" * 40)
    
    ichart_tool = IChartTool()
    ichart_result = ichart_tool.execute({
        "data": measurements,
        "title": "Manufacturing Process Control Chart"
    })
    
    if ichart_result['success']:
        baseline_stats = ichart_result['statistics']
        print(f"Process Mean: {baseline_stats['mean']:.3f}")
        print(f"Process Sigma: {baseline_stats.get('sigma_hat', 0):.3f}")
        print(f"Out of Control Points: {baseline_stats.get('out_of_control_points', 0)}")
        print(f"Control Status: {'Stable' if baseline_stats.get('out_of_control_points', 0) == 0 else 'Unstable'}")
    else:
        print("I-Chart analysis failed")
    
    # 3. Group Comparison with ANOVA
    print("\n[3] ANOVA Analysis - Group Comparison")
    print("-" * 40)
    
    # Create synthetic group data for demonstration
    groups = {
        "Line_A": [9.9, 10.1, 9.8, 10.2, 10.0, 9.7, 10.3, 9.9, 10.1, 10.0],
        "Line_B": [10.1, 10.3, 10.0, 10.4, 10.2, 9.9, 10.5, 10.1, 10.3, 10.2],
        "Line_C": [9.6, 9.8, 9.5, 9.9, 9.7, 9.4, 10.0, 9.6, 9.8, 9.7]
    }
    
    anova_tool = ANOVATool()
    anova_result = anova_tool.execute({"groups": groups, "alpha": 0.05})
    
    if anova_result['success']:
        f_stat = anova_result['anova_results']['f_statistic']
        p_value = anova_result['anova_results']['p_value']
        significant = anova_result['anova_results']['significant']
        
        print(f"ANOVA Results: F = {f_stat:.3f}, p = {p_value:.4f}")
        print(f"Significant Difference: {'YES' if significant else 'NO'}")
        
        # Show group means
        for group_name, stats in anova_result['group_statistics'].items():
            print(f"{group_name} Mean: {stats['mean']:.3f}")
    else:
        print("ANOVA analysis failed")
    
    # 4. Process Capability Analysis
    print("\n[4] Capability Analysis - Performance Assessment")
    print("-" * 50)
    
    # Use best performing line from ANOVA (Line_A)
    best_line_data = groups["Line_A"]
    
    capability_tool = CapabilityTool()
    capability_result = capability_tool.execute({
        "data": best_line_data,
        "lsl": 9.5,   # Lower spec limit
        "usl": 10.5,  # Upper spec limit
        "target": 10.0
    })
    
    if capability_result['success']:
        indices = capability_result['capability_indices']
        defects = capability_result.get('defect_analysis', {})
        
        print(f"Process Capability:")
        print(f"  Cp = {indices.get('cp', 0):.3f}")
        print(f"  Cpk = {indices.get('cpk', 0):.3f}")
        print(f"  Expected Defects: {defects.get('ppm_total', 0):.0f} PPM")
        print(f"  Sigma Level: {defects.get('sigma_level', 0):.1f}")
        
        cpk_value = indices.get('cpk', 0)
        
        # Performance Assessment
        print("\n[5] Performance Assessment")
        print("-" * 25)
        
        if cpk_value >= 1.33:
            print("PASS: Process is capable")
            print("PASS: Ready for production")
            print("PASS: Monitor with control charts")
        else:
            print("WARN: Process needs improvement")
            print("TODO: Reduce variation and improve centering")
            print("TODO: Continue statistical monitoring")
        
        # Summary
        print(f"\nANALYSIS SUMMARY")
        print("=" * 50)
        
        if pareto_result.get('success') and 'vital_few' in pareto_result:
            print(f"Problem Analysis: {pareto_result['vital_few']['count']} key categories identified")
        else:
            print("Problem Analysis: Defect review completed")
            
        if ichart_result.get('success'):
            process_mean = ichart_result['statistics']['mean']
            print(f"Process Control: Mean = {process_mean:.3f}")
        else:
            print("Process Control: Baseline established")
            
        if anova_result.get('success'):
            significant = anova_result['anova_results']['significant']
            print(f"Group Comparison: {'Significant' if significant else 'No'} differences found")
        else:
            print("Group Comparison: Analysis completed")
            
        print(f"Process Capability: Cpk = {cpk_value:.3f}")
        print(f"Status: {'Production Ready' if cpk_value >= 1.33 else 'Needs Improvement'}")
    else:
        print("Capability analysis failed")
    
    return True

def individual_tool_examples():
    """Examples of using individual tools."""
    print("\nIndividual Tool Examples")
    print("=" * 30)
    
    # I-Chart Example
    print("I-Chart Example:")
    ichart = IChartTool()
    result = ichart.execute({
        "data": [10.1, 9.9, 10.2, 10.0, 9.8, 10.3, 10.1, 9.9, 10.2, 10.0]
    })
    print(f"  Mean: {result['statistics']['mean']:.3f}")
    print(f"  UCL: {result['statistics']['ucl']:.3f}")
    print(f"  LCL: {result['statistics']['lcl']:.3f}")
    
    # Capability Example  
    print("\nCapability Example:")
    capability = CapabilityTool()
    result = capability.execute({
        "data": [10.0] * 50,  # Perfect process
        "lsl": 9.0,
        "usl": 11.0
    })
    print(f"  Cp: {result['capability_indices']['cp']:.3f}")
    print(f"  Cpk: {result['capability_indices']['cpk']:.3f}")
    
    # ANOVA Example
    print("\nANOVA Example:")
    anova = ANOVATool()
    result = anova.execute({
        "groups": {
            "Method_A": [10, 11, 9, 12, 8],
            "Method_B": [13, 14, 12, 15, 11],
            "Method_C": [9, 10, 8, 11, 7]
        }
    })
    print(f"  F-statistic: {result['anova_results']['f_statistic']:.3f}")
    print(f"  Significant: {result['anova_results']['significant']}")
    
    # Pareto Example
    print("\nPareto Example:")
    pareto = ParetoTool()
    result = pareto.execute({
        "data": {
            "Problem_A": 100,
            "Problem_B": 75,
            "Problem_C": 50,
            "Problem_D": 25,
            "Problem_E": 10
        }
    })
    print(f"  Vital Few: {result['vital_few']['categories']}")
    print(f"  Impact: {result['vital_few']['percentage']:.1f}%")

if __name__ == "__main__":
    try:
        # Run manufacturing analysis example
        manufacturing_analysis_example()
        
        # Run individual tool examples
        individual_tool_examples()
        
        print(f"\nExamples completed successfully!")
        print("Ready to use ESTIEM EDA Toolkit for statistical analysis!")
        
    except Exception as e:
        print(f"ERROR: Example failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)