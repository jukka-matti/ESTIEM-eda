# ESTIEM EDA Toolkit

**Professional Exploratory Data Analysis for Industrial Engineering Applications**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![ESTIEM](https://img.shields.io/badge/ESTIEM-60k%2B_Students-green.svg)](https://estiem.org)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jukka-matti/ESTIEM-eda/blob/main/notebooks/ESTIEM_EDA_Quick_Start.ipynb)

**Professional Six Sigma toolkit** with 3 core analysis tools and multiple access methods: Web App, Python Package, CLI Tool, Google Colab, and Claude Desktop integration via MCP protocol. Built with **pure NumPy/SciPy** for maximum reliability and compatibility.

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

### Option 5: Web Application Deployment
**For hosting your own web application instance:**

#### Security Headers Required
```html
<!-- Add to your web server configuration -->
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp
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

#### Features
- **Hybrid CDN System**: CloudFlare → UnPKG → Error handling
- **Cross-Origin Isolation**: SharedArrayBuffer support for performance
- **Auto-Fallback**: Graceful degradation when CDNs fail
- **Mobile Responsive**: Works on all device sizes

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

### **Dual Implementation Strategy**
ESTIEM EDA uses a **hybrid architecture** to provide maximum compatibility across all platforms:

```
🖥️ SERVER-SIDE (MCP/CLI/Colab)
├── core/calculations.py      # Full NumPy/SciPy implementation
├── core/validation.py        # Server-side validation
└── Advanced statistics ✅    # All scipy.stats features

🌐 BROWSER-SIDE (Web App)
├── browser/core_browser.py   # Browser-compatible calculations
├── browser/web_adapter.py    # Unified response formatting  
└── Pyodide + fallbacks ✅   # Works without scipy.stats
```

### **Hybrid CDN System** 🔄
Web application uses **enterprise-grade CDN fallback** for maximum reliability:

```
Primary CDN    : CloudFlare (99%+ reliability)
                      ↓ if fails
Fallback CDN   : UnPKG (automatic switching)  
                      ↓ if both fail
Error Handling : Graceful degradation
```

### **Multiple Access Methods**
```
🌐 Web App (Browser)     →  🔧 Browser Core + CDN Fallback
🐍 Python Package       →  🔧 Full NumPy/SciPy Core
💻 CLI Tool            →  🔧 Full NumPy/SciPy Core
📓 Google Colab        →  🔧 Full NumPy/SciPy Core  
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
│   ├── core/                    # 🔧 Server-side calculation engine
│   │   ├── calculations.py      # Full NumPy/SciPy algorithms  
│   │   └── validation.py        # Server-side data validation
│   ├── browser/                 # 🌐 Browser-compatible layer
│   │   ├── core_browser.py      # ⭐ Browser statistics (no scipy)
│   │   ├── generator.py         # ⭐ Auto browser tools generator
│   │   └── web_adapter.py       # ⭐ Unified response formatting
│   ├── utils/                   # Advanced features
│   │   ├── visualization_response.py  # ⭐ Multi-format system
│   │   ├── format_generators.py       # ⭐ HTML/text generators
│   │   └── simplified_visualization.py # Reliable chart system
│   ├── tools/                   # 3 Core Professional Tools
│   │   ├── process_analysis.py  # 🔬 Unified process assessment (I-Chart + Capability + Distribution)
│   │   ├── anova.py            # 📊 ANOVA with box plots and group comparison
│   │   ├── pareto.py           # 📉 Pareto analysis (80/20 rule) with priority ranking
│   │   └── enhanced_base.py    # Simplified base class for streamlined tools
│   ├── mcp_server.py           # Claude Desktop integration (3.0.0)
│   ├── cli.py                  # Command line interface (streamlined)
│   └── quick_analysis.py       # Python package interface
├── docs/                       # 🌐 Web application
│   ├── index.html             # Web app with CDN fallback
│   ├── app.js                 # ⭐ Hybrid CDN loading system
│   └── eda_tools.py          # ⭐ Auto-generated from browser core
├── notebooks/                  # 📓 Google Colab integration
├── tests/                      # Comprehensive test suite
└── examples/                   # Sample data and usage patterns
```

### **⭐ Key Features**
- **Dual Architecture**: Server (full SciPy) + Browser (Pyodide-compatible)
- **CDN Fallback**: CloudFlare primary → UnPKG fallback → Error handling
- **Auto-Generated Tools**: Browser tools sync automatically with core
- **Unified Responses**: Same format across MCP and Web platforms

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