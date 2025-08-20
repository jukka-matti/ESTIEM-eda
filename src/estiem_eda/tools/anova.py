"""Analysis of Variance (ANOVA) tool for comparing group means.

Performs one-way ANOVA to test for significant differences between group means,
including post-hoc Tukey HSD analysis when significant differences are found.
"""

import numpy as np
from typing import Dict, Any
from .base import BaseTool
from ..core.calculations import calculate_anova
from ..core.validation import validate_groups_data

try:
    from ..utils.visualization import create_boxplot
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False


class ANOVATool(BaseTool):
    """One-way Analysis of Variance tool.
    
    Tests for significant differences between group means:
    - F-test for overall significance
    - Tukey HSD post-hoc comparisons
    - Effect size analysis
    - Group statistics summary
    """
    
    def __init__(self):
        """Initialize the ANOVA tool."""
        self.name = "anova"
        self.description = "One-way ANOVA for comparing group means with post-hoc analysis"
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Return the JSON schema for tool inputs."""
        return {
            "type": "object",
            "properties": {
                "groups": {
                    "type": "object",
                    "description": "Dictionary with group names as keys and data arrays as values",
                    "additionalProperties": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2
                    },
                    "minProperties": 2
                },
                "alpha": {
                    "type": "number",
                    "minimum": 0.001,
                    "maximum": 0.1,
                    "default": 0.05,
                    "description": "Significance level (default 0.05)"
                }
            },
            "required": ["groups"]
        }
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform one-way ANOVA analysis.
        
        Args:
            params: Dictionary containing groups data and optional significance level.
            
        Returns:
            Dictionary containing ANOVA results, group statistics, and post-hoc analysis.
        """
        try:
            # Validate groups data
            groups_data = params.get("groups", {})
            validated_groups = validate_groups_data(groups_data)
            
            alpha = params.get("alpha", 0.05)
            
            # Use core calculation engine
            results = calculate_anova(validated_groups, alpha)
            
            # Add visualization if available
            if VISUALIZATION_AVAILABLE:
                try:
                    chart_html = create_boxplot(
                        data_groups=list(validated_groups.values()),
                        group_names=list(validated_groups.keys()),
                        title="ANOVA Group Comparison"
                    )
                    results['visualization'] = chart_html
                except Exception as e:
                    results['visualization_error'] = str(e)
            
            return results
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'analysis_type': 'anova'
            }