"""Simplified Process Capability Analysis implementation.

This module provides process capability analysis including Cp, Cpk, Pp, Ppk calculations
and Six Sigma level assessment.
"""

import numpy as np
from typing import Dict, Any
from .simplified_base import SimplifiedMCPTool
from ..core.calculations import calculate_process_capability
from ..core.validation import validate_numeric_data


class CapabilityTool(SimplifiedMCPTool):
    """Simplified Process Capability Analysis for quality assessment."""
    
    def __init__(self):
        """Initialize the Process Capability tool."""
        super().__init__(
            name="process_capability",
            description="Process capability analysis with Cp, Cpk, and Six Sigma metrics"
        )
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Return the JSON schema for tool inputs."""
        return {
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Array of process measurements",
                    "minItems": 10
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
                    "description": "Target value (optional)"
                },
                "title": {
                    "type": "string",
                    "description": "Optional title for the analysis",
                    "default": "Process Capability Analysis"
                }
            },
            "required": ["data", "lsl", "usl"]
        }
    
    def analyze(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Perform Process Capability analysis.
        
        Args:
            arguments: Validated input parameters
            
        Returns:
            Statistical analysis results
        """
        # Extract parameters
        values = np.array(arguments["data"])
        lsl = arguments["lsl"]
        usl = arguments["usl"]
        target = arguments.get("target")
        title = arguments.get("title", "Process Capability Analysis")
        
        # Validate specification limits
        if lsl >= usl:
            raise ValueError("Lower Specification Limit must be less than Upper Specification Limit")
        
        # Use core calculation engine
        results = calculate_process_capability(values, lsl, usl, target)
        
        # Format statistics for consistent output
        for key in ["statistics", "capability_indices", "defect_analysis"]:
            if key in results:
                results[key] = self.format_statistics(results[key])
        
        return results