#!/usr/bin/env python3
"""
ESTIEM EDA Toolkit - Six Sigma Examples
Complete examples for Lean Six Sigma DMAIC methodology
"""

import sys
from pathlib import Path
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from estiem_eda.tools.i_chart import IChartTool
from estiem_eda.tools.capability import CapabilityTool
from estiem_eda.tools.anova import ANOVATool
from estiem_eda.tools.pareto import ParetoTool

def dmaic_example():
    """Complete DMAIC methodology example using ESTIEM EDA tools."""
    print("ESTIEM EDA Toolkit - Six Sigma DMAIC Example")
    print("=" * 50)
    
    # Load sample manufacturing data
    data_file = Path(__file__).parent / "manufacturing_data.csv"
    df = pd.read_csv(data_file)
    
    print(f"Loaded {len(df)} manufacturing samples")
    
    # DEFINE Phase: Identify key problems with Pareto Analysis
    print("\n🎯 DEFINE Phase - Pareto Analysis")
    print("-" * 30)
    
    defect_counts = df.groupby('defect_type')['defect_count'].sum().to_dict()
    pareto_tool = ParetoTool()
    pareto_result = pareto_tool.execute({
        "data": defect_counts,
        "title": "Manufacturing Defects - Pareto Analysis",
        "unit": "defects"
    })
    
    vital_few = pareto_result['vital_few']['categories']
    print(f"Vital Few Problems: {vital_few}")
    print(f"Impact: {pareto_result['vital_few']['percentage']:.1f}% of defects")
    
    # MEASURE Phase: Baseline process with I-Chart
    print("\n📏 MEASURE Phase - Process Baseline")
    print("-" * 30)
    
    measurements = df['measurement'].tolist()
    ichart_tool = IChartTool()
    ichart_result = ichart_tool.execute({
        "data": measurements,
        "title": "Manufacturing Process - Baseline Control Chart"
    })
    
    baseline_stats = ichart_result['statistics']
    print(f"Process Mean: {baseline_stats['mean']:.3f}")
    print(f"Process Sigma: {baseline_stats['sigma_estimate']:.3f}")
    print(f"Out of Control Points: {ichart_result['control_analysis']['out_of_control_points']}")
    
    # ANALYZE Phase: Compare production lines with ANOVA
    print("\n🔍 ANALYZE Phase - Group Comparison")
    print("-" * 30)
    
    groups = {}
    for group in df['group'].unique():
        groups[group] = df[df['group'] == group]['measurement'].tolist()
    
    anova_tool = ANOVATool()
    anova_result = anova_tool.execute({"groups": groups})
    
    f_stat = anova_result['anova_results']['f_statistic']
    p_value = anova_result['anova_results']['p_value']
    significant = anova_result['anova_results']['significant']
    
    print(f"ANOVA Results: F = {f_stat:.3f}, p = {p_value:.4f}")
    print(f"Significant Difference: {'YES' if significant else 'NO'}")
    
    if significant and 'post_hoc_analysis' in anova_result:
        sig_pairs = anova_result['post_hoc_analysis']['significant_pairs']
        print(f"Significant Differences: {sig_pairs}")
    
    # IMPROVE Phase: Process capability after improvements
    print("\n🚀 IMPROVE Phase - Capability Analysis")
    print("-" * 30)
    
    # Simulate improved process (use Line_A as best performer)
    best_line_data = df[df['group'] == 'Line_A']['measurement'].tolist()
    
    capability_tool = CapabilityTool()
    capability_result = capability_tool.execute({
        "data": best_line_data,
        "lsl": 9.5,   # Lower spec limit
        "usl": 10.5,  # Upper spec limit
        "target": 10.0
    })
    
    indices = capability_result['capability_indices']
    defects = capability_result['defect_analysis']
    
    print(f"Process Capability:")
    print(f"  Cp = {indices['cp']:.3f}")
    print(f"  Cpk = {indices['cpk']:.3f}")
    print(f"  Expected Defects: {defects['ppm_total']:.0f} PPM")
    print(f"  Sigma Level: {defects['sigma_level']:.1f}")
    
    # CONTROL Phase: Recommendations
    print("\n🎛️  CONTROL Phase - Recommendations")
    print("-" * 30)
    
    if indices['cpk'] >= 1.33:
        print("✅ Process is capable - implement control charts")
        print("✅ Monitor with I-charts and capability studies")
        print("✅ Focus on maintaining current performance")
    else:
        print("⚠️  Process needs further improvement")
        print("📋 Actions: Reduce variation, improve centering")
        print("📊 Continue monitoring with statistical tools")
    
    # Summary
    print(f"\n📊 DMAIC SUMMARY")
    print("=" * 50)
    print(f"Define: Identified {len(vital_few)} key defect types")
    print(f"Measure: Process mean = {baseline_stats['mean']:.3f}")
    print(f"Analyze: {'Significant' if significant else 'No'} line differences found")
    print(f"Improve: Achieved Cpk = {indices['cpk']:.3f}")
    print(f"Control: {'Ready for production' if indices['cpk'] >= 1.33 else 'Needs more work'}")
    
    return True

def individual_tool_examples():
    """Examples of using individual tools."""
    print("\n🛠️  Individual Tool Examples")
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
        # Run DMAIC example
        dmaic_example()
        
        # Run individual tool examples
        individual_tool_examples()
        
        print(f"\n🎉 Examples completed successfully!")
        print("Ready to use ESTIEM EDA Toolkit for Six Sigma projects!")
        
    except Exception as e:
        print(f"❌ Example failed: {e}")
        sys.exit(1)