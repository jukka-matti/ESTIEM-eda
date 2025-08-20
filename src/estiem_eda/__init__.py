"""ESTIEM EDA Toolkit - Exploratory Data Analysis MCP Server"""

__version__ = "0.1.0"
__author__ = "ESTIEM"
__description__ = "MCP server for exploratory data analysis including I-charts, process capability, ANOVA, and Pareto analysis"

# Import quick analysis for easy access
from .quick_analysis import (
    QuickEDA,
    generate_sample_data,
    quick_capability,
    quick_i_chart,
    quick_pareto,
)

__all__ = [
    "mcp_server",
    "tools",
    "utils",
    "QuickEDA",
    "quick_i_chart",
    "quick_capability",
    "quick_pareto",
    "generate_sample_data",
]
