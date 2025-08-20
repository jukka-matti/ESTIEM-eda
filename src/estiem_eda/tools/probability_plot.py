"""Enhanced Probability Plot tool with multi-format visualization.

Creates probability plots to assess if data follows specified distributions,
with confidence intervals and outlier detection with support for multiple
visualization formats.
"""

import numpy as np
from typing import Dict, Any
from .enhanced_base import EnhancedBaseTool, create_estiem_chart_data
from ..core.calculations import calculate_probability_plot
from ..core.validation import validate_numeric_data
from ..utils.visualization_response import ChartData


class ProbabilityPlotTool(EnhancedBaseTool):
    """Enhanced Probability Plot analysis tool with multi-format support.
    
    Assesses data distribution fit with:
    - Normal, lognormal, and Weibull distributions
    - 95% confidence intervals
    - Correlation coefficient analysis
    - Outlier detection
    - Anderson-Darling normality test
    - Multi-format visualization (HTML, React, Config, Text)
    """
    
    @property
    def name(self) -> str:
        """Tool name for MCP registration."""
        return "probability_plot"
    
    @property
    def description(self) -> str:
        """Tool description for MCP listing."""
        return "Probability plots for distribution assessment with confidence intervals"
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Return the JSON schema for tool inputs."""
        return {
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
    
    def calculate_statistics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform Probability Plot statistical calculations.
        
        Args:
            params: Validated input parameters
            
        Returns:
            Statistical analysis results
        """
        # Validate data
        data_list = params.get("data", [])
        values = validate_numeric_data(data_list, min_points=3)
        
        distribution = params.get("distribution", "normal")
        confidence_level = params.get("confidence_level", 0.95)
        
        # Use core calculation engine
        results = calculate_probability_plot(values, distribution, confidence_level)
        
        return results
    
    def create_chart_data(self, results: Dict[str, Any], params: Dict[str, Any]) -> ChartData:
        """Create structured chart data for Probability Plot visualization.
        
        Args:
            results: Statistical analysis results
            params: Original input parameters
            
        Returns:
            Structured chart data for multi-format visualization
        """
        sorted_values = results.get("sorted_values", [])
        theoretical_quantiles = results.get("theoretical_quantiles", [])
        goodness_of_fit = results.get("goodness_of_fit", {})
        confidence_intervals = results.get("confidence_intervals", {})
        outliers = results.get("outliers", {})
        distribution = params.get("distribution", "normal")
        
        slope = goodness_of_fit.get("slope", 1)
        intercept = goodness_of_fit.get("intercept", 0)
        correlation = goodness_of_fit.get("correlation_coefficient", 0)
        
        # Main scatter plot trace
        scatter_trace = {
            "x": theoretical_quantiles,
            "y": sorted_values,
            "type": "scatter",
            "mode": "markers",
            "name": "Data Points",
            "marker": {
                "size": 6,
                "color": "#1f4e79",
                "symbol": "circle"
            },
            "hovertemplate": (
                f"<b>{distribution.title()} Quantile</b><br>" +
                "Theoretical: %{x:.3f}<br>" +
                "Observed: %{y:.3f}<br>" +
                "<extra></extra>"
            )
        }
        
        # Best fit line
        if theoretical_quantiles:
            x_line = np.array([min(theoretical_quantiles), max(theoretical_quantiles)])
            y_line = slope * x_line + intercept
            
            fit_line_trace = {
                "x": x_line.tolist(),
                "y": y_line.tolist(),
                "type": "scatter",
                "mode": "lines",
                "name": f"Best Fit Line (r={correlation:.4f})",
                "line": {"color": "#f8a978", "width": 3},
                "hovertemplate": (
                    f"<b>Best Fit Line</b><br>" +
                    f"Correlation: {correlation:.4f}<br>" +
                    f"Slope: {slope:.3f}<br>" +
                    f"Intercept: {intercept:.3f}<br>" +
                    "<extra></extra>"
                )
            }
        else:
            fit_line_trace = None
        
        plotly_data = [scatter_trace]
        if fit_line_trace:
            plotly_data.append(fit_line_trace)
        
        # Add confidence intervals if available
        upper_ci = confidence_intervals.get("upper", [])
        lower_ci = confidence_intervals.get("lower", [])
        
        if upper_ci and lower_ci and len(upper_ci) == len(theoretical_quantiles):
            # Upper confidence interval
            upper_ci_trace = {
                "x": theoretical_quantiles,
                "y": upper_ci,
                "type": "scatter",
                "mode": "lines",
                "name": f"{params.get('confidence_level', 0.95)*100:.0f}% CI Upper",
                "line": {"color": "#7ba7d1", "width": 1, "dash": "dash"},
                "showlegend": True,
                "hoverinfo": "skip"
            }
            
            # Lower confidence interval
            lower_ci_trace = {
                "x": theoretical_quantiles,
                "y": lower_ci,
                "type": "scatter",
                "mode": "lines",
                "name": f"{params.get('confidence_level', 0.95)*100:.0f}% CI Lower",
                "line": {"color": "#7ba7d1", "width": 1, "dash": "dash"},
                "showlegend": True,
                "hoverinfo": "skip"
            }
            
            plotly_data.extend([upper_ci_trace, lower_ci_trace])
        
        # Highlight outliers if any
        outlier_indices = outliers.get("indices", [])
        outlier_values = outliers.get("values", [])
        
        if outlier_indices and outlier_values:
            outlier_quantiles = [theoretical_quantiles[i] for i in outlier_indices if i < len(theoretical_quantiles)]
            
            outlier_trace = {
                "x": outlier_quantiles,
                "y": outlier_values,
                "type": "scatter",
                "mode": "markers",
                "name": f"Outliers ({len(outlier_values)})",
                "marker": {
                    "size": 8,
                    "color": "red",
                    "symbol": "diamond",
                    "line": {"width": 1, "color": "darkred"}
                },
                "hovertemplate": (
                    "<b>Outlier</b><br>" +
                    "Theoretical: %{x:.3f}<br>" +
                    "Observed: %{y:.3f}<br>" +
                    "<extra></extra>"
                )
            }
            plotly_data.append(outlier_trace)
        
        # Create layout
        title = params.get("title", f"{distribution.title()} Probability Plot")
        
        # Add goodness of fit to title
        r_squared = goodness_of_fit.get("r_squared", 0)
        fit_quality = "Excellent" if r_squared > 0.95 else "Good" if r_squared > 0.90 else "Fair" if r_squared > 0.80 else "Poor"
        fit_text = f"Goodness of Fit: r² = {r_squared:.4f} ({fit_quality})"
        
        # Axis labels based on distribution
        x_label_map = {
            "normal": "Standard Normal Quantiles",
            "lognormal": "Log-Normal Quantiles", 
            "weibull": "Weibull Quantiles"
        }
        
        plotly_layout = {
            "title": {
                "text": f"{title}<br><sub>{fit_text}</sub>",
                "font": {"size": 16}
            },
            "xaxis": {
                "title": x_label_map.get(distribution, "Theoretical Quantiles"),
                "showgrid": True,
                "zeroline": True
            },
            "yaxis": {
                "title": "Observed Values",
                "showgrid": True,
                "zeroline": True
            },
            "hovermode": "closest",
            "legend": {
                "orientation": "v",
                "yanchor": "bottom",
                "y": 0,
                "xanchor": "right",
                "x": 1
            },
            "annotations": []
        }
        
        # Add statistical summary annotation
        normality_test = results.get("normality_test", {})
        test_name = normality_test.get("test", "Anderson-Darling")
        test_stat = normality_test.get("statistic", 0)
        p_value = normality_test.get("p_value", 1)
        
        plotly_layout["annotations"].append({
            "x": 0.02,
            "y": 0.98,
            "xref": "paper",
            "yref": "paper",
            "text": f"<b>{test_name} Test</b><br>" +
                   f"Statistic: {test_stat:.3f}<br>" +
                   f"p-value: {p_value:.4f}<br>" +
                   f"Sample Size: {len(sorted_values)}<br>" +
                   f"Outliers: {len(outlier_values)}",
            "showarrow": False,
            "font": {"size": 12},
            "bgcolor": "rgba(255,255,255,0.8)",
            "bordercolor": "#1f4e79",
            "borderwidth": 1
        })
        
        # Add interpretation
        interpretation = results.get("interpretation", "")
        if interpretation:
            plotly_layout["annotations"].append({
                "x": 0.98,
                "y": 0.02,
                "xref": "paper",
                "yref": "paper",
                "text": f"<b>Interpretation</b><br>{interpretation}",
                "showarrow": False,
                "font": {"size": 11},
                "bgcolor": "rgba(255,255,255,0.8)",
                "bordercolor": "#f8a978",
                "borderwidth": 1,
                "xanchor": "right",
                "yanchor": "bottom"
            })
        
        # Apply ESTIEM styling
        plotly_layout = self._apply_estiem_styling(plotly_layout)
        
        # Create and return structured chart data
        return create_estiem_chart_data(
            tool_name=self.name,
            plotly_data=plotly_data,
            plotly_layout=plotly_layout,
            chart_type="probability_plot"
        )