"""Simplified Analysis of Variance (ANOVA) tool.

Performs one-way ANOVA to test for significant differences between group means,
including post-hoc Tukey HSD analysis when significant differences are found.
"""

from typing import Any

from ..core.calculations import calculate_anova
from ..core.validation import validate_groups_data
from .simplified_base import SimplifiedMCPTool


class ANOVATool(SimplifiedMCPTool):
    """Simplified One-way Analysis of Variance tool.

    Tests for significant differences between group means:
    - F-test for overall significance
    - Tukey HSD post-hoc comparisons
    - Effect size analysis
    - Group statistics summary
    """

    def __init__(self):
        """Initialize the ANOVA tool."""
        super().__init__(
            name="anova_boxplot",
            description="One-way ANOVA for comparing group means with post-hoc analysis",
        )

    def get_input_schema(self) -> dict[str, Any]:
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
                        "minItems": 2,
                        "maxItems": 1000,
                    },
                    "minProperties": 2,
                    "maxProperties": 20,
                },
                "alpha": {
                    "type": "number",
                    "minimum": 0.001,
                    "maximum": 0.1,
                    "default": 0.05,
                    "description": "Significance level (default 0.05)",
                },
                "title": {
                    "type": "string",
                    "description": "Optional title for the analysis",
                    "maxLength": 100,
                    "default": "ANOVA Analysis",
                },
            },
            "required": ["groups"],
        }

    def validate_arguments(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Validate ANOVA-specific arguments."""
        if not isinstance(arguments, dict):
            raise ValueError("Arguments must be a dictionary")

        validated = {}

        # Validate groups dictionary
        if "groups" in arguments:
            groups = arguments["groups"]
            if not isinstance(groups, dict):
                raise ValueError("Groups must be a dictionary with group names as keys")

            # Validate each group
            for group_name, group_data in groups.items():
                if not isinstance(group_data, list):
                    raise ValueError(f"Group '{group_name}' must be a list of numbers")

                # Validate numeric data
                for item in group_data:
                    try:
                        float(item)
                    except (ValueError, TypeError):
                        raise ValueError(f"Group '{group_name}' contains non-numeric data")

            validated["groups"] = groups

        # Validate other parameters
        for param in ["alpha", "title"]:
            if param in arguments:
                validated[param] = arguments[param]

        return validated

    def analyze(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Perform ANOVA statistical analysis.

        Args:
            arguments: Validated input parameters

        Returns:
            Statistical analysis results
        """
        # Extract parameters
        groups_data = arguments.get("groups", {})
        alpha = arguments.get("alpha", 0.05)
        arguments.get("title", "ANOVA Analysis")

        # Validate groups data
        validated_groups = validate_groups_data(groups_data)

        # Use core calculation engine
        results = calculate_anova(validated_groups, alpha)

        # Format statistics for consistent output
        for key in ["group_statistics", "anova_results", "effect_size"]:
            if key in results:
                results[key] = self.format_statistics(results[key])

        return results
