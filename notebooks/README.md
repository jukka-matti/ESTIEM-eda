# 📊 ESTIEM EDA - Google Colab Notebooks

**Quick Start Guide for Google Colab Integration**

## 🚀 Quick Launch

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jukka-matti/ESTIEM-eda/blob/main/notebooks/ESTIEM_EDA_Quick_Start.ipynb)

## 📋 What's Included

### ESTIEM_EDA_Quick_Start.ipynb
- **One-click setup** - Install toolkit directly in Colab
- **Sample data generation** - Manufacturing and quality datasets
- **All 5 statistical tools** with examples:
  - I-Chart (Process Control)
  - Process Capability (Cp/Cpk)
  - ANOVA (Group Comparisons) 
  - Pareto Analysis (80/20 Rule)
  - Probability Plots (Distribution Assessment)
- **File upload integration** - Analyze your own CSV files
- **Interactive visualizations** - Professional charts with ESTIEM branding

## 🔧 Usage Instructions

1. **Click the "Open in Colab" button** above
2. **Run the first cell** to install ESTIEM EDA toolkit
3. **Execute cells sequentially** to see examples
4. **Upload your data** using the file upload section
5. **Modify analysis parameters** for your specific needs

## 📊 Example Analyses

```python
# Process Control Chart
i_chart_tool = IChartTool()
results = i_chart_tool.execute({'data': measurements})

# Process Capability
capability_tool = CapabilityTool()
results = capability_tool.execute({
    'data': measurements,
    'lsl': 9.4, 'usl': 10.6, 'target': 10.0
})

# Pareto Analysis
pareto_tool = ParetoTool()
results = pareto_tool.execute({'data': defect_counts})
```

## 💡 Tips for Success

- **File Format**: Upload CSV files with headers
- **Data Requirements**: Numeric data for most analyses
- **Sample Size**: Minimum 30 points recommended for control charts
- **Missing Data**: Tools automatically handle NaN values

## 🌐 Alternative Access

- **Web App**: [https://jukka-matti.github.io/ESTIEM-eda/](https://jukka-matti.github.io/ESTIEM-eda/)
- **CLI Tool**: `pip install git+https://github.com/jukka-matti/ESTIEM-eda.git`
- **MCP Server**: For Claude Desktop integration

---

**🎓 Built by ESTIEM for 10,000+ Industrial Engineering students**