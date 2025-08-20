"""One-way ANOVA analysis with boxplots for comparing groups.

This module performs Analysis of Variance to test for significant differences
between group means, including assumption testing and post-hoc analysis.
"""

import numpy as np
from scipy import stats
from typing import Dict, Any, List, Tuple, Union
from .base import BaseTool

try:
    from ..utils.visualization import create_boxplot
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False


class ANOVATool(BaseTool):
    """One-way Analysis of Variance with comprehensive statistical analysis.
    
    Performs ANOVA to compare means across groups, checks assumptions,
    and provides post-hoc analysis when significant differences are found.
    """
    
    def __init__(self):
        """Initialize the ANOVA analysis tool."""
        self.name = "anova_boxplot"
        self.description = "One-way ANOVA analysis with assumption testing and post-hoc comparisons"
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Return JSON schema for ANOVA inputs.
        
        Returns:
            JSON schema defining group data and analysis options.
        """
        return {
            "type": "object",
            "properties": {
                "groups": {
                    "type": "object",
                    "description": "Dictionary where keys are group names and values are arrays of measurements",
                    "patternProperties": {
                        ".*": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 3
                        }
                    },
                    "minProperties": 2
                },
                "alpha": {
                    "type": "number",
                    "default": 0.05,
                    "minimum": 0.001,
                    "maximum": 0.10,
                    "description": "Significance level for ANOVA test (typically 0.05)"
                },
                "post_hoc": {
                    "type": "boolean",
                    "default": True,
                    "description": "Perform Tukey HSD post-hoc analysis if ANOVA is significant"
                },
                "assumption_tests": {
                    "type": "boolean",
                    "default": True,
                    "description": "Test ANOVA assumptions (normality and equal variances)"
                }
            },
            "required": ["groups"]
        }
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform one-way ANOVA analysis with assumption testing.
        
        Args:
            params: Dictionary containing group data and analysis options.
            
        Returns:
            Dictionary with ANOVA results, assumption tests, and post-hoc analysis.
            
        Raises:
            ValueError: If group data is invalid or insufficient.
        """
        # Validate inputs
        self.validate_inputs(params, ["groups"])
        
        groups_dict = params["groups"]
        alpha = params.get("alpha", 0.05)
        perform_posthoc = params.get("post_hoc", True)
        test_assumptions = params.get("assumption_tests", True)
        
        # Validate and prepare group data
        groups_data, group_names = self._prepare_group_data(groups_dict)
        
        # Descriptive statistics
        descriptive_stats = self._calculate_descriptive_stats(groups_data, group_names)
        
        # Perform one-way ANOVA
        anova_results = self._perform_anova(groups_data, group_names, alpha)
        
        # Test assumptions if requested
        assumption_results = {}
        if test_assumptions:
            assumption_results = self._test_assumptions(groups_data, group_names, alpha)
        
        # Post-hoc analysis if ANOVA is significant
        posthoc_results = {}
        if perform_posthoc and anova_results["significant"]:
            posthoc_results = self._perform_tukey_hsd(groups_data, group_names, alpha)
        
        # Effect size calculation
        effect_size = self._calculate_effect_size(groups_data, anova_results)
        
        # Generate interpretation
        interpretation = self._generate_interpretation(
            anova_results, assumption_results, posthoc_results, effect_size
        )
        
        # Create visualization
        chart_html = None
        if VISUALIZATION_AVAILABLE:
            try:
                chart_html = create_boxplot(
                    data_groups=groups_data,
                    group_names=group_names,
                    title="ANOVA Group Comparison - Boxplots",
                    y_label="Value"
                )
            except Exception as e:
                chart_html = f"Visualization error: {str(e)}"
        else:
            chart_html = "Visualization not available - install plotly>=5.0.0"
        
        return {
            "descriptive_statistics": descriptive_stats,
            "anova_results": anova_results,
            "assumption_tests": assumption_results,
            "post_hoc_analysis": posthoc_results,
            "effect_size": effect_size,
            "boxplot_data": self._prepare_boxplot_data(groups_data, group_names),
            "interpretation": interpretation,
            "chart_html": chart_html
        }
    
    def _prepare_group_data(self, groups_dict: Dict[str, List[float]]) -> Tuple[List[np.ndarray], List[str]]:
        """Prepare and validate group data for analysis.
        
        Args:
            groups_dict: Dictionary with group names as keys and data as values.
            
        Returns:
            Tuple of (group_arrays, group_names).
            
        Raises:
            ValueError: If group data is invalid.
        """
        if len(groups_dict) < 2:
            raise ValueError("At least 2 groups are required for ANOVA")
        
        group_names = list(groups_dict.keys())
        groups_data = []
        
        for name, data in groups_dict.items():
            if not data:
                raise ValueError(f"Group '{name}' cannot be empty")
            
            self.validate_data_array(data, min_length=3)
            groups_data.append(np.array(data, dtype=float))
        
        return groups_data, group_names
    
    def _calculate_descriptive_stats(self, groups_data: List[np.ndarray], 
                                   group_names: List[str]) -> Dict[str, Any]:
        """Calculate descriptive statistics for each group.
        
        Args:
            groups_data: List of arrays containing group measurements.
            group_names: List of group names.
            
        Returns:
            Dictionary with descriptive statistics for each group.
        """
        stats_by_group = {}
        all_data = np.concatenate(groups_data)
        
        for i, (name, data) in enumerate(zip(group_names, groups_data)):
            stats_by_group[name] = {
                "n": len(data),
                "mean": float(np.mean(data)),
                "std": float(np.std(data, ddof=1)),
                "min": float(np.min(data)),
                "max": float(np.max(data)),
                "median": float(np.median(data)),
                "q1": float(np.percentile(data, 25)),
                "q3": float(np.percentile(data, 75)),
                "iqr": float(np.percentile(data, 75) - np.percentile(data, 25))
            }
        
        # Overall statistics
        overall_stats = {
            "total_n": len(all_data),
            "overall_mean": float(np.mean(all_data)),
            "overall_std": float(np.std(all_data, ddof=1)),
            "groups": len(group_names)
        }
        
        return {
            "by_group": stats_by_group,
            "overall": overall_stats
        }
    
    def _perform_anova(self, groups_data: List[np.ndarray], 
                      group_names: List[str], alpha: float) -> Dict[str, Any]:
        """Perform one-way ANOVA analysis.
        
        Args:
            groups_data: List of group data arrays.
            group_names: List of group names.
            alpha: Significance level.
            
        Returns:
            Dictionary with ANOVA results.
        """
        # Perform one-way ANOVA
        f_statistic, p_value = stats.f_oneway(*groups_data)
        
        # Calculate degrees of freedom
        k = len(groups_data)  # Number of groups
        n = sum(len(group) for group in groups_data)  # Total sample size
        df_between = k - 1
        df_within = n - k
        df_total = n - 1
        
        # Calculate sum of squares
        all_data = np.concatenate(groups_data)
        grand_mean = np.mean(all_data)
        
        # Sum of squares between groups
        ss_between = sum(len(group) * (np.mean(group) - grand_mean)**2 for group in groups_data)
        
        # Sum of squares within groups
        ss_within = sum(np.sum((group - np.mean(group))**2) for group in groups_data)
        
        # Sum of squares total
        ss_total = np.sum((all_data - grand_mean)**2)
        
        # Mean squares
        ms_between = ss_between / df_between if df_between > 0 else 0
        ms_within = ss_within / df_within if df_within > 0 else 0
        
        # Critical F value
        f_critical = stats.f.ppf(1 - alpha, df_between, df_within)
        
        # Determine significance
        significant = p_value < alpha
        
        return {
            "f_statistic": float(f_statistic),
            "p_value": float(p_value),
            "significant": significant,
            "alpha": alpha,
            "f_critical": float(f_critical),
            "degrees_of_freedom": {
                "between_groups": df_between,
                "within_groups": df_within,
                "total": df_total
            },
            "sum_of_squares": {
                "between_groups": float(ss_between),
                "within_groups": float(ss_within),
                "total": float(ss_total)
            },
            "mean_squares": {
                "between_groups": float(ms_between),
                "within_groups": float(ms_within)
            }
        }
    
    def _test_assumptions(self, groups_data: List[np.ndarray], 
                         group_names: List[str], alpha: float) -> Dict[str, Any]:
        """Test ANOVA assumptions: normality and equal variances.
        
        Args:
            groups_data: List of group data arrays.
            group_names: List of group names.
            alpha: Significance level for assumption tests.
            
        Returns:
            Dictionary with assumption test results.
        """
        # Normality tests for each group (Shapiro-Wilk)
        normality_tests = {}
        all_normal = True
        
        for name, data in zip(group_names, groups_data):
            if len(data) >= 3:  # Shapiro-Wilk requires at least 3 observations
                stat, p_val = stats.shapiro(data)
                is_normal = p_val > alpha
                all_normal = all_normal and is_normal
                
                normality_tests[name] = {
                    "statistic": float(stat),
                    "p_value": float(p_val),
                    "is_normal": is_normal
                }
        
        # Equal variance test (Levene's test)
        levene_stat, levene_p = stats.levene(*groups_data)
        equal_variances = levene_p > alpha
        
        # Bartlett's test (more sensitive to normality violations)
        try:
            bartlett_stat, bartlett_p = stats.bartlett(*groups_data)
            bartlett_result = {
                "statistic": float(bartlett_stat),
                "p_value": float(bartlett_p),
                "equal_variances": bartlett_p > alpha
            }
        except:
            bartlett_result = {"error": "Could not perform Bartlett's test"}
        
        return {
            "normality": {
                "by_group": normality_tests,
                "all_groups_normal": all_normal,
                "test_used": "Shapiro-Wilk"
            },
            "equal_variances": {
                "levene_test": {
                    "statistic": float(levene_stat),
                    "p_value": float(levene_p),
                    "equal_variances": equal_variances
                },
                "bartlett_test": bartlett_result
            },
            "assumptions_met": all_normal and equal_variances,
            "alpha": alpha
        }
    
    def _perform_tukey_hsd(self, groups_data: List[np.ndarray], 
                          group_names: List[str], alpha: float) -> Dict[str, Any]:
        """Perform Tukey HSD post-hoc analysis for pairwise comparisons.
        
        Args:
            groups_data: List of group data arrays.
            group_names: List of group names.
            alpha: Significance level.
            
        Returns:
            Dictionary with pairwise comparison results.
        """
        from itertools import combinations
        
        # Calculate pooled standard error
        n_total = sum(len(group) for group in groups_data)
        k = len(groups_data)
        df_within = n_total - k
        
        # Calculate MSE (Mean Square Error) from ANOVA
        ss_within = sum(np.sum((group - np.mean(group))**2) for group in groups_data)
        mse = ss_within / df_within
        
        # Tukey HSD critical value
        from scipy.stats import studentized_range
        q_critical = studentized_range.ppf(1 - alpha, k, df_within)
        
        # Pairwise comparisons
        comparisons = []
        significant_pairs = []
        
        for i, j in combinations(range(len(groups_data)), 2):
            group1_name = group_names[i]
            group2_name = group_names[j]
            group1_data = groups_data[i]
            group2_data = groups_data[j]
            
            mean1 = np.mean(group1_data)
            mean2 = np.mean(group2_data)
            n1 = len(group1_data)
            n2 = len(group2_data)
            
            # Standard error for this comparison
            se = np.sqrt(mse * (1/n1 + 1/n2))
            
            # Tukey HSD statistic
            mean_diff = abs(mean1 - mean2)
            tukey_hsd = q_critical * se
            
            # Determine significance
            is_significant = mean_diff > tukey_hsd
            
            comparison = {
                "group1": group1_name,
                "group2": group2_name,
                "mean1": float(mean1),
                "mean2": float(mean2),
                "mean_difference": float(mean1 - mean2),
                "abs_difference": float(mean_diff),
                "standard_error": float(se),
                "tukey_hsd": float(tukey_hsd),
                "significant": is_significant
            }
            
            comparisons.append(comparison)
            
            if is_significant:
                significant_pairs.append(f"{group1_name} vs {group2_name}")
        
        return {
            "test": "Tukey HSD",
            "alpha": alpha,
            "q_critical": float(q_critical),
            "degrees_of_freedom": df_within,
            "mse": float(mse),
            "comparisons": comparisons,
            "significant_pairs": significant_pairs,
            "total_comparisons": len(comparisons),
            "significant_comparisons": len(significant_pairs)
        }
    
    def _calculate_effect_size(self, groups_data: List[np.ndarray], 
                             anova_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate effect size measures for ANOVA.
        
        Args:
            groups_data: List of group data arrays.
            anova_results: ANOVA results dictionary.
            
        Returns:
            Dictionary with effect size measures.
        """
        ss_between = anova_results["sum_of_squares"]["between_groups"]
        ss_total = anova_results["sum_of_squares"]["total"]
        ss_within = anova_results["sum_of_squares"]["within_groups"]
        
        # Eta-squared (proportion of variance explained)
        eta_squared = ss_between / ss_total if ss_total > 0 else 0
        
        # Partial eta-squared
        partial_eta_squared = ss_between / (ss_between + ss_within) if (ss_between + ss_within) > 0 else 0
        
        # Omega-squared (less biased estimate)
        df_between = anova_results["degrees_of_freedom"]["between_groups"]
        ms_within = anova_results["mean_squares"]["within_groups"]
        n_total = sum(len(group) for group in groups_data)
        
        omega_squared = (ss_between - df_between * ms_within) / (ss_total + ms_within) if (ss_total + ms_within) > 0 else 0
        omega_squared = max(0, omega_squared)  # Cannot be negative
        
        # Effect size interpretation
        if eta_squared >= 0.14:
            magnitude = "Large"
        elif eta_squared >= 0.06:
            magnitude = "Medium"
        elif eta_squared >= 0.01:
            magnitude = "Small"
        else:
            magnitude = "Negligible"
        
        return {
            "eta_squared": float(eta_squared),
            "partial_eta_squared": float(partial_eta_squared),
            "omega_squared": float(omega_squared),
            "magnitude": magnitude,
            "interpretation": {
                "eta_squared": f"{eta_squared:.1%} of variance explained by group differences",
                "magnitude": f"{magnitude} effect size"
            }
        }
    
    def _prepare_boxplot_data(self, groups_data: List[np.ndarray], 
                             group_names: List[str]) -> Dict[str, Any]:
        """Prepare data for boxplot visualization.
        
        Args:
            groups_data: List of group data arrays.
            group_names: List of group names.
            
        Returns:
            Dictionary with boxplot data structure.
        """
        boxplot_data = {}
        
        for name, data in zip(group_names, groups_data):
            # Calculate boxplot statistics
            q1 = np.percentile(data, 25)
            median = np.percentile(data, 50)
            q3 = np.percentile(data, 75)
            iqr = q3 - q1
            
            # Outlier detection using 1.5*IQR rule
            lower_fence = q1 - 1.5 * iqr
            upper_fence = q3 + 1.5 * iqr
            outliers = data[(data < lower_fence) | (data > upper_fence)]
            
            boxplot_data[name] = {
                "data": data.tolist(),
                "q1": float(q1),
                "median": float(median),
                "q3": float(q3),
                "iqr": float(iqr),
                "min": float(np.min(data)),
                "max": float(np.max(data)),
                "lower_fence": float(lower_fence),
                "upper_fence": float(upper_fence),
                "outliers": outliers.tolist(),
                "mean": float(np.mean(data))
            }
        
        return boxplot_data
    
    def _generate_interpretation(self, anova_results: Dict, assumption_results: Dict,
                               posthoc_results: Dict, effect_size: Dict) -> str:
        """Generate comprehensive interpretation of ANOVA results.
        
        Args:
            anova_results: ANOVA statistical results.
            assumption_results: Assumption test results.
            posthoc_results: Post-hoc analysis results.
            effect_size: Effect size calculations.
            
        Returns:
            Human-readable interpretation string.
        """
        lines = []
        
        # ANOVA results header
        if anova_results["significant"]:
            lines.append("✅ SIGNIFICANT GROUP DIFFERENCES DETECTED")
        else:
            lines.append("❌ NO SIGNIFICANT GROUP DIFFERENCES")
        
        lines.append(f"F({anova_results['degrees_of_freedom']['between_groups']}, {anova_results['degrees_of_freedom']['within_groups']}) = {anova_results['f_statistic']:.3f}, p = {anova_results['p_value']:.4f}")
        
        # Effect size interpretation
        lines.append(f"Effect Size: {effect_size['magnitude']} ({effect_size['eta_squared']:.1%} of variance explained)")
        
        # Detailed analysis
        if anova_results["significant"]:
            lines.append(f"\n📊 ANALYSIS RESULTS:")
            lines.append(f"• At least one group mean differs significantly from others")
            lines.append(f"• {effect_size['interpretation']['magnitude']}")
            
            # Post-hoc results
            if posthoc_results:
                if posthoc_results["significant_pairs"]:
                    lines.append(f"\n🔍 POST-HOC ANALYSIS (Tukey HSD):")
                    lines.append(f"• {len(posthoc_results['significant_pairs'])} of {posthoc_results['total_comparisons']} pairwise comparisons significant:")
                    for pair in posthoc_results["significant_pairs"]:
                        lines.append(f"  - {pair}")
                else:
                    lines.append(f"\n🔍 POST-HOC ANALYSIS:")
                    lines.append(f"• No individual pairwise differences significant after Tukey correction")
        else:
            lines.append(f"\n📊 ANALYSIS RESULTS:")
            lines.append(f"• Group means are not significantly different")
            lines.append(f"• Observed differences likely due to random variation")
            lines.append(f"• Effect size is {effect_size['magnitude'].lower()}")
        
        # Assumption checking
        if assumption_results:
            lines.append(f"\n🧪 ASSUMPTION CHECKS:")
            
            # Normality
            if assumption_results["normality"]["all_groups_normal"]:
                lines.append(f"✅ Normality: All groups appear normally distributed")
            else:
                lines.append(f"⚠️  Normality: Some groups may not be normally distributed")
                lines.append(f"   Consider non-parametric Kruskal-Wallis test")
            
            # Equal variances
            if assumption_results["equal_variances"]["levene_test"]["equal_variances"]:
                lines.append(f"✅ Equal Variances: Homogeneity assumption met")
            else:
                lines.append(f"⚠️  Equal Variances: Groups have unequal variances")
                lines.append(f"   Consider Welch's ANOVA for unequal variances")
            
            # Overall assumption assessment
            if assumption_results["assumptions_met"]:
                lines.append(f"✅ ANOVA assumptions satisfied")
            else:
                lines.append(f"⚠️  Some ANOVA assumptions violated - interpret results cautiously")
        
        # Recommendations
        lines.append(f"\n📋 RECOMMENDATIONS:")
        
        if anova_results["significant"]:
            lines.append(f"1. Investigate causes of group differences")
            lines.append(f"2. Focus on groups identified in post-hoc analysis")
            if not assumption_results.get("assumptions_met", True):
                lines.append(f"3. Consider robust statistical methods due to assumption violations")
            lines.append(f"4. Validate findings with additional data if possible")
        else:
            lines.append(f"1. Groups appear similar - no further action needed")
            lines.append(f"2. Consider increasing sample sizes if differences expected")
            lines.append(f"3. Review measurement methods for precision")
        
        return "\n".join(lines)