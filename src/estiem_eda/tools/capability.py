"""Enhanced Process Capability Analysis tool with multi-format visualization.

Calculates process capability indices (Cp, Cpk, Pp, Ppk) and performance metrics
for assessing process performance against specification limits with support for
multiple visualization formats.
"""

import numpy as np
from typing import Dict, Any
from .enhanced_base import EnhancedBaseTool, create_estiem_chart_data
from ..core.calculations import calculate_process_capability
from ..core.validation import validate_numeric_data, validate_capability_params
from ..utils.visualization_response import ChartData


class CapabilityTool(EnhancedBaseTool):
    """Enhanced Process capability analysis tool with multi-format support.
    
    Calculates capability indices and defect rates:
    - Cp/Cpk: Process capability indices
    - Pp/Ppk: Process performance indices
    - Six Sigma level and PPM defect rates
    - Process centering analysis
    - Multi-format visualization (HTML, React, Config, Text)
    """
    
    @property
    def name(self) -> str:
        """Tool name for MCP registration."""
        return "process_capability"
    
    @property
    def description(self) -> str:
        """Tool description for MCP listing."""
        return "Process capability analysis with Cp/Cpk indices and Six Sigma levels"
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Return the JSON schema for tool inputs."""
        return {
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
    
    def calculate_statistics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform Process Capability statistical calculations.
        
        Args:
            params: Validated input parameters
            
        Returns:
            Statistical analysis results
        """
        # Validate data
        data_list = params.get("data", [])
        values = validate_numeric_data(data_list, min_points=30)
        
        # Validate specification limits
        lsl = params.get("lsl")
        usl = params.get("usl") 
        target = params.get("target")
        
        lsl, usl, target = validate_capability_params(lsl, usl, target)
        
        # Use core calculation engine
        results = calculate_process_capability(values, lsl, usl, target)
        
        return results
    
    def create_chart_data(self, results: Dict[str, Any], params: Dict[str, Any]) -> ChartData:
        """Create structured chart data for Process Capability visualization.
        
        Args:
            results: Statistical analysis results
            params: Original input parameters
            
        Returns:
            Structured chart data for multi-format visualization
        """
        statistics = results.get("statistics", {})
        data_points = results.get("data_points", [])
        
        lsl = params.get("lsl")
        usl = params.get("usl")
        target = params.get("target")
        
        mean = statistics.get("mean", 0)
        std_dev = statistics.get("std_dev", 1)
        
        # Create histogram data
        hist_data, bin_edges = np.histogram(data_points, bins=30, density=True)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        
        # Main histogram trace
        histogram_trace = {
            "x": bin_centers,
            "y": hist_data,
            "type": "bar",
            "name": "Data Distribution",
            "marker": {"color": "#7ba7d1", "opacity": 0.7},
            "hovertemplate": "Bin: %{x:.3f}<br>Density: %{y:.4f}<extra></extra>"
        }
        
        # Normal curve overlay
        x_range = np.linspace(min(data_points), max(data_points), 200)
        normal_curve = (1 / (std_dev * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_range - mean) / std_dev) ** 2)
        
        normal_trace = {
            "x": x_range.tolist(),
            "y": normal_curve.tolist(),
            "type": "scatter",
            "mode": "lines",
            "name": "Normal Curve",
            "line": {"color": "#1f4e79", "width": 3},
            "hovertemplate": "Value: %{x:.3f}<br>Density: %{y:.4f}<extra></extra>"
        }
        
        plotly_data = [histogram_trace, normal_trace]
        
        # Add specification limits
        y_max = max(max(hist_data), max(normal_curve)) * 1.1
        
        if lsl is not None:
            lsl_trace = {
                "x": [lsl, lsl],
                "y": [0, y_max],
                "type": "scatter",
                "mode": "lines",
                "name": f"LSL ({lsl:.3f})",
                "line": {"color": "red", "width": 2, "dash": "dash"},
                "showlegend": True,
                "hovertemplate": f"LSL: {lsl:.3f}<extra></extra>"
            }
            plotly_data.append(lsl_trace)
        
        if usl is not None:
            usl_trace = {
                "x": [usl, usl],
                "y": [0, y_max],
                "type": "scatter",
                "mode": "lines",
                "name": f"USL ({usl:.3f})",
                "line": {"color": "red", "width": 2, "dash": "dash"},
                "showlegend": True,
                "hovertemplate": f"USL: {usl:.3f}<extra></extra>"
            }
            plotly_data.append(usl_trace)
        
        if target is not None:
            target_trace = {
                "x": [target, target],
                "y": [0, y_max],
                "type": "scatter",
                "mode": "lines",
                "name": f"Target ({target:.3f})",
                "line": {"color": "green", "width": 2, "dash": "dot"},
                "showlegend": True,
                "hovertemplate": f"Target: {target:.3f}<extra></extra>"
            }
            plotly_data.append(target_trace)
        
        # Process mean line
        mean_trace = {
            "x": [mean, mean],
            "y": [0, y_max],
            "type": "scatter",
            "mode": "lines",
            "name": f"Mean ({mean:.3f})",
            "line": {"color": "#f8a978", "width": 2, "dash": "solid"},
            "showlegend": True,
            "hovertemplate": f"Mean: {mean:.3f}<extra></extra>"
        }
        plotly_data.append(mean_trace)
        
        # Create layout
        title = params.get("title", "Process Capability Analysis")
        
        # Add capability indices to title
        cp = statistics.get("cp", 0)
        cpk = statistics.get("cpk", 0)
        six_sigma = statistics.get("six_sigma_level", 0)
        
        capability_text = f"Cp: {cp:.3f} | Cpk: {cpk:.3f} | 6σ Level: {six_sigma:.2f}"
        
        plotly_layout = {
            "title": {
                "text": f"{title}<br><sub>{capability_text}</sub>",
                "font": {"size": 16}
            },
            "xaxis": {
                "title": "Measurement Value",
                "showgrid": True,
                "zeroline": False
            },
            "yaxis": {
                "title": "Density",
                "showgrid": True,
                "zeroline": False
            },
            "hovermode": "closest",
            "legend": {
                "orientation": "v",
                "yanchor": "top",
                "y": 1,
                "xanchor": "left",
                "x": 1.02
            },
            "annotations": [
                {
                    "x": 0.02,
                    "y": 0.98,
                    "xref": "paper",
                    "yref": "paper",
                    "text": f"<b>Capability Assessment</b><br>" +
                           f"Sample Size: {statistics.get('sample_size', 'N/A')}<br>" +
                           f"Six Sigma Level: {six_sigma:.2f}<br>" +
                           f"Defect Rate: {statistics.get('defect_rate_ppm', 0):.1f} PPM",
                    "showarrow": False,
                    "font": {"size": 12},
                    "bgcolor": "rgba(255,255,255,0.8)",
                    "bordercolor": "#1f4e79",
                    "borderwidth": 1
                }
            ]
        }
        
        # Apply ESTIEM styling
        plotly_layout = self._apply_estiem_styling(plotly_layout)
        
        # Create and return structured chart data
        return create_estiem_chart_data(
            tool_name=self.name,
            plotly_data=plotly_data,
            plotly_layout=plotly_layout,
            chart_type="histogram"
        )