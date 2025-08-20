"""
Pure NumPy/SciPy statistical calculations for ESTIEM EDA
Shared calculation engine for all platforms (MCP, Web, CLI, Colab)
"""

import numpy as np
from scipy import stats
import math
from typing import Dict, List, Any, Optional, Tuple, Union


def calculate_i_chart(values: np.ndarray, title: str = "I-Chart Analysis") -> Dict[str, Any]:
    """
    Calculate Individual Control Chart (I-Chart) statistics
    
    Args:
        values: Array of numeric measurements
        title: Chart title
        
    Returns:
        Dictionary with statistics and control limits
    """
    n = len(values)
    mean = np.mean(values)
    
    # Moving range for sigma estimation
    moving_range = np.abs(np.diff(values))
    avg_mr = np.mean(moving_range)
    
    # Control limits (using moving range method)
    # d2 constant for n=2 (moving range of 2)
    d2 = 1.128
    sigma_hat = avg_mr / d2
    
    # Control limits for individuals (A2 = 3/sqrt(n) for n=1)
    ucl = mean + 3 * sigma_hat
    lcl = mean - 3 * sigma_hat
    
    # Check for out-of-control points
    out_of_control = []
    for i, value in enumerate(values):
        if value > ucl or value < lcl:
            out_of_control.append(i)
    
    # Western Electric Rules
    violations = check_western_electric_rules(values, mean, ucl, lcl, sigma_hat)
    
    # Process capability estimate (if no spec limits, use ±3sigma)
    natural_tolerance = 6 * sigma_hat
    
    return {
        'success': True,
        'statistics': {
            'sample_size': n,
            'mean': mean,
            'sigma_hat': sigma_hat,
            'ucl': ucl,
            'lcl': lcl,
            'avg_moving_range': avg_mr,
            'out_of_control_points': len(out_of_control),
            'natural_tolerance': natural_tolerance
        },
        'out_of_control_indices': out_of_control,
        'western_electric_violations': violations,
        'data_points': values.tolist(),
        'interpretation': interpret_i_chart(len(out_of_control), violations, n),
        'analysis_type': 'i_chart'
    }


def calculate_process_capability(values: np.ndarray, lsl: float, usl: float, 
                               target: float = None) -> Dict[str, Any]:
    """
    Calculate process capability indices (Cp, Cpk, Pp, Ppk)
    
    Args:
        values: Array of numeric measurements
        lsl: Lower specification limit
        usl: Upper specification limit
        target: Target value (defaults to center of spec limits)
        
    Returns:
        Dictionary with capability indices and defect analysis
    """
    n = len(values)
    mean = np.mean(values)
    std_dev = np.std(values, ddof=1)  # Sample standard deviation
    
    if target is None:
        target = (lsl + usl) / 2
    
    # Capability indices
    tolerance = usl - lsl
    cp = tolerance / (6 * std_dev) if std_dev > 0 else float('inf')
    
    cpu = (usl - mean) / (3 * std_dev) if std_dev > 0 else float('inf')
    cpl = (mean - lsl) / (3 * std_dev) if std_dev > 0 else float('inf')
    cpk = min(cpu, cpl)
    
    # Performance indices (using population standard deviation)
    pp = tolerance / (6 * np.std(values, ddof=0)) if np.std(values, ddof=0) > 0 else float('inf')
    ppu = (usl - mean) / (3 * np.std(values, ddof=0)) if np.std(values, ddof=0) > 0 else float('inf')
    ppl = (mean - lsl) / (3 * np.std(values, ddof=0)) if np.std(values, ddof=0) > 0 else float('inf')
    ppk = min(ppu, ppl)
    
    # Defect analysis
    z_lower = (lsl - mean) / std_dev if std_dev > 0 else -float('inf')
    z_upper = (usl - mean) / std_dev if std_dev > 0 else float('inf')
    
    ppm_lower = stats.norm.cdf(z_lower) * 1_000_000
    ppm_upper = (1 - stats.norm.cdf(z_upper)) * 1_000_000
    ppm_total = ppm_lower + ppm_upper
    
    # Six Sigma level calculation
    if ppm_total > 0:
        z_shift = stats.norm.ppf(1 - ppm_total / 2_000_000)  # Two-sided
        sigma_level = z_shift + 1.5  # Traditional 1.5 sigma shift
    else:
        sigma_level = 6.0
    
    return {
        'success': True,
        'capability_indices': {
            'cp': cp,
            'cpk': cpk,
            'cpu': cpu,
            'cpl': cpl,
            'pp': pp,
            'ppk': ppk,
            'ppu': ppu,
            'ppl': ppl
        },
        'statistics': {
            'sample_size': n,
            'mean': mean,
            'std_dev': std_dev,
            'lsl': lsl,
            'usl': usl,
            'target': target
        },
        'defect_analysis': {
            'ppm_lower': ppm_lower,
            'ppm_upper': ppm_upper,
            'ppm_total': ppm_total,
            'sigma_level': sigma_level
        },
        'interpretation': interpret_capability(cpk, ppm_total, sigma_level),
        'analysis_type': 'capability'
    }


def calculate_anova(groups: Dict[str, np.ndarray], alpha: float = 0.05) -> Dict[str, Any]:
    """
    Calculate one-way Analysis of Variance (ANOVA)
    
    Args:
        groups: Dictionary with group names as keys, data arrays as values
        alpha: Significance level
        
    Returns:
        Dictionary with ANOVA results and post-hoc comparisons
    """
    group_names = list(groups.keys())
    group_data = list(groups.values())
    
    # Basic statistics
    k = len(groups)  # Number of groups
    n_total = sum(len(group) for group in group_data)
    
    # Grand mean
    all_data = np.concatenate(group_data)
    grand_mean = np.mean(all_data)
    
    # Group means and sizes
    group_means = [np.mean(group) for group in group_data]
    group_sizes = [len(group) for group in group_data]
    
    # Sum of squares
    # Between groups (SSB)
    ssb = sum(n * (mean - grand_mean)**2 for n, mean in zip(group_sizes, group_means))
    
    # Within groups (SSW)
    ssw = sum(np.sum((group - np.mean(group))**2) for group in group_data)
    
    # Total sum of squares
    sst = ssb + ssw
    
    # Degrees of freedom
    df_between = k - 1
    df_within = n_total - k
    df_total = n_total - 1
    
    # Mean squares
    msb = ssb / df_between if df_between > 0 else 0
    msw = ssw / df_within if df_within > 0 else 0
    
    # F-statistic
    f_statistic = msb / msw if msw > 0 else float('inf')
    
    # p-value
    p_value = 1 - stats.f.cdf(f_statistic, df_between, df_within)
    
    # Significance
    significant = p_value < alpha
    
    # Post-hoc analysis (Tukey HSD)
    post_hoc = calculate_tukey_hsd(groups, msw, alpha) if significant else None
    
    results = {
        'success': True,
        'anova_results': {
            'f_statistic': f_statistic,
            'p_value': p_value,
            'significant': significant,
            'alpha': alpha,
            'df_between': df_between,
            'df_within': df_within,
            'ssb': ssb,
            'ssw': ssw,
            'sst': sst,
            'msb': msb,
            'msw': msw
        },
        'group_statistics': {
            name: {
                'mean': np.mean(data),
                'std': np.std(data, ddof=1),
                'size': len(data)
            } for name, data in groups.items()
        },
        'grand_mean': grand_mean,
        'interpretation': interpret_anova(f_statistic, p_value, significant, k),
        'analysis_type': 'anova'
    }
    
    if post_hoc:
        results['post_hoc'] = post_hoc
        
    return results


def calculate_pareto(data: Dict[str, float], threshold: float = 0.8) -> Dict[str, Any]:
    """
    Calculate Pareto analysis (80/20 rule)
    
    Args:
        data: Dictionary with categories as keys, values as values
        threshold: Threshold for identifying vital few (default 0.8 for 80%)
        
    Returns:
        Dictionary with Pareto analysis results
    """
    if not data:
        raise ValueError("Empty data provided for Pareto analysis")
    
    # Sort by value (descending)
    sorted_items = sorted(data.items(), key=lambda x: x[1], reverse=True)
    
    # Calculate percentages and cumulative percentages
    total = sum(data.values())
    
    categories = []
    values = []
    percentages = []
    cumulative_percentages = []
    
    cumulative = 0
    for category, value in sorted_items:
        categories.append(category)
        values.append(value)
        
        percentage = (value / total) * 100
        percentages.append(percentage)
        
        cumulative += percentage
        cumulative_percentages.append(cumulative)
    
    # Find vital few (categories contributing to threshold% of total)
    vital_few_indices = []
    for i, cum_pct in enumerate(cumulative_percentages):
        vital_few_indices.append(i)
        if cum_pct >= threshold * 100:
            break
    
    vital_few_categories = [categories[i] for i in vital_few_indices]
    vital_few_percentage = cumulative_percentages[vital_few_indices[-1]]
    
    # Calculate Gini coefficient
    gini = calculate_gini_coefficient(values)
    
    return {
        'success': True,
        'categories': categories,
        'values': values,
        'percentages': percentages,
        'cumulative_percentages': cumulative_percentages,
        'vital_few': {
            'categories': vital_few_categories,
            'count': len(vital_few_categories),
            'percentage': vital_few_percentage
        },
        'gini_coefficient': {
            'value': gini,
            'interpretation': interpret_gini_coefficient(gini)
        },
        'total_value': total,
        'interpretation': interpret_pareto(len(vital_few_categories), len(categories), vital_few_percentage),
        'analysis_type': 'pareto'
    }


def calculate_probability_plot(values: np.ndarray, distribution: str = 'normal', 
                             confidence_level: float = 0.95) -> Dict[str, Any]:
    """
    Calculate probability plot for distribution assessment
    
    Args:
        values: Array of numeric measurements
        distribution: Distribution type ('normal', 'lognormal', 'weibull')
        confidence_level: Confidence level for intervals
        
    Returns:
        Dictionary with probability plot results and goodness of fit
    """
    n = len(values)
    sorted_values = np.sort(values)
    
    # Calculate plotting positions (median rank)
    plotting_positions = np.array([(i + 0.5) / n for i in range(n)])
    
    # Transform data based on distribution
    if distribution == 'normal':
        theoretical_quantiles = stats.norm.ppf(plotting_positions)
        transformed_data = sorted_values
    elif distribution == 'lognormal':
        if np.any(sorted_values <= 0):
            raise ValueError("Lognormal distribution requires positive values")
        theoretical_quantiles = stats.norm.ppf(plotting_positions)
        transformed_data = np.log(sorted_values)
    elif distribution == 'weibull':
        if np.any(sorted_values <= 0):
            raise ValueError("Weibull distribution requires positive values")
        # Use log-log transformation for Weibull
        theoretical_quantiles = np.log(-np.log(1 - plotting_positions))
        transformed_data = np.log(sorted_values)
    else:
        raise ValueError(f"Unsupported distribution: {distribution}")
    
    # Calculate correlation coefficient
    correlation = np.corrcoef(theoretical_quantiles, transformed_data)[0, 1]
    
    # Fit line
    slope, intercept, r_value, p_value, std_err = stats.linregress(theoretical_quantiles, transformed_data)
    
    # Calculate confidence intervals
    alpha = 1 - confidence_level
    t_critical = stats.t.ppf(1 - alpha/2, n - 2)
    
    # Prediction intervals for new observations
    residuals = transformed_data - (slope * theoretical_quantiles + intercept)
    s_res = np.std(residuals, ddof=2)
    
    # Calculate outliers (points outside confidence bands)
    outliers = []
    for i in range(n):
        expected = slope * theoretical_quantiles[i] + intercept
        deviation = abs(transformed_data[i] - expected)
        if deviation > 2 * s_res:  # Simple outlier detection
            outliers.append(i)
    
    # Normality tests
    if distribution == 'normal':
        # Anderson-Darling test
        ad_stat, ad_critical, ad_significance = stats.anderson(values, dist='norm')
        normality_test = {
            'test': 'Anderson-Darling',
            'statistic': ad_stat,
            'critical_values': ad_critical.tolist(),
            'significance_levels': ad_significance.tolist(),
            'p_value': estimate_anderson_darling_p_value(ad_stat, n)
        }
    else:
        normality_test = None
    
    return {
        'success': True,
        'distribution': distribution,
        'plotting_positions': plotting_positions.tolist(),
        'theoretical_quantiles': theoretical_quantiles.tolist(),
        'sorted_values': sorted_values.tolist(),
        'transformed_data': transformed_data.tolist(),
        'goodness_of_fit': {
            'correlation_coefficient': correlation,
            'r_squared': r_value**2,
            'slope': slope,
            'intercept': intercept,
            'interpretation': interpret_correlation(correlation, distribution)
        },
        'outliers': {
            'indices': outliers,
            'count': len(outliers),
            'values': [sorted_values[i] for i in outliers]
        },
        'confidence_level': confidence_level,
        'normality_test': normality_test,
        'interpretation': interpret_probability_plot(correlation, len(outliers), distribution),
        'analysis_type': 'probability_plot'
    }


# Helper functions

def check_western_electric_rules(values: np.ndarray, mean: float, ucl: float, 
                               lcl: float, sigma: float) -> List[Dict[str, Any]]:
    """Check Western Electric rules for control chart violations"""
    violations = []
    n = len(values)
    
    # Rule 1: Point beyond control limits (already checked in main function)
    
    # Rule 2: 2 out of 3 consecutive points beyond 2-sigma
    two_sigma_upper = mean + 2 * sigma
    two_sigma_lower = mean - 2 * sigma
    
    for i in range(n - 2):
        beyond_2sigma = sum(1 for j in range(i, i + 3) 
                           if values[j] > two_sigma_upper or values[j] < two_sigma_lower)
        if beyond_2sigma >= 2:
            violations.append({
                'rule': 2,
                'description': '2 out of 3 points beyond 2-sigma',
                'points': list(range(i, i + 3))
            })
    
    # Rule 3: 4 out of 5 consecutive points beyond 1-sigma
    one_sigma_upper = mean + sigma
    one_sigma_lower = mean - sigma
    
    for i in range(n - 4):
        beyond_1sigma = sum(1 for j in range(i, i + 5) 
                           if values[j] > one_sigma_upper or values[j] < one_sigma_lower)
        if beyond_1sigma >= 4:
            violations.append({
                'rule': 3,
                'description': '4 out of 5 points beyond 1-sigma',
                'points': list(range(i, i + 5))
            })
    
    # Rule 4: 8 consecutive points on one side of center line
    for i in range(n - 7):
        all_above = all(values[j] > mean for j in range(i, i + 8))
        all_below = all(values[j] < mean for j in range(i, i + 8))
        if all_above or all_below:
            violations.append({
                'rule': 4,
                'description': '8 consecutive points on one side of center line',
                'points': list(range(i, i + 8))
            })
    
    return violations


def calculate_tukey_hsd(groups: Dict[str, np.ndarray], msw: float, alpha: float = 0.05) -> Dict[str, Any]:
    """Calculate Tukey HSD post-hoc comparisons"""
    group_names = list(groups.keys())
    group_means = {name: np.mean(data) for name, data in groups.items()}
    group_sizes = {name: len(data) for name, data in groups.items()}
    
    # Degrees of freedom for error
    df_error = sum(len(data) for data in groups.values()) - len(groups)
    
    # Critical value for Tukey HSD
    k = len(groups)
    q_critical = stats.tukey_hsd.critical_value(alpha, k, df_error)
    
    comparisons = []
    
    for i, name1 in enumerate(group_names):
        for j, name2 in enumerate(group_names):
            if i < j:  # Avoid duplicate comparisons
                mean1 = group_means[name1]
                mean2 = group_means[name2]
                n1 = group_sizes[name1]
                n2 = group_sizes[name2]
                
                # Calculate HSD
                pooled_error = msw * (1/n1 + 1/n2) / 2
                hsd = q_critical * np.sqrt(pooled_error)
                
                # Test significance
                diff = abs(mean1 - mean2)
                significant = diff > hsd
                
                comparisons.append({
                    'groups': f"{name1} vs {name2}",
                    'mean_difference': mean1 - mean2,
                    'hsd': hsd,
                    'significant': significant,
                    'p_value': estimate_tukey_p_value(diff, hsd, k, df_error)
                })
    
    return {
        'method': 'Tukey HSD',
        'alpha': alpha,
        'critical_value': q_critical,
        'comparisons': comparisons
    }


def calculate_gini_coefficient(values: List[float]) -> float:
    """Calculate Gini coefficient for inequality measurement"""
    sorted_values = sorted(values)
    n = len(sorted_values)
    
    if n == 0:
        return 0
    
    # Calculate Gini coefficient
    total = sum(sorted_values)
    if total == 0:
        return 0
    
    gini_sum = sum((2 * (i + 1) - n - 1) * value for i, value in enumerate(sorted_values))
    gini = gini_sum / (n * total)
    
    return gini


def estimate_anderson_darling_p_value(statistic: float, n: int) -> float:
    """Estimate p-value for Anderson-Darling test"""
    # Simplified p-value estimation
    if statistic < 0.2:
        return 0.8
    elif statistic < 0.34:
        return 0.5
    elif statistic < 0.47:
        return 0.25
    elif statistic < 0.64:
        return 0.1
    elif statistic < 0.78:
        return 0.05
    elif statistic < 0.91:
        return 0.025
    elif statistic < 1.09:
        return 0.01
    else:
        return 0.005


def estimate_tukey_p_value(diff: float, hsd: float, k: int, df: int) -> float:
    """Estimate p-value for Tukey HSD comparison"""
    # Simplified p-value estimation
    ratio = diff / hsd
    if ratio < 1.0:
        return 0.9
    elif ratio < 1.5:
        return 0.5
    elif ratio < 2.0:
        return 0.1
    else:
        return 0.01


# Interpretation functions

def interpret_i_chart(out_of_control_count: int, violations: List, n: int) -> str:
    """Generate interpretation for I-Chart results"""
    if out_of_control_count == 0 and not violations:
        return "Process appears to be in statistical control with no points beyond control limits or Western Electric rule violations."
    elif out_of_control_count > 0:
        return f"Process shows {out_of_control_count} out-of-control points ({out_of_control_count/n*100:.1f}% of data). Investigate special causes."
    else:
        return f"Process has {len(violations)} Western Electric rule violations. Pattern suggests potential process instability."


def interpret_capability(cpk: float, ppm: float, sigma_level: float) -> str:
    """Generate interpretation for capability analysis"""
    if cpk >= 1.67:
        capability = "Excellent"
    elif cpk >= 1.33:
        capability = "Good"
    elif cpk >= 1.0:
        capability = "Marginal"
    else:
        capability = "Poor"
    
    return f"Process capability is {capability} (Cpk = {cpk:.3f}). Expected defect rate: {ppm:.0f} PPM ({sigma_level:.1f} sigma level)."


def interpret_anova(f_stat: float, p_value: float, significant: bool, k: int) -> str:
    """Generate interpretation for ANOVA results"""
    if significant:
        return f"Significant difference detected between groups (F = {f_stat:.3f}, p = {p_value:.4f}). At least one group mean differs from others."
    else:
        return f"No significant difference between group means (F = {f_stat:.3f}, p = {p_value:.4f}). Groups appear statistically similar."


def interpret_pareto(vital_count: int, total_count: int, vital_percentage: float) -> str:
    """Generate interpretation for Pareto analysis"""
    return f"Pareto analysis identifies {vital_count} out of {total_count} categories ({vital_count/total_count*100:.1f}%) as 'vital few', accounting for {vital_percentage:.1f}% of total impact."


def interpret_probability_plot(correlation: float, outlier_count: int, distribution: str) -> str:
    """Generate interpretation for probability plot"""
    if correlation >= 0.99:
        fit = "Excellent"
    elif correlation >= 0.95:
        fit = "Good"
    elif correlation >= 0.90:
        fit = "Fair"
    else:
        fit = "Poor"
    
    outlier_text = f" {outlier_count} potential outliers detected." if outlier_count > 0 else ""
    
    return f"{fit} fit to {distribution} distribution (r = {correlation:.4f}).{outlier_text}"


def interpret_correlation(correlation: float, distribution: str) -> str:
    """Interpret correlation coefficient for distribution fit"""
    if correlation >= 0.99:
        return "Excellent fit - data closely follows expected distribution"
    elif correlation >= 0.95:
        return "Good fit - data generally follows expected distribution"
    elif correlation >= 0.90:
        return "Fair fit - data shows some deviation from expected distribution"
    else:
        return "Poor fit - data significantly deviates from expected distribution"


def interpret_gini_coefficient(gini: float) -> str:
    """Interpret Gini coefficient values"""
    if gini < 0.2:
        return "Low inequality - values are relatively evenly distributed"
    elif gini < 0.5:
        return "Moderate inequality - some concentration of values"
    elif gini < 0.8:
        return "High inequality - significant concentration in few categories"
    else:
        return "Very high inequality - extreme concentration (classic Pareto pattern)"