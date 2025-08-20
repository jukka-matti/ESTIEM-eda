# Contributing to ESTIEM EDA Toolkit

Welcome! We're excited you want to contribute to the ESTIEM Exploratory Data Analysis Toolkit. This guide will help you get started.

## 🚀 Quick Start for Developers

### Prerequisites

- Python 3.9+ (3.11+ recommended)
- Git
- Basic knowledge of statistical process control and Lean Six Sigma

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/ESTIEM-eda.git
   cd ESTIEM-eda
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -e .  # Install in development mode
   ```

4. **Install Pre-commit Hooks**
   ```bash
   pip install pre-commit
   pre-commit install
   ```

5. **Verify Setup**
   ```bash
   python simple_test.py
   ```

## 🏗️ Project Structure

```
ESTIEM-eda/
├── src/estiem_eda/
│   ├── mcp_server.py          # Main MCP server
│   ├── tools/                 # Statistical analysis tools
│   │   ├── base.py           # Base tool class
│   │   ├── i_chart.py        # Individual control charts
│   │   ├── capability.py     # Process capability analysis
│   │   ├── anova.py          # ANOVA analysis
│   │   ├── pareto.py         # Pareto analysis
│   │   └── probability_plot.py # Probability plots
│   └── utils/                 # Utilities
│       ├── visualization.py   # Plotly charts
│       └── branding.py        # ESTIEM branding
├── tests/                     # Test suite
├── examples/                  # Sample data and usage
└── docs/                      # Documentation
```

## 🛠️ Development Workflow

### 1. Choose an Issue
- Check [GitHub Issues](https://github.com/jukka-matti/ESTIEM-eda/issues)
- Look for `good-first-issue` or `help-wanted` labels
- Comment on the issue to claim it

### 2. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 3. Make Changes
- Follow the existing code style and patterns
- Add tests for new functionality
- Update documentation as needed

### 4. Test Your Changes
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_your_feature.py -v

# Run simple integration test
python simple_test.py

# Check code quality
pre-commit run --all-files
```

### 5. Submit Pull Request
- Push your branch to GitHub
- Create a Pull Request with clear description
- Link to related issues
- Ensure CI passes

## 📝 Code Style Guidelines

### Python Code Style
- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://black.readthedocs.io/) for formatting (configured in pre-commit)
- Use [Ruff](https://docs.astral.sh/ruff/) for linting
- Type hints recommended for new functions

### Documentation Style
- Docstrings in [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- Clear, concise comments
- Update README.md for user-facing changes

### Example Function Template
```python
def analyze_process_data(data: List[float], 
                        control_limits: Dict[str, float]) -> Dict[str, Any]:
    """Analyze process data for control chart violations.
    
    Args:
        data: List of measurement values
        control_limits: Dictionary with 'ucl', 'lcl', 'center' keys
        
    Returns:
        Dictionary containing analysis results with keys:
        - violations: List of out-of-control points
        - patterns: List of detected patterns
        - statistics: Summary statistics
        
    Raises:
        ValueError: If data is empty or control limits invalid
    """
    pass
```

## 🧪 Testing Guidelines

### Test Structure
- Unit tests for individual functions
- Integration tests for tool workflows
- MCP protocol tests for server functionality

### Writing Tests
```python
import pytest
from estiem_eda.tools.your_tool import YourTool

class TestYourTool:
    @pytest.fixture
    def tool(self):
        return YourTool()
    
    @pytest.fixture
    def sample_data(self):
        return [10.1, 9.9, 10.2, 10.0, 9.8]
    
    def test_basic_functionality(self, tool, sample_data):
        result = tool.execute({"data": sample_data})
        assert result["success"] is True
        assert "analysis_results" in result
```

### Test Coverage
- Aim for >90% test coverage
- Test both happy path and error conditions
- Include edge cases (empty data, invalid inputs)

## 📊 Adding New Statistical Tools

### 1. Create Tool Class
```python
# src/estiem_eda/tools/your_tool.py
from .base import BaseTool

class YourTool(BaseTool):
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Input data for analysis"
                }
            },
            "required": ["data"]
        }
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # Implementation here
        pass
```

### 2. Add Visualization
```python
# In utils/visualization.py
def create_your_chart(data, title="Your Chart"):
    # Plotly implementation
    # Apply ESTIEM branding
    return fig.to_html()
```

### 3. Register in MCP Server
```python
# In mcp_server.py initialize_tools method
try:
    from .tools.your_tool import YourTool
    self.tools["your_tool"] = YourTool()
    self.logger.debug("Your Tool loaded successfully")
except ImportError as e:
    self.logger.warning(f"Your Tool not available: {e}")
```

### 4. Add Tests
```python
# tests/test_your_tool.py
```

### 5. Update Documentation
- Add tool to README.md table
- Include usage examples
- Update simple_test.py if needed

## 🎨 ESTIEM Branding Guidelines

### Visual Identity
- Primary color: `#2E8B57` (ESTIEM Green)
- Font: Arial, sans-serif
- Logo placement: Bottom-right corner with 40% opacity

### Branding Implementation
```python
from ..utils.branding import add_estiem_branding, apply_estiem_theme

# Apply to Plotly figures
fig = apply_estiem_theme(fig)
fig = add_estiem_branding(fig, style="subtle")
```

## 🔍 Quality Assurance

### Code Quality Checks
- **Linting**: Ruff for code style
- **Formatting**: Black for consistent formatting
- **Type Checking**: MyPy for type safety
- **Security**: Bandit for security vulnerabilities
- **Testing**: Pytest with coverage reporting

### Pre-commit Hooks
All checks run automatically on commit:
```bash
# Manual run
pre-commit run --all-files
```

## 📚 Educational Focus

### Statistical Accuracy
- Use industry-standard formulas and methods
- Validate against established statistical software (Minitab, R)
- Include proper interpretation and recommendations

### Learning Experience
- Clear, educational output messages
- Comprehensive error handling with helpful hints
- Examples following DMAIC methodology

## 🤝 Community Guidelines

### Be Respectful
- Follow the [Code of Conduct](CODE_OF_CONDUCT.md)
- Be patient with new contributors
- Provide constructive feedback

### Communication
- Use clear, professional language
- Include context in issues and PRs
- Tag relevant maintainers when needed

## 🎯 Priority Areas

Looking for contributors in these areas:

1. **New Statistical Tools**
   - Histogram analysis
   - Regression analysis  
   - Design of experiments (DOE)
   - Measurement system analysis (MSA)

2. **Enhanced Visualizations**
   - Interactive dashboards
   - Mobile-responsive charts
   - Export capabilities (PDF, PNG)

3. **Educational Content**
   - More DMAIC examples
   - Tutorial notebooks
   - Video demonstrations

4. **Performance Optimization**
   - Large dataset handling
   - Computation efficiency
   - Memory optimization

## 📞 Getting Help

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **ESTIEM Community**: Connect through [estiem.org](https://estiem.org)

## 🏆 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Acknowledged in release notes
- Invited to ESTIEM events (when applicable)
- Featured in ESTIEM newsletters

---

**Thank you for contributing to ESTIEM EDA Toolkit!** 

Your contributions help 60,000+ Industrial Engineering students worldwide learn statistical process control and Lean Six Sigma methodologies.

*Built by students, for students. Forever free for educational use.*