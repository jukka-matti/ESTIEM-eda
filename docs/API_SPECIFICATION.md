# 📡 ESTIEM EDA Streamlined MCP Server API Specification

## 📋 Document Information

**API Version**: 3.0.0  
**Protocol**: Model Context Protocol (MCP) 2025-06-18  
**Transport**: JSON-RPC 2.0 over stdio  
**Last Updated**: August 20, 2025  

---

## 🌟 API Overview

The Streamlined ESTIEM EDA MCP Server provides professional Six Sigma tools with focused, comprehensive analysis capabilities. The server delivers optimal response formats for statistical process control workflows.

### Core Features
- **3 Core Tools**: Process Analysis, ANOVA, Pareto Analysis
- **Professional Workflow**: Unified process assessment combining stability, capability, and distribution analysis
- **HTML Visualizations**: Plotly charts with professional ESTIEM branding
- **Comprehensive Interpretations**: Human-readable statistical insights with actionable recommendations
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
      "name": "process_analysis",
      "description": "Comprehensive process assessment combining stability, capability, and distribution analysis",
      "inputSchema": { /* JSON Schema */ }
    },
    {
      "name": "anova_boxplot",
      "description": "One-way ANOVA for comparing group means with statistical significance testing",
      "inputSchema": { /* JSON Schema */ }
    },
    {
      "name": "pareto_analysis",
      "description": "Pareto analysis for vital few identification using 80/20 principle",
      "inputSchema": { /* JSON Schema */ }
    }
  ]
}
```

---

## 📊 Core Analysis Tools API

### 1. Process Analysis

**Tool Name**: `process_analysis`  
**Description**: Comprehensive process assessment combining stability (I-Chart), capability (Cp/Cpk), and distribution analysis in a unified Six Sigma workflow.

#### Input Schema
```json
{
  "type": "object",
  "properties": {
    "data": {
      "type": "array",
      "items": {"type": "number"},
      "description": "Array of measurement values for comprehensive process analysis",
      "minItems": 10,
      "maxItems": 10000
    },
    "title": {
      "type": "string",
      "description": "Optional title for the analysis",
      "default": "Process Analysis"
    },
    "specification_limits": {
      "type": "object",
      "properties": {
        "lsl": {"type": "number", "description": "Lower specification limit"},
        "usl": {"type": "number", "description": "Upper specification limit"},
        "target": {"type": "number", "description": "Target value (optional, defaults to midpoint of LSL/USL)"}
      },
      "description": "Specification limits for capability analysis",
      "anyOf": [
        {"required": ["lsl", "usl"]},
        {"required": ["lsl"]},
        {"required": ["usl"]}
      ]
    },
    "distribution": {
      "type": "string",
      "enum": ["normal", "lognormal", "exponential", "weibull"],
      "description": "Distribution type for probability plot analysis",
      "default": "normal"
    },
    "confidence_level": {
      "type": "number",
      "minimum": 0.8,
      "maximum": 0.99,
      "description": "Confidence level for statistical tests",
      "default": 0.95
    }
  },
  "required": ["data"]
}
```

#### Response Format
```json
{
  "success": true,
  "analysis_type": "process_analysis",
  "process_summary": {
    "sample_size": 50,
    "measurement_range": {
      "minimum": 9.7,
      "maximum": 10.3,
      "mean": 10.012,
      "std_dev": 0.156
    }
  },
  "stability_analysis": {
    "type": "i_chart",
    "statistics": {
      "mean": 10.012,
      "sigma_hat": 0.156,
      "ucl": 10.480,
      "lcl": 9.544,
      "out_of_control_points": 0
    },
    "out_of_control_indices": [],
    "control_status": "in_control"
  },
  "capability_analysis": {
    "type": "capability",
    "statistics": {
      "mean": 10.012,
      "std_dev": 0.156,
      "process_spread": 0.936
    },
    "capability_indices": {
      "cp": 1.068,
      "cpk": 1.051,
      "cpm": 1.045,
      "pp": 1.064,
      "ppk": 1.047
    },
    "defect_analysis": {
      "ppm_total": 45.2,
      "sigma_level": 4.8
    },
    "specification_limits": {
      "lsl": 9.5,
      "usl": 10.5,
      "target": 10.0
    }
  },
  "distribution_analysis": {
    "type": "probability_plot",
    "distribution": "normal",
    "statistics": {
      "mean": 10.012,
      "std_dev": 0.156
    },
    "goodness_of_fit": {
      "test_statistic": 0.142,
      "p_value": 0.876,
      "is_normal": true
    },
    "theoretical_quantiles": [/* array */],
    "sorted_values": [/* array */]
  },
  "overall_assessment": {
    "stability_status": "in_control",
    "capability_status": "capable",
    "distribution_status": "fits_assumed",
    "overall_status": "excellent",
    "recommendations": [
      "Continue monitoring with control charts",
      "Maintain current performance levels"
    ]
  },
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

### 2. ANOVA with Boxplot

**Tool Name**: `anova_boxplot`  
**Description**: One-way ANOVA for comparing group means with statistical significance testing.

#### Input Schema
```json
{
  "type": "object",
  "properties": {
    "groups": {
      "type": "object",
      "description": "Groups with their corresponding data values",
      "patternProperties": {
        "^[a-zA-Z0-9_-]+$": {
          "type": "array",
          "items": {"type": "number"},
          "minItems": 3,
          "description": "Array of numeric values for this group"
        }
      },
      "minProperties": 2,
      "maxProperties": 20
    },
    "alpha": {
      "type": "number",
      "minimum": 0.001,
      "maximum": 0.2,
      "description": "Significance level for ANOVA test",
      "default": 0.05
    },
    "title": {
      "type": "string",
      "description": "Optional title for the analysis",
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
    "f_statistic": 12.45,
    "p_value": 0.0023,
    "degrees_of_freedom": {
      "between_groups": 2,
      "within_groups": 27,
      "total": 29
    },
    "significant": true,
    "alpha": 0.05
  },
  "group_statistics": {
    "Group_A": {
      "count": 10,
      "mean": 9.85,
      "std_dev": 0.42,
      "variance": 0.18
    },
    "Group_B": {
      "count": 10,
      "mean": 10.45,
      "std_dev": 0.38,
      "variance": 0.14
    },
    "Group_C": {
      "count": 10,
      "mean": 10.12,
      "std_dev": 0.35,
      "variance": 0.12
    }
  },
  "post_hoc_analysis": {
    "method": "tukey_hsd",
    "pairwise_comparisons": [
      {
        "groups": ["Group_A", "Group_B"],
        "mean_difference": -0.60,
        "p_value": 0.0015,
        "significant": true
      }
    ]
  },
  "interpretation": "Significant difference found between groups (F=12.45, p=0.0023). Post-hoc analysis shows Group_A differs significantly from Group_B.",
  "visualization_formats": {
    "html_plotly": "/* Boxplot with ANOVA results */",
    "fallback_text": "ANOVA Results: F=12.45, p=0.0023 (Significant)\nGroup means: A=9.85, B=10.45, C=10.12"
  }
}
```

### 3. Pareto Analysis

**Tool Name**: `pareto_analysis`  
**Description**: Pareto analysis for vital few identification using the 80/20 principle.

#### Input Schema
```json
{
  "type": "object",
  "properties": {
    "data": {
      "type": "object",
      "description": "Categories with their corresponding values",
      "patternProperties": {
        "^.+$": {
          "type": "number",
          "minimum": 0,
          "description": "Numeric value for this category"
        }
      },
      "minProperties": 2,
      "maxProperties": 50
    },
    "threshold": {
      "type": "number",
      "minimum": 0.5,
      "maximum": 0.99,
      "description": "Cumulative percentage threshold for vital few identification",
      "default": 0.8
    },
    "title": {
      "type": "string",
      "description": "Optional title for the analysis",
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
  "categories": [
    {
      "name": "Surface Defects",
      "value": 450,
      "percentage": 45.0,
      "cumulative_percentage": 45.0
    },
    {
      "name": "Dimensional Issues", 
      "value": 320,
      "percentage": 32.0,
      "cumulative_percentage": 77.0
    },
    {
      "name": "Assembly Problems",
      "value": 180,
      "percentage": 18.0,
      "cumulative_percentage": 95.0
    },
    {
      "name": "Material Defects",
      "value": 50,
      "percentage": 5.0,
      "cumulative_percentage": 100.0
    }
  ],
  "vital_few": {
    "threshold": 0.8,
    "count": 2,
    "categories": ["Surface Defects", "Dimensional Issues"],
    "contribution_percent": 77.0,
    "total_value": 770
  },
  "summary": {
    "total_value": 1000,
    "total_categories": 4,
    "vital_few_ratio": "50% of categories contribute to 77% of problems"
  },
  "interpretation": "2 categories (Surface Defects, Dimensional Issues) represent 77% of total defects, following the 80/20 principle.",
  "visualization_formats": {
    "html_plotly": "/* Pareto chart with bars and cumulative line */",
    "fallback_text": "Pareto Analysis:\n1. Surface Defects: 450 (45%)\n2. Dimensional Issues: 320 (32%)\nVital Few: 2 categories = 77% of problems"
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
- **Current Version**: 3.0.0 (Streamlined 3-Tool Architecture)
- **Architecture**: Clean break from legacy versions - no backward compatibility
- **Focus**: Professional Six Sigma workflow with 3 core tools only
- **Design**: Modern, streamlined API designed for optimal user experience

### Protocol Support
- **MCP Protocol**: 2025-06-18 (latest specification)
- **JSON-RPC**: 2.0 strict compliance
- **Transport**: stdio (optimized for Claude Desktop integration)
- **Response Format**: Modern HTML visualization with embedded Plotly charts

---

This API specification serves as the definitive reference for integrating with the Enhanced ESTIEM EDA MCP Server, providing comprehensive statistical analysis with intelligent visualization adaptation.

**Document Version**: 3.0 (Streamlined Architecture)  
**API Version**: 3.0.0  
**Last Updated**: August 20, 2025  
**Next Review**: November 20, 2025