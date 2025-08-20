"""
ESTIEM EDA Core - Pure NumPy/SciPy Statistical Calculations
Shared calculation engine for all platforms (MCP, Web, CLI, Colab)
"""

from .calculations import (
    calculate_i_chart,
    calculate_process_capability, 
    calculate_anova,
    calculate_pareto,
    calculate_probability_plot
)

from .validation import (
    validate_numeric_data,
    validate_groups_data,
    validate_pareto_data
)

__all__ = [
    "calculate_i_chart",
    "calculate_process_capability", 
    "calculate_anova",
    "calculate_pareto", 
    "calculate_probability_plot",
    "validate_numeric_data",
    "validate_groups_data",
    "validate_pareto_data"
]