"""Probability Plot tool for distribution assessment and normality testing.

Creates probability plots to assess if data follows specified distributions,
with confidence intervals and outlier detection.
"""

import numpy as np
from typing import Dict, Any
from .base import BaseTool
from ..core.calculations import calculate_probability_plot
from ..core.validation import validate_numeric_data

try:
    from ..utils.visualization import create_probability_plot_chart
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False


class ProbabilityPlotTool(BaseTool):
    """Probability Plot analysis tool.
    
    Assesses data distribution fit with:
    - Normal, lognormal, and Weibull distributions
    - 95% confidence intervals
    - Correlation coefficient analysis
    - Outlier detection
    - Anderson-Darling normality test
    """
    
    def __init__(self):
        """Initialize the Probability Plot tool."""
        self.name = "probability_plot"
        self.description = "Probability plots for distribution assessment with confidence intervals"
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Return the JSON schema for tool inputs."""
        return {
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Numerical data for probability plot analysis",
                    "minItems": 3
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
                }
            },
            "required": ["data"]
        }
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create probability plot and assess distribution fit.
        
        Args:
            params: Dictionary containing data, distribution type, and confidence level.
            
        Returns:
            Dictionary containing probability plot results and goodness of fit analysis.
        """
        try:
            # Validate data
            data_list = params.get("data", [])
            values = validate_numeric_data(data_list, min_points=3)
            
            distribution = params.get("distribution", "normal")
            confidence_level = params.get("confidence_level", 0.95)
            
            # Use core calculation engine
            results = calculate_probability_plot(values, distribution, confidence_level)
            
            # Add visualization if available
            if VISUALIZATION_AVAILABLE:
                try:
                    chart_html = create_probability_plot_chart(
                        results['sorted_values'],
                        results['theoretical_quantiles'],
                        results['goodness_of_fit']['slope'],
                        results['goodness_of_fit']['intercept'],
                        distribution,
                        confidence_level
                    )
                    results['visualization'] = chart_html
                except Exception as e:
                    results['visualization_error'] = str(e)
            
            return results
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'analysis_type': 'probability_plot'
            }