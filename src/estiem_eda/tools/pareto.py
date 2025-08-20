"""Enhanced Pareto Analysis tool with multi-format visualization.

Analyzes categorical data to identify which categories contribute
most significantly to problems or outcomes with support for multiple
visualization formats.
"""

import numpy as np
from typing import Dict, Any
from .enhanced_base import EnhancedBaseTool, create_estiem_chart_data
from ..core.calculations import calculate_pareto
from ..core.validation import validate_pareto_data
from ..utils.visualization_response import ChartData


class ParetoTool(EnhancedBaseTool):
    """Enhanced Pareto Analysis tool with multi-format support.
    
    Identifies vital few categories that contribute most to problems:
    - Pareto chart with cumulative percentages
    - Vital few identification
    - Gini coefficient calculation
    - Category ranking and analysis
    - Multi-format visualization (HTML, React, Config, Text)
    """
    
    @property
    def name(self) -> str:
        """Tool name for MCP registration."""
        return "pareto_analysis"
    
    @property
    def description(self) -> str:
        """Tool description for MCP listing."""
        return "Pareto analysis for identifying vital few categories (80/20 rule)"
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Return the JSON schema for tool inputs."""
        return {
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
    
    def calculate_statistics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform Pareto analysis calculations.
        
        Args:
            params: Validated input parameters
            
        Returns:
            Statistical analysis results
        """
        # Validate data
        data = params.get("data", {})
        validated_data = validate_pareto_data(data)
        
        threshold = params.get("threshold", 0.8)
        
        # Use core calculation engine
        results = calculate_pareto(validated_data, threshold)
        
        return results
    
    def create_chart_data(self, results: Dict[str, Any], params: Dict[str, Any]) -> ChartData:
        """Create structured chart data for Pareto visualization.
        
        Args:
            results: Statistical analysis results
            params: Original input parameters
            
        Returns:
            Structured chart data for multi-format visualization
        """
        categories = results.get("categories", [])
        values = results.get("values", [])
        percentages = results.get("percentages", [])
        cumulative_percentages = results.get("cumulative_percentages", [])
        vital_few = results.get("vital_few", {})
        
        # Bar chart for frequencies
        bar_trace = {
            "x": categories,
            "y": values,
            "type": "bar",
            "name": "Count",
            "yaxis": "y",
            "marker": {
                "color": [
                    "#1f4e79" if cat in vital_few.get("categories", []) 
                    else "#7ba7d1" for cat in categories
                ],
                "opacity": 0.8
            },
            "hovertemplate": (
                "<b>%{x}</b><br>" +
                "Count: %{y}<br>" +
                "Percentage: %{customdata:.1f}%<br>" +
                "<extra></extra>"
            ),
            "customdata": percentages
        }
        
        # Line chart for cumulative percentages
        line_trace = {
            "x": categories,
            "y": cumulative_percentages,
            "type": "scatter",
            "mode": "lines+markers",
            "name": "Cumulative %",
            "yaxis": "y2",
            "line": {"color": "#f8a978", "width": 3},
            "marker": {"size": 8, "color": "#f8a978"},
            "hovertemplate": (
                "<b>%{x}</b><br>" +
                "Cumulative: %{y:.1f}%<br>" +
                "<extra></extra>"
            )
        }
        
        plotly_data = [bar_trace, line_trace]
        
        # Add threshold line
        threshold = params.get("threshold", 0.8) * 100
        
        threshold_trace = {
            "x": [categories[0], categories[-1]] if categories else [0, 1],
            "y": [threshold, threshold],
            "type": "scatter",
            "mode": "lines",
            "name": f"Threshold ({threshold:.0f}%)",
            "yaxis": "y2",
            "line": {"color": "red", "width": 2, "dash": "dash"},
            "showlegend": True,
            "hovertemplate": f"Threshold: {threshold:.0f}%<extra></extra>"
        }
        plotly_data.append(threshold_trace)
        
        # Create layout
        title = params.get("title", "Pareto Analysis")
        
        # Add vital few summary to title
        vital_count = vital_few.get("count", 0)
        vital_percent = vital_few.get("contribution_percent", 0)
        pareto_text = f"Vital Few: {vital_count} categories ({vital_percent:.1f}%)"
        
        plotly_layout = {
            "title": {
                "text": f"{title}<br><sub>{pareto_text}</sub>",
                "font": {"size": 16}
            },
            "xaxis": {
                "title": "Categories",
                "showgrid": False,
                "zeroline": False,
                "tickangle": -45 if len(categories) > 8 else 0
            },
            "yaxis": {
                "title": "Count",
                "side": "left",
                "showgrid": True,
                "zeroline": False
            },
            "yaxis2": {
                "title": "Cumulative Percentage (%)",
                "side": "right",
                "overlaying": "y",
                "showgrid": False,
                "zeroline": False,
                "range": [0, 105]
            },
            "hovermode": "x unified",
            "legend": {
                "orientation": "h",
                "yanchor": "bottom",
                "y": -0.3,
                "xanchor": "center",
                "x": 0.5
            },
            "annotations": [
                {
                    "x": 0.02,
                    "y": 0.98,
                    "xref": "paper",
                    "yref": "paper",
                    "text": f"<b>Pareto Analysis</b><br>" +
                           f"Total Categories: {len(categories)}<br>" +
                           f"Vital Few: {vital_count}<br>" +
                           f"Total Count: {results.get('statistics', {}).get('total_count', 0)}<br>" +
                           f"Gini Coefficient: {results.get('statistics', {}).get('gini_coefficient', 0):.3f}",
                    "showarrow": False,
                    "font": {"size": 12},
                    "bgcolor": "rgba(255,255,255,0.8)",
                    "bordercolor": "#1f4e79",
                    "borderwidth": 1
                }
            ]
        }
        
        # Highlight vital few categories in annotation
        if vital_few.get("categories"):
            vital_list = ", ".join(vital_few["categories"][:3])  # Show first 3
            if len(vital_few["categories"]) > 3:
                vital_list += f" (+{len(vital_few['categories'])-3} more)"
            
            plotly_layout["annotations"].append({
                "x": 0.98,
                "y": 0.98,
                "xref": "paper",
                "yref": "paper",
                "text": f"<b>Vital Few Categories</b><br>{vital_list}",
                "showarrow": False,
                "font": {"size": 11},
                "bgcolor": "rgba(255,255,255,0.8)",
                "bordercolor": "#f8a978",
                "borderwidth": 1,
                "xanchor": "right"
            })
        
        # Apply ESTIEM styling
        plotly_layout = self._apply_estiem_styling(plotly_layout)
        
        # Create and return structured chart data
        return create_estiem_chart_data(
            tool_name=self.name,
            plotly_data=plotly_data,
            plotly_layout=plotly_layout,
            chart_type="pareto"
        )