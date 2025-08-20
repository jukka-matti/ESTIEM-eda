"""Individual Control Chart (I-Chart) implementation for process monitoring.

This module provides statistical process control using Individual control charts,
including control limits calculation, out-of-control point detection, and runs analysis.
"""

import numpy as np
from typing import Dict, Any, List
from .base import BaseTool
from ..core.calculations import calculate_i_chart
from ..core.validation import validate_numeric_data

try:
    from ..utils.visualization import create_control_chart
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False


class IChartTool(BaseTool):
    """Individual Control Chart for process monitoring.
    
    Creates control charts for individual measurements with:
    - Center line (process mean)
    - Upper and Lower Control Limits (UCL, LCL)
    - Out-of-control point detection
    - Western Electric rules checking
    """
    
    def __init__(self):
        """Initialize the I-Chart tool."""
        self.name = "i_chart"
        self.description = "Individual control chart for process monitoring and SPC"
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Return the JSON schema for tool inputs."""
        return {
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Array of numerical measurements for control chart analysis",
                    "minItems": 3
                },
                "title": {
                    "type": "string",
                    "description": "Optional title for the control chart"
                }
            },
            "required": ["data"]
        }
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate control chart statistics and create analysis.
        
        Args:
            params: Dictionary containing 'data' array and optional parameters.
            
        Returns:
            Dictionary containing statistics, analysis results, and interpretation.
            
        Raises:
            ValueError: If input data is invalid or insufficient.
        """
        try:
            # Validate and clean data using core validation
            data_list = params.get("data", [])
            values = validate_numeric_data(data_list, min_points=3)
            
            title = params.get("title", "Individual Control Chart")
            
            # Use core calculation engine
            results = calculate_i_chart(values, title)
            
            # Add visualization if available
            if VISUALIZATION_AVAILABLE:
                try:
                    chart_html = create_control_chart(
                        values,
                        results['statistics']['mean'],
                        results['statistics']['ucl'], 
                        results['statistics']['lcl'],
                        title
                    )
                    results['visualization'] = chart_html
                except Exception as e:
                    results['visualization_error'] = str(e)
            
            return results
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'analysis_type': 'i_chart'
            }