"""Enhanced Analysis of Variance (ANOVA) tool with multi-format visualization.

Performs one-way ANOVA to test for significant differences between group means,
including post-hoc Tukey HSD analysis when significant differences are found
with support for multiple visualization formats.
"""

import numpy as np
from typing import Dict, Any, List
from .enhanced_base import EnhancedBaseTool, create_estiem_chart_data
from ..core.calculations import calculate_anova
from ..core.validation import validate_groups_data
from ..utils.visualization_response import ChartData


class ANOVATool(EnhancedBaseTool):
    """Enhanced One-way Analysis of Variance tool with multi-format support.
    
    Tests for significant differences between group means:
    - F-test for overall significance
    - Tukey HSD post-hoc comparisons
    - Effect size analysis
    - Group statistics summary
    - Multi-format visualization (HTML, React, Config, Text)
    """
    
    @property
    def name(self) -> str:
        """Tool name for MCP registration."""
        return "anova_boxplot"
    
    @property
    def description(self) -> str:
        """Tool description for MCP listing."""
        return "One-way ANOVA for comparing group means with post-hoc analysis"
    
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
                        "minItems": 2,
                        "maxItems": 1000
                    },
                    "minProperties": 2,
                    "maxProperties": 20
                },
                "alpha": {
                    "type": "number",
                    "minimum": 0.001,
                    "maximum": 0.1,
                    "default": 0.05,
                    "description": "Significance level (default 0.05)"
                },
                "title": {
                    "type": "string",
                    "description": "Optional title for the boxplot",
                    "maxLength": 100
                }
            },
            "required": ["groups"]
        }
    
    def calculate_statistics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform ANOVA statistical calculations.
        
        Args:
            params: Validated input parameters
            
        Returns:
            Statistical analysis results
        """
        # Validate groups data
        groups_data = params.get("groups", {})
        validated_groups = validate_groups_data(groups_data)
        
        alpha = params.get("alpha", 0.05)
        
        # Use core calculation engine
        results = calculate_anova(validated_groups, alpha)
        
        return results
    
    def create_chart_data(self, results: Dict[str, Any], params: Dict[str, Any]) -> ChartData:
        """Create structured chart data for ANOVA boxplot visualization.
        
        Args:
            results: Statistical analysis results
            params: Original input parameters
            
        Returns:
            Structured chart data for multi-format visualization
        """
        groups_data = params.get("groups", {})
        group_stats = results.get("group_statistics", {})
        anova_results = results.get("anova_results", {})
        
        plotly_data = []
        
        # Create boxplot traces for each group
        for group_name, group_values in groups_data.items():
            # Determine box color based on significance
            group_color = "#7ba7d1"  # Default ESTIEM secondary color
            
            boxplot_trace = {
                "y": group_values,
                "type": "box",
                "name": group_name,
                "boxpoints": "outliers",
                "marker": {"color": group_color},
                "line": {"color": "#1f4e79"},
                "fillcolor": group_color,
                "opacity": 0.7,
                "hovertemplate": (
                    f"<b>{group_name}</b><br>" +
                    "Value: %{y}<br>" +
                    f"Mean: {group_stats.get(group_name, {}).get('mean', 0):.3f}<br>" +
                    f"SD: {group_stats.get(group_name, {}).get('std', 0):.3f}<br>" +
                    f"n: {group_stats.get(group_name, {}).get('n', 0)}" +
                    "<extra></extra>"
                )
            }
            plotly_data.append(boxplot_trace)
        
        # Create layout
        title = params.get("title", "ANOVA Group Comparison")
        
        # Add ANOVA results to title
        f_stat = anova_results.get("f_statistic", 0)
        p_value = anova_results.get("p_value", 1)
        df_between = anova_results.get("degrees_freedom", [0, 0])[0]
        df_within = anova_results.get("degrees_freedom", [0, 0])[1]
        
        significance_text = "Significant" if p_value < 0.05 else "Not Significant"
        anova_text = f"F({df_between},{df_within}) = {f_stat:.3f}, p = {p_value:.4f} ({significance_text})"
        
        plotly_layout = {
            "title": {
                "text": f"{title}<br><sub>{anova_text}</sub>",
                "font": {"size": 16}
            },
            "xaxis": {
                "title": "Groups",
                "showgrid": False,
                "zeroline": False
            },
            "yaxis": {
                "title": "Values",
                "showgrid": True,
                "zeroline": False
            },
            "hovermode": "closest",
            "showlegend": False,  # Box plots don't need legend typically
            "annotations": []
        }
        
        # Add statistical annotation
        eta_squared = anova_results.get("effect_size", {}).get("eta_squared", 0)
        
        plotly_layout["annotations"].append({
            "x": 0.02,
            "y": 0.98,
            "xref": "paper",
            "yref": "paper",
            "text": f"<b>ANOVA Results</b><br>" +
                   f"F-statistic: {f_stat:.3f}<br>" +
                   f"p-value: {p_value:.4f}<br>" +
                   f"Effect Size (η²): {eta_squared:.3f}<br>" +
                   f"Groups: {len(groups_data)}",
            "showarrow": False,
            "font": {"size": 12},
            "bgcolor": "rgba(255,255,255,0.8)",
            "bordercolor": "#1f4e79",
            "borderwidth": 1
        })
        
        # Add post-hoc results if available
        post_hoc = results.get("post_hoc_analysis", {})
        if post_hoc and "pairwise_comparisons" in post_hoc:
            significant_pairs = [
                comp for comp in post_hoc["pairwise_comparisons"] 
                if comp.get("significant", False)
            ]
            
            if significant_pairs:
                sig_text = f"Significant pairs ({post_hoc.get('method', 'Tukey HSD')}):<br>"
                for comp in significant_pairs[:5]:  # Show first 5
                    groups = comp.get("groups", ["", ""])
                    p_val = comp.get("p_value", 1)
                    sig_text += f"{groups[0]} vs {groups[1]} (p={p_val:.3f})<br>"
                
                plotly_layout["annotations"].append({
                    "x": 0.98,
                    "y": 0.98,
                    "xref": "paper",
                    "yref": "paper",
                    "text": sig_text.rstrip("<br>"),
                    "showarrow": False,
                    "font": {"size": 10},
                    "bgcolor": "rgba(255,255,255,0.8)",
                    "bordercolor": "#f8a978",
                    "borderwidth": 1,
                    "xanchor": "right"
                })
        
        # Apply ESTIEM styling
        plotly_layout = self._apply_estiem_styling(plotly_layout)
        
        # Create and return structured chart data
        return create_estiem_chart_data(
            tool_name=self.name,
            plotly_data=plotly_data,
            plotly_layout=plotly_layout,
            chart_type="boxplot"
        )