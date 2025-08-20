"""Normal Probability Plot Tool with 95% Confidence Intervals.

Implements Minitab-style normal probability plots for assessing normality
and analyzing different operating modes in datasets.
"""

import numpy as np
from scipy import stats
from typing import Dict, List, Any, Optional, Union
from .base import BaseTool


class ProbabilityPlotTool(BaseTool):
    """Normal Probability Plot analysis tool.
    
    Creates probability plots to assess normality of data and identify
    different operating modes or outliers. Includes 95% confidence 
    intervals for individual percentiles following Minitab methodology.
    """
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Return the JSON schema for tool inputs."""
        return {
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Numerical data for probability plot analysis",
                    "minItems": 3
                },
                "groups": {
                    "type": "object",
                    "description": "Optional: grouped data for multi-modal analysis",
                    "additionalProperties": {
                        "type": "array",
                        "items": {"type": "number"}
                    }
                },
                "distribution": {
                    "type": "string",
                    "enum": ["normal", "lognormal", "weibull"],
                    "default": "normal",
                    "description": "Distribution type for probability plot"
                },
                "confidence_level": {
                    "type": "number",
                    "minimum": 0.5,
                    "maximum": 0.999,
                    "default": 0.95,
                    "description": "Confidence level for percentile intervals"
                },
                "title": {
                    "type": "string",
                    "default": "Normal Probability Plot",
                    "description": "Chart title"
                }
            },
            "required": ["data"],
            "additionalProperties": False
        }
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute probability plot analysis."""
        try:
            data = inputs["data"]
            groups = inputs.get("groups", {})
            distribution = inputs.get("distribution", "normal")
            confidence_level = inputs.get("confidence_level", 0.95)
            title = inputs.get("title", "Normal Probability Plot")
            
            # Validate inputs
            self.validate_data(data, min_length=3)
            
            if groups:
                # Multi-group analysis
                return self._analyze_grouped_data(groups, distribution, confidence_level, title)
            else:
                # Single dataset analysis
                return self._analyze_single_dataset(data, distribution, confidence_level, title)
                
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def _analyze_single_dataset(self, data: List[float], distribution: str, 
                              confidence_level: float, title: str) -> Dict[str, Any]:
        """Analyze single dataset with probability plot."""
        data_array = np.array(data)
        n = len(data_array)
        
        # Calculate plotting positions using median rank (Benard's method)
        sorted_data = np.sort(data_array)
        plotting_positions = self._calculate_plotting_positions(n, method="median_rank")
        
        # Get theoretical quantiles based on distribution
        if distribution == "normal":
            theoretical_quantiles = stats.norm.ppf(plotting_positions)
            fitted_params = stats.norm.fit(data_array)
            distribution_obj = stats.norm(*fitted_params)
        elif distribution == "lognormal":
            log_data = np.log(data_array[data_array > 0])
            theoretical_quantiles = stats.norm.ppf(plotting_positions)
            fitted_params = stats.lognorm.fit(data_array)
            distribution_obj = stats.lognorm(*fitted_params)
        elif distribution == "weibull":
            theoretical_quantiles = stats.weibull_min.ppf(plotting_positions)
            fitted_params = stats.weibull_min.fit(data_array)
            distribution_obj = stats.weibull_min(*fitted_params)
        
        # Calculate confidence intervals for percentiles
        confidence_intervals = self._calculate_confidence_intervals(
            sorted_data, plotting_positions, distribution, fitted_params, confidence_level
        )
        
        # Perform Anderson-Darling normality test
        if distribution == "normal":
            ad_statistic, critical_values, significance_level = stats.anderson(data_array, dist='norm')
            p_value = self._estimate_ad_p_value(ad_statistic)
        else:
            ad_statistic, p_value = None, None
        
        # Calculate correlation coefficient (measure of linearity)
        correlation = stats.pearsonr(theoretical_quantiles, sorted_data)[0]
        
        # Identify outliers (points outside confidence intervals)
        outliers = self._identify_outliers(sorted_data, confidence_intervals)
        
        # Calculate percentile estimates
        percentile_estimates = self._calculate_percentile_estimates(
            distribution_obj, [5, 10, 25, 50, 75, 90, 95]
        )
        
        # Create visualization
        chart_html = self._create_probability_plot(
            theoretical_quantiles, sorted_data, confidence_intervals,
            title, distribution, fitted_params, correlation
        )
        
        return {
            "success": True,
            "distribution_type": distribution,
            "sample_size": n,
            "fitted_parameters": {
                "mean": float(fitted_params[0]) if distribution == "normal" else None,
                "std": float(fitted_params[1]) if distribution == "normal" else None,
                "parameters": [float(p) for p in fitted_params]
            },
            "normality_test": {
                "anderson_darling_statistic": float(ad_statistic) if ad_statistic else None,
                "p_value": float(p_value) if p_value else None,
                "is_normal": p_value > 0.05 if p_value else None
            },
            "goodness_of_fit": {
                "correlation_coefficient": float(correlation),
                "interpretation": self._interpret_correlation(correlation)
            },
            "outliers": {
                "count": len(outliers),
                "values": [float(x) for x in outliers],
                "positions": [int(i) for i in range(len(sorted_data)) if sorted_data[i] in outliers]
            },
            "percentile_estimates": percentile_estimates,
            "confidence_intervals": {
                "level": confidence_level,
                "lower_bounds": [float(x) for x in confidence_intervals["lower"]],
                "upper_bounds": [float(x) for x in confidence_intervals["upper"]]
            },
            "plotting_data": {
                "theoretical_quantiles": [float(x) for x in theoretical_quantiles],
                "observed_values": [float(x) for x in sorted_data],
                "plotting_positions": [float(x) for x in plotting_positions]
            },
            "visualization": chart_html,
            "interpretation": self._generate_interpretation(correlation, p_value, outliers)
        }
    
    def _analyze_grouped_data(self, groups: Dict[str, List[float]], distribution: str,
                            confidence_level: float, title: str) -> Dict[str, Any]:
        """Analyze multiple groups for multi-modal analysis."""
        group_results = {}
        all_data = []
        
        for group_name, group_data in groups.items():
            if len(group_data) >= 3:
                result = self._analyze_single_dataset(
                    group_data, distribution, confidence_level, 
                    f"{title} - {group_name}"
                )
                group_results[group_name] = result
                all_data.extend(group_data)
        
        # Overall analysis
        overall_result = self._analyze_single_dataset(
            all_data, distribution, confidence_level, f"{title} - Combined"
        )
        
        # Compare groups
        group_comparison = self._compare_groups(groups)
        
        return {
            "success": True,
            "overall_analysis": overall_result,
            "group_analyses": group_results,
            "group_comparison": group_comparison,
            "recommendation": self._recommend_analysis_approach(group_results, overall_result)
        }
    
    def _calculate_plotting_positions(self, n: int, method: str = "median_rank") -> np.ndarray:
        """Calculate plotting positions using specified method."""
        i = np.arange(1, n + 1)
        
        if method == "median_rank":
            # Benard's approximation (Minitab default)
            return (i - 0.3) / (n + 0.4)
        elif method == "mean_rank":
            # Herd-Johnson estimate
            return i / (n + 1)
        elif method == "hazen":
            # Modified Kaplan-Meier
            return (i - 0.5) / n
        else:
            return (i - 0.3) / (n + 0.4)  # Default to median rank
    
    def _calculate_confidence_intervals(self, sorted_data: np.ndarray, 
                                     plotting_positions: np.ndarray,
                                     distribution: str, fitted_params: tuple,
                                     confidence_level: float) -> Dict[str, np.ndarray]:
        """Calculate confidence intervals for percentiles."""
        n = len(sorted_data)
        alpha = 1 - confidence_level
        z_score = stats.norm.ppf(1 - alpha/2)
        
        # Standard error estimation for percentiles
        p = plotting_positions
        se = np.sqrt(p * (1 - p) / n)  # Binomial standard error approximation
        
        # Transform to confidence intervals
        p_lower = np.maximum(0.001, p - z_score * se)
        p_upper = np.minimum(0.999, p + z_score * se)
        
        if distribution == "normal":
            mean, std = fitted_params
            lower_bounds = stats.norm.ppf(p_lower, mean, std)
            upper_bounds = stats.norm.ppf(p_upper, mean, std)
        elif distribution == "lognormal":
            s, loc, scale = fitted_params
            lower_bounds = stats.lognorm.ppf(p_lower, s, loc, scale)
            upper_bounds = stats.lognorm.ppf(p_upper, s, loc, scale)
        elif distribution == "weibull":
            c, loc, scale = fitted_params
            lower_bounds = stats.weibull_min.ppf(p_lower, c, loc, scale)
            upper_bounds = stats.weibull_min.ppf(p_upper, c, loc, scale)
        
        return {
            "lower": lower_bounds,
            "upper": upper_bounds
        }
    
    def _estimate_ad_p_value(self, ad_statistic: float) -> float:
        """Estimate p-value for Anderson-Darling test."""
        # Approximation based on Anderson-Darling critical values
        if ad_statistic < 0.2:
            return 0.8
        elif ad_statistic < 0.34:
            return 0.5
        elif ad_statistic < 0.47:
            return 0.25
        elif ad_statistic < 0.64:
            return 0.15
        elif ad_statistic < 0.78:
            return 0.10
        elif ad_statistic < 1.09:
            return 0.05
        elif ad_statistic < 1.31:
            return 0.025
        elif ad_statistic < 1.61:
            return 0.01
        else:
            return 0.001
    
    def _identify_outliers(self, sorted_data: np.ndarray, 
                          confidence_intervals: Dict[str, np.ndarray]) -> List[float]:
        """Identify outliers based on confidence intervals."""
        outliers = []
        lower_bounds = confidence_intervals["lower"]
        upper_bounds = confidence_intervals["upper"]
        
        for i, value in enumerate(sorted_data):
            if value < lower_bounds[i] or value > upper_bounds[i]:
                outliers.append(value)
        
        return outliers
    
    def _calculate_percentile_estimates(self, distribution_obj, percentiles: List[int]) -> Dict[str, float]:
        """Calculate percentile estimates from fitted distribution."""
        estimates = {}
        for p in percentiles:
            estimates[f"{p}th_percentile"] = float(distribution_obj.ppf(p/100))
        return estimates
    
    def _interpret_correlation(self, correlation: float) -> str:
        """Interpret correlation coefficient for goodness of fit."""
        if correlation > 0.99:
            return "Excellent fit - data strongly follows the assumed distribution"
        elif correlation > 0.98:
            return "Good fit - data reasonably follows the assumed distribution"
        elif correlation > 0.95:
            return "Fair fit - some deviation from the assumed distribution"
        else:
            return "Poor fit - data does not follow the assumed distribution"
    
    def _compare_groups(self, groups: Dict[str, List[float]]) -> Dict[str, Any]:
        """Compare statistical properties between groups."""
        group_stats = {}
        for name, data in groups.items():
            arr = np.array(data)
            group_stats[name] = {
                "mean": float(np.mean(arr)),
                "std": float(np.std(arr, ddof=1)),
                "median": float(np.median(arr)),
                "size": len(arr)
            }
        
        # Perform ANOVA if multiple groups
        if len(groups) > 1:
            group_arrays = [np.array(data) for data in groups.values()]
            f_stat, p_value = stats.f_oneway(*group_arrays)
            
            return {
                "group_statistics": group_stats,
                "anova_test": {
                    "f_statistic": float(f_stat),
                    "p_value": float(p_value),
                    "significant_difference": p_value < 0.05
                }
            }
        
        return {"group_statistics": group_stats}
    
    def _recommend_analysis_approach(self, group_results: Dict, overall_result: Dict) -> str:
        """Recommend analysis approach based on group vs overall fit."""
        overall_correlation = overall_result.get("goodness_of_fit", {}).get("correlation_coefficient", 0)
        
        if overall_correlation > 0.95:
            return "Single distribution model recommended - all data fits well together"
        else:
            group_correlations = []
            for result in group_results.values():
                corr = result.get("goodness_of_fit", {}).get("correlation_coefficient", 0)
                group_correlations.append(corr)
            
            avg_group_correlation = np.mean(group_correlations)
            
            if avg_group_correlation > overall_correlation + 0.05:
                return "Multi-modal analysis recommended - groups show better individual fit"
            else:
                return "Consider transformation or alternative distribution"
    
    def _create_probability_plot(self, theoretical_quantiles: np.ndarray,
                               observed_values: np.ndarray,
                               confidence_intervals: Dict[str, np.ndarray],
                               title: str, distribution: str,
                               fitted_params: tuple, correlation: float) -> str:
        """Create probability plot visualization."""
        try:
            from ..utils.visualization import create_probability_plot_chart
            return create_probability_plot_chart(
                theoretical_quantiles, observed_values, confidence_intervals,
                title, distribution, fitted_params, correlation
            )
        except ImportError:
            return f"Probability plot for {distribution} distribution (r={correlation:.3f})"
    
    def _generate_interpretation(self, correlation: float, p_value: Optional[float], 
                               outliers: List[float]) -> str:
        """Generate interpretation of probability plot results."""
        interpretation = []
        
        # Distribution fit assessment
        if correlation > 0.98:
            interpretation.append("✅ Data follows the assumed distribution very well")
        elif correlation > 0.95:
            interpretation.append("⚠️ Data reasonably follows the distribution with some deviation")
        else:
            interpretation.append("❌ Data shows poor fit to the assumed distribution")
        
        # Normality test results
        if p_value is not None:
            if p_value > 0.05:
                interpretation.append("✅ Anderson-Darling test supports normality assumption")
            else:
                interpretation.append("❌ Anderson-Darling test rejects normality assumption")
        
        # Outliers assessment
        if len(outliers) == 0:
            interpretation.append("✅ No outliers detected")
        elif len(outliers) <= 2:
            interpretation.append(f"⚠️ {len(outliers)} potential outlier(s) detected")
        else:
            interpretation.append(f"❌ {len(outliers)} outliers detected - investigate data quality")
        
        return " | ".join(interpretation)