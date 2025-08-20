"""Pareto Analysis tool for identifying the vital few (80/20 rule).

Analyzes categorical data to identify which categories contribute
most significantly to problems or outcomes.
"""

import numpy as np
from typing import Dict, Any
from .base import BaseTool
from ..core.calculations import calculate_pareto
from ..core.validation import validate_pareto_data

try:
    from ..utils.visualization import create_pareto_chart
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False


class ParetoTool(BaseTool):
    """Pareto Analysis tool for the 80/20 rule.
    
    Identifies vital few categories that contribute most to problems:
    - Pareto chart with cumulative percentages
    - Vital few identification
    - Gini coefficient calculation
    - Category ranking and analysis
    """
    
    def __init__(self):
        """Initialize the Pareto Analysis tool."""
        self.name = "pareto"
        self.description = "Pareto analysis for identifying vital few categories (80/20 rule)"
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Return the JSON schema for tool inputs."""
        return {
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "description": "Dictionary with categories as keys and values as values",
                    "additionalProperties": {"type": "number", "minimum": 0}
                },
                "threshold": {
                    "type": "number",
                    "minimum": 0.5,
                    "maximum": 0.99,
                    "default": 0.8,
                    "description": "Threshold for vital few identification (default 0.8 for 80%)"
                }
            },
            "required": ["data"]
        }
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform Pareto analysis.
        
        Args:
            params: Dictionary containing categorical data and optional threshold.
            
        Returns:
            Dictionary containing Pareto analysis results and vital few identification.
        """
        try:
            # Validate data
            data = params.get("data", {})
            validated_data = validate_pareto_data(data)
            
            threshold = params.get("threshold", 0.8)
            
            # Use core calculation engine
            results = calculate_pareto(validated_data, threshold)
            
            # Add visualization if available
            if VISUALIZATION_AVAILABLE:
                try:
                    chart_html = create_pareto_chart(
                        results['categories'],
                        results['values'],
                        results['cumulative_percentages']
                    )
                    results['visualization'] = chart_html
                except Exception as e:
                    results['visualization_error'] = str(e)
            
            return results
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'analysis_type': 'pareto'
            }