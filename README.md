# ESTIEM EDA Toolkit

**Professional Exploratory Data Analysis for Industrial Engineering Applications**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![ESTIEM](https://img.shields.io/badge/ESTIEM-60k%2B_Students-green.svg)](https://estiem.org)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jukka-matti/ESTIEM-eda/blob/main/notebooks/ESTIEM_EDA_Quick_Start.ipynb)

**Comprehensive exploratory data analysis toolkit** with multiple access methods: Web App, Python Package, CLI Tool, Google Colab, and Claude Desktop integration via MCP protocol. Built with **pure NumPy/SciPy** for maximum reliability and compatibility.

## 🚀 Quick Start

### 🌐 Web Application (Zero Installation)
**[Launch Web App →](https://jukka-matti.github.io/ESTIEM-eda/)**
- Drag-and-drop CSV upload
- Interactive visualizations  
- Mobile-friendly design
- 100% browser-based

### 📊 Google Colab (One-Click Setup)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jukka-matti/ESTIEM-eda/blob/main/notebooks/ESTIEM_EDA_Quick_Start.ipynb)

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
estiem-eda i-chart sample_data.csv
estiem-eda capability sample_data.csv --lsl 9.0 --usl 11.0
estiem-eda anova sample_data.csv --value measurement --group line
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

## 📊 Statistical Tools Available

| Tool | Description | Use Case |
|------|-------------|----------|
| **I-Chart** | Individual control charts with Western Electric rules | Process monitoring, SPC |
| **Process Capability** | Cp/Cpk analysis with Six Sigma levels | Process qualification |
| **ANOVA** | One-way ANOVA with pairwise comparisons | Group comparisons |
| **Pareto Analysis** | 80/20 rule identification | Root cause analysis |
| **Probability Plot** | Normal/Weibull/Lognormal plots with 95% confidence intervals | Distribution assessment, outlier detection |

## 💡 Usage Examples

### Quick Analysis
```python
from estiem_eda import quick_i_chart, quick_capability, quick_pareto

# Quick analyses without data loading
measurements = [9.8, 10.2, 9.9, 10.1, 10.3, 9.7, 10.0, 10.4]

# Control chart
i_results = quick_i_chart(measurements)

# Process capability  
cap_results = quick_capability(measurements, lsl=9.5, usl=10.5)

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

# Run all analyses
results = eda.analyze_all(
    measurement_column='measurement',
    lsl=9.0, usl=11.0,
    group_column='line'
)
```

### With Claude Desktop
```
"Analyze this manufacturing data for process capability:
Data: [9.8, 10.2, 9.9, 10.1, 10.3, 9.7, 10.0, 10.4]
LSL: 9.5, USL: 10.5"

"Create a probability plot to assess normality:
Data: [9.8, 10.2, 9.9, 10.1, 10.3, 9.7, 10.0, 10.4, 10.2, 9.9]
Check for outliers and distribution fit"
```

## 🔧 Installation Options

### Option 1: Web Application (Recommended)
**Zero installation required**
- Visit: [https://jukka-matti.github.io/ESTIEM-eda/](https://jukka-matti.github.io/ESTIEM-eda/)
- Upload CSV files directly
- Interactive charts and reports

### Option 2: Google Colab
**One-click setup in browser**
- Click: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jukka-matti/ESTIEM-eda/blob/main/notebooks/ESTIEM_EDA_Quick_Start.ipynb)
- Install with: `!pip install git+https://github.com/jukka-matti/ESTIEM-eda.git`

### Option 3: Local Installation
```bash
git clone https://github.com/jukka-matti/ESTIEM-eda.git
cd ESTIEM-eda
pip install -r requirements.txt
pip install -e .
```

### Option 4: MCP Server Only
```bash
pip install git+https://github.com/jukka-matti/ESTIEM-eda.git
python -m estiem_eda.mcp_server  # Test installation
```

## 🔧 MCP Server Features

- **JSON-RPC Protocol** - Standard MCP v1.0 compliance
- **Interactive Charts** - Plotly visualizations with ESTIEM branding
- **Comprehensive Analysis** - Statistics, interpretations, recommendations
- **Error Handling** - Graceful validation and meaningful error messages
- **Professional Output** - Publication-ready charts and reports

## 📈 For Lean Six Sigma Students

Perfect for DMAIC methodology:
- **Define**: Pareto analysis to identify vital problems
- **Measure**: I-charts for baseline process monitoring  
- **Analyze**: ANOVA to compare process conditions
- **Improve**: Capability analysis to verify improvements
- **Control**: Ongoing SPC with control charts

## 🎓 Educational Focus

Built specifically for:
- **ESTIEM Lean Six Sigma Certification**
- **Industrial Engineering applications**
- **Quality Management education**
- **Statistical process control training**

## 🏗️ Architecture

### **Unified Core Engine**
All platforms use the **same statistical calculations** for consistent results:

```
🔧 Core Engine (Pure NumPy/SciPy)
├── core/calculations.py    # 5 statistical algorithms
├── core/validation.py     # Data validation & cleaning
└── Consistent results across ALL platforms ✅
```

### **Multiple Access Methods**
```
🌐 Web App (Browser)     →  🔧 Core Engine
🐍 Python Package       →  🔧 Core Engine  
💻 CLI Tool            →  🔧 Core Engine
📓 Google Colab        →  🔧 Core Engine
🤖 Claude Desktop MCP  →  🔧 Core Engine
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
│   ├── core/                  # 🔧 Unified calculation engine
│   │   ├── calculations.py    # Core statistical algorithms
│   │   └── validation.py      # Data validation functions
│   ├── mcp_server.py          # Claude Desktop integration
│   ├── cli.py                 # Command line interface
│   ├── quick_analysis.py      # Python package interface
│   ├── tools/                 # MCP protocol tools
│   └── utils/                 # Visualization & branding
├── docs/                      # 🌐 Web application (Pyodide)
├── notebooks/                 # 📓 Google Colab integration
├── tests/                     # Comprehensive test suite
└── examples/                  # Sample data and usage
```

## 🏆 Key Features

- **🔧 Unified Core Engine** - Pure NumPy/SciPy for maximum compatibility
- **📊 Consistent Results** - Same calculations across all platforms
- **🌐 Zero Installation** - Browser-based web app with no setup
- **🐍 Multiple Access Points** - Web, CLI, Python, MCP, Colab
- **📱 Cross-Platform** - Works on desktop, mobile, tablets
- **🎓 Educational Focus** - Built for Industrial Engineering students
- **🚀 Production Ready** - Comprehensive testing, error handling
- **🎨 Professional Visuals** - ESTIEM-branded interactive charts
- **🔒 Privacy First** - All processing in your browser/local environment
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

[ESTIEM](https://estiem.org) connects 60,000+ Industrial Engineering students across Europe through education, conferences, and professional development.

## 👨‍💻 Creator

**Created by [Jukka-Matti Turtiainen](https://www.rdmaic.com)**
- Lean Six Sigma Expert & Trainer
- Website: [rdmaic.com](https://www.rdmaic.com)

---

*Built by students, for students. Forever free for educational use.*

**🔗 Links**: [ESTIEM.org](https://estiem.org) | [Lean Six Sigma](https://estiem.org/leansixsigma) | [Issues](https://github.com/jukka-matti/ESTIEM-eda/issues)