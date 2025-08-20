"""Simplified Pareto Analysis tool.

Analyzes categorical data to identify which categories contribute
most significantly to problems or outcomes.
"""

from typing import Any

from ..core.calculations import calculate_pareto
from ..core.validation import validate_pareto_data
from .simplified_base import SimplifiedMCPTool


class ParetoTool(SimplifiedMCPTool):
    """Simplified Pareto Analysis tool.

    Identifies vital few categories that contribute most to problems:
    - Pareto chart with cumulative percentages
    - Vital few identification
    - Gini coefficient calculation
    - Category ranking and analysis
    """

    def __init__(self):
        """Initialize the Pareto Analysis tool."""
        super().__init__(
            name="pareto_analysis",
            description="Pareto analysis for identifying vital few categories (80/20 rule)",
        )

    def get_input_schema(self) -> dict[str, Any]:
        """Return the JSON schema for tool inputs."""
        return {
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "description": "Dictionary with categories as keys and values as values",
                    "additionalProperties": {"type": "number", "minimum": 0},
                    "minProperties": 2,
                    "maxProperties": 50,
                },
                "threshold": {
                    "type": "number",
                    "minimum": 0.5,
                    "maximum": 0.99,
                    "default": 0.8,
                    "description": "Threshold for vital few identification (default 0.8 for 80%)",
                },
                "title": {
                    "type": "string",
                    "description": "Optional title for the analysis",
                    "maxLength": 100,
                    "default": "Pareto Analysis",
                },
            },
            "required": ["data"],
        }

    def validate_arguments(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Validate Pareto-specific arguments."""
        if not isinstance(arguments, dict):
            raise ValueError("Arguments must be a dictionary")

        validated = {}

        # Validate data dictionary
        if "data" in arguments:
            data = arguments["data"]
            if not isinstance(data, dict):
                raise ValueError("Data must be a dictionary with category names as keys")

            # Validate each category value
            for key, value in data.items():
                try:
                    float(value)
                except (ValueError, TypeError):
                    raise ValueError(f"Category '{key}' must have a numeric value")

            validated["data"] = data

        # Validate other parameters
        for param in ["threshold", "title"]:
            if param in arguments:
                validated[param] = arguments[param]

        return validated

    def analyze(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Perform Pareto analysis.

        Args:
            arguments: Validated input parameters

        Returns:
            Statistical analysis results
        """
        # Extract parameters
        data = arguments.get("data", {})
        threshold = arguments.get("threshold", 0.8)
        arguments.get("title", "Pareto Analysis")

        # Validate data
        validated_data = validate_pareto_data(data)

        # Use core calculation engine
        results = calculate_pareto(validated_data, threshold)

        # Format statistics for consistent output
        for key in ["statistics", "vital_few"]:
            if key in results:
                results[key] = self.format_statistics(results[key])

        return results
