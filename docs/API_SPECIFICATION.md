# 📡 ESTIEM EDA Enhanced MCP Server API Specification

## 📋 Document Information

**API Version**: 2.0.0  
**Protocol**: Model Context Protocol (MCP) 2025-06-18  
**Transport**: JSON-RPC 2.0 over stdio  
**Last Updated**: August 20, 2025  

---

## 🌟 API Overview

The Enhanced ESTIEM EDA MCP Server provides statistical process control tools with multi-format visualization capabilities. The server automatically detects client capabilities and provides optimal response formats.

### Core Features
- **5 Statistical Tools**: I-Chart, Process Capability, ANOVA, Pareto Analysis, Probability Plots
- **Dual Implementation**: Server-side (NumPy/SciPy) + Browser-compatible (Pyodide) cores
- **HTML Visualizations**: Plotly charts with professional ESTIEM branding
- **Text Summaries**: Human-readable statistical interpretations
- **Unified Format**: Consistent responses across MCP and Web platforms

---

## 🔧 Server Capabilities

### MCP Protocol Methods

#### Initialize
```json
{
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-06-18",
    "capabilities": {},
    "clientInfo": {
      "name": "claude-ai",
      "version": "0.1.0"
    }
  }
}
```

**Response:**
```json
{
  "protocolVersion": "2025-06-18",
  "capabilities": {
    "tools": {"listChanged": true},
    "resources": {"subscribe": false}
  },
  "serverInfo": {
    "name": "estiem-eda",
    "version": "2.0.0",
    "description": "Statistical Process Control tools with enhanced visualization"
  }
}
```

#### List Tools
```json
{
  "method": "tools/list",
  "params": {}
}
```

**Response:**
```json
{
  "tools": [
    {
      "name": "i_chart",
      "description": "Individual control chart for process monitoring and SPC",
      "inputSchema": { /* JSON Schema */ }
    },
    {
      "name": "process_capability", 
      "description": "Process capability analysis with Cp/Cpk indices",
      "inputSchema": { /* JSON Schema */ }
    },
    {
      "name": "anova_boxplot",
      "description": "One-way ANOVA for comparing group means",
      "inputSchema": { /* JSON Schema */ }
    },
    {
      "name": "pareto_analysis",
      "description": "Pareto analysis for vital few identification",
      "inputSchema": { /* JSON Schema */ }
    },
    {
      "name": "probability_plot",
      "description": "Probability plots for distribution assessment",
      "inputSchema": { /* JSON Schema */ }
    }
  ]
}
```

---

## 📊 Statistical Tools API

### 1. I-Chart Analysis

**Tool Name**: `i_chart`  
**Description**: Individual control chart for process monitoring and statistical process control.

#### Input Schema
```json
{
  "type": "object",
  "properties": {
    "data": {
      "type": "array",
      "items": {"type": "number"},
      "description": "Array of numerical measurements for control chart analysis",
      "minItems": 3,
      "maxItems": 10000
    },
    "title": {
      "type": "string",
      "description": "Optional title for the control chart",
      "maxLength": 100
    },
    "specification_limits": {
      "type": "object",
      "properties": {
        "lsl": {"type": "number", "description": "Lower specification limit"},
        "usl": {"type": "number", "description": "Upper specification limit"}
      }
    }
  },
  "required": ["data"]
}
```

#### Enhanced Response Format
```json
{
  "success": true,
  "analysis_type": "i_chart",
  "statistics": {
    "sample_size": 9,
    "mean": 9.922222222222224,
    "sigma_hat": 0.8865248226950357,
    "ucl": 12.581796690307332,
    "lcl": 7.262647754137117,
    "out_of_control_points": 0,
    "western_electric_violations": [
      {
        "rule": 3,
        "description": "4 out of 5 points beyond 1-sigma",
        "points": [0, 1, 2, 3, 4]
      }
    ]
  },
  "out_of_control_indices": [],
  "data_points": [10.0, 11.0, 11.3, 9.0, 8.0, 9.0, 9.5, 10.1, 11.4],
  "interpretation": "Process shows Western Electric rule violations indicating potential instability",
  "visualization_formats": {
    "html_plotly": {
      "content": "<html>...</html>",
      "type": "interactive_html",
      "size_kb": 45
    },
    "artifact_data": {
      "react": {
        "type": "react",
        "language": "jsx",
        "content": "import React from 'react'...",
        "dependencies": ["react", "react-plotly.js"]
      },
      "html": {
        "type": "html",
        "language": "html", 
        "content": "<!DOCTYPE html>...",
        "dependencies": []
      }
    },
    "chart_config": {
      "type": "control_chart",
      "data": [
        {
          "x": [1,2,3,4,5,6,7,8,9],
          "y": [10.0,11.0,11.3,9.0,8.0,9.0,9.5,10.1,11.4],
          "type": "scatter",
          "mode": "lines+markers",
          "name": "Process Data"
        }
      ],
      "layout": {
        "title": "Individual Control Chart",
        "xaxis": {"title": "Sample Number"},
        "yaxis": {"title": "Measurement Value"},
        "shapes": [
          {
            "type": "line",
            "x0": 0, "x1": 1,
            "y0": 9.922, "y1": 9.922,
            "line": {"color": "green", "width": 2}
          }
        ]
      }
    },
    "fallback_text": "I-Chart Analysis:\nMean: 9.92\nUCL: 12.58\nLCL: 7.26\nOut of Control Points: 0\nWestern Electric Violations: 3"
  },
  "rendering_metadata": {
    "primary_format": "artifact_data",
    "fallback_chain": ["html_plotly", "chart_config", "fallback_text"],
    "client_hints": {
      "supports_html": false,
      "supports_artifacts": true,
      "interactive_preferred": true
    },
    "generation_time_ms": 234,
    "total_size_kb": 67
  }
}
```

### 2. Process Capability Analysis

**Tool Name**: `process_capability`  
**Description**: Process capability analysis with Cp, Cpk indices and Six Sigma levels.

#### Input Schema
```json
{
  "type": "object",
  "properties": {
    "data": {
      "type": "array", 
      "items": {"type": "number"},
      "description": "Array of numerical measurements for capability analysis",
      "minItems": 30,
      "maxItems": 10000
    },
    "lsl": {
      "type": "number",
      "description": "Lower Specification Limit"
    },
    "usl": {
      "type": "number", 
      "description": "Upper Specification Limit"
    },
    "target": {
      "type": "number",
      "description": "Target value (optional, defaults to center of spec limits)"
    },
    "title": {
      "type": "string",
      "description": "Optional title for the capability chart",
      "maxLength": 100
    }
  },
  "required": ["data", "lsl", "usl"]
}
```

#### Response Format
```json
{
  "success": true,
  "analysis_type": "process_capability",
  "statistics": {
    "sample_size": 100,
    "mean": 10.05,
    "std_dev": 0.85,
    "cp": 1.96,
    "cpk": 1.89,
    "cpm": 1.84,
    "pp": 1.94,
    "ppk": 1.87,
    "six_sigma_level": 5.67,
    "defect_rate_ppm": 0.32,
    "specification_limits": {
      "lsl": 7.5,
      "usl": 12.5,
      "target": 10.0
    }
  },
  "capability_assessment": {
    "cp_interpretation": "Excellent capability (Cp > 1.67)",
    "cpk_interpretation": "Process well-centered and capable",
    "overall_rating": "Excellent"
  },
  "visualization_formats": {
    "html_plotly": "/* Histogram with normal curve and spec limits */",
    "artifact_data": {
      "react": "/* React histogram component */",
      "html": "/* Standalone HTML histogram */"
    },
    "chart_config": {
      "type": "histogram",
      "data": [/* Histogram data */],
      "layout": {/* Layout config */}
    },
    "fallback_text": "Capability Analysis:\nCp: 1.96 (Excellent)\nCpk: 1.89 (Excellent)\n6σ Level: 5.67"
  }
}
```

### 3. ANOVA with Boxplot

**Tool Name**: `anova_boxplot`  
**Description**: One-way ANOVA for comparing group means with post-hoc analysis.

#### Input Schema
```json
{
  "type": "object",
  "properties": {
    "groups": {
      "type": "object",
      "description": "Dictionary with group names as keys and data arrays as values",
      "additionalProperties": {
        "type": "array",
        "items": {"type": "number"},
        "minItems": 2,
        "maxItems": 1000
      },
      "minProperties": 2,
      "maxProperties": 20
    },
    "alpha": {
      "type": "number",
      "minimum": 0.001,
      "maximum": 0.1,
      "default": 0.05,
      "description": "Significance level (default 0.05)"
    },
    "title": {
      "type": "string", 
      "description": "Optional title for the boxplot",
      "maxLength": 100
    }
  },
  "required": ["groups"]
}
```

#### Response Format
```json
{
  "success": true,
  "analysis_type": "anova_boxplot",
  "anova_results": {
    "f_statistic": 15.67,
    "p_value": 0.0001,
    "degrees_freedom": [2, 27],
    "sum_squares": {
      "between": 234.5,
      "within": 123.8,
      "total": 358.3
    },
    "mean_squares": {
      "between": 117.25,
      "within": 4.59
    },
    "effect_size": {
      "eta_squared": 0.537,
      "omega_squared": 0.498
    }
  },
  "post_hoc_analysis": {
    "method": "Tukey HSD",
    "pairwise_comparisons": [
      {
        "groups": ["Group A", "Group B"],
        "mean_difference": 2.34,
        "p_value": 0.012,
        "significant": true
      }
    ]
  },
  "group_statistics": {
    "Group A": {"mean": 12.3, "std": 2.1, "n": 10},
    "Group B": {"mean": 9.96, "std": 1.8, "n": 10},
    "Group C": {"mean": 11.5, "std": 2.3, "n": 10}
  },
  "interpretation": "Significant differences between groups (p < 0.001)",
  "visualization_formats": {
    "html_plotly": "/* Interactive boxplot with ANOVA results */",
    "artifact_data": {
      "react": "/* React boxplot component */",
      "html": "/* Standalone HTML boxplot */"
    },
    "chart_config": {
      "type": "boxplot",
      "data": [/* Boxplot data for each group */],
      "layout": {/* Layout with ANOVA results annotation */}
    },
    "fallback_text": "ANOVA Results:\nF(2,27) = 15.67, p < 0.001\nSignificant differences detected"
  }
}
```

### 4. Pareto Analysis

**Tool Name**: `pareto_analysis`  
**Description**: Pareto analysis for identifying vital few categories (80/20 rule).

#### Input Schema
```json
{
  "type": "object",
  "properties": {
    "data": {
      "type": "object",
      "description": "Dictionary with categories as keys and values as values",
      "additionalProperties": {
        "type": "number",
        "minimum": 0
      },
      "minProperties": 2,
      "maxProperties": 50
    },
    "threshold": {
      "type": "number",
      "minimum": 0.5,
      "maximum": 0.99,
      "default": 0.8,
      "description": "Threshold for vital few identification (default 0.8 for 80%)"
    },
    "title": {
      "type": "string",
      "description": "Optional title for the Pareto chart",
      "maxLength": 100
    }
  },
  "required": ["data"]
}
```

#### Response Format
```json
{
  "success": true,
  "analysis_type": "pareto_analysis",
  "categories": ["Defect A", "Defect B", "Defect C", "Defect D", "Other"],
  "values": [45, 32, 18, 12, 8],
  "percentages": [39.1, 27.8, 15.7, 10.4, 7.0],
  "cumulative_percentages": [39.1, 66.9, 82.6, 93.0, 100.0],
  "vital_few": {
    "categories": ["Defect A", "Defect B", "Defect C"],
    "count": 3,
    "contribution_percent": 82.6,
    "threshold_used": 80.0
  },
  "statistics": {
    "total_count": 115,
    "gini_coefficient": 0.43,
    "concentration_ratio": 0.826
  },
  "interpretation": "3 categories account for 82.6% of total issues (above 80% threshold)",
  "visualization_formats": {
    "html_plotly": "/* Interactive Pareto chart with bars and cumulative line */",
    "artifact_data": {
      "react": "/* React Pareto component */",
      "html": "/* Standalone HTML Pareto chart */"
    },
    "chart_config": {
      "type": "pareto",
      "data": [
        {
          "x": ["Defect A", "Defect B", "Defect C", "Defect D", "Other"],
          "y": [45, 32, 18, 12, 8],
          "type": "bar",
          "name": "Count"
        },
        {
          "x": ["Defect A", "Defect B", "Defect C", "Defect D", "Other"],
          "y": [39.1, 66.9, 82.6, 93.0, 100.0],
          "type": "scatter",
          "mode": "lines+markers",
          "name": "Cumulative %",
          "yaxis": "y2"
        }
      ],
      "layout": {
        "title": "Pareto Analysis",
        "yaxis": {"title": "Count"},
        "yaxis2": {"title": "Cumulative %", "overlaying": "y", "side": "right"}
      }
    },
    "fallback_text": "Pareto Analysis:\nVital Few: Defect A (39%), Defect B (28%), Defect C (16%)\nTotal: 82.6% of issues"
  }
}
```

### 5. Probability Plot

**Tool Name**: `probability_plot`  
**Description**: Probability plots for distribution assessment with confidence intervals.

#### Input Schema
```json
{
  "type": "object",
  "properties": {
    "data": {
      "type": "array",
      "items": {"type": "number"},
      "description": "Numerical data for probability plot analysis",
      "minItems": 3,
      "maxItems": 10000
    },
    "distribution": {
      "type": "string",
      "enum": ["normal", "lognormal", "weibull"],
      "default": "normal",
      "description": "Distribution type for probability plot"
    },
    "confidence_level": {
      "type": "number",
      "minimum": 0.5,
      "maximum": 0.999,
      "default": 0.95,
      "description": "Confidence level for intervals (default 0.95)"
    },
    "title": {
      "type": "string",
      "description": "Optional title for the probability plot",
      "maxLength": 100
    }
  },
  "required": ["data"]
}
```

#### Response Format
```json
{
  "success": true,
  "analysis_type": "probability_plot",
  "distribution": "normal",
  "sorted_values": [8.0, 9.0, 9.0, 9.5, 10.0, 10.1, 11.0, 11.3, 11.4],
  "theoretical_quantiles": [-1.59, -0.97, -0.59, -0.28, 0.0, 0.28, 0.59, 0.97, 1.59],
  "goodness_of_fit": {
    "correlation_coefficient": 0.9768,
    "r_squared": 0.9542,
    "slope": 1.152,
    "intercept": 9.922,
    "interpretation": "Good fit - data generally follows expected distribution"
  },
  "outliers": {
    "indices": [],
    "count": 0,
    "values": []
  },
  "normality_test": {
    "test": "Anderson-Darling",
    "statistic": 0.247,
    "p_value": 0.5,
    "critical_values": [0.507, 0.578, 0.693, 0.808, 0.961],
    "significance_levels": [15.0, 10.0, 5.0, 2.5, 1.0]
  },
  "confidence_intervals": {
    "upper": [/* Upper CI bounds */],
    "lower": [/* Lower CI bounds */]
  },
  "interpretation": "Good fit to normal distribution (r = 0.9768)",
  "visualization_formats": {
    "html_plotly": "/* Interactive probability plot with confidence bands */",
    "artifact_data": {
      "react": "/* React probability plot component */", 
      "html": "/* Standalone HTML probability plot */"
    },
    "chart_config": {
      "type": "probability_plot",
      "data": [/* Scatter plot data with confidence bands */],
      "layout": {/* Layout with distribution info */}
    },
    "fallback_text": "Probability Plot:\nDistribution: Normal\nCorrelation: 0.977 (Good Fit)\nOutliers: 0"
  }
}
```

---

## 🎨 Visualization Formats

### Format Types

#### 1. HTML Plotly Format
```json
{
  "html_plotly": {
    "content": "<!DOCTYPE html>...",
    "type": "interactive_html",
    "size_kb": 45,
    "features": ["interactive", "responsive", "exportable"],
    "dependencies": ["plotly-2.27.0.min.js"]
  }
}
```

#### 2. Artifact Data Format
```json
{
  "artifact_data": {
    "react": {
      "type": "react",
      "language": "jsx", 
      "content": "import React from 'react'...",
      "dependencies": ["react", "react-plotly.js"],
      "props_schema": {
        "data": "array",
        "layout": "object"
      }
    },
    "html": {
      "type": "html",
      "language": "html",
      "content": "<!DOCTYPE html>...",
      "dependencies": [],
      "standalone": true
    }
  }
}
```

#### 3. Chart Configuration Format
```json
{
  "chart_config": {
    "type": "control_chart",
    "data": [/* Plotly data traces */],
    "layout": {/* Plotly layout object */},
    "config": {
      "responsive": true,
      "displayModeBar": true,
      "toImageButtonOptions": {
        "format": "png",
        "filename": "estiem_chart",
        "height": 500,
        "width": 900
      }
    }
  }
}
```

#### 4. Text Fallback Format
```json
{
  "fallback_text": {
    "summary": "Statistical summary in text format",
    "ascii_chart": "Simple ASCII visualization",
    "interpretation": "Human-readable analysis results",
    "recommendations": "Actionable insights"
  }
}
```

---

## 🔍 Client Detection

### Client Capability Detection

The server automatically detects client capabilities from the MCP request context:

#### Claude Desktop
```json
{
  "client_capabilities": {
    "supports_html": false,
    "supports_artifacts": true,
    "supports_react": true,
    "supports_interactive": true,
    "preferred_format": "artifact_data"
  }
}
```

#### Claude Code
```json
{
  "client_capabilities": {
    "supports_html": true,
    "supports_artifacts": true,
    "supports_interactive": true,
    "preferred_format": "html_plotly"
  }
}
```

#### Generic/Unknown Client
```json
{
  "client_capabilities": {
    "supports_html": false,
    "supports_artifacts": false,
    "preferred_format": "fallback_text"
  }
}
```

---

## 🚨 Error Handling

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "data",
      "issue": "Array must contain at least 3 numeric values",
      "received": "['a', 'b', 'c']"
    }
  },
  "analysis_type": "i_chart",
  "fallback_visualization": {
    "type": "error_message",
    "content": "Unable to generate chart due to invalid input data"
  }
}
```

### Error Codes

| Code | Description | HTTP Equivalent |
|------|-------------|-----------------|
| `VALIDATION_ERROR` | Input validation failed | 400 |
| `CALCULATION_ERROR` | Statistical calculation failed | 422 |
| `VISUALIZATION_ERROR` | Chart generation failed | 500 |
| `RESOURCE_LIMIT_ERROR` | Resource limits exceeded | 413 |
| `TIMEOUT_ERROR` | Processing timeout | 408 |

---

## 📈 Performance Specifications

### Response Time Targets

| Tool | Calculation Time | Visualization Time | Total Time |
|------|------------------|-------------------|------------|
| I-Chart | <100ms | <400ms | <500ms |
| Process Capability | <200ms | <500ms | <700ms |
| ANOVA | <300ms | <600ms | <900ms |
| Pareto Analysis | <150ms | <450ms | <600ms |
| Probability Plot | <250ms | <550ms | <800ms |

### Resource Limits

| Resource | Limit | Enforcement |
|----------|-------|-------------|
| Input Array Size | 10,000 elements | Hard limit |
| Memory Usage | 50MB per request | Soft limit |
| Processing Time | 30 seconds | Hard timeout |
| Response Size | 10MB | Compression applied |

---

## 🔒 Security Considerations

### Input Validation
- **Data Sanitization**: All input data sanitized and validated
- **Type Checking**: Strict type enforcement for all parameters
- **Range Validation**: Numeric values within reasonable ranges
- **Size Limits**: Arrays and objects within specified limits

### Resource Protection
- **Memory Limits**: Maximum memory usage per request
- **Processing Limits**: CPU time and calculation complexity limits
- **Rate Limiting**: Request frequency limitations per client
- **Timeout Protection**: Maximum processing time enforcement

### Data Privacy
- **Local Processing**: All calculations performed locally
- **No Data Persistence**: No user data stored or cached
- **Secure Communication**: TLS encryption for all communications
- **Access Control**: MCP authentication and authorization

---

## 📝 Usage Examples

### Example 1: Basic I-Chart Analysis
```json
{
  "method": "tools/call",
  "params": {
    "name": "i_chart",
    "arguments": {
      "data": [10.0, 11.0, 11.3, 9.0, 8.0, 9.0, 9.5, 10.1, 11.4],
      "title": "Manufacturing Process Control Chart"
    }
  }
}
```

### Example 2: Process Capability with Specifications
```json
{
  "method": "tools/call", 
  "params": {
    "name": "process_capability",
    "arguments": {
      "data": [/* 100 data points */],
      "lsl": 7.5,
      "usl": 12.5,
      "target": 10.0,
      "title": "Process Capability Analysis"
    }
  }
}
```

### Example 3: ANOVA Comparison
```json
{
  "method": "tools/call",
  "params": {
    "name": "anova_boxplot",
    "arguments": {
      "groups": {
        "Method A": [12.1, 11.8, 12.3, 11.9, 12.0],
        "Method B": [10.2, 9.8, 10.1, 9.9, 10.3],
        "Method C": [11.5, 11.2, 11.8, 11.4, 11.6]
      },
      "alpha": 0.05,
      "title": "Manufacturing Method Comparison"
    }
  }
}
```

---

## 🔄 Version Compatibility

### API Versioning
- **Current Version**: 2.0.0
- **Backward Compatibility**: Supports 1.x responses for legacy clients
- **Migration Path**: Automatic detection and conversion
- **Deprecation Policy**: 12-month notice for breaking changes

### Protocol Support
- **MCP Protocol**: 2025-06-18 (primary)
- **Fallback Support**: Earlier MCP versions with limited features
- **JSON-RPC**: 2.0 strict compliance
- **Transport**: stdio (current), HTTP/SSE (future)

---

This API specification serves as the definitive reference for integrating with the Enhanced ESTIEM EDA MCP Server, providing comprehensive statistical analysis with intelligent visualization adaptation.

**Document Version**: 1.0  
**API Version**: 2.0.0  
**Last Updated**: August 20, 2025  
**Next Review**: November 20, 2025