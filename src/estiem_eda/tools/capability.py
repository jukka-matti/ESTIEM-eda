"""Process Capability Analysis tool for Six Sigma and quality management.

Calculates process capability indices (Cp, Cpk, Pp, Ppk) and performance metrics
for assessing process performance against specification limits.
"""

import numpy as np
from typing import Dict, Any
from .base import BaseTool
from ..core.calculations import calculate_process_capability
from ..core.validation import validate_numeric_data, validate_capability_params

try:
    from ..utils.visualization import create_capability_histogram
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False


class CapabilityTool(BaseTool):
    """Process capability analysis tool.
    
    Calculates capability indices and defect rates:
    - Cp/Cpk: Process capability indices
    - Pp/Ppk: Process performance indices
    - Six Sigma level and PPM defect rates
    - Process centering analysis
    """
    
    def __init__(self):
        """Initialize the Process Capability tool."""
        self.name = "capability"
        self.description = "Process capability analysis with Cp/Cpk indices and Six Sigma levels"
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Return the JSON schema for tool inputs."""
        return {
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Array of numerical measurements for capability analysis",
                    "minItems": 30
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
                }
            },
            "required": ["data", "lsl", "usl"]
        }
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate process capability indices and analysis.
        
        Args:
            params: Dictionary containing data, lsl, usl, and optional target.
            
        Returns:
            Dictionary containing capability indices, defect analysis, and interpretation.
        """
        try:
            # Validate data
            data_list = params.get("data", [])
            values = validate_numeric_data(data_list, min_points=30)
            
            # Validate specification limits
            lsl = params.get("lsl")
            usl = params.get("usl") 
            target = params.get("target")
            
            lsl, usl, target = validate_capability_params(lsl, usl, target)
            title = params.get("title", "Process Capability Analysis")
            
            # Use core calculation engine
            results = calculate_process_capability(values, lsl, usl, target)
            
            # Add visualization if available
            if VISUALIZATION_AVAILABLE:
                try:
                    chart_html = create_capability_histogram(
                        data=values,
                        lsl=lsl, 
                        usl=usl, 
                        target=target,
                        mean=results['statistics']['mean'],
                        std=results['statistics']['std_dev'],
                        title=title
                    )
                    results['visualization'] = chart_html
                except Exception as e:
                    results['visualization_error'] = str(e)
            
            return results
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'analysis_type': 'capability'
            }