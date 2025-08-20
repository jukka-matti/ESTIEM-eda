"""Pareto Analysis for identifying the vital few causes (80/20 rule).

This module implements Pareto analysis to identify which factors contribute
most significantly to problems or outcomes, supporting root cause analysis
and priority setting in quality improvement.
"""

import numpy as np
from typing import Dict, Any, List, Tuple, Union
from .base import BaseTool

try:
    from ..utils.visualization import create_pareto_chart
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False


class ParetoTool(BaseTool):
    """Pareto Analysis tool for 80/20 rule identification.
    
    Analyzes categorical data to identify the "vital few" categories that
    contribute to the majority of problems or effects, following the
    Pareto principle (80/20 rule).
    """
    
    def __init__(self):
        """Initialize the Pareto Analysis tool."""
        self.name = "pareto_analysis"
        self.description = "Pareto analysis to identify vital few causes using 80/20 rule"
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Return JSON schema for Pareto analysis inputs.
        
        Returns:
            JSON schema defining category data and analysis options.
        """
        return {
            "type": "object",
            "properties": {
                "data": {
                    "oneOf": [
                        {
                            "type": "object",
                            "description": "Dictionary with categories as keys and counts/values as values",
                            "patternProperties": {
                                ".*": {"type": "number", "minimum": 0}
                            },
                            "minProperties": 2
                        },
                        {
                            "type": "array",
                            "description": "Array of objects with 'category' and 'value' fields",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "category": {"type": "string"},
                                    "value": {"type": "number", "minimum": 0}
                                },
                                "required": ["category", "value"]
                            },
                            "minItems": 2
                        }
                    ]
                },
                "threshold": {
                    "type": "number",
                    "default": 80,
                    "minimum": 50,
                    "maximum": 95,
                    "description": "Percentage threshold for vital few identification (typically 80)"
                },
                "title": {
                    "type": "string",
                    "description": "Title for the Pareto chart"
                },
                "unit": {
                    "type": "string",
                    "description": "Unit of measurement for values (e.g., 'defects', 'costs', 'incidents')"
                }
            },
            "required": ["data"]
        }
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform Pareto analysis on categorical data.
        
        Args:
            params: Dictionary containing category data and analysis options.
            
        Returns:
            Dictionary with Pareto analysis results, vital few identification, and recommendations.
            
        Raises:
            ValueError: If data format is invalid or contains no positive values.
        """
        # Validate inputs
        self.validate_inputs(params, ["data"])
        
        raw_data = params["data"]
        threshold = params.get("threshold", 80)
        title = params.get("title", "Pareto Analysis")
        unit = params.get("unit", "count")
        
        # Parse and validate data
        categories, values = self._parse_data(raw_data)
        
        # Sort data by value (descending)
        sorted_data = self._sort_data(categories, values)
        
        # Calculate cumulative statistics
        cumulative_stats = self._calculate_cumulative_stats(sorted_data, threshold)
        
        # Identify vital few
        vital_few = self._identify_vital_few(sorted_data, cumulative_stats, threshold)
        
        # Generate insights and recommendations
        insights = self._generate_insights(sorted_data, cumulative_stats, vital_few, threshold)
        
        # Prepare chart data
        chart_data = self._prepare_chart_data(sorted_data, cumulative_stats, title, unit)
        
        # Create visualization
        chart_html = None
        if VISUALIZATION_AVAILABLE:
            try:
                chart_html = create_pareto_chart(
                    categories=categories,
                    values=values,
                    cumulative_pct=[item["cumulative_percentage"] for item in sorted_data],
                    vital_few=vital_few["categories"],
                    threshold=threshold,
                    title=title,
                    unit=unit
                )
            except Exception as e:
                chart_html = f"Visualization error: {str(e)}"
        else:
            chart_html = "Visualization not available - install plotly>=5.0.0"
        
        return {
            "summary": {
                "total_categories": len(categories),
                "total_value": cumulative_stats["total_value"],
                "vital_few_count": len(vital_few["categories"]),
                "vital_few_percentage": vital_few["percentage"],
                "threshold_used": threshold,
                "unit": unit
            },
            "sorted_data": sorted_data,
            "cumulative_analysis": cumulative_stats,
            "vital_few": vital_few,
            "insights": insights,
            "chart_data": chart_data,
            "interpretation": self._generate_interpretation(sorted_data, vital_few, insights, threshold),
            "chart_html": chart_html
        }
    
    def _parse_data(self, raw_data: Union[Dict[str, float], List[Dict[str, Any]]]) -> Tuple[List[str], List[float]]:
        """Parse input data into categories and values.
        
        Args:
            raw_data: Raw data in dictionary or list format.
            
        Returns:
            Tuple of (categories, values) lists.
            
        Raises:
            ValueError: If data format is invalid.
        """
        if isinstance(raw_data, dict):
            categories = list(raw_data.keys())
            values = [float(raw_data[cat]) for cat in categories]
        elif isinstance(raw_data, list):
            categories = []
            values = []
            for item in raw_data:
                if not isinstance(item, dict) or "category" not in item or "value" not in item:
                    raise ValueError("List format requires objects with 'category' and 'value' fields")
                categories.append(str(item["category"]))
                values.append(float(item["value"]))
        else:
            raise ValueError("Data must be either a dictionary or a list of objects")
        
        if len(categories) < 2:
            raise ValueError("At least 2 categories are required for Pareto analysis")
        
        # Check for duplicate categories
        if len(set(categories)) != len(categories):
            raise ValueError("Duplicate categories found - each category must be unique")
        
        # Validate values
        if any(v < 0 for v in values):
            raise ValueError("All values must be non-negative")
        
        if sum(values) == 0:
            raise ValueError("At least one category must have a positive value")
        
        return categories, values
    
    def _sort_data(self, categories: List[str], values: List[float]) -> List[Dict[str, Any]]:
        """Sort data by values in descending order.
        
        Args:
            categories: List of category names.
            values: List of corresponding values.
            
        Returns:
            List of dictionaries with sorted category data.
        """
        # Combine and sort by value (descending)
        combined = list(zip(categories, values))
        combined.sort(key=lambda x: x[1], reverse=True)
        
        sorted_data = []
        for i, (category, value) in enumerate(combined):
            sorted_data.append({
                "rank": i + 1,
                "category": category,
                "value": float(value),
                "percentage": 0.0,  # Will be calculated in cumulative stats
                "cumulative_value": 0.0,  # Will be calculated in cumulative stats
                "cumulative_percentage": 0.0  # Will be calculated in cumulative stats
            })
        
        return sorted_data
    
    def _calculate_cumulative_stats(self, sorted_data: List[Dict], threshold: float) -> Dict[str, Any]:
        """Calculate cumulative statistics for Pareto analysis.
        
        Args:
            sorted_data: Sorted list of category data.
            threshold: Threshold percentage for vital few.
            
        Returns:
            Dictionary with cumulative statistics.
        """
        total_value = sum(item["value"] for item in sorted_data)
        cumulative_value = 0
        
        # Calculate percentages and cumulative values
        for item in sorted_data:
            item["percentage"] = (item["value"] / total_value) * 100
            cumulative_value += item["value"]
            item["cumulative_value"] = cumulative_value
            item["cumulative_percentage"] = (cumulative_value / total_value) * 100
        
        # Find threshold crossing point
        threshold_index = None
        for i, item in enumerate(sorted_data):
            if item["cumulative_percentage"] >= threshold:
                threshold_index = i
                break
        
        return {
            "total_value": float(total_value),
            "threshold_index": threshold_index,
            "threshold_percentage": threshold,
            "categories_at_threshold": threshold_index + 1 if threshold_index is not None else len(sorted_data)
        }
    
    def _identify_vital_few(self, sorted_data: List[Dict], cumulative_stats: Dict, 
                           threshold: float) -> Dict[str, Any]:
        """Identify the vital few categories based on threshold.
        
        Args:
            sorted_data: Sorted category data with cumulative statistics.
            cumulative_stats: Cumulative analysis results.
            threshold: Threshold percentage.
            
        Returns:
            Dictionary with vital few analysis.
        """
        threshold_index = cumulative_stats["threshold_index"]
        
        if threshold_index is not None:
            vital_categories = sorted_data[:threshold_index + 1]
        else:
            # If no category crosses threshold, take all categories
            vital_categories = sorted_data
        
        vital_few_value = sum(cat["value"] for cat in vital_categories)
        vital_few_percentage = (vital_few_value / cumulative_stats["total_value"]) * 100
        
        # Trivial many (remaining categories)
        trivial_categories = sorted_data[len(vital_categories):] if len(vital_categories) < len(sorted_data) else []
        trivial_value = sum(cat["value"] for cat in trivial_categories)
        trivial_percentage = (trivial_value / cumulative_stats["total_value"]) * 100
        
        return {
            "categories": [cat["category"] for cat in vital_categories],
            "count": len(vital_categories),
            "value": float(vital_few_value),
            "percentage": float(vital_few_percentage),
            "trivial_many": {
                "categories": [cat["category"] for cat in trivial_categories],
                "count": len(trivial_categories),
                "value": float(trivial_value),
                "percentage": float(trivial_percentage)
            }
        }
    
    def _generate_insights(self, sorted_data: List[Dict], cumulative_stats: Dict,
                          vital_few: Dict, threshold: float) -> Dict[str, Any]:
        """Generate insights and analysis from Pareto data.
        
        Args:
            sorted_data: Sorted category data.
            cumulative_stats: Cumulative statistics.
            vital_few: Vital few analysis.
            threshold: Threshold percentage.
            
        Returns:
            Dictionary with insights and recommendations.
        """
        total_categories = len(sorted_data)
        vital_count = vital_few["count"]
        
        # Key insights
        insights = {
            "pareto_ratio": f"{vital_count}/{total_categories}",
            "pareto_percentage": f"{(vital_count/total_categories)*100:.1f}%",
            "concentration": f"{vital_few['percentage']:.1f}% of impact from {(vital_count/total_categories)*100:.1f}% of categories"
        }
        
        # Top contributor analysis
        if sorted_data:
            top_contributor = sorted_data[0]
            insights["top_contributor"] = {
                "category": top_contributor["category"],
                "value": top_contributor["value"],
                "percentage": top_contributor["percentage"],
                "impact": f"Single largest contributor at {top_contributor['percentage']:.1f}%"
            }
        
        # Distribution analysis
        if len(sorted_data) >= 3:
            top_3_percentage = sum(item["percentage"] for item in sorted_data[:3])
            insights["top_3_impact"] = f"{top_3_percentage:.1f}%"
            
        # Inequality assessment
        if total_categories >= 5:
            # Calculate Gini coefficient (measure of inequality)
            values = [item["value"] for item in sorted_data]
            gini = self._calculate_gini_coefficient(values)
            
            if gini > 0.7:
                inequality_level = "Very High"
            elif gini > 0.5:
                inequality_level = "High"
            elif gini > 0.3:
                inequality_level = "Moderate"
            else:
                inequality_level = "Low"
                
            insights["inequality"] = {
                "gini_coefficient": float(gini),
                "level": inequality_level
            }
        
        # Improvement potential
        potential_impact = vital_few["percentage"]
        if potential_impact >= 80:
            improvement_focus = "Excellent focus opportunity - high impact potential"
        elif potential_impact >= 60:
            improvement_focus = "Good focus opportunity - moderate impact potential"
        else:
            improvement_focus = "Distributed impact - consider broader approach"
            
        insights["improvement_potential"] = improvement_focus
        
        return insights
    
    def _calculate_gini_coefficient(self, values: List[float]) -> float:
        """Calculate Gini coefficient to measure inequality.
        
        Args:
            values: List of values.
            
        Returns:
            Gini coefficient (0 = perfect equality, 1 = perfect inequality).
        """
        if not values or sum(values) == 0:
            return 0.0
            
        # Sort values
        sorted_values = sorted(values)
        n = len(values)
        total = sum(values)
        
        # Calculate Gini coefficient
        cumulative = 0
        for i, value in enumerate(sorted_values):
            cumulative += value
            # Gini formula using Lorenz curve
        
        # Simplified Gini calculation
        sum_diff = sum(abs(x - y) for x in values for y in values)
        gini = sum_diff / (2 * n * total) if total > 0 else 0
        
        return min(1.0, gini)  # Cap at 1.0
    
    def _prepare_chart_data(self, sorted_data: List[Dict], cumulative_stats: Dict,
                           title: str, unit: str) -> Dict[str, Any]:
        """Prepare data structure for Pareto chart visualization.
        
        Args:
            sorted_data: Sorted category data.
            cumulative_stats: Cumulative statistics.
            title: Chart title.
            unit: Unit of measurement.
            
        Returns:
            Dictionary with chart data structure.
        """
        categories = [item["category"] for item in sorted_data]
        values = [item["value"] for item in sorted_data]
        percentages = [item["percentage"] for item in sorted_data]
        cumulative_percentages = [item["cumulative_percentage"] for item in sorted_data]
        
        return {
            "title": title,
            "categories": categories,
            "values": values,
            "percentages": percentages,
            "cumulative_percentages": cumulative_percentages,
            "threshold_line": cumulative_stats["threshold_percentage"],
            "unit": unit,
            "total_value": cumulative_stats["total_value"],
            "chart_type": "pareto",
            "colors": self._generate_colors(len(categories), cumulative_stats["categories_at_threshold"])
        }
    
    def _generate_colors(self, total_categories: int, vital_count: int) -> List[str]:
        """Generate color scheme for Pareto chart.
        
        Args:
            total_categories: Total number of categories.
            vital_count: Number of vital few categories.
            
        Returns:
            List of color codes for categories.
        """
        colors = []
        
        # Vital few in green/blue shades
        vital_colors = ["#2E8B57", "#3CB371", "#20B2AA", "#4682B4", "#6495ED"]
        
        # Trivial many in lighter colors
        trivial_colors = ["#D3D3D3", "#C0C0C0", "#A9A9A9", "#B0B0B0", "#DCDCDC"]
        
        for i in range(total_categories):
            if i < vital_count:
                color_index = i % len(vital_colors)
                colors.append(vital_colors[color_index])
            else:
                color_index = (i - vital_count) % len(trivial_colors)
                colors.append(trivial_colors[color_index])
        
        return colors
    
    def _generate_interpretation(self, sorted_data: List[Dict], vital_few: Dict,
                               insights: Dict, threshold: float) -> str:
        """Generate comprehensive interpretation of Pareto analysis.
        
        Args:
            sorted_data: Sorted category data.
            vital_few: Vital few analysis results.
            insights: Generated insights.
            threshold: Threshold percentage used.
            
        Returns:
            Human-readable interpretation string.
        """
        lines = []
        
        # Header
        lines.append("📊 PARETO ANALYSIS RESULTS")
        lines.append(f"Threshold: {threshold}% | Categories analyzed: {len(sorted_data)}")
        
        # Key finding
        vital_count = vital_few["count"]
        total_count = len(sorted_data)
        vital_percentage = vital_few["percentage"]
        
        lines.append(f"\n🎯 KEY FINDING:")
        lines.append(f"• {vital_count} out of {total_count} categories ({(vital_count/total_count)*100:.1f}%) account for {vital_percentage:.1f}% of total impact")
        lines.append(f"• {insights['concentration']}")
        
        # Vital few categories
        lines.append(f"\n✅ VITAL FEW (Focus Areas):")
        for i, category in enumerate(vital_few["categories"], 1):
            cat_data = next(item for item in sorted_data if item["category"] == category)
            lines.append(f"{i}. {category}: {cat_data['value']} ({cat_data['percentage']:.1f}%)")
        
        # Top contributor insight
        if "top_contributor" in insights:
            top = insights["top_contributor"]
            lines.append(f"\n🔝 TOP CONTRIBUTOR:")
            lines.append(f"• '{top['category']}' is the single largest factor")
            lines.append(f"• Contributes {top['percentage']:.1f}% of total impact")
        
        # Pareto principle assessment
        lines.append(f"\n📈 PARETO PRINCIPLE ASSESSMENT:")
        if vital_percentage >= 80 and (vital_count/total_count) <= 0.2:
            lines.append(f"✅ Classic 80/20 rule strongly applies")
        elif vital_percentage >= 70:
            lines.append(f"✅ Strong concentration effect observed")
        elif vital_percentage >= 60:
            lines.append(f"⚠️  Moderate concentration - consider broader focus")
        else:
            lines.append(f"❌ Impact is distributed - may need comprehensive approach")
        
        # Inequality analysis
        if "inequality" in insights:
            ineq = insights["inequality"]
            lines.append(f"• Distribution inequality: {ineq['level']} (Gini: {ineq['gini_coefficient']:.3f})")
        
        # Recommendations
        lines.append(f"\n📋 STRATEGIC RECOMMENDATIONS:")
        
        if vital_percentage >= 70:
            lines.append(f"1. FOCUS STRATEGY: Prioritize the {vital_count} vital categories")
            lines.append(f"2. Resource allocation: Dedicate 80% of resources to vital few")
            lines.append(f"3. Root cause analysis: Deep dive into top contributors")
            lines.append(f"4. Quick wins: Address top 1-2 categories for immediate impact")
        else:
            lines.append(f"1. BROAD STRATEGY: Address multiple categories simultaneously")
            lines.append(f"2. System approach: Look for common underlying causes")
            lines.append(f"3. Balanced resources: Distribute effort across categories")
        
        # Action priorities
        lines.append(f"\n🎯 IMMEDIATE ACTION PRIORITIES:")
        if sorted_data:
            top_3 = min(3, len(sorted_data))
            for i in range(top_3):
                cat = sorted_data[i]
                lines.append(f"{i+1}. Investigate and address '{cat['category']}' ({cat['percentage']:.1f}% impact)")
        
        # Impact potential
        lines.append(f"\n💡 IMPROVEMENT POTENTIAL:")
        lines.append(f"• Addressing vital few could improve {vital_percentage:.1f}% of total performance")
        lines.append(f"• {insights['improvement_potential']}")
        
        return "\n".join(lines)