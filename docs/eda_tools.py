"""
ESTIEM EDA Toolkit - Browser Optimized Version
Auto-generated from unified core - DO NOT EDIT MANUALLY
Generated from: C:\Projects\ESTIEM-eda\src\estiem_eda\browser\core_browser.py
"""

"""
Browser-compatible core calculations for ESTIEM EDA
Unified source of truth for both MCP and web implementations
"""

# Browser compatibility imports - these work in both Python and Pyodide
try:
    import numpy as np
    from scipy import stats
    import json
    import math
    HAS_SCIPY = True
except ImportError:
    # Fallback for minimal environments
    import math
    import json
    np = None
    stats = None
    HAS_SCIPY = False

from typing import Dict, Any, List, Union, Optional


class BrowserCompatibleStats:
    """Statistics functions that work in browser environment."""
    
    @staticmethod
    def mean(data):
        """Calculate mean."""
        if np is not None:
            return float(np.mean(data))
        return sum(data) / len(data)
    
    @staticmethod
    def std(data, ddof=0):
        """Calculate standard deviation."""
        if np is not None:
            return float(np.std(data, ddof=ddof))
        
        n = len(data)
        if n < 2:
            return 0.0
        mean_val = sum(data) / n
        variance = sum((x - mean_val) ** 2 for x in data) / (n - ddof)
        return math.sqrt(variance)
    
    @staticmethod
    def norm_cdf(x):
        """Normal CDF approximation."""
        if stats is not None:
            return float(stats.norm.cdf(x))
        
        # Abramowitz and Stegun approximation
        if x < 0:
            return 1 - BrowserCompatibleStats.norm_cdf(-x)
        
        # Constants
        a1, a2, a3, a4, a5 = 0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429
        p = 0.3275911
        
        t = 1.0 / (1.0 + p * x)
        y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-x * x / 2)
        
        return y / math.sqrt(2 * math.pi)
    
    @staticmethod
    def norm_ppf(p):
        """Normal percent point function (inverse CDF)."""
        if stats is not None:
            return float(stats.norm.ppf(p))
        
        # Beasley-Springer-Moro approximation
        if p <= 0 or p >= 1:
            raise ValueError("Probability must be between 0 and 1")
        
        if p == 0.5:
            return 0.0
        
        # Transform to standard normal
        if p < 0.5:
            sign = -1
            p = 1 - p
        else:
            sign = 1
        
        t = math.sqrt(-2 * math.log(p))
        
        # Coefficients
        c0, c1, c2 = 2.515517, 0.802853, 0.010328
        d1, d2, d3 = 1.432788, 0.189269, 0.001308
        
        x = t - ((c2 * t + c1) * t + c0) / (((d3 * t + d2) * t + d1) * t + 1.0)
        
        return sign * x
    
    @staticmethod
    def f_cdf(x, df1, df2):
        """F-distribution CDF approximation."""
        if stats is not None:
            return float(stats.f.cdf(x, df1, df2))
        
        # Simple approximation for browser - not highly accurate but functional
        if x <= 0:
            return 0.0
        if x >= 100:
            return 1.0
        
        # Rough approximation based on normal approximation
        # This is simplified for browser compatibility
        z = (x - 1) / math.sqrt(2 * (1/df1 + 1/df2))
        return BrowserCompatibleStats.norm_cdf(z)


# Helper function for JsProxy conversion
def convert_js_to_python(obj):
    """Convert JavaScript objects to Python equivalents in Pyodide."""
    # Check if we're in a Pyodide environment and obj is a JsProxy
    try:
        # Try to access the pyodide module
        import pyodide
        if hasattr(pyodide.ffi, 'JsProxy') and isinstance(obj, pyodide.ffi.JsProxy):
            # Convert JsProxy to Python object
            return obj.to_py()
    except (ImportError, AttributeError):
        # Not in Pyodide or no JsProxy, return as-is
        pass
    return obj

def safe_float_conversion(value):
    """Safely convert a value to float, handling JsProxy objects."""
    # First convert from JsProxy if needed
    value = convert_js_to_python(value)
    
    # Handle string representations
    if isinstance(value, str):
        value = value.strip()
        if value == '' or value.lower() in ['nan', 'null', 'undefined']:
            return None
    
    try:
        result = float(value)
        return result if not (math.isnan(result) or math.isinf(result)) else None
    except (ValueError, TypeError):
        return None

# Core validation functions
def validate_numeric_data_browser(data: Any, min_points: int = 3) -> List[float]:
    """Validate numeric data for browser environment."""
    # Convert JsProxy objects to Python first
    data = convert_js_to_python(data)
    
    # Handle various input formats
    if isinstance(data, dict):
        if 'data' in data:
            data = data['data']
        else:
            # Find first numeric column
            for value in data.values():
                if isinstance(value, (list, tuple)):
                    data = value
                    break
            else:
                raise ValueError("No suitable numeric data found")
    
    # Extract from list of dictionaries 
    if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
        # Find first numeric column
        numeric_col = None
        for key in data[0].keys():
            if safe_float_conversion(data[0][key]) is not None:
                numeric_col = key
                break
        
        if numeric_col is None:
            raise ValueError("No numeric columns found")
        
        values = []
        for row in data:
            row = convert_js_to_python(row)
            if numeric_col in row:
                val = safe_float_conversion(row[numeric_col])
                if val is not None:
                    values.append(val)
        data = values
    
    # Convert to list of floats
    try:
        if np is not None:
            # Convert each item safely first
            safe_data = []
            for item in data:
                val = safe_float_conversion(item)
                if val is not None:
                    safe_data.append(val)
            values = safe_data
        else:
            values = []
            for item in data:
                val = safe_float_conversion(item)
                if val is not None:
                    values.append(val)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Cannot convert to numeric array: {e}")
    
    if len(values) < min_points:
        raise ValueError(f"Need at least {min_points} valid points, got {len(values)}")
    
    return values


def validate_groups_data_browser(data: Dict[str, Any]) -> Dict[str, List[float]]:
    """Validate groups data for ANOVA."""
    # Convert JsProxy objects to Python first
    data = convert_js_to_python(data)
    
    if not isinstance(data, dict) or len(data) < 2:
        raise ValueError("Need at least 2 groups")
    
    validated_groups = {}
    for name, group_data in data.items():
        values = validate_numeric_data_browser(group_data, min_points=2)
        validated_groups[str(name)] = values
    
    if len(validated_groups) < 2:
        raise ValueError("Need at least 2 valid groups")
    
    return validated_groups


def validate_pareto_data_browser(data: Any) -> Dict[str, float]:
    """Validate Pareto data."""
    # Convert JsProxy objects to Python first
    data = convert_js_to_python(data)
    
    # Handle list of records
    if isinstance(data, list) and data and isinstance(data[0], dict):
        first_row = data[0]
        cat_col = None
        val_col = None
        
        for key, value in first_row.items():
            if isinstance(value, str) and cat_col is None:
                cat_col = key
            elif isinstance(value, (int, float)) and val_col is None:
                val_col = key
        
        if cat_col is None:
            raise ValueError("No categorical column found")
        
        if val_col is None:
            # Count occurrences
            categories = {}
            for row in data:
                cat = str(row[cat_col])
                categories[cat] = categories.get(cat, 0) + 1
            data = categories
        else:
            # Sum values by category
            categories = {}
            for row in data:
                row = convert_js_to_python(row)
                cat = str(row[cat_col])
                val = safe_float_conversion(row[val_col])
                if val is not None:
                    categories[cat] = categories.get(cat, 0) + val
            data = categories
    
    if not isinstance(data, dict) or not data:
        raise ValueError("Invalid Pareto data format")
    
    validated_data = {}
    for category, value in data.items():
        val = safe_float_conversion(value)
        if val is None:
            raise ValueError(f"Invalid value for {category}: {value}")
        if val < 0:
            raise ValueError(f"Negative value for {category}: {val}")
        validated_data[str(category)] = val
    
    if sum(validated_data.values()) == 0:
        raise ValueError("All values are zero")
    
    return validated_data


# Core calculation functions - unified for both environments
def calculate_i_chart_browser(values: List[float], title: str = "I-Chart Analysis") -> Dict[str, Any]:
    """Calculate I-Chart statistics - browser compatible."""
    n = len(values)
    mean = BrowserCompatibleStats.mean(values)
    
    # Moving range calculation
    moving_range = [abs(values[i+1] - values[i]) for i in range(n-1)]
    avg_mr = BrowserCompatibleStats.mean(moving_range) if moving_range else 0
    
    # Control limits
    d2 = 1.128  # Constant for individual charts
    sigma_hat = avg_mr / d2 if avg_mr > 0 else 0
    ucl = mean + 3 * sigma_hat
    lcl = mean - 3 * sigma_hat
    
    # Out of control points
    out_of_control = []
    for i, value in enumerate(values):
        if value > ucl or value < lcl:
            out_of_control.append(i)
    
    # Control assessment
    if len(out_of_control) == 0:
        control_status = "In Statistical Control"
        stability = "Process appears stable"
    else:
        control_status = "Out of Control"
        stability = f"Process has {len(out_of_control)} out-of-control points"
    
    return {
        'success': True,
        'analysis_type': 'i_chart',
        'statistics': {
            'sample_size': n,
            'mean': round(mean, 4),
            'sigma_hat': round(sigma_hat, 4),
            'ucl': round(ucl, 4),
            'lcl': round(lcl, 4),
            'out_of_control_points': len(out_of_control),
            'avg_moving_range': round(avg_mr, 4),
            'control_status': control_status
        },
        'out_of_control_indices': out_of_control,
        'data_points': values,
        'control_limits': {'ucl': ucl, 'lcl': lcl, 'center_line': mean},
        'interpretation': f"{stability} with process mean of {mean:.3f}. {control_status.lower()} based on 3-sigma limits."
    }


def calculate_capability_browser(values: List[float], lsl: float, usl: float, target: Optional[float] = None) -> Dict[str, Any]:
    """Calculate process capability - browser compatible."""
    n = len(values)
    mean = BrowserCompatibleStats.mean(values)
    std_dev = BrowserCompatibleStats.std(values, ddof=1)
    
    if target is None:
        target = (lsl + usl) / 2
    
    # Capability indices
    tolerance = usl - lsl
    cp = tolerance / (6 * std_dev) if std_dev > 0 else float('inf')
    
    cpu = (usl - mean) / (3 * std_dev) if std_dev > 0 else float('inf')
    cpl = (mean - lsl) / (3 * std_dev) if std_dev > 0 else float('inf')
    cpk = min(cpu, cpl)
    
    # Performance indices (population std dev)
    pop_std = BrowserCompatibleStats.std(values, ddof=0)
    pp = tolerance / (6 * pop_std) if pop_std > 0 else float('inf')
    ppk = min((usl - mean) / (3 * pop_std), (mean - lsl) / (3 * pop_std)) if pop_std > 0 else float('inf')
    
    # Defect analysis using normal approximation
    z_lower = (lsl - mean) / std_dev if std_dev > 0 else -float('inf')
    z_upper = (usl - mean) / std_dev if std_dev > 0 else float('inf')
    
    try:
        ppm_lower = BrowserCompatibleStats.norm_cdf(z_lower) * 1_000_000
        ppm_upper = (1 - BrowserCompatibleStats.norm_cdf(z_upper)) * 1_000_000
        ppm_total = ppm_lower + ppm_upper
        
        # Six Sigma level approximation
        if ppm_total > 0 and ppm_total < 2_000_000:
            z_shift = BrowserCompatibleStats.norm_ppf(1 - ppm_total / 2_000_000)
            sigma_level = z_shift + 1.5  # Add typical 1.5 sigma shift
            if sigma_level < 0:
                sigma_level = 0
            elif sigma_level > 6:
                sigma_level = 6
        else:
            sigma_level = 6.0 if ppm_total <= 3.4 else 0.0
            
    except (ValueError, ZeroDivisionError):
        ppm_lower = ppm_upper = ppm_total = 0
        sigma_level = 6.0
    
    # Capability assessment
    if cpk >= 1.67:
        capability = "Excellent"
    elif cpk >= 1.33:
        capability = "Good"  
    elif cpk >= 1.0:
        capability = "Marginal"
    else:
        capability = "Poor"
    
    return {
        'success': True,
        'analysis_type': 'process_capability',
        'statistics': {
            'sample_size': n,
            'mean': round(mean, 4),
            'std_dev': round(std_dev, 4),
            'lsl': lsl,
            'usl': usl,
            'target': target
        },
        'capability_indices': {
            'cp': round(cp, 4),
            'cpk': round(cpk, 4), 
            'cpu': round(cpu, 4),
            'cpl': round(cpl, 4),
            'pp': round(pp, 4),
            'ppk': round(ppk, 4)
        },
        'defect_analysis': {
            'ppm_lower': round(ppm_lower, 0),
            'ppm_upper': round(ppm_upper, 0),
            'ppm_total': round(ppm_total, 0),
            'sigma_level': round(sigma_level, 2)
        },
        'interpretation': f"{capability} process capability (Cpk = {cpk:.3f}). Expected defect rate: {ppm_total:.0f} PPM, {sigma_level:.1f} Sigma level."
    }


def calculate_anova_browser(groups: Dict[str, List[float]], alpha: float = 0.05) -> Dict[str, Any]:
    """Calculate one-way ANOVA - browser compatible."""
    group_names = list(groups.keys())
    group_data = list(groups.values())
    
    k = len(groups)  # Number of groups
    group_sizes = [len(group) for group in group_data]
    n_total = sum(group_sizes)
    
    if n_total < k + 1:
        raise ValueError("Insufficient data for ANOVA")
    
    # Calculate means
    all_data = []
    for group in group_data:
        all_data.extend(group)
    
    grand_mean = BrowserCompatibleStats.mean(all_data)
    group_means = [BrowserCompatibleStats.mean(group) for group in group_data]
    
    # Sum of squares
    # Between groups (SSB)
    ssb = sum(n * (mean - grand_mean)**2 for n, mean in zip(group_sizes, group_means))
    
    # Within groups (SSW) 
    ssw = 0
    for group in group_data:
        group_mean = BrowserCompatibleStats.mean(group)
        ssw += sum((x - group_mean)**2 for x in group)
    
    # Degrees of freedom
    df_between = k - 1
    df_within = n_total - k
    
    # Mean squares
    msb = ssb / df_between if df_between > 0 else 0
    msw = ssw / df_within if df_within > 0 else 0
    
    # F-statistic and p-value
    f_statistic = msb / msw if msw > 0 else float('inf')
    
    try:
        p_value = 1 - BrowserCompatibleStats.f_cdf(f_statistic, df_between, df_within)
        if p_value < 0:
            p_value = 0
        elif p_value > 1:
            p_value = 1
    except (ValueError, ZeroDivisionError):
        p_value = 0 if f_statistic > 10 else 1
    
    significant = p_value < alpha
    
    # Effect size (eta-squared)
    eta_squared = ssb / (ssb + ssw) if (ssb + ssw) > 0 else 0
    
    return {
        'success': True,
        'analysis_type': 'anova_boxplot',
        'anova_results': {
            'f_statistic': round(f_statistic, 4),
            'p_value': round(p_value, 4),
            'significant': significant,
            'alpha': alpha,
            'degrees_freedom': [df_between, df_within]
        },
        'group_statistics': {
            name: {
                'mean': round(BrowserCompatibleStats.mean(data), 4),
                'std': round(BrowserCompatibleStats.std(data, ddof=1), 4),
                'size': len(data)
            } for name, data in groups.items()
        },
        'effect_size': {
            'eta_squared': round(eta_squared, 4)
        },
        'grand_mean': round(grand_mean, 4),
        'interpretation': f"{'Significant' if significant else 'No significant'} difference between groups (F({df_between},{df_within}) = {f_statistic:.3f}, p = {p_value:.4f}). Effect size η² = {eta_squared:.3f}."
    }


def calculate_pareto_browser(data: Dict[str, float], threshold: float = 0.8) -> Dict[str, Any]:
    """Calculate Pareto analysis - browser compatible."""
    # Sort by value descending
    sorted_items = sorted(data.items(), key=lambda x: x[1], reverse=True)
    total = sum(data.values())
    
    if total == 0:
        raise ValueError("Total value cannot be zero")
    
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
    
    # Find vital few (categories that contribute to threshold%)
    vital_few_indices = []
    for i, cum_pct in enumerate(cumulative_percentages):
        vital_few_indices.append(i)
        if cum_pct >= threshold * 100:
            break
    
    vital_few_categories = [categories[i] for i in vital_few_indices]
    vital_few_percentage = cumulative_percentages[vital_few_indices[-1]] if vital_few_indices else 0
    
    # Gini coefficient calculation
    sorted_values = sorted(values)
    n = len(sorted_values)
    if n > 1:
        gini_sum = sum((2 * (i + 1) - n - 1) * value for i, value in enumerate(sorted_values))
        gini = gini_sum / (n * total)
    else:
        gini = 0
    
    # Gini interpretation
    if gini > 0.5:
        gini_interp = "High inequality"
    elif gini > 0.2:
        gini_interp = "Moderate inequality"
    else:
        gini_interp = "Low inequality"
    
    return {
        'success': True,
        'analysis_type': 'pareto_analysis',
        'categories': categories,
        'values': values,
        'percentages': [round(p, 1) for p in percentages],
        'cumulative_percentages': [round(cp, 1) for cp in cumulative_percentages],
        'vital_few': {
            'categories': vital_few_categories,
            'count': len(vital_few_categories),
            'contribution_percent': round(vital_few_percentage, 1)
        },
        'statistics': {
            'total_count': round(total, 0),
            'gini_coefficient': round(gini, 4),
            'gini_interpretation': gini_interp,
            'categories_analyzed': len(categories)
        },
        'interpretation': f"The vital few: {len(vital_few_categories)} categories account for {vital_few_percentage:.1f}% of total impact. Gini coefficient of {gini:.3f} indicates {gini_interp.lower()}."
    }


def calculate_probability_plot_browser(values: List[float], distribution: str = 'normal', confidence_level: float = 0.95) -> Dict[str, Any]:
    """Calculate probability plot - browser compatible."""
    n = len(values)
    sorted_values = sorted(values)
    
    # Plotting positions using median rank
    plotting_positions = [(i + 0.5) / n for i in range(n)]
    
    # Generate theoretical quantiles based on distribution
    if distribution == 'normal':
        try:
            theoretical_quantiles = [BrowserCompatibleStats.norm_ppf(p) for p in plotting_positions]
            transformed_data = sorted_values
        except ValueError as e:
            raise ValueError(f"Error calculating normal quantiles: {e}")
            
    elif distribution == 'lognormal':
        if any(v <= 0 for v in sorted_values):
            raise ValueError("Lognormal distribution requires positive values")
        try:
            theoretical_quantiles = [BrowserCompatibleStats.norm_ppf(p) for p in plotting_positions]
            transformed_data = [math.log(v) for v in sorted_values]
        except ValueError as e:
            raise ValueError(f"Error calculating lognormal quantiles: {e}")
            
    elif distribution == 'weibull':
        if any(v <= 0 for v in sorted_values):
            raise ValueError("Weibull distribution requires positive values")
        try:
            # Weibull plotting positions: ln(-ln(1-p))
            theoretical_quantiles = [math.log(-math.log(1 - p)) for p in plotting_positions]
            transformed_data = [math.log(v) for v in sorted_values]
        except (ValueError, math.domain) as e:
            raise ValueError(f"Error calculating Weibull quantiles: {e}")
            
    else:
        raise ValueError(f"Unsupported distribution: {distribution}")
    
    # Calculate correlation coefficient
    n_points = len(theoretical_quantiles)
    if n_points < 2:
        correlation = 0
    else:
        # Manual correlation calculation
        mean_x = sum(theoretical_quantiles) / n_points
        mean_y = sum(transformed_data) / n_points
        
        numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(theoretical_quantiles, transformed_data))
        sum_sq_x = sum((x - mean_x) ** 2 for x in theoretical_quantiles)
        sum_sq_y = sum((y - mean_y) ** 2 for y in transformed_data)
        
        if sum_sq_x > 0 and sum_sq_y > 0:
            correlation = numerator / math.sqrt(sum_sq_x * sum_sq_y)
        else:
            correlation = 0
    
    # Assess goodness of fit
    if correlation >= 0.99:
        fit_quality = "Excellent"
    elif correlation >= 0.95:
        fit_quality = "Good"  
    elif correlation >= 0.90:
        fit_quality = "Fair"
    else:
        fit_quality = "Poor"
    
    # Simple outlier detection (2 standard deviations)
    if len(transformed_data) > 2:
        data_mean = BrowserCompatibleStats.mean(transformed_data)
        data_std = BrowserCompatibleStats.std(transformed_data, ddof=1)
        outlier_threshold = 2 * data_std
        
        outlier_indices = []
        outlier_values = []
        for i, value in enumerate(transformed_data):
            if abs(value - data_mean) > outlier_threshold:
                outlier_indices.append(i)
                outlier_values.append(sorted_values[i])  # Original scale
    else:
        outlier_indices = []
        outlier_values = []
    
    return {
        'success': True,
        'analysis_type': 'probability_plot', 
        'distribution': distribution,
        'plotting_positions': plotting_positions,
        'theoretical_quantiles': theoretical_quantiles,
        'sorted_values': sorted_values,
        'goodness_of_fit': {
            'correlation_coefficient': round(correlation, 4),
            'r_squared': round(correlation ** 2, 4),
            'interpretation': fit_quality
        },
        'outliers': {
            'indices': outlier_indices,
            'count': len(outlier_indices), 
            'values': outlier_values
        },
        'confidence_level': confidence_level,
        'interpretation': f"{fit_quality} fit to {distribution} distribution (r = {correlation:.4f}). {len(outlier_indices)} potential outliers detected."
    }


def generate_sample_data_browser(sample_type: str = 'manufacturing') -> Dict[str, Any]:
    """Generate sample data for testing - browser compatible."""
    # Simple random number generation for browser compatibility
    def simple_random():
        # Linear congruential generator for reproducible results
        if not hasattr(simple_random, 'seed'):
            simple_random.seed = 42
        simple_random.seed = (simple_random.seed * 1664525 + 1013904223) % (2**32)
        return simple_random.seed / (2**32)
    
    def normal_approx(mean=0, std=1):
        # Box-Muller approximation
        if not hasattr(normal_approx, 'has_spare'):
            normal_approx.has_spare = False
        
        if normal_approx.has_spare:
            normal_approx.has_spare = False
            return normal_approx.spare * std + mean
        
        normal_approx.has_spare = True
        u = simple_random()
        v = simple_random()
        mag = std * math.sqrt(-2 * math.log(u))
        normal_approx.spare = mag * math.cos(2 * math.pi * v)
        return mag * math.sin(2 * math.pi * v) + mean
    
    if sample_type == 'manufacturing':
        n = 100
        lines = ['Line_A', 'Line_B', 'Line_C']
        
        data = []
        for i in range(n):
            line_idx = int(simple_random() * 3)
            line = lines[line_idx]
            
            if line == 'Line_A':
                measurement = normal_approx(10.0, 0.3)
            elif line == 'Line_B':
                measurement = normal_approx(9.8, 0.5)
            else:
                measurement = normal_approx(10.2, 0.4)
            
            data.append({
                'sample_id': i + 1,
                'measurement': round(measurement, 3),
                'line': line,
                'defects': int(simple_random() * 5),
                'temperature': round(normal_approx(25, 2), 1)
            })
        
        return {
            'data': data,
            'headers': ['sample_id', 'measurement', 'line', 'defects', 'temperature'],
            'filename': 'manufacturing_sample.csv'
        }
        
    elif sample_type == 'quality':
        defect_types = ['Surface', 'Dimensional', 'Assembly', 'Material', 'Electrical']
        defect_counts = [45, 32, 18, 12, 8]
        
        data = []
        for defect_type, count in zip(defect_types, defect_counts):
            data.append({
                'defect_type': defect_type,
                'count': count
            })
        
        return {
            'data': data,
            'headers': ['defect_type', 'count'],
            'filename': 'quality_sample.csv'
        }
        
    elif sample_type == 'process':
        n = 100
        data = []
        for i in range(n):
            value = 100 + 0.1 * i + normal_approx(0, 2)
            data.append({
                'time': i + 1,
                'process_value': round(value, 2),
                'temperature': round(normal_approx(80, 5), 1)
            })
        
        return {
            'data': data,
            'headers': ['time', 'process_value', 'temperature'],
            'filename': 'process_sample.csv'
        }
    
    return {'data': [], 'headers': [], 'filename': 'empty_sample.csv'}


# Web-specific adapter functions
def run_analysis(analysis_type: str, data: Any, headers: List[str], parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main analysis dispatcher for web app - unified with MCP.
    
    Args:
        analysis_type: Type of analysis to run
        data: Input data in various formats
        headers: Column headers if applicable
        parameters: Analysis parameters
        
    Returns:
        Standardized analysis results
    """
    
    try:
        print(f"DEBUG: Starting {analysis_type} analysis")
        print(f"DEBUG: Data type: {type(data)}")
        print(f"DEBUG: Parameters: {parameters}")
        
        if analysis_type == 'process_analysis':
            # Handle web data format with column selection
            if isinstance(data, list) and data and isinstance(data[0], dict):
                data_column = parameters.get('dataColumn')
                if not data_column:
                    raise ValueError("Process analysis requires a data column selection")
                
                # Extract numeric values from selected column
                values = []
                for row in data:
                    row = convert_js_to_python(row)
                    value = row.get(data_column)
                    converted_value = safe_float_conversion(value)
                    if converted_value is not None:
                        values.append(converted_value)
                
                print(f"DEBUG: Extracted {len(values)} values from column '{data_column}'")
                if len(values) < 10:
                    raise ValueError(f"Process analysis requires at least 10 valid numeric values, got {len(values)}")
            else:
                values = validate_numeric_data_browser(data, min_points=10)
            
            # Parse parameters
            spec_limits = parameters.get('specification_limits', {})
            distribution = parameters.get('distribution', 'normal')
            confidence_level = float(parameters.get('confidence_level', 0.95))
            
            # Run individual analyses
            result = {}
            
            # 1. Stability Analysis (I-Chart)
            print("DEBUG: Starting I-Chart analysis")
            try:
                stability_result = calculate_i_chart_browser(values, "Stability Assessment")
                print("DEBUG: I-Chart analysis completed successfully")
                result['stability_analysis'] = {
                    'statistics': stability_result.get('statistics', {}),
                    'out_of_control_indices': stability_result.get('out_of_control_indices', []),
                    'control_status': 'in_control' if len(stability_result.get('out_of_control_indices', [])) == 0 else 'out_of_control'
                }
            except Exception as e:
                print(f"DEBUG: I-Chart analysis failed: {e}")
                result['stability_analysis'] = {'error': str(e)}
            
            # 2. Capability Analysis (if spec limits provided)
            print(f"DEBUG: Checking capability analysis - spec_limits: {spec_limits}")
            if spec_limits and ('lsl' in spec_limits or 'usl' in spec_limits):
                print("DEBUG: Starting capability analysis")
                try:
                    lsl = spec_limits.get('lsl')
                    usl = spec_limits.get('usl')
                    target = spec_limits.get('target')
                    
                    capability_result = calculate_capability_browser(values, lsl, usl, target)
                    print("DEBUG: Capability analysis completed successfully")
                    result['capability_analysis'] = {
                        'statistics': capability_result.get('statistics', {}),
                        'capability_indices': capability_result.get('capability_indices', {}),
                        'defect_analysis': capability_result.get('defect_analysis', {}),
                        'specification_limits': spec_limits
                    }
                except Exception as e:
                    print(f"DEBUG: Capability analysis failed: {e}")
                    result['capability_analysis'] = {'error': str(e)}
            else:
                result['capability_analysis'] = {
                    'note': 'Specification limits not provided - capability analysis skipped'
                }
            
            # 3. Distribution Analysis (Probability Plot)
            print("DEBUG: Starting probability plot analysis")
            try:
                distribution_result = calculate_probability_plot_browser(values, distribution, confidence_level)
                print("DEBUG: Probability plot analysis completed successfully")
                result['distribution_analysis'] = {
                    'distribution': distribution,
                    'statistics': distribution_result.get('statistics', {}),
                    'goodness_of_fit': distribution_result.get('goodness_of_fit', {}),
                    'theoretical_quantiles': distribution_result.get('theoretical_quantiles', []),
                    'sorted_values': distribution_result.get('sorted_values', [])
                }
            except Exception as e:
                print(f"DEBUG: Probability plot analysis failed: {e}")
                result['distribution_analysis'] = {'error': str(e)}
            
            # Create comprehensive interpretation
            print("DEBUG: Creating interpretation")
            result['interpretation'] = _create_process_analysis_interpretation(result, len(values))
            
            # Generate combined visualization
            print("DEBUG: Generating chart data")
            result['chart_data'] = _generate_process_analysis_plotly(result, values, spec_limits)
            result['success'] = True
            result['analysis_type'] = 'process_analysis'
            print("DEBUG: Process analysis completed successfully")
            
            return result
            
        elif analysis_type == 'anova':
            # Handle web data format
            if isinstance(data, list) and data and isinstance(data[0], dict):
                value_column = parameters.get('valueColumn')
                group_column = parameters.get('groupColumn')
                
                if not value_column or not group_column:
                    raise ValueError("ANOVA requires value and group columns")
                
                # Group the data
                groups = {}
                for row in data:
                    group = str(row.get(group_column, 'Unknown'))
                    value = row.get(value_column)
                    
                    if value is not None:
                        if group not in groups:
                            groups[group] = []
                        groups[group].append(float(value))
                
                validated_groups = validate_groups_data_browser(groups)
            else:
                validated_groups = validate_groups_data_browser(data)
                
            alpha = float(parameters.get('alpha', 0.05))
            result = calculate_anova_browser(validated_groups, alpha)
            result['chart_data'] = _generate_anova_plotly(result, validated_groups)
            result['success'] = True
            result['analysis_type'] = 'anova'
            return result
            
        elif analysis_type == 'pareto':
            pareto_data = validate_pareto_data_browser(data)
            threshold = float(parameters.get('threshold', 0.8))
            result = calculate_pareto_browser(pareto_data, threshold)
            result['chart_data'] = _generate_pareto_plotly(result)
            result['success'] = True
            result['analysis_type'] = 'pareto'
            return result
            
        else:
            raise ValueError(f'Unknown analysis type: {analysis_type}')
            
    except Exception as e:
        error_message = str(e)
        print(f"ERROR: Analysis error: {error_message}")
        
        # Provide more helpful error messages
        user_message = error_message
        if 'requires at least' in error_message:
            user_message = f"Insufficient data: {error_message}"
        elif 'not provided' in error_message or 'missing' in error_message.lower():
            user_message = f"Missing parameters: {error_message}"
        elif 'invalid' in error_message.lower():
            user_message = f"Data validation failed: {error_message}"
        elif 'column' in error_message.lower():
            user_message = f"Column error: {error_message}"
        
        return {
            'success': False,
            'error': user_message,
            'analysis_type': analysis_type,
            'technical_error': error_message,  # Keep original for debugging
            'chart_data': None,
            'statistics': {},
            'interpretation': ''
        }


def generate_sample_data(sample_type: str) -> Dict[str, Any]:
    """Generate sample data for web app testing."""
    return generate_sample_data_browser(sample_type)


# Plotly.js chart generation functions
def _generate_i_chart_plotly(result: Dict[str, Any], title: str) -> str:
    """Generate Plotly.js chart data for I-Chart."""
    data_points = result.get('data_points', [])
    control_limits = result.get('control_limits', {})
    out_of_control_indices = result.get('out_of_control_indices', [])
    
    x_values = list(range(1, len(data_points) + 1))
    
    # Main data trace
    main_trace = {
        "x": x_values,
        "y": data_points,
        "type": "scatter",
        "mode": "lines+markers",
        "name": "Individual Values",
        "line": {"color": "#1f4e79", "width": 2},
        "marker": {"color": "#1f4e79", "size": 6}
    }
    
    # Out of control points
    if out_of_control_indices:
        ooc_x = [x_values[i] for i in out_of_control_indices]
        ooc_y = [data_points[i] for i in out_of_control_indices]
        
        ooc_trace = {
            "x": ooc_x,
            "y": ooc_y,
            "type": "scatter",
            "mode": "markers",
            "name": f"Out of Control ({len(out_of_control_indices)})",
            "marker": {"color": "red", "size": 8, "symbol": "x"}
        }
    else:
        ooc_trace = None
    
    # Control limit lines
    ucl = control_limits.get('ucl', 0)
    lcl = control_limits.get('lcl', 0)
    center_line = control_limits.get('center_line', 0)
    
    ucl_trace = {
        "x": [1, len(data_points)],
        "y": [ucl, ucl],
        "type": "scatter",
        "mode": "lines",
        "name": f"UCL ({ucl:.3f})",
        "line": {"color": "#f8a978", "width": 2, "dash": "dash"}
    }
    
    lcl_trace = {
        "x": [1, len(data_points)],
        "y": [lcl, lcl],
        "type": "scatter",
        "mode": "lines",
        "name": f"LCL ({lcl:.3f})",
        "line": {"color": "#f8a978", "width": 2, "dash": "dash"}
    }
    
    center_trace = {
        "x": [1, len(data_points)],
        "y": [center_line, center_line],
        "type": "scatter",
        "mode": "lines",
        "name": f"Center Line ({center_line:.3f})",
        "line": {"color": "#7ba7d1", "width": 2}
    }
    
    # Combine traces
    traces = [main_trace, center_trace, ucl_trace, lcl_trace]
    if ooc_trace:
        traces.append(ooc_trace)
    
    layout = {
        "title": {
            "text": title,
            "font": {"size": 16, "color": "#1f4e79"}
        },
        "xaxis": {"title": "Sample Number"},
        "yaxis": {"title": "Individual Value"},
        "legend": {"orientation": "h", "y": -0.2},
        "hovermode": "closest",
        "showlegend": True
    }
    
    return json.dumps({"data": traces, "layout": layout})


def _generate_capability_plotly(result: Dict[str, Any], values: List[float]) -> str:
    """Generate Plotly.js chart data for Process Capability."""
    statistics = result.get('statistics', {})
    lsl = statistics.get('lsl')
    usl = statistics.get('usl')
    target = statistics.get('target')
    capability_indices = result.get('capability_indices', {})
    
    # Histogram of data
    hist_trace = {
        "x": values,
        "type": "histogram",
        "name": "Process Data",
        "marker": {"color": "#7ba7d1", "opacity": 0.7},
        "nbinsx": min(20, max(5, len(values) // 5))
    }
    
    traces = [hist_trace]
    
    # Add specification limits
    y_max = len(values) * 0.8  # Estimate histogram height
    
    if lsl is not None:
        lsl_trace = {
            "x": [lsl, lsl],
            "y": [0, y_max],
            "type": "scatter",
            "mode": "lines",
            "name": f"LSL ({lsl})",
            "line": {"color": "red", "width": 3}
        }
        traces.append(lsl_trace)
    
    if usl is not None:
        usl_trace = {
            "x": [usl, usl],
            "y": [0, y_max],
            "type": "scatter",
            "mode": "lines", 
            "name": f"USL ({usl})",
            "line": {"color": "red", "width": 3}
        }
        traces.append(usl_trace)
    
    if target is not None:
        target_trace = {
            "x": [target, target],
            "y": [0, y_max],
            "type": "scatter",
            "mode": "lines",
            "name": f"Target ({target})",
            "line": {"color": "green", "width": 2, "dash": "dot"}
        }
        traces.append(target_trace)
    
    cpk = capability_indices.get('cpk', 0)
    
    layout = {
        "title": {
            "text": f"Process Capability Analysis (Cpk = {cpk:.3f})",
            "font": {"size": 16, "color": "#1f4e79"}
        },
        "xaxis": {"title": "Value"},
        "yaxis": {"title": "Frequency"},
        "legend": {"orientation": "h", "y": -0.2},
        "showlegend": True
    }
    
    return json.dumps({"data": traces, "layout": layout})


def _generate_anova_plotly(result: Dict[str, Any], groups: Dict[str, List[float]]) -> str:
    """Generate Plotly.js chart data for ANOVA boxplot."""
    anova_results = result.get('anova_results', {})
    f_stat = anova_results.get('f_statistic', 0)
    p_value = anova_results.get('p_value', 1)
    significant = anova_results.get('significant', False)
    
    traces = []
    
    for group_name, group_data in groups.items():
        box_trace = {
            "y": group_data,
            "type": "box",
            "name": group_name,
            "boxpoints": "outliers",
            "marker": {"color": "#1f4e79" if significant else "#7ba7d1"}
        }
        traces.append(box_trace)
    
    significance_text = "Significant" if significant else "Not Significant"
    
    layout = {
        "title": {
            "text": f"ANOVA Results: F = {f_stat:.3f}, p = {p_value:.4f} ({significance_text})",
            "font": {"size": 16, "color": "#1f4e79"}
        },
        "xaxis": {"title": "Groups"},
        "yaxis": {"title": "Values"},
        "showlegend": False
    }
    
    return json.dumps({"data": traces, "layout": layout})


def _generate_pareto_plotly(result: Dict[str, Any]) -> str:
    """Generate Plotly.js chart data for Pareto analysis."""
    categories = result.get('categories', [])
    values = result.get('values', [])
    cumulative_percentages = result.get('cumulative_percentages', [])
    vital_few = result.get('vital_few', {})
    vital_few_categories = vital_few.get('categories', [])
    
    # Bar chart
    bar_colors = ["#1f4e79" if cat in vital_few_categories else "#7ba7d1" for cat in categories]
    
    bar_trace = {
        "x": categories,
        "y": values,
        "type": "bar",
        "name": "Count",
        "yaxis": "y",
        "marker": {"color": bar_colors, "opacity": 0.8}
    }
    
    # Cumulative percentage line
    line_trace = {
        "x": categories,
        "y": cumulative_percentages,
        "type": "scatter",
        "mode": "lines+markers",
        "name": "Cumulative %",
        "yaxis": "y2",
        "line": {"color": "#f8a978", "width": 3},
        "marker": {"size": 8, "color": "#f8a978"}
    }
    
    # 80% threshold line
    threshold_trace = {
        "x": [categories[0], categories[-1]] if categories else [0, 1],
        "y": [80, 80],
        "type": "scatter",
        "mode": "lines",
        "name": "80% Threshold",
        "yaxis": "y2",
        "line": {"color": "red", "width": 2, "dash": "dash"}
    }
    
    vital_count = vital_few.get('count', 0)
    vital_percent = vital_few.get('contribution_percent', 0)
    
    layout = {
        "title": {
            "text": f"Pareto Analysis - Vital Few: {vital_count} categories ({vital_percent:.1f}%)",
            "font": {"size": 16, "color": "#1f4e79"}
        },
        "xaxis": {"title": "Categories"},
        "yaxis": {"title": "Count", "side": "left"},
        "yaxis2": {
            "title": "Cumulative Percentage (%)",
            "side": "right",
            "overlaying": "y",
            "range": [0, 105]
        },
        "legend": {"orientation": "h", "y": -0.2}
    }
    
    return json.dumps({"data": [bar_trace, line_trace, threshold_trace], "layout": layout})


def _generate_probability_plot_plotly(result: Dict[str, Any]) -> str:
    """Generate Plotly.js chart data for Probability Plot."""
    theoretical_quantiles = result.get('theoretical_quantiles', [])
    sorted_values = result.get('sorted_values', [])
    goodness_of_fit = result.get('goodness_of_fit', {})
    correlation = goodness_of_fit.get('correlation_coefficient', 0)
    distribution = result.get('distribution', 'normal')
    outliers = result.get('outliers', {})
    outlier_indices = outliers.get('indices', [])
    
    # Main scatter plot
    scatter_trace = {
        "x": theoretical_quantiles,
        "y": sorted_values,
        "type": "scatter",
        "mode": "markers",
        "name": "Data Points",
        "marker": {"color": "#1f4e79", "size": 6}
    }
    
    traces = [scatter_trace]
    
    # Best fit line (simple linear regression)
    if len(theoretical_quantiles) >= 2:
        # Calculate slope and intercept
        n = len(theoretical_quantiles)
        sum_x = sum(theoretical_quantiles)
        sum_y = sum(sorted_values)
        sum_xy = sum(x * y for x, y in zip(theoretical_quantiles, sorted_values))
        sum_x2 = sum(x * x for x in theoretical_quantiles)
        
        if n * sum_x2 - sum_x * sum_x != 0:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            intercept = (sum_y - slope * sum_x) / n
            
            x_line = [min(theoretical_quantiles), max(theoretical_quantiles)]
            y_line = [slope * x + intercept for x in x_line]
            
            line_trace = {
                "x": x_line,
                "y": y_line,
                "type": "scatter",
                "mode": "lines",
                "name": f"Best Fit (r={correlation:.4f})",
                "line": {"color": "#f8a978", "width": 3}
            }
            traces.append(line_trace)
    
    # Highlight outliers
    if outlier_indices:
        outlier_x = [theoretical_quantiles[i] for i in outlier_indices if i < len(theoretical_quantiles)]
        outlier_y = [sorted_values[i] for i in outlier_indices if i < len(sorted_values)]
        
        outlier_trace = {
            "x": outlier_x,
            "y": outlier_y,
            "type": "scatter",
            "mode": "markers",
            "name": f"Outliers ({len(outlier_indices)})",
            "marker": {"color": "red", "size": 8, "symbol": "diamond"}
        }
        traces.append(outlier_trace)
    
    layout = {
        "title": {
            "text": f"{distribution.title()} Probability Plot (r = {correlation:.4f})",
            "font": {"size": 16, "color": "#1f4e79"}
        },
        "xaxis": {"title": "Theoretical Quantiles"},
        "yaxis": {"title": "Observed Values"},
        "legend": {"orientation": "h", "y": -0.2}
    }
    
    return json.dumps({"data": traces, "layout": layout})


def _create_process_analysis_interpretation(result: Dict[str, Any], sample_size: int) -> str:
    """Create comprehensive interpretation for process analysis."""
    interpretations = []
    
    interpretations.append(f"Process analysis of {sample_size} measurements.")
    
    # Stability assessment
    stability = result.get('stability_analysis', {})
    control_status = stability.get('control_status', 'unknown')
    if control_status == 'in_control':
        interpretations.append("Process appears statistically stable with no out-of-control points detected.")
    elif control_status == 'out_of_control':
        ooc_count = len(stability.get('out_of_control_indices', []))
        interpretations.append(f"Process shows instability with {ooc_count} out-of-control points requiring investigation.")
    
    # Capability assessment
    capability = result.get('capability_analysis', {})
    if 'capability_indices' in capability:
        indices = capability['capability_indices']
        cpk = indices.get('cpk', 0)
        if cpk >= 1.33:
            interpretations.append(f"Process is capable (Cpk = {cpk:.3f}) and meets specification requirements.")
        elif cpk >= 1.0:
            interpretations.append(f"Process has marginal capability (Cpk = {cpk:.3f}) and may need improvement.")
        else:
            interpretations.append(f"Process is not capable (Cpk = {cpk:.3f}) and requires significant improvement.")
    elif 'note' in capability:
        interpretations.append("Capability analysis requires specification limits for assessment.")
    
    # Distribution assessment
    distribution = result.get('distribution_analysis', {})
    if 'goodness_of_fit' in distribution:
        gof = distribution['goodness_of_fit']
        dist_type = distribution.get('distribution', 'normal')
        p_value = gof.get('p_value', 0)
        if p_value > 0.05:
            interpretations.append(f"Data follows {dist_type} distribution (p-value = {p_value:.4f}).")
        else:
            interpretations.append(f"Data does not follow {dist_type} distribution (p-value = {p_value:.4f}).")
    
    return " ".join(interpretations)


def _generate_process_analysis_plotly(result: Dict[str, Any], values: List[float], spec_limits: Dict[str, Any]) -> str:
    """Generate multi-chart Plotly visualization for process analysis."""
    print(f"SUCCESS: Generating process analysis charts with {len(values)} data points")
    print(f"SUCCESS: Available analyses: {list(result.keys())}")
    print(f"SUCCESS: Spec limits provided: {bool(spec_limits)}")
    
    charts = []
    
    # 1. Stability Analysis (I-Chart) - Primary Chart
    stability = result.get('stability_analysis', {})
    if 'statistics' in stability:
        i_chart_result = {
            'data_points': values,
            'control_limits': {
                'ucl': stability['statistics'].get('ucl', 0),
                'lcl': stability['statistics'].get('lcl', 0),
                'cl': stability['statistics'].get('mean', 0),
                'center_line': stability['statistics'].get('mean', 0)
            },
            'out_of_control_indices': stability.get('out_of_control_indices', [])
        }
        
        i_chart_json = _generate_i_chart_plotly(i_chart_result, "Process Control Chart")
        i_chart_data = json.loads(i_chart_json)
        
        charts.append({
            'id': 'stability',
            'title': 'Process Control Chart',
            'subtitle': 'Individual Values Over Time',
            'data': i_chart_data['data'],
            'layout': i_chart_data['layout']
        })
    
    # 2. Capability Analysis (Histogram) - Secondary Chart
    capability = result.get('capability_analysis', {})
    if capability and not capability.get('error') and spec_limits:
        try:
            # Create capability result structure with spec limits
            capability_result = {
                'statistics': {
                    **capability.get('statistics', {}),
                    'lsl': spec_limits.get('lsl'),
                    'usl': spec_limits.get('usl'),
                    'target': spec_limits.get('target')
                },
                'capability_indices': capability.get('capability_indices', {})
            }
            
            capability_chart_json = _generate_capability_plotly(capability_result, values)
            capability_chart_data = json.loads(capability_chart_json)
            
            # Enhance layout for capability chart
            capability_chart_data['layout']['title'] = {
                'text': 'Process Capability Analysis',
                'font': {'size': 14, 'color': '#1f4e79'}
            }
            
            charts.append({
                'id': 'capability',
                'title': 'Process Capability',
                'subtitle': 'Distribution vs. Specification Limits',
                'data': capability_chart_data['data'],
                'layout': capability_chart_data['layout']
            })
        except Exception as e:
            print(f"WARNING: Capability chart generation failed: {e}")
    
    # 3. Distribution Analysis (Probability Plot) - Secondary Chart
    distribution = result.get('distribution_analysis', {})
    if distribution and not distribution.get('error'):
        try:
            prob_plot_chart_json = _generate_probability_plot_plotly(distribution)
            prob_plot_chart_data = json.loads(prob_plot_chart_json)
            
            # Enhance layout for probability plot
            prob_plot_chart_data['layout']['title'] = {
                'text': 'Distribution Assessment',
                'font': {'size': 14, 'color': '#1f4e79'}
            }
            
            charts.append({
                'id': 'distribution',
                'title': 'Distribution Assessment',
                'subtitle': 'Probability Plot Analysis',
                'data': prob_plot_chart_data['data'],
                'layout': prob_plot_chart_data['layout']
            })
        except Exception as e:
            print(f"WARNING: Probability plot generation failed: {e}")
    
    # Return multi-chart structure or fallback to single chart
    print(f"SUCCESS: Generated {len(charts)} charts for process analysis")
    
    if len(charts) > 1:
        print("SUCCESS: Returning multi-chart structure")
        return json.dumps({
            'type': 'multi_chart',
            'charts': charts,
            'primary_chart': 'stability'
        })
    elif len(charts) == 1:
        print("SUCCESS: Returning single chart fallback")
        # Fallback to single chart format
        chart = charts[0]
        return json.dumps({
            'data': chart['data'],
            'layout': chart['layout']
        })
    else:
        print("WARNING: No charts generated, using simple fallback")
        # Ultimate fallback: Simple line chart
        x_values = list(range(1, len(values) + 1))
        
        trace = {
            "x": x_values,
            "y": values,
            "type": "scatter",
            "mode": "lines+markers",
            "name": "Process Data",
            "line": {"color": "#1f4e79", "width": 2},
            "marker": {"color": "#1f4e79", "size": 6}
        }
        
        layout = {
            "title": {"text": "Process Analysis", "font": {"size": 16, "color": "#1f4e79"}},
            "xaxis": {"title": "Sample Number"},
            "yaxis": {"title": "Measurement Value"}
        }
        
        return json.dumps({"data": [trace], "layout": layout})


print("SUCCESS: ESTIEM EDA Browser Tools loaded - unified with MCP implementation")
