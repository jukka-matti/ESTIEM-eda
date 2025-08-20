"""Enhanced Individual Control Chart (I-Chart) implementation with multi-format visualization.

This module provides statistical process control using Individual control charts,
including control limits calculation, out-of-control point detection, and runs analysis
with support for multiple visualization formats.
"""

import numpy as np
from typing import Dict, Any, List
from .enhanced_base import EnhancedBaseTool, create_estiem_chart_data
from ..core.calculations import calculate_i_chart
from ..core.validation import validate_numeric_data
from ..utils.visualization_response import ChartData


class IChartTool(EnhancedBaseTool):
    """Enhanced Individual Control Chart for process monitoring with multi-format support.
    
    Creates control charts for individual measurements with:
    - Center line (process mean)
    - Upper and Lower Control Limits (UCL, LCL)
    - Out-of-control point detection
    - Western Electric rules checking
    - Multi-format visualization (HTML, React, Config, Text)
    """
    
    @property
    def name(self) -> str:
        """Tool name for MCP registration."""
        return "i_chart"
    
    @property
    def description(self) -> str:
        """Tool description for MCP listing."""
        return "Individual control chart for process monitoring and SPC"
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Return the JSON schema for tool inputs."""
        return {
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
                    },
                    "description": "Optional specification limits for chart"
                }
            },
            "required": ["data"]
        }
    
    def calculate_statistics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform I-Chart statistical calculations.
        
        Args:
            params: Validated input parameters
            
        Returns:
            Statistical analysis results
        """
        # Validate and clean data using core validation
        data_list = params.get("data", [])
        values = validate_numeric_data(data_list, min_points=3)
        
        title = params.get("title", "Individual Control Chart")
        
        # Use core calculation engine
        results = calculate_i_chart(values, title)
        
        # Add specification limits if provided
        spec_limits = params.get("specification_limits")
        if spec_limits:
            results["specification_limits"] = spec_limits
        
        return results
    
    def create_chart_data(self, results: Dict[str, Any], params: Dict[str, Any]) -> ChartData:
        """Create structured chart data for I-Chart visualization.
        
        Args:
            results: Statistical analysis results
            params: Original input parameters
            
        Returns:
            Structured chart data for multi-format visualization
        """
        statistics = results.get("statistics", {})
        data_points = results.get("data_points", [])
        ooc_indices = results.get("out_of_control_indices", [])
        
        # Create sample numbers for x-axis
        sample_numbers = list(range(1, len(data_points) + 1))
        
        # Main data trace - process data
        data_trace = {
            "x": sample_numbers,
            "y": data_points,
            "type": "scatter",
            "mode": "lines+markers",
            "name": "Process Data",
            "line": {"color": "#1f4e79", "width": 2},
            "marker": {
                "size": 8,
                "color": ["red" if i in ooc_indices else "#1f4e79" for i in range(len(data_points))]
            }
        }
        
        # Center line (mean)
        center_line_trace = {
            "x": [1, len(data_points)],
            "y": [statistics.get("mean", 0)] * 2,
            "type": "scatter",
            "mode": "lines",
            "name": f"Mean ({statistics.get('mean', 0):.3f})",
            "line": {"color": "green", "width": 2, "dash": "solid"},
            "showlegend": True
        }
        
        # Upper Control Limit
        ucl_trace = {
            "x": [1, len(data_points)],
            "y": [statistics.get("ucl", 0)] * 2,
            "type": "scatter",
            "mode": "lines",
            "name": f"UCL ({statistics.get('ucl', 0):.3f})",
            "line": {"color": "red", "width": 2, "dash": "dash"},
            "showlegend": True
        }
        
        # Lower Control Limit
        lcl_trace = {
            "x": [1, len(data_points)],
            "y": [statistics.get("lcl", 0)] * 2,
            "type": "scatter",
            "mode": "lines",
            "name": f"LCL ({statistics.get('lcl', 0):.3f})",
            "line": {"color": "red", "width": 2, "dash": "dash"},
            "showlegend": True
        }
        
        plotly_data = [data_trace, center_line_trace, ucl_trace, lcl_trace]
        
        # Add specification limits if provided
        spec_limits = results.get("specification_limits")
        if spec_limits:
            if "lsl" in spec_limits:
                lsl_trace = {
                    "x": [1, len(data_points)],
                    "y": [spec_limits["lsl"]] * 2,
                    "type": "scatter",
                    "mode": "lines",
                    "name": f"LSL ({spec_limits['lsl']:.3f})",
                    "line": {"color": "orange", "width": 2, "dash": "dot"},
                    "showlegend": True
                }
                plotly_data.append(lsl_trace)
            
            if "usl" in spec_limits:
                usl_trace = {
                    "x": [1, len(data_points)],
                    "y": [spec_limits["usl"]] * 2,
                    "type": "scatter",
                    "mode": "lines",
                    "name": f"USL ({spec_limits['usl']:.3f})",
                    "line": {"color": "orange", "width": 2, "dash": "dot"},
                    "showlegend": True
                }
                plotly_data.append(usl_trace)
        
        # Create layout
        title = params.get("title", "Individual Control Chart")
        plotly_layout = {
            "title": title,
            "xaxis": {
                "title": "Sample Number",
                "showgrid": True,
                "zeroline": False
            },
            "yaxis": {
                "title": "Measurement Value",
                "showgrid": True,
                "zeroline": False
            },
            "hovermode": "x unified",
            "legend": {
                "orientation": "h",
                "yanchor": "bottom",
                "y": -0.3,
                "xanchor": "center",
                "x": 0.5
            }
        }
        
        # Apply ESTIEM styling
        plotly_layout = self._apply_estiem_styling(plotly_layout)
        
        # Create and return structured chart data
        return create_estiem_chart_data(
            tool_name=self.name,
            plotly_data=plotly_data,
            plotly_layout=plotly_layout,
            chart_type="control_chart"
        )