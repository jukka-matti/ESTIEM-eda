"""Simplified Individual Control Chart (I-Chart) implementation with reliable visualization.

This module provides statistical process control using Individual control charts,
including control limits calculation, out-of-control point detection, and runs analysis.
"""

import numpy as np
from typing import Dict, Any
from .simplified_base import SimplifiedMCPTool
from ..core.calculations import calculate_i_chart
from ..core.validation import validate_numeric_data


class IChartTool(SimplifiedMCPTool):
    """Simplified Individual Control Chart for process monitoring.
    
    Creates control charts for individual measurements with:
    - Center line (process mean)
    - Upper and Lower Control Limits (UCL, LCL)
    - Out-of-control point detection
    - Western Electric rules checking
    - HTML visualization with text fallback
    """
    
    def __init__(self):
        """Initialize the I-Chart tool."""
        super().__init__(
            name="i_chart",
            description="Individual control chart for process monitoring and SPC"
        )
    
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
                    "description": "Optional title for the analysis",
                    "default": "Individual Control Chart Analysis"
                },
                "specification_limits": {
                    "type": "object",
                    "properties": {
                        "lsl": {"type": "number"},
                        "usl": {"type": "number"}
                    },
                    "description": "Optional specification limits for chart"
                }
            },
            "required": ["data"]
        }
    
    def analyze(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Perform I-Chart statistical analysis.
        
        Args:
            arguments: Validated input parameters
            
        Returns:
            Statistical analysis results
        """
        # Extract validated data
        values = np.array(arguments["data"])
        title = arguments.get("title", "Individual Control Chart")
        
        # Use core calculation engine
        results = calculate_i_chart(values, title)
        
        # Format statistics for consistent output
        if "statistics" in results:
            results["statistics"] = self.format_statistics(results["statistics"])
        
        # Add specification limits if provided
        spec_limits = arguments.get("specification_limits")
        if spec_limits:
            results["specification_limits"] = spec_limits
        
        return results
    
    def create_interpretation(self, stats: Dict[str, Any], **kwargs) -> str:
        """Create interpretation for I-Chart results.
        
        Args:
            stats: Analysis statistics
            **kwargs: Additional context (ooc_indices, data_points, etc.)
            
        Returns:
            Human-readable interpretation string
        """
        mean = stats.get("mean", 0)
        sample_size = stats.get("sample_size", 0)
        ooc_count = stats.get("out_of_control_points", 0)
        
        if ooc_count == 0:
            stability = "appears to be in statistical control"
        else:
            stability = f"has {ooc_count} out-of-control points"
        
        return (f"Process {stability} with a mean of {mean:.4f}. "
                f"Analysis based on {sample_size} data points.")