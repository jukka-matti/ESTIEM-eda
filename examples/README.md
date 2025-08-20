# 📊 ESTIEM EDA Examples

This directory contains working examples demonstrating the ESTIEM EDA Toolkit capabilities.

## 🚀 Available Examples

### **`statistical_analysis_examples.py`**
Complete manufacturing analysis workflow demonstrating:
- Pareto Analysis for problem identification
- I-Chart Analysis for process control
- ANOVA Analysis for group comparison  
- Capability Analysis for performance assessment

**Usage:**
```bash
cd examples
python statistical_analysis_examples.py
```

### **`quick_analysis_examples.py`**
Simplified examples for individual tool usage:
- Individual I-Chart creation
- Basic capability analysis
- Simple ANOVA comparison
- Quick Pareto analysis

## 📋 Sample Data

### **`manufacturing_data.csv`**
Sample manufacturing dataset with:
- Temperature measurements
- Defect categories and counts
- Quality control data

## 🔧 Configuration

### **`claude_desktop_config.json`**
Example configuration for Claude Desktop MCP integration.

## 🎯 Recent Updates

- **Removed DMAIC methodology examples** - Replaced with general statistical analysis workflow
- **Fixed Unicode encoding issues** - Examples now work on Windows without emoji errors
- **Updated Pareto field names** - Uses correct `percentage` field instead of deprecated `contribution_percent`
- **Enhanced error handling** - Better error messages and debugging information

## 📖 Running Examples

All examples are self-contained and include:
- ✅ Automatic sample data generation if CSV files are missing
- ✅ Clear output formatting with section headers
- ✅ Error handling with helpful messages
- ✅ Cross-platform compatibility (Windows, macOS, Linux)

## 🛠️ Dependencies

Examples require:
- Python 3.10+
- ESTIEM EDA Toolkit (from src/ directory)
- NumPy, SciPy, Pandas (automatically installed)

The examples automatically add the `src/` directory to the Python path, so they work directly from the repository.