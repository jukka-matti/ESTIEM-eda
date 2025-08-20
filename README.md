# ESTIEM EDA Toolkit

**Professional Exploratory Data Analysis for Industrial Engineering Applications**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![ESTIEM](https://img.shields.io/badge/ESTIEM-10k%2B_Students-green.svg)](https://estiem.org)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jukka-matti/ESTIEM-eda/blob/main/notebooks/ESTIEM_EDA_Quick_Start.ipynb)

**Professional Six Sigma toolkit** with 3 core analysis tools and streamlined access methods: Google Colab (recommended), Python Package, CLI Tool, and Claude Desktop integration via MCP protocol. Built with **pure NumPy/SciPy** for maximum reliability and compatibility.

## 🚀 Quick Start

### 📊 Google Colab (Recommended - Zero Installation)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jukka-matti/ESTIEM-eda/blob/main/notebooks/ESTIEM_EDA_Quick_Start.ipynb)

- **One-click setup**: No installation required, runs in any browser
- **Full Python environment**: Complete NumPy/SciPy statistical libraries
- **Interactive notebooks**: Professional Jupyter interface with visualizations
- **Mobile-friendly**: Works on phones, tablets, and desktops
- **Easy sharing**: Shareable links for collaboration and teaching
- **Reliable execution**: Google's infrastructure handles all complexity

### 💻 Python Package
```bash
pip install git+https://github.com/jukka-matti/ESTIEM-eda.git
```

```python
from estiem_eda import QuickEDA, generate_sample_data

# Load sample data
data = generate_sample_data('manufacturing')
eda = QuickEDA().load_data(data)

# Run comprehensive analysis
results = eda.analyze_all('measurement', lsl=9.0, usl=11.0, group_column='line')
```

### 🖥️ Command Line Tool
```bash
# Generate sample data
estiem-eda sample-data --type manufacturing

# Run analyses
estiem-eda process-analysis sample_data.csv --column measurement --lsl 9.0 --usl 11.0
estiem-eda anova sample_data.csv --value measurement --group line
estiem-eda pareto sample_data.csv --category defect_type --value count
```

### 🤖 Claude Desktop Integration
Add to your Claude Desktop config:
```json
{
  "mcpServers": {
    "estiem-eda": {
      "command": "python",
      "args": ["C:/path/to/ESTIEM-eda/src/estiem_eda/mcp_server.py"]
    }
  }
}
```

## 📊 Core Analysis Tools

| Tool | Description | Use Case |
|------|-------------|----------|
| **🔬 Process Analysis** | Complete process assessment: stability (I-Chart), capability (Cp/Cpk), and distribution analysis | Individual measurement analysis, Six Sigma studies |
| **📊 ANOVA** | One-way ANOVA with pairwise comparisons and boxplot visualization | Multi-group statistical comparison |
| **📉 Pareto Analysis** | 80/20 rule identification with cumulative percentage analysis | Root cause analysis, priority setting |

## 💡 Usage Examples

### Quick Analysis
```python
from estiem_eda import quick_process_analysis, quick_anova, quick_pareto

# Complete process analysis
measurements = [9.8, 10.2, 9.9, 10.1, 10.3, 9.7, 10.0, 10.4]
process_results = quick_process_analysis(
    measurements, 
    lsl=9.5, usl=10.5, 
    distribution='normal'
)

# Group comparison
groups = {
    'Line_A': [9.8, 10.2, 9.9, 10.1],
    'Line_B': [10.1, 10.3, 10.0, 10.4], 
    'Line_C': [9.7, 9.9, 9.8, 10.0]
}
anova_results = quick_anova(groups)

# Pareto analysis
defects = {'Surface': 45, 'Dimensional': 32, 'Assembly': 18}
pareto_results = quick_pareto(defects)
```

### Comprehensive Analysis
```python
from estiem_eda import QuickEDA, generate_sample_data

# Load sample manufacturing data
data = generate_sample_data('manufacturing', 100)
eda = QuickEDA().load_data(data).preview()

# Run comprehensive process analysis
results = eda.process_analysis(
    measurement_column='measurement',
    lsl=9.0, usl=11.0,
    distribution='normal'
)

# Multi-group comparison
anova_results = eda.anova_analysis(
    value_column='measurement',
    group_column='line'
)
```

### With Claude Desktop
```
"Run complete process analysis on this manufacturing data:
Data: [9.8, 10.2, 9.9, 10.1, 10.3, 9.7, 10.0, 10.4]
LSL: 9.5, USL: 10.5, Distribution: normal"

"Compare these production lines using ANOVA:
Line_A: [9.8, 10.2, 9.9, 10.1]
Line_B: [10.1, 10.3, 10.0, 10.4] 
Line_C: [9.7, 9.9, 9.8, 10.0]"

"Create Pareto analysis for these defect counts:
Surface: 45, Dimensional: 32, Assembly: 18, Material: 12, Other: 8"
```

## 🔧 Installation Options

### Option 1: Google Colab (Recommended)
**One-click setup in browser**
- Click: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jukka-matti/ESTIEM-eda/blob/main/notebooks/ESTIEM_EDA_Quick_Start.ipynb)
- Install with: `!pip install git+https://github.com/jukka-matti/ESTIEM-eda.git`

### Option 2: Local Installation
```bash
git clone https://github.com/jukka-matti/ESTIEM-eda.git
cd ESTIEM-eda
pip install -r requirements.txt
pip install -e .
```

### Option 3: MCP Server Only
```bash
pip install git+https://github.com/jukka-matti/ESTIEM-eda.git
python -m estiem_eda.mcp_server  # Test installation
```

#### Claude Desktop Configuration
```json
{
  "mcpServers": {
    "estiem-eda": {
      "command": "python",
      "args": ["C:/path/to/ESTIEM-eda/src/estiem_eda/mcp_server.py"]
    }
  }
}
```


## 🔧 MCP Server Features

- **JSON-RPC Protocol** - Standard MCP v1.0 compliance
- **Interactive Charts** - Plotly visualizations with ESTIEM branding
- **Comprehensive Analysis** - Statistics, interpretations, recommendations
- **Error Handling** - Graceful validation and meaningful error messages
- **Professional Output** - Publication-ready charts and reports

## 📈 For Statistical Process Control

Professional quality analysis workflow:
- **Problem Identification**: Pareto analysis to identify key issues
- **Process Monitoring**: I-charts for statistical control  
- **Group Comparison**: ANOVA to analyze differences
- **Performance Assessment**: Capability analysis for specifications
- **Continuous Monitoring**: Statistical process control

## 🎓 Educational Focus

Built specifically for:
- **ESTIEM Lean Six Sigma Certification**
- **Industrial Engineering applications**
- **Quality Management education**
- **Statistical process control training**

## 🏗️ Architecture

### **Streamlined Architecture**
ESTIEM EDA uses a **unified NumPy/SciPy core** for maximum reliability across all platforms:

```
🔧 CORE ENGINE (All Platforms)
├── core/calculations.py      # Full NumPy/SciPy implementation
├── core/validation.py        # Robust data validation
└── Advanced statistics ✅    # All scipy.stats features
```

### **Multiple Access Methods**
```
📓 Google Colab         →  🔧 Full NumPy/SciPy Core (Recommended)
🐍 Python Package       →  🔧 Full NumPy/SciPy Core
💻 CLI Tool            →  🔧 Full NumPy/SciPy Core
🤖 Claude Desktop MCP  →  🔧 Full NumPy/SciPy Core
```

## 🛠️ Requirements

- **Python 3.8+** (broad compatibility)
- **NumPy, SciPy** (core calculations)
- **Click** (CLI interface)
- **Plotly** (visualizations, optional)
- **No pandas dependency** (browser-compatible)

## 📁 Project Structure

```
estiem-eda/
├── src/estiem_eda/
│   ├── core/                    # 🔧 Unified calculation engine
│   │   ├── calculations.py      # Full NumPy/SciPy algorithms  
│   │   └── validation.py        # Robust data validation
│   ├── utils/                   # Advanced features
│   │   ├── visualization_response.py  # Multi-format visualization system
│   │   ├── format_generators.py       # HTML/text chart generators
│   │   └── simplified_visualization.py # Reliable chart generation
│   ├── tools/                   # 3 Core Professional Tools
│   │   ├── process_analysis.py  # 🔬 Unified process assessment (I-Chart + Capability + Distribution)
│   │   ├── anova.py            # 📊 ANOVA with box plots and group comparison
│   │   ├── pareto.py           # 📉 Pareto analysis (80/20 rule) with priority ranking
│   │   └── simplified_base.py   # Streamlined base class
│   ├── mcp_server.py           # Claude Desktop integration
│   ├── cli.py                  # Command line interface
│   └── quick_analysis.py       # Python package interface
├── notebooks/                  # 📓 Google Colab integration (Primary Platform)
├── tests/                      # Comprehensive test suite
├── examples/                   # Sample data and usage patterns
└── archive/                    # Archived legacy components
    └── webapp/                 # Previous web application (archived)
```

### **⭐ Key Features**
- **Unified Architecture**: Single NumPy/SciPy core for all platforms
- **Google Colab Focus**: Primary platform with zero installation
- **MCP Integration**: AI-assisted analysis with Claude Desktop
- **Reliable Execution**: No browser compatibility issues

## 🏆 Key Features

- **🔧 Unified Core Engine** - Pure NumPy/SciPy for maximum reliability
- **📊 Consistent Results** - Same calculations across all platforms
- **📓 Google Colab Focus** - Zero installation, runs in any browser
- **🐍 Multiple Access Points** - Colab, CLI, Python, MCP integration
- **📱 Mobile-Friendly** - Colab works on phones, tablets, desktops
- **🎓 Educational Focus** - Built for Industrial Engineering students
- **🚀 Production Ready** - Comprehensive testing, reliable execution
- **🎨 Professional Visuals** - ESTIEM-branded interactive charts
- **🔒 Privacy First** - All processing in your environment
- **📖 Open Source** - Apache 2.0 license, contribute freely

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

Apache 2.0 - see [LICENSE](LICENSE) for details.

## 🌟 About ESTIEM

[ESTIEM](https://estiem.org) connects 10,000+ Industrial Engineering students across 27 countries through education, conferences, and professional development.

## 👨‍💻 Creator

**Created by [Jukka-Matti Turtiainen](https://www.rdmaic.com)**
- Lean Six Sigma Expert & Trainer
- Website: [rdmaic.com](https://www.rdmaic.com)

---

*Built by students, for students. Forever free for educational use.*

**🔗 Links**: [ESTIEM.org](https://estiem.org) | [Lean Six Sigma](https://estiem.org/leansixsigma) | [Issues](https://github.com/jukka-matti/ESTIEM-eda/issues)