"""Simplified Probability Plot tool.

Creates probability plots to assess if data follows specified distributions,
with confidence intervals and outlier detection.
"""

from typing import Any

from ..core.calculations import calculate_probability_plot
from ..core.validation import validate_numeric_data
from .simplified_base import SimplifiedMCPTool


class ProbabilityPlotTool(SimplifiedMCPTool):
    """Simplified Probability Plot analysis tool.

    Assesses data distribution fit with:
    - Normal, lognormal, and Weibull distributions
    - 95% confidence intervals
    - Correlation coefficient analysis
    - Outlier detection
    - Anderson-Darling normality test
    """

    def __init__(self):
        """Initialize the Probability Plot tool."""
        super().__init__(
            name="probability_plot",
            description="Probability plots for distribution assessment with confidence intervals",
        )

    def get_input_schema(self) -> dict[str, Any]:
        """Return the JSON schema for tool inputs."""
        return {
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Numerical data for probability plot analysis",
                    "minItems": 3,
                    "maxItems": 10000,
                },
                "distribution": {
                    "type": "string",
                    "enum": ["normal", "lognormal", "weibull"],
                    "default": "normal",
                    "description": "Distribution type for probability plot",
                },
                "confidence_level": {
                    "type": "number",
                    "minimum": 0.5,
                    "maximum": 0.999,
                    "default": 0.95,
                    "description": "Confidence level for intervals (default 0.95)",
                },
                "title": {
                    "type": "string",
                    "description": "Optional title for the analysis",
                    "maxLength": 100,
                    "default": "Probability Plot Analysis",
                },
            },
            "required": ["data"],
        }

    def analyze(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Perform Probability Plot analysis.

        Args:
            arguments: Validated input parameters

        Returns:
            Statistical analysis results
        """
        # Extract parameters
        data_list = arguments.get("data", [])
        distribution = arguments.get("distribution", "normal")
        confidence_level = arguments.get("confidence_level", 0.95)
        arguments.get("title", "Probability Plot Analysis")

        # Validate data
        values = validate_numeric_data(data_list, min_points=3)

        # Use core calculation engine
        results = calculate_probability_plot(values, distribution, confidence_level)

        # Format statistics for consistent output
        for key in ["goodness_of_fit", "confidence_intervals", "outliers", "normality_test"]:
            if key in results:
                results[key] = self.format_statistics(results[key])

        return results
