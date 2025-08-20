#!/usr/bin/env python3
"""
ESTIEM EDA Toolkit - Quick Analysis Examples
Demonstrate streamlined statistical analysis workflows
"""

from estiem_eda import QuickEDA, generate_sample_data, quick_i_chart, quick_capability, quick_pareto
import pandas as pd
import numpy as np

# Example 1: Quick Analysis from CSV
print("=" * 60)
print("🏭 ESTIEM EDA - Quick Analysis Examples")
print("=" * 60)

# Generate sample data
print("\n📊 Example 1: Manufacturing Data Analysis")
print("-" * 40)

# Create sample data
manufacturing_data = generate_sample_data('manufacturing', 100)
print(f"Generated {len(manufacturing_data)} manufacturing samples")

# Quick analysis workflow
eda = QuickEDA()
eda.load_data(manufacturing_data)
eda.preview(3)

# Run comprehensive analysis
results = eda.analyze_all(
    measurement_column='measurement',
    lsl=9.0, usl=11.0,
    group_column='line'
)

print("\n📉 Example 2: Quality Defects Analysis")  
print("-" * 40)

# Quality data
quality_data = generate_sample_data('quality', 200)
eda_quality = QuickEDA()
eda_quality.load_data(quality_data)

# Pareto analysis of defects
pareto_results = eda_quality.pareto('defect_type', 'defect_count')

print("\n⚡ Example 3: Quick Functions")
print("-" * 30)

# Direct analysis without loading data
measurements = np.random.normal(10.0, 0.5, 50)

# Quick I-Chart
i_results = quick_i_chart(measurements, "Quick Process Control")

# Quick Capability
cap_results = quick_capability(measurements, lsl=9.0, usl=11.0, target=10.0)

# Quick Pareto
defects = {'Surface': 45, 'Dimensional': 32, 'Assembly': 18, 'Material': 12, 'Other': 8}
pareto_results = quick_pareto(defects)

print("\n🎯 Example 4: Chain Analysis")
print("-" * 30)

# Fluent interface
results = (QuickEDA()
          .load_data(manufacturing_data)
          .preview(2)
          .i_chart('measurement')
          )

print("\n✅ All examples completed!")
print("🌐 Try the web app: https://jukka-matti.github.io/ESTIEM-eda/")
print("📚 Colab notebook: https://colab.research.google.com/github/jukka-matti/ESTIEM-eda/blob/main/notebooks/ESTIEM_EDA_Quick_Start.ipynb")