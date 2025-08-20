"""Simplified Visualization Response System for Reliable Chart Generation.

This module provides a streamlined approach to visualization generation, focusing
on HTML-first delivery with text fallbacks for maximum reliability.
"""

import time
import json
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

from .visualization_response import ChartData, create_chart_data
from .format_generators import PlotlyHTMLGenerator, TextFallbackGenerator


@dataclass
class SimpleVisualizationResult:
    """Simple container for visualization results."""
    
    html_content: str
    text_summary: str
    size_kb: float
    success: bool
    error_message: Optional[str] = None


class SimplifiedVisualizationResponse:
    """Simplified single-format visualization response generator.
    
    This class replaces the complex multi-format system with a reliable
    HTML-first approach that always works across all Claude interfaces.
    """
    
    def __init__(self, analysis_data: Dict[str, Any], analysis_type: str):
        """Initialize the simplified visualization response.
        
        Args:
            analysis_data: Statistical analysis results
            analysis_type: Type of analysis (i_chart, process_capability, etc.)
        """
        self.analysis_data = analysis_data
        self.analysis_type = analysis_type
        self.logger = logging.getLogger(__name__)
        self.generation_start_time = time.time()
    
    def generate_response(self) -> Dict[str, Any]:
        """Generate HTML visualization with text fallback.
        
        Returns:
            Complete response dictionary with HTML visualization and text summary
        """
        try:
            # Create chart data from analysis results
            chart_data = self._create_chart_data()
            
            # Generate HTML visualization (primary format)
            html_result = self._generate_html_visualization(chart_data)
            
            # Generate text summary (fallback format)  
            text_result = self._generate_text_summary(chart_data)
            
            # Calculate generation metrics
            generation_time_ms = (time.time() - self.generation_start_time) * 1000
            
            return {
                "success": True,
                "analysis_type": self.analysis_type,
                **self.analysis_data,  # Include all statistical results
                "html_visualization": html_result.html_content,
                "text_summary": text_result.text_summary,
                "visualization_metadata": {
                    "format": "html_plotly",
                    "size_kb": html_result.size_kb,
                    "generation_time_ms": round(generation_time_ms, 1),
                    "generated_at": time.time(),
                    "generator": "ESTIEM EDA Simplified MCP Server"
                }
            }
            
        except Exception as e:
            self.logger.error(f"Visualization generation failed: {e}")
            return self._create_fallback_response(str(e))
    
    def _create_chart_data(self) -> ChartData:
        """Create structured chart data from analysis results."""
        # Extract visualization data based on analysis type
        if self.analysis_type == "i_chart":
            return self._create_control_chart_data()
        elif self.analysis_type == "process_capability":
            return self._create_capability_chart_data()
        elif self.analysis_type == "anova":
            return self._create_anova_chart_data()
        elif self.analysis_type == "pareto_analysis":
            return self._create_pareto_chart_data()
        elif self.analysis_type == "probability_plot":
            return self._create_probability_chart_data()
        else:
            # Generic chart data
            return create_chart_data(
                chart_type=self.analysis_type,
                plotly_data=[{"x": [1, 2, 3], "y": [1, 2, 3], "type": "scatter"}],
                plotly_layout={"title": f"{self.analysis_type.replace('_', ' ').title()} Analysis"}
            )
    
    def _create_control_chart_data(self) -> ChartData:
        """Create chart data for control charts."""
        data_points = self.analysis_data.get('data_points', [])
        stats = self.analysis_data.get('statistics', {})
        ooc_indices = self.analysis_data.get('out_of_control_indices', [])
        
        # Create data series
        x_values = list(range(1, len(data_points) + 1))
        
        plotly_data = [
            {
                "x": x_values,
                "y": data_points,
                "type": "scatter",
                "mode": "lines+markers",
                "name": "Process Data",
                "line": {"color": "#1f4e79", "width": 2},
                "marker": {
                    "size": 8,
                    "color": ["red" if i in ooc_indices else "#1f4e79" for i in range(len(data_points))]
                }
            },
            {
                "x": [1, len(data_points)],
                "y": [stats.get('mean', 0), stats.get('mean', 0)],
                "type": "scatter",
                "mode": "lines",
                "name": f"Mean ({stats.get('mean', 0):.3f})",
                "line": {"color": "green", "width": 2, "dash": "solid"},
                "showlegend": True
            },
            {
                "x": [1, len(data_points)],
                "y": [stats.get('ucl', 0), stats.get('ucl', 0)],
                "type": "scatter",
                "mode": "lines", 
                "name": f"UCL ({stats.get('ucl', 0):.3f})",
                "line": {"color": "red", "width": 2, "dash": "dash"},
                "showlegend": True
            },
            {
                "x": [1, len(data_points)],
                "y": [stats.get('lcl', 0), stats.get('lcl', 0)],
                "type": "scatter",
                "mode": "lines",
                "name": f"LCL ({stats.get('lcl', 0):.3f})",
                "line": {"color": "red", "width": 2, "dash": "dash"},
                "showlegend": True
            }
        ]
        
        plotly_layout = {
            "title": {
                "text": "Individual Control Chart Analysis",
                "font": {"size": 16, "color": "#1f4e79"},
                "x": 0.5, "xanchor": "center"
            },
            "xaxis": {"title": "Sample Number", "showgrid": True},
            "yaxis": {"title": "Measurement Value", "showgrid": True},
            "hovermode": "x unified",
            "legend": {"orientation": "h", "y": -0.3, "x": 0.5, "xanchor": "center"}
        }
        
        return create_chart_data("control_chart", plotly_data, plotly_layout)
    
    def _create_capability_chart_data(self) -> ChartData:
        """Create chart data for process capability analysis."""
        stats = self.analysis_data.get('statistics', {})
        capability = self.analysis_data.get('capability_indices', {})
        
        # For now, create a simple bar chart of capability indices
        plotly_data = [{
            "x": ["Cp", "Cpk", "Pp", "Ppk"],
            "y": [
                capability.get('cp', 0),
                capability.get('cpk', 0), 
                capability.get('pp', 0),
                capability.get('ppk', 0)
            ],
            "type": "bar",
            "marker": {"color": "#1f4e79"},
            "name": "Capability Indices"
        }]
        
        plotly_layout = {
            "title": {
                "text": "Process Capability Analysis", 
                "font": {"size": 16, "color": "#1f4e79"},
                "x": 0.5, "xanchor": "center"
            },
            "xaxis": {"title": "Capability Index"},
            "yaxis": {"title": "Value"},
            "showlegend": False
        }
        
        return create_chart_data("capability_histogram", plotly_data, plotly_layout)
    
    def _create_anova_chart_data(self) -> ChartData:
        """Create chart data for ANOVA analysis."""
        group_stats = self.analysis_data.get('group_statistics', {})
        
        # Create box plot data
        plotly_data = []
        for group_name, stats in group_stats.items():
            # Simple representation - in real implementation would need actual data
            plotly_data.append({
                "y": [stats.get('mean', 0)],  # Simplified - would need full data
                "type": "box",
                "name": str(group_name),
                "boxmean": True
            })
        
        plotly_layout = {
            "title": {
                "text": "ANOVA Group Comparison",
                "font": {"size": 16, "color": "#1f4e79"},
                "x": 0.5, "xanchor": "center"
            },
            "xaxis": {"title": "Groups"},
            "yaxis": {"title": "Values"}
        }
        
        return create_chart_data("boxplot", plotly_data, plotly_layout)
    
    def _create_pareto_chart_data(self) -> ChartData:
        """Create chart data for Pareto analysis."""
        categories = self.analysis_data.get('categories', [])
        values = self.analysis_data.get('values', [])
        cumulative_percentages = self.analysis_data.get('cumulative_percentages', [])
        
        plotly_data = [
            {
                "x": categories,
                "y": values,
                "type": "bar",
                "name": "Count",
                "marker": {"color": "#1f4e79"},
                "yaxis": "y"
            },
            {
                "x": categories,
                "y": cumulative_percentages,
                "type": "scatter",
                "mode": "lines+markers",
                "name": "Cumulative %",
                "line": {"color": "red", "width": 3},
                "yaxis": "y2"
            }
        ]
        
        plotly_layout = {
            "title": {
                "text": "Pareto Analysis",
                "font": {"size": 16, "color": "#1f4e79"},
                "x": 0.5, "xanchor": "center"
            },
            "xaxis": {"title": "Categories"},
            "yaxis": {"title": "Count", "side": "left"},
            "yaxis2": {"title": "Cumulative %", "side": "right", "overlaying": "y"}
        }
        
        return create_chart_data("pareto", plotly_data, plotly_layout)
    
    def _create_probability_chart_data(self) -> ChartData:
        """Create chart data for probability plots."""
        theoretical_quantiles = self.analysis_data.get('theoretical_quantiles', [])
        sorted_values = self.analysis_data.get('sorted_values', [])
        goodness = self.analysis_data.get('goodness_of_fit', {})
        
        plotly_data = [
            {
                "x": theoretical_quantiles,
                "y": sorted_values,
                "type": "scatter",
                "mode": "markers",
                "name": "Data Points",
                "marker": {"size": 6, "color": "#1f4e79", "symbol": "circle"}
            }
        ]
        
        # Add best fit line if correlation data available
        correlation = goodness.get('correlation_coefficient', 0)
        if correlation > 0:
            slope = goodness.get('slope', 1)
            intercept = goodness.get('intercept', 0)
            
            if theoretical_quantiles:
                fit_x = [min(theoretical_quantiles), max(theoretical_quantiles)]
                fit_y = [intercept + slope * x for x in fit_x]
                
                plotly_data.append({
                    "x": fit_x,
                    "y": fit_y,
                    "type": "scatter",
                    "mode": "lines",
                    "name": f"Best Fit Line (r={correlation:.3f})",
                    "line": {"color": "#f8a978", "width": 3}
                })
        
        plotly_layout = {
            "title": {
                "text": f"Normal Probability Plot Analysis<br><sub>Goodness of Fit: r = {correlation:.4f}</sub>",
                "font": {"size": 16, "color": "#1f4e79"}
            },
            "xaxis": {"title": "Standard Normal Quantiles", "showgrid": True},
            "yaxis": {"title": "Observed Values", "showgrid": True},
            "hovermode": "closest"
        }
        
        return create_chart_data("probability_plot", plotly_data, plotly_layout)
    
    def _generate_html_visualization(self, chart_data: ChartData) -> SimpleVisualizationResult:
        """Generate HTML visualization from chart data."""
        try:
            html_generator = PlotlyHTMLGenerator()
            html_content = html_generator.generate(chart_data)
            
            return SimpleVisualizationResult(
                html_content=html_content.content,
                text_summary="",
                size_kb=html_content.size_kb,
                success=True
            )
            
        except Exception as e:
            self.logger.error(f"HTML generation failed: {e}")
            return SimpleVisualizationResult(
                html_content="",
                text_summary="",
                size_kb=0,
                success=False,
                error_message=str(e)
            )
    
    def _generate_text_summary(self, chart_data: ChartData) -> SimpleVisualizationResult:
        """Generate text summary from analysis data."""
        try:
            text_generator = TextFallbackGenerator()
            text_content = text_generator.generate(chart_data, self.analysis_data)
            
            return SimpleVisualizationResult(
                html_content="",
                text_summary=text_content.content,
                size_kb=text_content.size_kb,
                success=True
            )
            
        except Exception as e:
            self.logger.error(f"Text generation failed: {e}")
            # Create basic text summary as last resort
            basic_summary = self._create_basic_text_summary()
            
            return SimpleVisualizationResult(
                html_content="",
                text_summary=basic_summary,
                size_kb=len(basic_summary.encode('utf-8')) / 1024,
                success=True
            )
    
    def _create_basic_text_summary(self) -> str:
        """Create a basic text summary when generation fails."""
        stats = self.analysis_data.get('statistics', {})
        interpretation = self.analysis_data.get('interpretation', 'Analysis completed successfully.')
        
        summary_parts = [
            f"ESTIEM EDA - {self.analysis_type.replace('_', ' ').title()} Analysis",
            "=" * 50,
            "",
            "Key Statistics:"
        ]
        
        # Add key statistics
        for key, value in list(stats.items())[:5]:  # Show top 5 stats
            formatted_key = key.replace('_', ' ').title()
            if isinstance(value, (int, float)):
                summary_parts.append(f"• {formatted_key}: {value:.4f}")
            else:
                summary_parts.append(f"• {formatted_key}: {value}")
        
        summary_parts.extend([
            "",
            "Interpretation:",
            interpretation,
            "",
            "Generated by ESTIEM EDA Toolkit - Statistical Process Control"
        ])
        
        return "\n".join(summary_parts)
    
    def _create_fallback_response(self, error_message: str) -> Dict[str, Any]:
        """Create fallback response when visualization generation fails completely."""
        generation_time_ms = (time.time() - self.generation_start_time) * 1000
        
        return {
            "success": True,  # Still successful analysis, just no visualization
            "analysis_type": self.analysis_type,
            **self.analysis_data,
            "html_visualization": None,
            "text_summary": self._create_basic_text_summary(),
            "visualization_metadata": {
                "format": "text_only",
                "size_kb": 0,
                "generation_time_ms": round(generation_time_ms, 1),
                "generated_at": time.time(),
                "generator": "ESTIEM EDA Simplified MCP Server",
                "error": f"Visualization generation failed: {error_message}"
            }
        }